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
    import re
    import io
    import requests
    from PIL import Image, ImageEnhance

    def _get_local_ocr(image_path: str) -> list:
        # Smart pre-processing to stay under OCR.space 1MB limit while maintaining sharpness
        try:
            with Image.open(image_path) as img:
                img = img.convert('L')  # Convert to Grayscale
                
                # Enhance contrast for better OCR
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
                
                # Resize if too large, but keep it sharp enough
                w, h = img.size
                max_dim = 1800
                if max(w, h) > max_dim:
                    scale = max_dim / max(w, h)
                    img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
                
                # Iteratively compress to fit within 950KB (OCR.space limit is 1024KB)
                quality = 90
                while quality > 30:
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=quality)
                    if buffer.tell() < 950 * 1024:
                        break
                    quality -= 10
                
                base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Image processing failed: {e}")

        payload = {
            'base64Image': f"data:image/jpeg;base64,{base64_image}",
            'language': 'eng',
            'isOverlayRequired': True,
            'OCREngine': 2  # Engine 2 is better for complex/blurry text
        }
        headers = {
            'apikey': 'helloworld'
        }
        
        resp = requests.post('https://api.ocr.space/parse/image', data=payload, headers=headers, timeout=60)
        
        if resp.status_code != 200:
            raise Exception(f"OCR API failed: {resp.text}")
            
        result = resp.json()
        if result.get('IsErroredOnProcessing'):
            error_msg = result.get('ErrorMessage', ['Unknown error'])[0]
            if "not a valid image" in error_msg.lower() or "limit" in error_msg.lower():
                # Fallback to Engine 1 if Engine 2 rejects the image size
                payload['OCREngine'] = 1
                resp = requests.post('https://api.ocr.space/parse/image', data=payload, headers=headers, timeout=60)
                result = resp.json()
                if result.get('IsErroredOnProcessing'):
                    raise Exception(result.get('ErrorMessage', ['Unknown error'])[0])
            else:
                raise Exception(error_msg)
            
        parsed_results = result.get('ParsedResults', [])
        if not parsed_results:
            return []
            
        lines = parsed_results[0].get('TextOverlay', {}).get('Lines', [])
        extracted_data = []
        
        for line in lines:
            text = line.get('LineText', '')
            words = line.get('Words', [])
            if not words:
                continue
                
            left = min(w.get('Left', 0) for w in words)
            top = min(w.get('Top', 0) for w in words)
            right = max(w.get('Left', 0) + w.get('Width', 0) for w in words)
            bottom = max(w.get('Top', 0) + w.get('Height', 0) for w in words)
            
            box = [[left, top], [right, top], [right, bottom], [left, bottom]]
            extracted_data.append((box, text, 0.9))
            
        return extracted_data

    # 1. OCR Extraction
    try:
        parsed_lines = _get_local_ocr(image_path)
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "declarations": []}

    # 2. Rule Engine matching
    declarations = []
    
    try:
        with Image.open(image_path) as img:
            w, h = img.size
            scale = 1.0
            max_dim = 1800
            if max(w, h) > max_dim:
                scale = max(w, h) / max_dim
    except:
        scale = 1.0

    for item in parsed_lines:
        box, text, conf = item
        text_lower = text.lower()
        
        tag = None
        failure_reason = None

        if any(k in text_lower for k in ["mrp", "m.r.p", "maximum retail price", "rs.", "incl. of all taxes", "inclusive of all taxes", "?"]):
            tag = "mrp"
        elif any(k in text_lower for k in ["net qty", "net weight", "net volume", "net quantity", "net vol"]):
            tag = "net_quantity"
        elif any(k in text_lower for k in ["mfg", "mfd", "manufactured date", "manufacturing date", "pkd", "packed on"]):
            tag = "manufacturing_date"
        elif any(k in text_lower for k in ["exp", "use by", "best before", "expiry"]):
            tag = "manufacturing_date"
        elif any(k in text_lower for k in ["customer care", "consumer care", "toll free", "feedback", "complaints", "email", "helpline", "customercare", "care@"]):
            tag = "consumer_care"
        elif any(k in text_lower for k in ["store below", "protect from", "do not freeze", "storage:", "keep away", "dry place"]):
            tag = "storage"
        elif any(k in text_lower for k in ["marketed by", "manufactured by", "mfd. by", "mfd by", "mfg. lic", "mfg by", "cipla health", "ltd.", "private limited"]):
            tag = "manufacturer"
        elif any(k in text_lower for k in ["batch", "lot no", "b. no", "b.no", "batch code"]):
            tag = "batch_code"
        elif any(k in text_lower for k in ["fssai", "lic. no", "license no"]):
            tag = "fssai_license"

        if tag:
            x_coords = [p[0] for p in box]
            y_coords = [p[1] for p in box]
            box_height_px = (max(y_coords) - min(y_coords)) * scale
            height_mm = round((box_height_px * distance_mm) / focal_length_px, 2)
            
            is_compliant = True
            
            # Powerful Rule Engine Validations
            if tag == "net_quantity":
                if weight_under_10g:
                    failure_reason = "Product under 10g may have exemptions, check Rule 26."
            elif tag == "mrp":
                if not any(k in text_lower for k in ["rs", "?", "inclusive", "incl"]):
                    is_compliant = False
                    failure_reason = "MRP must include 'Rs' or '?' and state 'Inclusive of all taxes'."
            
            declarations.append({
                "text": text,
                "tag": tag.upper(),
                "finding_status": "DETECTED" if is_compliant else "FLAGGED",
                "field": tag,
                "confidence": round(conf, 2),
                "box": box,
                "height_mm": height_mm,
                "is_compliant": is_compliant,
                "message": failure_reason if failure_reason else "Declaration verified.",
                "failure_reason": failure_reason
            })

    found_tags = {d["tag"].upper() for d in declarations}
    
    missing_tags = []
    if db is not None:
        from backend.app.db.models import ComplianceRule
        mandatory_rules = db.query(ComplianceRule).filter(ComplianceRule.category_id == category_id, ComplianceRule.is_mandatory == True).all()
        mandatory_tags = {r.tag for r in mandatory_rules}
        
        has_valid_language = any(re.search(r'[a-zA-Zऀ-ॿ]', p[1]) for p in parsed_lines)
        if has_valid_language:
            found_tags.add("LANGUAGE_CHECK")
            
        missing_tags = list(mandatory_tags - found_tags)

    return {
        "status": "POTENTIAL_ISSUES" if (len(declarations) == 0 or len(missing_tags) > 0 or any(not d["is_compliant"] for d in declarations)) else "NO_FLAGS",
        "ocr_engine": "OCR.space (Grayscale Optimized)",
        "product_type": product_type,
        "declarations": declarations,
        "missing_tags": missing_tags,
        "warnings": ["Scanner reverted to OCR.space per user request."],
        "ar_parameters": {
            "distance_mm": distance_mm,
            "focal_length_px": focal_length_px
        }
    }
