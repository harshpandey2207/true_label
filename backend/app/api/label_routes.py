import os
import base64
import json
import tempfile
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import urllib.request
import urllib.error

router = APIRouter(tags=["Label Generator"])

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
LLAMA_API_KEY = os.environ.get("LLAMA_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def call_llama_vision(prompt: str, images_b64: List[str]) -> str:
    """Call Llama-3.2-90B-Vision-Instruct (Open Source) via Together AI or Groq API."""
    if not LLAMA_API_KEY and not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="No Open Source API key set.")
        
    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}]
        }
    ]
    
    for img_b64 in images_b64:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
        })
        
    if GROQ_API_KEY:
        url = "https://api.groq.com/openai/v1/chat/completions"
        model = "llama-3.2-90b-vision-preview"
        api_key = GROQ_API_KEY
    else:
        url = "https://api.together.xyz/v1/chat/completions"
        model = "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"
        api_key = LLAMA_API_KEY
        
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.3
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise HTTPException(status_code=502, detail=f"Llama API error: {body}")

def call_gemini_vision(prompt: str, images_b64: List[str]) -> str:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set.")
    parts = []
    for img_b64 in images_b64:
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_b64}})
    parts.append({"text": prompt})
    payload = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.4, "topK": 32, "topP": 1, "maxOutputTokens": 4096}
    }).encode("utf-8")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise HTTPException(status_code=502, detail=f"Gemini error: {body}")


@router.post("/generate")
async def generate_label(
    images: List[UploadFile] = File(...),
    product_name: str = Form(...),
    product_category: str = Form("General Packaged Commodity"),
    shape: str = Form("Rectangular"),
    dimensions: str = Form("10cm x 15cm"),
    custom_prompt: str = Form(""),
    missing_tag_values: str = Form("{}"), 
    model_override: str = Form("auto")  # 'llama' or 'gemini' or 'auto'
):
    temp_dir = tempfile.mkdtemp()
    images_b64 = []
    try:
        for img in images:
            temp_path = os.path.join(temp_dir, img.filename or "image.jpg")
            with open(temp_path, "wb") as f:
                f.write(await img.read())
            with open(temp_path, "rb") as f:
                images_b64.append(base64.b64encode(f.read()).decode("utf-8"))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    try:
        tag_values = json.loads(missing_tag_values)
    except Exception:
        tag_values = {}

    mrp_value = tag_values.get("MRP", tag_values.get("mrp", ""))
    net_qty = tag_values.get("NET_QUANTITY", tag_values.get("net_quantity", ""))
    usp_value = ""
    if mrp_value:
        try:
            usp_value = f"₹{float(mrp_value.replace('₹','').replace('Rs','').strip()):.2f}"
        except Exception:
            usp_value = mrp_value

    num_sides = len(images_b64)
    compliance_block = "\n".join([f"- {k}: {v}" for k, v in tag_values.items()])
    if usp_value:
        compliance_block += f"\n- USP (Unit Sale Price, auto-calculated): {usp_value}"

    prompt = f"""You are a master packaging designer and Legal Metrology expert.
I am providing {num_sides} reference image(s) of a product package. 
Extract the exact brand colors (primary, secondary, accent) and typography style.

Then, create a complete, dynamic, beautiful vector layout (SVG code) for a fully compliant replacement label for EACH uploaded image side.

PRODUCT DETAILS:
- Name: {product_name}
- Shape: {shape}
- Dimensions: {dimensions}
- User Instructions: {custom_prompt if custom_prompt else "Match brand DNA"}

MANDATORY COMPLIANCE DATA TO INJECT:
{compliance_block if compliance_block else "Extract all visible compliance info"}

INSTRUCTIONS:
- You must return a strict JSON object containing an array of sides.
- Inside each side, provide raw, complete, beautifully styled SVG code (inside the "svg_code" string field).
- The SVG MUST have a viewBox (e.g. viewBox="0 0 800 1200") to be responsive.
- Do NOT use external images inside the SVG, use only vector shapes, rects, paths, and <text>.
- The front label SVG should be highly branded with background colors/patterns matching the brand DNA.
- The back/side label SVGs MUST contain all mandatory compliance data formatted clearly.
- Ensure Rule 7 compliance: all text elements must be clearly legible with good contrast.
- Ensure the SVG string is properly escaped for JSON.

Return this EXACT JSON format (and nothing else):
{{
  "brand_dna": {{
    "primary_color": "#hex", "font_style": "description"
  }},
  "sides": [
    {{
      "side_name": "Front Label",
      "svg_code": "<svg xmlns=\\\"http://www.w3.org/2000/svg\\\" viewBox=\\\"0 0 800 1200\\\">...fully styled SVG...</svg>"
    }}
  ]
}}
Generate {num_sides} sides in the array. Return only the raw JSON.
"""

    used_model = "Llama-3.2-Vision (Open Source)"
    if (model_override == "llama" or (model_override == "auto" and (LLAMA_API_KEY or GROQ_API_KEY))):
        try:
            result_text = call_llama_vision(prompt, images_b64)
        except Exception as e:
            # We want to see the ACTUAL Groq error, not hide it behind Gemini fallback
            raise HTTPException(status_code=502, detail=f"Groq/Llama API Error: {str(e)}")
    else:
        used_model = "Gemini-2.0-Flash (Fallback)"
        result_text = call_gemini_vision(prompt, images_b64)

    # Extract JSON
    try:
        import re
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            label_data = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI output parsing failed: {e}\nRaw output: {result_text}")

    return {"success": True, "label_data": label_data, "usp_auto_calculated": usp_value, "model_used": used_model}
