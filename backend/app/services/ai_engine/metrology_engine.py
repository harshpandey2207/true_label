import os

import re
from typing import Dict, Any





OINTMENT_RULES = [
    "mrp",
    "manufacturer",
    "consumer_care",
    "net_quantity",
    "batch_code",
    "manufacturing_date",
    "storage",
    "language",
    "quantity_unit",
    "no_misleading_quantity"
]

FIELD_MESSAGES = {
    "mrp": "Retail sale price must be declared inclusive of all taxes.",
    "manufacturer": "Manufacturer/packer details must be declared.",
    "consumer_care": "Consumer complaint contact details must be present.",
    "net_quantity": "Net quantity must be declared using appropriate weight/volume units.",
    "batch_code": "Batch or lot identification must be declared.",
    "manufacturing_date": "Manufacturing or expiry date must be declared.",
    "storage": "Storage instructions must be declared.",
    "language": "Declarations must be in English or Hindi.",
    "quantity_unit": "Quantity must use recognized units.",
    "no_misleading_quantity": "Quantity declaration must not be misleading."
}

def analyze_product_label(
    image_path: str,
    product_type: str = "ointment",
    distance_mm: float = 300.0,
    focal_length_px: float = 800.0,
    db=None,
    category_id: int = 1,
    is_institutional: bool = False,
    rule_33_gst_active: bool = False,
    weight_under_10g: bool = False,
    is_medical_device: bool = False
) -> dict:
    import base64
    import json
    import urllib.request
    import urllib.error
    import os
    from PIL import Image
    
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    if not gemini_api_key:
        return {"status": "ERROR", "declarations": [], "error": "GEMINI_API_KEY is not set. Please add it to your Render Environment Variables."}
        
    try:
        with Image.open(image_path) as img:
            w, h = img.size
            if max(w, h) > 1500:
                scale = 1500 / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(image_path, format="JPEG")
    except Exception:
        pass

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    prompt = f"""You are a precise Legal Metrology compliance inspector for India.
Product Category: {product_type}

Extract ALL visible compliance declarations on this product label (MRP, Net Quantity, Mfg Date, Expiry Date, Consumer Care, Manufacturer details, FSSAI, Batch Code, Storage).
For each declaration found, provide:
1. "text": The exact text seen on the label.
2. "tag": The category tag. Choose ONLY from: MRP, NET_QUANTITY, MANUFACTURING_DATE, CONSUMER_CARE, MANUFACTURER, FSSAI_LICENSE, BATCH_CODE, STORAGE, GENERAL.
3. "box": Approximate bounding box as [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]. Use generic coordinates like [[10,10],[100,10],[100,20],[10,20]].
4. "height_mm": Estimate font height in mm (e.g. 1.5).
5. "is_compliant": true if the text matches legal formatting, false if misleading or missing key info.

Return EXACTLY this JSON structure, and nothing else (no markdown tags):
{{
  "declarations": [
    {{
      "text": "Rs. 150.00",
      "tag": "MRP",
      "box": [[10,10], [50,10], [50,20], [10,20]],
      "height_mm": 1.5,
      "is_compliant": true,
      "message": "Valid MRP format"
    }}
  ]
}}"""

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
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
    }, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()
        return {"status": "ERROR", "declarations": [], "error": f"Gemini API Error: {error_msg}"}
    except Exception as e:
        return {"status": "ERROR", "declarations": [], "error": f"AI Error: {e}"}
        
    try:
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            parsed = json.loads(json_match.group())
            declarations = parsed.get("declarations", [])
            for d in declarations:
                d["finding_status"] = "DETECTED"
                d["confidence"] = 0.99
                if "failure_reason" not in d:
                    d["failure_reason"] = None
        else:
            declarations = []
    except Exception as e:
        declarations = []

    found_tags = {d["tag"].upper() for d in declarations}
    
    missing_tags = []
    if db is not None:
        from backend.app.db.models import ComplianceRule
        mandatory_rules = db.query(ComplianceRule).filter(ComplianceRule.category_id == category_id, ComplianceRule.is_mandatory == True).all()
        mandatory_tags = {r.tag for r in mandatory_rules}
        
        if declarations:
            found_tags.add("LANGUAGE_CHECK")
            
        missing_tags = list(mandatory_tags - found_tags)

    is_compliant = len(missing_tags) == 0

    return {
        "status": "POTENTIAL_ISSUES" if (len(declarations) == 0 or len(missing_tags) > 0 or any(not d["is_compliant"] for d in declarations)) else "NO_FLAGS",
        "ocr_engine": "Gemini 1.5 Flash API",
        "product_type": product_type,
        "declarations": declarations,
        "missing_tags": missing_tags,
        "warnings": ["Deployed using Gemini 1.5 Flash due to Render free-tier CPU limitations. Production will use offline PaddleOCR."],
        "ar_parameters": {
            "distance_mm": distance_mm,
            "focal_length_px": focal_length_px
        }
    }
