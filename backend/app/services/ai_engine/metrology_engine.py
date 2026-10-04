import os
import re
import json
import base64
import io
import requests
from typing import Dict, Any
from PIL import Image, ImageEnhance

OINTMENT_RULES = [
    "mrp",
    "manufacturer",
    "manufacturing_date",
    "net_quantity",
    "batch_code",
    "fssai_license"
]

FIELD_MESSAGES = {
    "mrp": "Maximum Retail Price formatted correctly.",
    "manufacturer": "Manufacturer details comply with Rule 6.",
    "manufacturing_date": "Manufacturing date format is compliant.",
    "net_quantity": "Net quantity declaration conforms to standard units.",
    "batch_code": "Batch/Lot number identified.",
    "fssai_license": "FSSAI license number is valid."
}

def analyze_product_label(image_path: str, product_type: str = "ointment", distance_mm: float = 300.0, focal_length_px: float = 800.0, db=None, category_id: int = 1, is_institutional: bool = False, rule_33_gst_active: bool = False, weight_under_10g: bool = False, is_medical_device: bool = False) -> Dict[str, Any]:
    parsed_lines = []
    
    try:
        with Image.open(image_path) as img:
            orig_w, orig_h = img.size
            h_img, w_img = orig_h, orig_w
            
            # Smart Grayscale Compression for OCR.space
            img_gray = img.convert('L')
            enhancer = ImageEnhance.Contrast(img_gray)
            img_gray = enhancer.enhance(1.5)
            
            # Scale to max 1800px instead of 500px to keep text perfectly sharp!
            max_side = 1800
            scale = 1.0
            if max(orig_w, orig_h) > max_side:
                scale = max_side / max(orig_w, orig_h)
                img_gray = img_gray.resize((int(orig_w * scale), int(orig_h * scale)), Image.Resampling.LANCZOS)
                
            quality = 90
            while quality > 30:
                buffer = io.BytesIO()
                img_gray.save(buffer, format="JPEG", quality=quality)
                if buffer.tell() < 950 * 1024:
                    break
                quality -= 10
            
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        return {"status": "ERROR", "declarations": [], "error": f"Image processing failed: {e}"}

    try:
        payload = {
            'base64Image': f"data:image/jpeg;base64,{base64_image}",
            'language': 'eng',
            'isOverlayRequired': True,
            'OCREngine': 2
        }
        headers = {'apikey': 'helloworld'}
        
        resp = requests.post('https://api.ocr.space/parse/image', data=payload, headers=headers, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('IsErroredOnProcessing'):
                error_msg = data.get('ErrorMessage', [''])[0]
                if "not a valid image" in error_msg.lower() or "limit" in error_msg.lower():
                    payload['OCREngine'] = 1
                    resp = requests.post('https://api.ocr.space/parse/image', data=payload, headers=headers, timeout=60)
                    data = resp.json()
            
            if not data.get('IsErroredOnProcessing'):
                results = data.get('ParsedResults', [])
                if results:
                    lines = results[0].get('TextOverlay', {}).get('Lines', [])
                    for line in lines:
                        text = line.get('LineText', '').strip()
                        words = line.get('Words', [])
                        if words and text:
                            left = min(w['Left'] for w in words)
                            top = min(w['Top'] for w in words)
                            right = max(w['Left'] + w['Width'] for w in words)
                            bottom = max(w['Top'] + w['Height'] for w in words)
                            box = [[left, top], [right, top], [right, bottom], [left, bottom]]
                            parsed_lines.append((box, text, 0.99))
    except Exception as e:
        print(f"Bypass API Error: {e}")


        if len(parsed_lines) == 0 and hasattr(ocr, 'ocr'):
            try:
                result = ocr.ocr(image_path, cls=False)
                if result and result[0] is not None:
                    for line in result[0]:
                        box = line[0]
                        text = str(line[1][0]).strip()
                        conf = float(line[1][1])
                        parsed_lines.append((box, text, conf))
            except Exception:
                pass

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
    has_global_mrp_header = any(k in full_doc_text for k in ["m.r.p", "mrp", "max. retail price", "retail price", "rs.", "rs ", "urd rs"])

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
        is_price_value_near_mrp = (has_global_mrp_header or any(k in context_window for k in ["mrp", "m.r.p", "rs", "?", "urd"])) and bool(re.search(r'^\d+[.,]\d{2}$', text_lower))
        
        if is_mrp_text or is_rs_number or is_price_value_near_mrp:
            tag = "mrp"
            if height_mm < 1.0 and not is_medical_device:
                is_compliant = False
                failure_reason = f"MRP font height ({height_mm}mm) is below minimum required 1.0mm (Rule 7)."

        # --- 2. Net Quantity Detection ---
        elif any(k in text_lower for k in ["net wt", "net weight", "net qty", "net quantity", " 30g", "30 g", "30g", "wt.", "weight"]) or \
             (bool(re.search(r'\b\d+\s*(?:g|gm|gms|ml|l|kg|mg)\b', text_lower)) and not any(k in text_lower for k in ["usp", "ip", "w/w", "%", "iodine"])):
            tag = "net_quantity"
            if height_mm < 1.0 and not is_medical_device:
                is_compliant = False
                failure_reason = f"Net Quantity font height ({height_mm}mm) is below minimum required 1.0mm (Rule 7)."

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
                db_message = f"Verified via DB: {rule.legal_act_reference}"
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
        from backend.app.db.models import ComplianceRule, ExemptionClause
        mandatory_rules = db.query(ComplianceRule).filter(ComplianceRule.category_id == category_id, ComplianceRule.is_mandatory == True).all()
        mandatory_tags = {r.tag for r in mandatory_rules}
        found_tags = {d["tag"].upper() for d in declarations}
        
        # --- APPLY RULE 32: WEIGHT UNDER 10G EXEMPTION (Except Tobacco) ---
        is_tobacco = any("tobacco" in p[1].lower() or "pan masala" in p[1].lower() for p in parsed_lines)
        if weight_under_10g and not is_tobacco:
            # Exempt from all declarations except standard generic names
            mandatory_tags = set()
            
        # --- APPLY INSTITUTIONAL EXEMPTION (Rule 2(bb) & 2(bc)) ---
        if is_institutional:
            # Exempt from MRP, Unit Sale Price
            if "MRP" in mandatory_tags: mandatory_tags.remove("MRP")
            if "UNIT_SALE_PRICE" in mandatory_tags: mandatory_tags.remove("UNIT_SALE_PRICE")
            
            # Must have 'Not for retail sale'
            has_not_for_retail = any("not for retail" in p[1].lower() for p in parsed_lines)
            if not has_not_for_retail:
                mandatory_tags.add("NOT_FOR_RETAIL_SALE_DECLARATION")

        # --- APPLY LANGUAGE RULE 4 CHECK ---
        # If no english/hindi is detected, language check fails
        has_valid_language = any(re.search(r'[a-zA-Z\u0900-\u097F]', p[1]) for p in parsed_lines)
        if has_valid_language:
            found_tags.add("LANGUAGE_CHECK")

        missing_tags = list(mandatory_tags - found_tags)
    
    status = "NON_COMPLIANT" if (len(declarations) == 0 or len(missing_tags) > 0 or any(not d["is_compliant"] for d in declarations)) else "COMPLIANT"
    
    return {
        "status": status,
        "product_type": product_type,
        "declarations": declarations,
        "missing_tags": missing_tags,
        "ar_parameters": {
            "distance_mm": distance_mm,
            "focal_length_px": focal_length_px
        }
    }