import os
import shutil
import tempfile
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from backend.app.services.ai_engine.metrology_engine import analyze_product_label
from backend.app.db.database import get_db
from backend.app.db.crud import log_scan_result

# REMOVED the duplicate prefix here, since main.py already handles /scan
router = APIRouter(tags=["Scanner"])

@router.post("/analyze-ar")
def analyze_ar_scan(
    images: List[UploadFile] = File(...),
    distance_mm: float = Form(300.0),      
    focal_length_px: float = Form(1050.0),
    category_id: int = Form(1),
    is_institutional: bool = Form(False),
    rule_33_gst_active: bool = Form(False),
    weight_under_10g: bool = Form(False),
    is_medical_device: bool = Form(False),
    db: Session = Depends(get_db)
):
    results = []
    temp_paths = []
    
    global_found_tags = set()
    
    try:
        # Phase 1: Run OCR on all images to gather all found tags
        for image in images:
            suffix = os.path.splitext(image.filename or ".jpg")[1]
            if not suffix:
                suffix = ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(image.file, tmp)
                temp_path = tmp.name
            temp_paths.append((image.filename, temp_path))
            
        raw_analyses = []
        for filename, temp_path in temp_paths:
            try:
                analysis = analyze_product_label(
                    image_path=temp_path, 
                    distance_mm=distance_mm, 
                    focal_length_px=focal_length_px,
                    db=db,
                    category_id=category_id,
                    is_institutional=is_institutional,
                    rule_33_gst_active=rule_33_gst_active,
                    weight_under_10g=weight_under_10g,
                    is_medical_device=is_medical_device
                )
                
                # Aggregate found tags
                for decl in analysis.get("declarations", []):
                    if decl.get("is_compliant", False):
                        global_found_tags.add(decl["tag"].upper())
                
                if "LANGUAGE_CHECK" not in analysis.get("missing_tags", []):
                    global_found_tags.add("LANGUAGE_CHECK")
                    
                raw_analyses.append((filename, temp_path, analysis))
            except Exception as e:
                raw_analyses.append((filename, temp_path, {
                    "status": "ERROR",
                    "error": f"OCR processing failed: {str(e)}",
                    "declarations": [],
                    "missing_tags": []
                }))
                
        # Phase 2: Post-process to remove globally found tags from missing lists
        for filename, temp_path, analysis in raw_analyses:
            if analysis.get("status") != "ERROR":
                # Remove tags from missing_tags if they were found on ANY image
                original_missing = analysis.get("missing_tags", [])
                new_missing = [tag for tag in original_missing if tag not in global_found_tags]
                analysis["missing_tags"] = new_missing
                
                # Update status for the specific image
                has_non_compliant_decl = any(not d["is_compliant"] for d in analysis.get("declarations", []))
                
                # An image is "COMPLIANT" if it has no missing tags AND no non-compliant declarations
                if len(new_missing) == 0 and not has_non_compliant_decl:
                    analysis["status"] = "COMPLIANT"
                else:
                    analysis["status"] = "NON_COMPLIANT"
            
            results.append({
                "filename": filename,
                "analysis": analysis
            })
            
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        return {"status": "SUCCESS", "results": results}
    except Exception as e:
        for _, temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        return {"status": "ERROR", "error": str(e)}