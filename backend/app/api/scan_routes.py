import os
import tempfile
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.db.crud import log_scan_result
from backend.app.db.database import get_db
from backend.app.db.models import ProductCategory
from backend.app.services.ai_engine.metrology_engine import analyze_product_label

router = APIRouter(tags=["Scanner"])
MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.post("/analyze-ar")
def analyze_ar_scan(
    images: List[UploadFile] = File(...),
    distance_mm: float = Form(300.0),
    focal_length_px: float = Form(1050.0),
    category_name: str = Form(""),
    category_id: int = Form(1),
    is_institutional: bool = Form(False),
    rule_33_gst_active: bool = Form(False),
    weight_under_10g: bool = Form(False),
    is_medical_device: bool = Form(False),
    db: Session = Depends(get_db),
):
    if not images:
        raise HTTPException(status_code=422, detail="Upload at least one package image.")
    if len(images) > 6:
        raise HTTPException(status_code=413, detail="Upload no more than six package-side images.")
    if distance_mm <= 0 or focal_length_px <= 0:
        raise HTTPException(status_code=422, detail="Camera geometry values must be positive.")

    category = None
    if category_name.strip():
        category = db.query(ProductCategory).filter(ProductCategory.name == category_name.strip()).first()
    else:
        category = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=422, detail="Unknown product category. Please choose a listed category.")
    category_id = category.id

    temp_paths: list[tuple[str, str]] = []
    results = []
    try:
        for image in images:
            raw = image.file.read(MAX_IMAGE_BYTES + 1)
            if not raw:
                raise HTTPException(status_code=422, detail="An uploaded image is empty.")
            if len(raw) > MAX_IMAGE_BYTES:
                raise HTTPException(status_code=413, detail="Each image must be 10 MB or smaller.")
            from PIL import Image
            import io
            try:
                img = Image.open(io.BytesIO(raw))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                image_width, image_height = img.size
                if image_width * image_height > 40_000_000 or max(image_width, image_height) > 12_000:
                    raise HTTPException(status_code=413, detail="Images must be no larger than 40 megapixels.")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    temp_path = tmp.name
                    img.save(temp_path, format="JPEG", quality=85)
                temp_paths.append((image.filename or "package-side.jpg", temp_path))
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(status_code=415, detail="A file could not be decoded as an image.")

        for filename, temp_path in temp_paths:
            analysis = analyze_product_label(
                image_path=temp_path,
                distance_mm=distance_mm,
                focal_length_px=focal_length_px,
                db=db,
                category_id=category_id,
                is_institutional=is_institutional,
                rule_33_gst_active=rule_33_gst_active,
                weight_under_10g=weight_under_10g,
                is_medical_device=is_medical_device,
            )
            if analysis.get("status") == "ERROR":
                raise HTTPException(status_code=503, detail=analysis.get("error", "Local OCR failed."))
            results.append({"filename": filename, "analysis": analysis})

        # Declarations can be on different package panels. Assess the package
        # from the combined set, while retaining per-image OCR evidence.
        found_tags = {
            declaration.get("tag", "").upper()
            for result in results
            for declaration in result["analysis"].get("declarations", [])
            if declaration.get("is_compliant")
        }
        all_missing = {
            tag
            for result in results
            for tag in result["analysis"].get("missing_tags", [])
            if tag.upper() not in found_tags
        }
        any_failed_declaration = any(
            not declaration.get("is_compliant")
            for result in results
            for declaration in result["analysis"].get("declarations", [])
        )
        package_status = "NO_FLAGS" if not all_missing and not any_failed_declaration else "POTENTIAL_ISSUES"
        for result in results:
            result["analysis"]["missing_tags"] = sorted(all_missing)
            result["analysis"]["status"] = package_status

        declaration_confidences = [
            declaration.get("confidence", 0.0)
            for result in results
            for declaration in result["analysis"].get("declarations", [])
        ]
        try:
            log_scan_result(
                db,
                category_id,
                package_status == "NO_FLAGS",
                sorted(all_missing),
                (sum(declaration_confidences) / len(declaration_confidences)) if declaration_confidences else 0.0,
            )
        except Exception:
            db.rollback()

        return {"status": "SUCCESS", "package_status": package_status, "results": results}
    finally:
        for _, temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)
