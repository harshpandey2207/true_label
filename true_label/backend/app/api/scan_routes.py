import shutil
import uuid
import os
from typing import List
from fastapi import APIRouter, UploadFile, File, Form
from backend.app.services.ai_engine.metrology_engine import analyze_product_label

# REMOVED the duplicate prefix here, since main.py already handles /scan
router = APIRouter(tags=["Scanner"])

@router.post("/analyze-ar")
async def analyze_ar_scan(
    images: List[UploadFile] = File(...),   # <--- Changed to accept multiple files
    distance_mm: float = Form(300.0),      
    focal_length_px: float = Form(1050.0)   
):
    results = []
    temp_paths = []
    
    try:
        for image in images:
            # Cross-platform temporary path for each individual image
            temp_filename = f"{uuid.uuid4()}_{image.filename}"
            temp_path = os.path.join(os.getcwd(), temp_filename)
            temp_paths.append(temp_path)
            
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            # Run the AI engine analysis on each image using keyword arguments
                analysis = analyze_product_label(
                    image_path=temp_path, 
                    distance_mm=distance_mm, 
                    focal_length_px=focal_length_px
                )
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