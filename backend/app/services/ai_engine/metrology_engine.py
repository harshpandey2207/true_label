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

def analyze_product_label(image_path: str, product_type: str = "ointment", distance_mm: float = 300.0, focal_length_px: float = 800.0, db=None, category_id: int = 1, is_institutional: bool = False, rule_33_gst_active: bool = False, weight_under_10g: bool = False, is_medical_device: bool = False) -> Dict[str, Any]:
    img = cv2.imread(image_path)
    if img is None:
        return {"status": "ERROR", "declarations": [], "error": "Could not read image file."}
        
    orig_h, orig_w = img.shape[:2]
    h_img, w_img = orig_h, orig_w
    
    # Keep enough detail for small package text while limiting peak memory and
    # network payload size on the small hosted instance.
    max_side = 1800
    scale = 1.0
    if max(orig_h, orig_w) > max_side:
        scale = max_side / max(orig_h, orig_w)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        cv2.imwrite(image_path, img_resized)

    parsed_lines = []

    # OCR.Space is the deployment-safe default for small instances. It receives
    # the submitted image; set OCR_ENGINE=paddle on a host with enough RAM to
    # run PaddleOCR locally instead.
    ocr_engine = os.getenv("OCR_ENGINE", "ocr_space").strip().lower()
    try:
        if ocr_engine in {"paddle", "paddleocr"}:
            engine = _get_local_ocr()
            if engine is None:
                raise RuntimeError(_ocr_error or "PaddleOCR could not be loaded.")
            pages = engine.ocr(image_path, cls=False) or []
            for page in pages:
                if not page:
                    continue
                for item in page:
                    try:
                        box, (text, confidence) = item
                        text = str(text).strip()
                        if text:
                            parsed_lines.append((box, text, float(confidence)))
                    except (TypeError, ValueError):
                        continue
        elif ocr_engine == "ocr_space":
            import requests
            import base64

            api_key = os.getenv("OCR_SPACE_API_KEY", "helloworld").strip()
            if not api_key:
                raise RuntimeError("OCR_SPACE_API_KEY must be configured when OCR_ENGINE=ocr_space.")

            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("ascii")

            payload = {
                "base64Image": f"data:image/jpeg;base64,{base64_image}",
                "language": "eng",
                "isOverlayRequired": True,
            }
            headers = {"apikey": api_key}
            response = requests.post("https://api.ocr.space/parse/image", data=payload, headers=headers, timeout=(5, 20))
            response.raise_for_status()
            result = response.json()
            if result.get("IsErroredOnProcessing"):
                raise RuntimeError(result.get("ErrorMessage") or "OCR.Space could not process the image.")

            parsed_results = result.get("ParsedResults") or []
            if parsed_results:
                parsed_page = parsed_results[0]
                lines = (parsed_page.get("TextOverlay") or {}).get("Lines") or []
                for line in lines:
                    words = line.get("Words") or []
                    text = " ".join(str(word.get("WordText", "")).strip() for word in words).strip()
                    if not text or not words:
                        continue
                    try:
                        top = min(int(word["Top"]) for word in words)
                        left = min(int(word["Left"]) for word in words)
                        bottom = max(int(word["Top"]) + int(word["Height"]) for word in words)
                        right = max(int(word["Left"]) + int(word["Width"]) for word in words)
                    except (KeyError, TypeError, ValueError):
                        continue
                    box = [[left, top], [right, top], [right, bottom], [left, bottom]]
                    # OCR.Space's documented overlay response has word geometry
                    # but no confidence score; do not fabricate one.
                    parsed_lines.append((box, text, None))
                if not parsed_lines:
                    for text in str(parsed_page.get("ParsedText") or "").splitlines():
                        text = text.strip()
                        if text:
                            parsed_lines.append(([[0, 0], [0, 0], [0, 0], [0, 0]], text, None))
        else:
            raise RuntimeError("OCR_ENGINE must be 'ocr_space' or 'paddle'.")
    except Exception as exc:
        return {
            "status": "ERROR",
            "declarations": [],
            "missing_tags": [],
            "error": f"{ocr_engine} text recognition failed: {exc}",
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
    product_category = (product_type or "").lower()
    food_category = "food" in product_category
    cosmetics_category = "cosmetic" in product_category or "pharma" in product_category

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

        # Category-specific declarations that are otherwise easy to miss with
        # general-purpose text heuristics. Symbols and applicability still
        # require direct human review.
        if "fssai" in text_lower:
            tag = "fssai_license"
        elif re.search(r"\b(?:non[\s-]?vegetarian|vegetarian|veg[\s-]?(?:logo|mark|symbol|dot)|green dot|brown dot)\b", text_lower):
            tag = "veg_non_veg_logo"
        elif re.search(r"\b(?:bis|isi)\s*(?:mark|licen[cs]e|standard|no\.?|registration)?\b", text_lower) or "bureau of indian standards" in text_lower:
            tag = "bis_mark"
        elif "country of origin" in text_lower or re.search(r"\bmade\s+in\s+[a-z][a-z .'-]+", text_lower):
            tag = "country_of_origin"
        elif re.search(r"\bmodel\s*(?:no\.?|number)\b|\bmodel\s*:", text_lower):
            tag = "model"
        elif re.search(r"\bserial\s*(?:no\.?|number)\b|\bserial\s*:", text_lower):
            tag = "serial_number"
        elif re.search(r"\bsize\s*:", text_lower):
            tag = "size"
        elif "ingredients" in text_lower or "allergen" in text_lower:
            tag = "ingredients"
        elif re.search(r"\b(?:best\s+before|use\s+by)\b", text_lower):
            tag = "best_before_date"
        
        # --- 1. MRP Detection ---
        # Matches: "M.R.P. Rs. 105.41", "M.R.P. Rs.", "105.41" next to MRP, "₹105", "Rs. 105", etc.
        is_mrp_text = any(k in text_lower for k in ["m.r.p", "mrp", "r.p.", "₹", "inr", "max. retail"])
        is_rs_number = bool(re.search(r'(?:rs\.?|₹|inr)\s*\d+', text_lower))
        is_price_value_near_mrp = (has_global_mrp_header or "mrp" in context_window or "m.r.p" in context_window) and bool(re.search(r'^\d+[.,]\d{2}$', text_lower))
        
        if tag != "general":
            pass
        elif is_mrp_text or is_rs_number or is_price_value_near_mrp:
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
        elif any(k in text_lower for k in ["expiry", "exp.", "exp date"]):
            tag = "expiry_date" if cosmetics_category else ("best_before_date" if food_category else "manufacturing_date")
        elif any(k in text_lower for k in ["mfg", "mfd", "pkd", "packed", "date"]):
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
        elif any(k in text_lower for k in ["marketed by", "manufactured by", "imported by", "importer", "mfd. by", "mfd by", "mfg. lic", "mfg by", "cipla health"]):
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
        db_message = "Text detected; verify the declaration's content and applicability."
        if db is not None:
            # Query the database for the specific compliance rule
            from backend.app.db.models import ComplianceRule
            rule = db.query(ComplianceRule).filter(ComplianceRule.tag == tag.upper(), ComplianceRule.category_id == category_id).first()
            if rule and rule.legal_act_reference:
                db_message = f"Configured rule reference: {rule.legal_act_reference}"
            else:
                db_message = FIELD_MESSAGES.get(tag, "Text detected; verify the declaration's content and applicability.")
        else:
            db_message = FIELD_MESSAGES.get(tag, "Text detected; verify the declaration's content and applicability.")

        declarations.append({
            "text": text,
            "tag": tag.upper(),
            "field": tag,
            "confidence": round(conf, 2) if conf is not None else None,
            "box": scaled_box,
            "height_mm": height_mm,
            "is_compliant": False if not is_compliant else None,
            "finding_status": "FLAGGED" if not is_compliant else "DETECTED",
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

        # Context-dependent exemptions are not evaluated here. Do not silently
        # remove declarations based on a user-supplied checkbox.
        has_valid_language = any(re.search(r'[a-zA-Z\u0900-\u097F]', p[1]) for p in parsed_lines)
        if has_valid_language:
            found_tags.add("LANGUAGE_CHECK")

        missing_tags = list(mandatory_tags - found_tags)

    warnings = [
        "Displayed text-height values are rough estimates from fixed, uncalibrated camera geometry. They are not used to determine scan status or establish compliance."
    ]
    if is_institutional or rule_33_gst_active or weight_under_10g or is_medical_device:
        warnings.append("Special category or exemption context was supplied but is not automatically evaluated. Review the applicable rules manually.")
    
    status = "POTENTIAL_ISSUES" if (
        len(declarations) == 0
        or len(missing_tags) > 0
        or any(d["finding_status"] == "FLAGGED" for d in declarations)
    ) else "NO_FLAGS"
    
    return {
        "status": status,
        "ocr_engine": ocr_engine,
        "product_type": product_type,
        "declarations": declarations,
        "missing_tags": missing_tags,
        "warnings": warnings,
        "ar_parameters": {
            "distance_mm": distance_mm,
            "focal_length_px": focal_length_px
        }
    }
