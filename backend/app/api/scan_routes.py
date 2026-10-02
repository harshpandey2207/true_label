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
    
    try:
        for image in images:
            suffix = os.path.splitext(image.filename or ".jpg")[1]
            if not suffix:
                suffix = ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(image.file, tmp)
                temp_path = tmp.name
            temp_paths.append(temp_path)
            
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
            except Exception as e:
                analysis = {
                    "status": "ERROR",
                    "error": f"OCR processing failed: {str(e)}",
                    "declarations": []
                }

            results.append({
                "filename": image.filename,
                "analysis": analysis
            })
            
            # Log this scan into the database architecture
            if analysis.get("status") != "ERROR":
                is_compliant = analysis.get("status") == "COMPLIANT"
                declarations = analysis.get("declarations", [])
                
                # Missing tags are determined dynamically by the engine now
                missing = analysis.get("missing_tags", [])
                
                try:
                    log_scan_result(
                        db=db, 
                        category_id=category_id, 
                        is_compliant=is_compliant, 
                        missing_tags=missing, 
                        confidence_score=0.99
                    )
                except Exception:
                    pass
            
        return {
            "status": "SUCCESS",
            "total_scanned": len(results),
            "results": results
        }
        
    finally:
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass