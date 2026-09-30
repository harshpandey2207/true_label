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
    db: Session = Depends(get_db)
):
    results = []
    temp_paths = []
    
    try:
        for image in images:
            # Safe temporary file in OS temp folder
            suffix = os.path.splitext(image.filename or ".jpg")[1]
            if not suffix:
                suffix = ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(image.file, tmp)
                temp_path = tmp.name
            temp_paths.append(temp_path)
            
            # Run the AI engine analysis on each image
            try:
                analysis = analyze_product_label(
                    image_path=temp_path, 
                    distance_mm=distance_mm, 
                    focal_length_px=focal_length_px,
                    db=db
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
                
                # Determine missing tags for logging
                found_tags = {d["tag"].upper() for d in declarations if d["tag"] != "GENERAL"}
                mandatory = {"MRP", "NET_QUANTITY", "MANUFACTURER", "MANUFACTURING_DATE"}
                missing = list(mandatory - found_tags)
                
                # Default category 1 (General Packaged Commodity)
                try:
                    log_scan_result(
                        db=db, 
                        category_id=1, 
                        is_compliant=is_compliant, 
                        missing_tags=missing, 
                        confidence_score=0.99
                    )
                except Exception:
                    pass # Failsafe so DB errors don't break the scan
            
        return {
            "status": "SUCCESS",
            "total_scanned": len(results),
            "results": results
        }
        
    finally:
        # Clean up all temporary files safely after processing
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass