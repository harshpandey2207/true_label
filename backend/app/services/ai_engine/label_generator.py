import base64
import json
import urllib.request
import urllib.error
import os
import re
from PIL import Image

def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not gemini_api_key:
        raise Exception("GEMINI_API_KEY is not set. Please add it to your Render Environment Variables.")

    try:
        with Image.open(image_path) as img:
            w, h = img.size
            if max(w, h) > 1000:
                scale = 1000 / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(image_path, format="JPEG")
    except Exception:
        pass

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = f"""You are a packaging design AI.
The user wants to generate a new compliant product label based on the attached reference image.
Make sure to address these missing requirements: {context_details.get('missing_tags', '')}

Additional details from user: {context_details.get('user_prompt', '')}

Return ONLY valid SVG code for the label. No markdown formatting, no explanations. 
Start exactly with <svg and end exactly with </svg>."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"

    payload = json.dumps({
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_b64
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
    }, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            svg_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
        svg_match = re.search(r'(<svg[\s\S]*?</svg>)', svg_text, re.IGNORECASE)
        if svg_match:
            return svg_match.group(1)
        return svg_text.strip()
    except Exception as e:
        raise Exception(f"Gemini API Error: {e}")

def generate_compliant_label(
    category_name: str,
    missing_tags: str,
    tag_values: dict,
    reference_image_paths: list,
    user_prompt: str = ""
) -> dict:
    if not reference_image_paths:
        return {"status": "ERROR", "svg_body": "", "error": "No reference images provided."}

    context = {
        "category": category_name,
        "missing_tags": missing_tags,
        "tag_values": tag_values,
        "user_prompt": user_prompt
    }

    try:
        svg_result = _generate_svg_with_groq(reference_image_paths[0], context)
        return {
            "status": "SUCCESS",
            "svg_body": svg_result,
            "error": None
        }
    except Exception as e:
        return {"status": "ERROR", "svg_body": "", "error": str(e)}
