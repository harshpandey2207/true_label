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

def analyze_product_label(image_path: str, product_type: str = "ointment", distance_mm: float = 300.0, focal_length_px: float = 800.0, db=None, category_id: int = 1, is_institutional: bool = False, rule_33_gst_active: bool = False, weight_under_10g: bool = False, is_medical_device: bool = False) -> Dict[str, Any]:
    from PIL import Image
    try:
        with Image.open(image_path) as img:
            orig_w, orig_h = img.size
            h_img, w_img = orig_h, orig_w
            
            max_side = 500
            scale = 1.0
            if max(orig_h, orig_w) > max_side:
                scale = max_side / max(orig_h, orig_w)
                new_w, new_h = int(orig_w * scale), int(orig_h * scale)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(image_path, format="JPEG")
                h_img, w_img = new_h, new_w
    except Exception as e:
        return {"status": "ERROR", "declarations": [], "error": f"Could not read image file: {e}"}

    parsed_lines = []

    # Using OCR.space API
    try:
        import requests
        import base64
        
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
        payload = {
            'base64Image': f"data:image/jpeg;base64,{base64_image}",
            'language': 'eng',
            'isOverlayRequired': True
        }
        headers = {
            'apikey': 'helloworld'
        }
        
        response = requests.post('https://api.ocr.space/parse/image', data=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('IsErroredOnProcessing'):
            raise Exception(result.get('ErrorMessage', ['Unknown error'])[0])
            
        parsed_results = result.get('ParsedResults', [])
        if parsed_results:
            lines = parsed_results[0].get('TextOverlay', {}).get('Lines', [])
            for line in lines:
                linetext = line.get('LineText', '').strip()
                if not linetext: continue
                
                words = line.get('Words', [])
                if words:
                    top = min(w['Top'] for w in words)
                    left = min(w['Left'] for w in words)
                    height = max(w['Height'] for w in words)
                    width = sum(w['Width'] for w in words)
                    
                    box = [
                        [left, top],
                        [left + width, top],
                        [left + width, top + height],
                        [left, top + height]
                    ]
                    parsed_lines.append((box, linetext, 0.95))
                    
    except Exception as exc:
        return {
            "status": "ERROR",
            "declarations": [],
            "missing_tags": [],
            "error": f"OCR API failed: {exc}",
        }

    misleading_patterns = [
        r"\bminimum\s+\d+(?:[.,]\d+)?",
        r"\bnot\s+less\s+than\s+\d+(?:[.,]\d+)?",
        r"\bat\s+least\s+\d+(?:[.,]\d+)?",
        r"\bapproximately\s+\d+(?:[.,]\d+)?",
        r"\bapprox\.?\s*\d+(?:[.,]\d+)?"
    ]

    declarations = []
    
    # Pre-scan full document context to help multi-line detection
    full_doc_text = " ".join([p[1] for p in parsed_lines]).lower()
    has_global_mrp_header = any(k in full_doc_text for k in ["m.r.p", "mrp", "max. retail price", "retail price"])

    for idx, (box, text, conf) in enumerate(parsed_lines):
        # Calculate bounding box height
        pts = box.tolist() if hasattr(box, 'tolist') else box
        y_coords = [p[1] for p in pts]
        box_height_px = (max(y_coords) - min(y_coords)) / scale
        
        # Physical height estimate in mm via AR geometry
        height_mm = round((box_height_px * distance_mm) / focal_length_px, 2)
        
        tag = "general"
        is_compliant = True
        failure_reason = None
        
        text_lower = text.lower()
        has_digits = bool(re.search(r'\d', text))
        
        # Context window: inspect previous and next lines
        prev_text = parsed_lines[idx - 1][1].lower() if idx > 0 else ""
        next_text = parsed_lines[idx + 1][1].lower() if idx < len(parsed_lines) - 1 else ""
        context_window = f"{prev_text} {text_lower} {next_text}"
        
        # --- 1. MRP Detection ---
        # Matches: "M.R.P. Rs. 105.41", "M.R.P. Rs.", "105.41" next to MRP, "₹105", "Rs. 105", etc.
        is_mrp_text = any(k in text_lower for k in ["m.r.p", "mrp", "r.p.", "₹", "inr", "max. retail"])
        is_rs_number = bool(re.search(r'(?:rs\.?|₹|inr)\s*\d+', text_lower))
        is_price_value_near_mrp = (has_global_mrp_header or "mrp" in context_window or "m.r.p" in context_window) and bool(re.search(r'^\d+[.,]\d{2}$', text_lower))
        
        if is_mrp_text or is_rs_number or is_price_value_near_mrp:
            tag = "mrp"

        # Unit sale price is a separate declaration; it cannot be derived from
        # MRP alone because its basis depends on the declared quantity/unit.
        elif "unit sale price" in text_lower or "unit price" in text_lower or re.search(
            r"(?:₹\s*\d|rs\.?\s*\d).{0,30}(?:/|\bper\b)\s*(?:100\s*)?(?:kg|g|l|ml|piece|unit)\b",
            text_lower,
        ):
            tag = "unit_sale_price"

        # --- 2. Net Quantity Detection ---
        elif any(k in text_lower for k in ["net wt", "net weight", "net qty", "net quantity", " 30g", "30 g", "30g", "wt.", "weight"]) or \
             (bool(re.search(r'\b\d+\s*(?:g|gm|gms|ml|l|kg|mg)\b', text_lower)) and not any(k in text_lower for k in ["usp", "ip", "w/w", "%", "iodine"])):
            tag = "net_quantity"

        # --- 3. Batch Code Detection ---
        elif any(k in text_lower for k in ["batch", "lot no", "b. no", "b.no", "batch no"]):
            tag = "batch_code"
        elif "batch" in prev_text and has_digits:
            tag = "batch_code"

        # --- 4. Manufacturing & Expiry Date Detection ---
        elif any(k in text_lower for k in ["mfg", "mfd", "expiry", "exp.", "exp date", "pkd", "packed", "date"]):
            tag = "manufacturing_date"
        elif any(k in prev_text for k in ["mfg", "expiry", "exp"]) and bool(re.search(r'\d{2}/\d{4}|\d{2}/\d{2}', text_lower)):
            tag = "manufacturing_date"

        # --- 5. Consumer Care Detection ---
        elif any(k in text_lower for k in ["toll free", "feedback", "complaint", "queries", "customer care", "helpline", "email:"]):
            tag = "consumer_care"

        # --- 6. Storage Instructions ---
        elif any(k in text_lower for k in ["store below", "protect from", "do not freeze", "storage:", "keep away", "dry place"]):
            tag = "storage"

        # --- 7. Manufacturer / Marketing Details ---
        elif any(k in text_lower for k in ["marketed by", "manufactured by", "mfd. by", "mfd by", "mfg. lic", "mfg by", "cipla health"]):
            tag = "manufacturer"

        # Check for misleading quantity expressions
        if tag == "net_quantity":
            for pattern in misleading_patterns:
                if re.search(pattern, text_lower):
                    is_compliant = False
                    failure_reason = "Potentially misleading quantity expression detected."
                    break

        # Normalize coordinates to 250x350 preview canvas
        scaled_box = [
            [int((pt[0] / (w_img * scale)) * 250), int((pt[1] / (h_img * scale)) * 350)]
            for pt in pts
        ]

    # Determine dynamic message from Database Rules
        db_message = "Declaration verified."
        if db is not None:
            # Query the database for the specific compliance rule
            from backend.app.db.models import ComplianceRule
            rule = db.query(ComplianceRule).filter(ComplianceRule.tag == tag.upper(), ComplianceRule.category_id == category_id).first()
            if rule and rule.legal_act_reference:
                db_message = f"Prototype rule reference: {rule.legal_act_reference}"
            else:
                db_message = FIELD_MESSAGES.get(tag, "Declaration verified.")
        else:
            db_message = FIELD_MESSAGES.get(tag, "Declaration verified.")

        declarations.append({
            "text": text,
            "tag": tag.upper(),
            "field": tag,
            "confidence": round(conf, 2),
            "box": scaled_box,
            "height_mm": height_mm,
            "is_compliant": is_compliant,
            "message": failure_reason if failure_reason else db_message,
            "failure_reason": failure_reason
        })

    # Check missing mandatory tags against the Database
    missing_tags = []
    if db is not None:
        from backend.app.db.models import ComplianceRule
        mandatory_rules = db.query(ComplianceRule).filter(ComplianceRule.category_id == category_id, ComplianceRule.is_mandatory == True).all()
        mandatory_tags = {r.tag for r in mandatory_rules}
        found_tags = {d["tag"].upper() for d in declarations}

        # This prototype has no ruleset for applying these context-dependent
        # exemptions. Do not silently remove declarations based on a checkbox.
        has_valid_language = any(re.search(r'[a-zA-Z\u0900-\u097F]', p[1]) for p in parsed_lines)
        if has_valid_language:
            found_tags.add("LANGUAGE_CHECK")

        missing_tags = list(mandatory_tags - found_tags)

    warnings = [
        "Displayed text-height values are rough estimates from fixed, uncalibrated camera geometry. They are not used to determine scan status or establish compliance."
    ]
    if is_institutional or rule_33_gst_active or weight_under_10g or is_medical_device:
        warnings.append("Special category or exemption context was supplied but is not automatically evaluated. Review the applicable rules manually.")
    
    status = "POTENTIAL_ISSUES" if (len(declarations) == 0 or len(missing_tags) > 0 or any(not d["is_compliant"] for d in declarations)) else "NO_FLAGS"
    
    return {
        "status": status,
        "product_type": product_type,
        "declarations": declarations,
        "missing_tags": missing_tags,
        "warnings": warnings,
        "ar_parameters": {
            "distance_mm": distance_mm,
            "focal_length_px": focal_length_px
        }
    }
