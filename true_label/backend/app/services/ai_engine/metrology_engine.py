import cv2
import re
import os
from typing import Dict, Any

# Ensure compatibility and disable MKLDNN/oneDNN issues with new PIR executor on CPU
try:
    import paddlex.inference.models.runners.paddle_static.runner as runner_mod
    orig_create = runner_mod.PaddleStaticRunner._create
    def safe_create(self, *args, **kwargs):
        self._config['run_mode'] = 'paddle'
        return orig_create(self, *args, **kwargs)
    runner_mod.PaddleStaticRunner._create = safe_create
    import paddle.inference as p_inf
    p_inf.Config.enable_mkldnn = lambda self: None
except Exception:
    pass

from paddleocr import PaddleOCR

# Initialize PaddleOCR with lightweight PP-OCRv4 mobile models to fit strictly within free tier memory
ocr = PaddleOCR(
    ocr_version='PP-OCRv4',
    lang='en',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

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

def analyze_product_label(image_path: str, product_type: str = "ointment", distance_mm: float = 300.0, focal_length_px: float = 800.0) -> Dict[str, Any]:
    img = cv2.imread(image_path)
    if img is None:
        return {"status": "ERROR", "declarations": [], "error": "Could not read image file."}
        
    orig_h, orig_w = img.shape[:2]
    h_img, w_img = orig_h, orig_w
    
    # Auto-downscale high-res images to max 800px for sub-4-second inference on free tier CPU
    max_side = 800
    scale = 1.0
    if max(orig_h, orig_w) > max_side:
        scale = max_side / max(orig_h, orig_w)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        cv2.imwrite(image_path, img_resized)

    # Run OCR inference
    result = ocr.predict(image_path)
    
    parsed_lines = []
    if result and len(result) > 0:
        for res in result:
            boxes = res.get('dt_polys', [])
            texts = res.get('rec_texts', [])
            scores = res.get('rec_scores', [])
            for box, text, conf in zip(boxes, texts, scores):
                parsed_lines.append((box, str(text).strip(), float(conf)))

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
            if height_mm < 1.0:
                is_compliant = False
                failure_reason = f"MRP font height ({height_mm}mm) is below minimum required 1.0mm (Rule 7)."

        # --- 2. Net Quantity Detection ---
        elif any(k in text_lower for k in ["net wt", "net weight", "net qty", "net quantity", " 30g", "30 g", "30g", "wt.", "weight"]) or \
             (bool(re.search(r'\b\d+\s*(?:g|gm|gms|ml|l|kg|mg)\b', text_lower)) and not any(k in text_lower for k in ["usp", "ip", "w/w", "%", "iodine"])):
            tag = "net_quantity"
            if height_mm < 1.0:
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
            [int((pt[0] / w_img) * 250), int((pt[1] / h_img) * 350)]
            for pt in pts
        ]

        declarations.append({
            "text": text,
            "tag": tag.upper(),
            "field": tag,
            "confidence": round(conf, 2),
            "box": scaled_box,
            "height_mm": height_mm,
            "is_compliant": is_compliant,
            "message": failure_reason if failure_reason else FIELD_MESSAGES.get(tag, "Declaration verified."),
            "failure_reason": failure_reason
        })

    status = "NON_COMPLIANT" if (len(declarations) == 0 or any(not d["is_compliant"] for d in declarations)) else "COMPLIANT"
    
    return {
        "status": status,
        "product_type": product_type,
        "declarations": declarations,
        "ar_parameters": {
            "distance_mm": distance_mm,
            "focal_length_px": focal_length_px
        }
    }