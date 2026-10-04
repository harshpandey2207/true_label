import jsondef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
import base64def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
import urllib.requestdef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
import urllib.errordef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
from typing import Any, Dict, List, Tupledef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
from fastapi import HTTPExceptiondef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
CATEGORIES = [def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    "General Packaged Commodity",def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    "Food & Beverages",def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    "Electronics & Appliances",def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    "Cosmetics, Ointments & Pharma Goods",def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    "Apparel & Textiles",def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    "Medical Devices",def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
]def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def generate_label_draft(def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    product_name: str,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    product_category: str,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    shape: str,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    dimensions: str,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    custom_prompt: str,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    label_values: Dict[str, Any],def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    additional_details: str,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    images: List[Tuple[str, bytes]],def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    side_count: int,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
) -> dict:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    import osdef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    llama_api_key = os.environ.get("LLAMA_API_KEY", "").strip()def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    images_b64 = []def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    for _, img_bytes in images:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        from PIL import Imagedef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        import iodef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        try:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            img = Image.open(io.BytesIO(img_bytes))def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            if img.mode != "RGB":def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
                img = img.convert("RGB")def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            buffer = io.BytesIO()def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            img.save(buffer, format="JPEG", quality=75)def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            images_b64.append(base64.b64encode(buffer.getvalue()).decode("utf-8"))def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        except Exception:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            continuedef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    num_sides = max(side_count, len(images_b64)) if len(images_b64) > 0 else side_countdef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    compliance_block = "\n".join([f"- {k}: {v}" for k, v in label_values.items()])def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    prompt = f"""You are a master packaging designer and Legal Metrology expert.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
I am providing {len(images_b64)} reference image(s) of a product package. def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
If images are provided, extract the exact brand colors (primary, secondary, accent) and typography style.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
Then, create a complete, dynamic, beautiful vector layout (SVG code) for a fully compliant replacement label for {num_sides} sides.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
PRODUCT DETAILS:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- Name: {product_name}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- Category: {product_category}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- Shape: {shape}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- Dimensions: {dimensions}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- User Instructions: {custom_prompt if custom_prompt else "Match brand DNA"}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- Additional Details: {additional_details}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
MANDATORY COMPLIANCE DATA TO INJECT:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
{compliance_block if compliance_block else "Extract all visible compliance info"}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
INSTRUCTIONS:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- You must return a strict JSON object containing an array of sides.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- Inside each side, provide raw, complete, beautifully styled SVG code (inside the "svg_code" string field).def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- The SVG MUST have a viewBox (e.g. viewBox="0 0 800 1200") to be responsive.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- Do NOT use external images inside the SVG, use only vector shapes, rects, paths, and <text>.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- The front label SVG should be highly branded with background colors/patterns matching the brand DNA.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- The back/side label SVGs MUST contain all mandatory compliance data formatted clearly.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- Ensure Rule 7 compliance: all text elements must be clearly legible with good contrast.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
- Ensure the SVG string is properly escaped for JSON.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
Return this EXACT JSON format (and nothing else):def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
{{def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
  "brand_dna": {{def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    "primary_color": "#hex", "font_style": "description"def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
  }},def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
  "sides": [def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    {{def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
      "side_name": "Front Label",def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
      "svg_code": "<svg xmlns=\\\"http://www.w3.org/2000/svg\\\" viewBox=\\\"0 0 800 1200\\\">...fully styled SVG...</svg>"def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    }}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
  ]def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
}}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
Generate {num_sides} sides in the array. Return only the raw JSON.def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
"""def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    for img_b64 in images_b64:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        messages[0]["content"].append({def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            "type": "image_url",def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        })def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    if not groq_api_key and not llama_api_key:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        raise ValueError("GROQ_API_KEY environment variable is missing. Required for Llama Vision API.")def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    url = "https://api.groq.com/openai/v1/chat/completions" if groq_api_key else "https://api.together.xyz/v1/chat/completions"def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    model = "llama-3.2-11b-vision-preview" if groq_api_key else "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    api_key = groq_api_key or llama_api_keydef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    payload = json.dumps({def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        "model": model,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        "messages": messages,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        "max_tokens": 4096,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        "temperature": 0.3def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    }).encode("utf-8")def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    req = urllib.request.Request(url, data=payload, headers={def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        "Content-Type": "application/json",def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        "Authorization": f"Bearer {api_key}"def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    }, method="POST")def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    try:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        with urllib.request.urlopen(req, timeout=90) as resp:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            data = json.loads(resp.read().decode("utf-8"))def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            result_text = data["choices"][0]["message"]["content"]def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    except urllib.error.HTTPError as e:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        body = e.read().decode("utf-8")def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        raise ValueError(f"AI Model Error: {body}")def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    try:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        import redef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        json_match = re.search(r'\{[\s\S]*\}', result_text)def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        if json_match:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            label_data = json.loads(json_match.group())def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        else:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
            raise ValueError("No JSON found")def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    except Exception as e:def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        raise ValueError(f"AI output parsing failed: {e}\\nRaw output: {result_text}")def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    # Format output for the UIdef _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    return {def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        "label_data": label_data,def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        "warnings": [],def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
        "engine_used": "Groq Llama-3.2-90B-Vision"def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
    }def _generate_svg_with_groq(image_path: str, context_details: dict) -> str:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image

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
            
        import re
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
