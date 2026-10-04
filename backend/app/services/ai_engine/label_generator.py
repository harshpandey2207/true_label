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
    label_values: dict,
    additional_details: str,
    images: list,
    side_count: int = 2
) -> dict:
    
    import os
    import json
    import base64
    import urllib.request
    import urllib.error

    gemini_api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing. Please add it to your Render Environment Variables.")

    images_b64 = []
    
    for _, img_bytes in images:
        try:
            from PIL import Image
            import io
            with Image.open(io.BytesIO(img_bytes)) as img:
                w, h = img.size
                if max(w, h) > 800:
                    scale = 800 / max(w, h)
                    img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    img_bytes = buffer.getvalue()
        except Exception:
            pass
        
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        images_b64.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": img_b64
            }
        })

    prompt_text = f"""You are a senior packaging designer and Legal Metrology compliance officer.
Your task is to generate a beautiful, compliant product label for a new product based on the provided requirements.

Product Name: {product_name}
Category: {product_category}
Target Shape: {shape}
Dimensions: {dimensions}
Number of Label Panels/Sides: {side_count}

MANDATORY DECLARATION DATA (These must be perfectly visible on the label):
{json.dumps(label_values, indent=2)}

Additional Context/Notes:
{additional_details}

User's Custom Design Prompt:
{custom_prompt}

Return a completely valid SVG string for the requested {side_count} panels. 
Wrap the panels inside a single <svg viewBox="0 0 1600 800"> (if multiple sides).
Make the design professional, highly realistic, and use beautiful fonts and contrasting colors.

Respond with EXACTLY this JSON structure:
{{
  "svg_body": "<svg>...</svg>",
  "explanation": "Brief explanation of the layout and where declarations are placed."
}}"""

    contents = [{"parts": [{"text": prompt_text}] + images_b64}]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"

    payload = json.dumps({
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
    }, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()
        raise ValueError(f"Gemini API Error: {error_msg}")
    except Exception as e:
        raise ValueError(f"AI API Error: {e}")
        
    try:
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            label_data = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found")
    except Exception as e:
        raise ValueError(f"AI output parsing failed: {e}\nRaw output: {result_text}")

    return {
        "label_data": label_data,
        "warnings": ["Using Gemini 1.5 Flash due to Render memory limits."],
        "engine_used": "Gemini 1.5 Flash API"
    }
