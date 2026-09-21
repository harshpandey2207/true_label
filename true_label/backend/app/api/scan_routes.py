import os
import shutil
import tempfile
from typing import List
from fastapi import APIRouter, UploadFile, File, Form
from backend.app.services.ai_engine.metrology_engine import analyze_product_label

# REMOVED the duplicate prefix here, since main.py already handles /scan
router = APIRouter(tags=["Scanner"])

@router.post("/analyze-ar")
def analyze_ar_scan(
    images: List[UploadFile] = File(...),
    distance_mm: float = Form(300.0),      
    focal_length_px: float = Form(1050.0)   
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
                    focal_length_px=focal_length_px
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