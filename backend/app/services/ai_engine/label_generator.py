import json
import base64
import urllib.request
import urllib.error
from typing import Any, Dict, List, Tuple
from fastapi import HTTPException

CATEGORIES = [
    "General Packaged Commodity",
    "Food & Beverages",
    "Electronics & Appliances",
    "Cosmetics, Ointments & Pharma Goods",
    "Apparel & Textiles",
    "Medical Devices",
]

def generate_label_draft(
    product_name: str,
    product_category: str,
    shape: str,
    dimensions: str,
    custom_prompt: str,
    label_values: Dict[str, Any],
    additional_details: str,
    images: List[Tuple[str, bytes]],
    side_count: int,
) -> dict:
    
    import os
    groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
    llama_api_key = os.environ.get("LLAMA_API_KEY", "").strip()

    images_b64 = []
    
    for _, img_bytes in images:
        from PIL import Image
        import io
        try:
            img = Image.open(io.BytesIO(img_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=75)
            images_b64.append(base64.b64encode(buffer.getvalue()).decode("utf-8"))
        except Exception:
            continue
        
    num_sides = max(side_count, len(images_b64)) if len(images_b64) > 0 else side_count
    compliance_block = "\n".join([f"- {k}: {v}" for k, v in label_values.items()])
    
    prompt = f"""You are a master packaging designer and Legal Metrology expert.
I am providing {len(images_b64)} reference image(s) of a product package. 
If images are provided, extract the exact brand colors (primary, secondary, accent) and typography style.

Then, create a complete, dynamic, beautiful vector layout (SVG code) for a fully compliant replacement label for {num_sides} sides.

PRODUCT DETAILS:
- Name: {product_name}
- Category: {product_category}
- Shape: {shape}
- Dimensions: {dimensions}
- User Instructions: {custom_prompt if custom_prompt else "Match brand DNA"}
- Additional Details: {additional_details}

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

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    
    for img_b64 in images_b64:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
        })

    if not groq_api_key and not llama_api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing. Required for Llama Vision API.")

    url = "https://api.groq.com/openai/v1/chat/completions" if groq_api_key else "https://api.together.xyz/v1/chat/completions"
    model = "llama-3.2-11b-vision-preview" if groq_api_key else "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"
    api_key = groq_api_key or llama_api_key

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
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result_text = data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise ValueError(f"AI Model Error: {body}")

    try:
        import re
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            label_data = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found")
    except Exception as e:
        raise ValueError(f"AI output parsing failed: {e}\\nRaw output: {result_text}")

    # Format output for the UI
    return {
        "label_data": label_data,
        "warnings": [],
        "engine_used": "Groq Llama-3.2-90B-Vision"
    }
