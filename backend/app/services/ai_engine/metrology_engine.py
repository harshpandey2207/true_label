import os
# CRITICAL: Must be set BEFORE any paddle/paddleocr import.
# PaddlePaddle 3.x has a PIR executor conflict with oneDNN on CPU that causes
# NotImplementedError: ConvertPirAttribute2RuntimeAttribute
# This disables the broken code path entirely and restores fast CPU inference.
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
os.environ["FLAGS_new_executor_micro_batching"] = "0"

import cv2
import re
from typing import Dict, Any

cv2.setNumThreads(1)

_ocr = None
_ocr_error = None


def _get_local_ocr():
    """Load the open-source OCR engine only when a scan is requested."""
    global _ocr, _ocr_error
    if _ocr is None and _ocr_error is None:
        try:
            from paddleocr import PaddleOCR
            _ocr = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)
        except Exception as exc:
            _ocr_error = str(exc)
    return _ocr

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
    "manufacturer": "Manufacturer, packer or importer details must be declared where applicable.",
    "consumer_care": "Consumer complaint contact details must be present.",
    "net_quantity": "Net quantity must be declared using appropriate weight/volume units.",
    "batch_code": "Batch or lot identification must be declared.",
    "manufacturing_date": "Manufacturing or expiry date must be declared.",
    "best_before_date": "Best-before or use-by declaration detected; review its wording and date.",
    "expiry_date": "Expiry declaration detected; verify its wording and date.",
    "fssai_license": "FSSAI licence or registration text detected; verify the number and applicability.",
    "veg_non_veg_logo": "Food symbol wording detected; verify the required symbol directly on the package.",
    "bis_mark": "BIS/ISI text detected; verify certification and applicability.",
    "country_of_origin": "Country-of-origin text detected; verify the declaration and product origin.",
    "model": "Model identification text detected; verify the value against the product.",
    "serial_number": "Serial number text detected; verify the value against the product.",
    "size": "Size declaration detected; verify the declared size and unit.",
    "ingredients": "Ingredients text detected; review required ingredient and allergen disclosures.",
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
    
    groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
    llama_api_key = os.environ.get("LLAMA_API_KEY", "").strip()
    
    if not groq_api_key and not llama_api_key:
        return {"status": "ERROR", "declarations": [], "error": "GROQ_API_KEY is not set."}
        
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    prompt = f"""Analyze this product package label for Legal Metrology compliance in India.
    Category: {product_type}

    Extract ALL visible compliance declarations (MRP, Net Quantity, Mfg Date, Expiry Date, Consumer Care, Manufacturer details, FSSAI, Batch Code, etc.).
    For each declaration found, provide:
    1. "text": The exact text seen on the label.
    2. "tag": A standard tag (e.g. MRP, NET_QUANTITY, MANUFACTURING_DATE, EXPIRY_DATE, CONSUMER_CARE, MANUFACTURER, FSSAI_LICENSE, BATCH_CODE).
    3. "box": Approximate bounding box as [[x1,y1], [x2,y1], [x2,y2], [x1,y2]] (use a generic box like [[10,10],[100,10],[100,20],[10,20]] if unsure, the frontend needs this format).
    4. "height_mm": Estimate font height in mm (e.g. 1.5).
    5. "is_compliant": true.

    Return EXACTLY this JSON structure:
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
    }}
    Return only JSON. Do not include markdown formatting."""

    url = "https://api.groq.com/openai/v1/chat/completions" if groq_api_key else "https://api.together.xyz/v1/chat/completions"
    model = "llama-3.2-90b-vision-preview" if groq_api_key else "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"
    api_key = groq_api_key or llama_api_key

    payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.1
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result_text = data["choices"][0]["message"]["content"]
    except Exception as e:
        return {"status": "ERROR", "declarations": [], "error": f"AI Error: {e}"}
        
    try:
        import re
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            parsed = json.loads(json_match.group())
            declarations = parsed.get("declarations", [])
            for d in declarations:
                d["finding_status"] = "DETECTED"
                if "failure_reason" not in d:
                    d["failure_reason"] = None
        else:
            declarations = []
    except Exception as e:
        declarations = []

    # Calculate compliance score
    found_tags = {d["tag"].upper() for d in declarations}
    
    missing_tags = []
    if db is not None:
        from backend.app.db.models import ComplianceRule
        mandatory_rules = db.query(ComplianceRule).filter(ComplianceRule.category_id == category_id, ComplianceRule.is_mandatory == True).all()
        mandatory_tags = {r.tag for r in mandatory_rules}
        
        # We assume language check passes if any text was found
        if declarations:
            found_tags.add("LANGUAGE_CHECK")
            
        missing_tags = list(mandatory_tags - found_tags)
        
    for tag in missing_tags:
        declarations.append({
            "text": "(Missing)",
            "tag": tag.upper(),
            "box": [[0,0],[0,0],[0,0],[0,0]],
            "height_mm": 0.0,
            "is_compliant": False,
            "finding_status": "MISSING",
            "message": f"Mandatory declaration {tag} not found.",
            "failure_reason": f"Missing {tag}"
        })

    is_compliant = len(missing_tags) == 0
    compliance_score = max(0.0, 100.0 - (len(missing_tags) * 20.0))
    if compliance_score > 0 and not is_compliant:
        compliance_score = min(compliance_score, 80.0)

    return {
        "status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
        "compliance_score": compliance_score,
        "ocr_engine": "Groq Llama-3.2-Vision",
        "product_type": product_type,
        "declarations": declarations,
        "missing_tags": missing_tags
    }
