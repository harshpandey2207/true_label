"""Evidence-aware package scanning endpoints for the jury prototype."""

from __future__ import annotations

import hashlib
import io
import os
import tempfile
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image, ImageOps
from sqlalchemy.orm import Session

from backend.app.api.security import get_optional_user
from backend.app.db.database import get_db
from backend.app.db.models import ComplianceRule, ProductCategory, ScanEvidence, ScanRecord, UserAccount
from backend.app.services.ai_engine.metrology_engine import analyze_product_label, orb_overlap_score
from backend.app.services.ai_engine.rule_engine import (
    CONFIRMED_VIOLATION,
    RULE_ENGINE_VERSION,
    UNRESOLVED,
    clarification_requests,
    evaluate_rules,
    overall_status,
)

router = APIRouter(tags=["Scanner"])
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_INITIAL_IMAGES = 6
MAX_EVIDENCE_IMAGES = 9


def _hamming_distance(first: str, second: str) -> int:
    return sum(left != right for left, right in zip(first, second)) + abs(len(first) - len(second))


def _temporary_image(raw: bytes, filename: str) -> tuple[str, dict[str, Any]]:
    """Validate/de-orient an image while retaining the original bytes as evidence."""
    try:
        with Image.open(io.BytesIO(raw)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            if image.width * image.height > 40_000_000 or max(image.size) > 12_000:
                raise HTTPException(status_code=413, detail="Images must be no larger than 40 megapixels.")
            suffix = os.path.splitext(filename)[1].lower() or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
                image.save(handle, format="JPEG", quality=92)
                path = handle.name
            return path, {"width": image.width, "height": image.height}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=415, detail="A file could not be decoded as an image.") from exc


def _serialise_check(check: dict[str, Any]) -> dict[str, Any]:
    # JSON values are already primitive, but this keeps response/persistence
    # construction in one place if rule data is expanded later.
    return dict(check)


@router.post("/analyze-ar")
def analyze_ar_scan(
    images: List[UploadFile] = File(...),
    distance_mm: float = Form(300.0),
    focal_length_px: float = Form(1050.0),
    category_name: str = Form(""),
    category_id: int = Form(1),
    scan_id: Optional[int] = Form(None),
    is_institutional: bool = Form(False),
    rule_33_gst_active: bool = Form(False),
    weight_under_10g: bool = Form(False),
    is_medical_device: bool = Form(False),
    user: Optional[UserAccount] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Create or clarify a scan without converting unreadable text into a violation."""
    if not images:
        raise HTTPException(status_code=422, detail="Upload at least one package image.")
    if len(images) > MAX_INITIAL_IMAGES:
        raise HTTPException(status_code=413, detail="Upload no more than six package-side images at a time.")
    if distance_mm <= 0 or focal_length_px <= 0:
        raise HTTPException(status_code=422, detail="Camera geometry values must be positive.")

    category = (
        db.query(ProductCategory).filter(ProductCategory.name == category_name.strip()).first()
        if category_name.strip()
        else db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    )
    if category is None:
        raise HTTPException(status_code=422, detail="Unknown product category. Please choose a listed category.")

    existing = db.query(ScanRecord).filter(ScanRecord.id == scan_id).first() if scan_id is not None else None
    if scan_id is not None and existing is None:
        raise HTTPException(status_code=404, detail="Scan not found. Start a new scan instead.")
    if existing is not None and existing.user_id is not None and existing.user_id != (user.id if user else None):
        raise HTTPException(status_code=404, detail="Scan not found. Start a new scan instead.")
    if existing is not None and existing.category != category.name:
        raise HTTPException(status_code=422, detail="Clarification images must use the same category as the original scan.")
    if existing is not None and len(existing.evidence) + len(images) > MAX_EVIDENCE_IMAGES:
        raise HTTPException(status_code=413, detail="This scan already has the maximum of nine evidence images. Start a new scan for a different package.")

    temp_paths: list[str] = []
    uploaded: list[dict[str, Any]] = []
    all_inputs: list[dict[str, Any]] = []
    try:
        if existing is not None:
            for evidence in existing.evidence:
                path, dimensions = _temporary_image(evidence.payload, evidence.filename)
                temp_paths.append(path)
                all_inputs.append({"filename": evidence.filename, "path": path, "evidence_id": evidence.id, "dimensions": dimensions})

        for image in images:
            raw = image.file.read(MAX_IMAGE_BYTES + 1)
            if not raw:
                raise HTTPException(status_code=422, detail="An uploaded image is empty.")
            if len(raw) > MAX_IMAGE_BYTES:
                raise HTTPException(status_code=413, detail="Each image must be 10 MB or smaller.")
            filename = image.filename or "package-side.jpg"
            path, dimensions = _temporary_image(raw, filename)
            temp_paths.append(path)
            item = {
                "filename": filename,
                "path": path,
                "raw": raw,
                "content_type": image.content_type,
                "dimensions": dimensions,
            }
            uploaded.append(item)
            all_inputs.append(item)

        results: list[dict[str, Any]] = []
        all_declarations: list[dict[str, Any]] = []
        hashes: list[str] = []
        duplicate_of: dict[int, int] = {}
        duplicate_match_details: dict[int, dict[str, Any]] = {}
        for index, item in enumerate(all_inputs):
            analysis = analyze_product_label(
                image_path=item["path"],
                distance_mm=distance_mm,
                focal_length_px=focal_length_px,
            )
            if analysis.get("status") == "ERROR":
                raise HTTPException(status_code=422, detail=analysis.get("error", "The image could not be analysed."))
            current_hash = analysis.pop("perceptual_hash", "")
            for earlier, previous_hash in enumerate(hashes):
                orb = orb_overlap_score(item["path"], all_inputs[earlier]["path"])
                if orb is not None:
                    duplicate_match_details[index] = {"compared_to": earlier, **orb}
                similar_hash = current_hash and previous_hash and _hamming_distance(current_hash, previous_hash) <= 5
                similar_orb = bool(orb and orb.get("status") == "evaluated" and orb.get("good_matches", 0) >= 18 and orb.get("overlap_ratio", 0) >= 0.12)
                if similar_hash or similar_orb:
                    duplicate_of[index] = earlier
                    basis = "visual hash" if similar_hash else "ORB keypoint overlap"
                    analysis.setdefault("warnings", []).append(f"This may be another angle of image {earlier + 1} ({basis}); it will remain separate evidence until a reviewer confirms the package side.")
                    break
            hashes.append(current_hash)
            declarations = analysis.get("declarations", [])
            for declaration in declarations:
                declaration["image_index"] = index
                declaration["filename"] = item["filename"]
                all_declarations.append(declaration)
            results.append({"filename": item["filename"], "analysis": analysis})

        context = {
            "is_institutional": is_institutional,
            "rule_33_gst_active": rule_33_gst_active,
            "weight_under_10g": weight_under_10g,
            "is_medical_device": is_medical_device,
            "is_tobacco": any("tobacco" in str(item.get("text", "")).lower() for item in all_declarations),
        }
        rules = db.query(ComplianceRule).filter(ComplianceRule.category_id == category.id).all()
        checks = [_serialise_check(check) for check in evaluate_rules(rules, all_declarations, context)]
        overall = overall_status(checks)
        unresolved_tags = [check["tag"] for check in checks if check["status"] == UNRESOLVED]
        confirmed_tags = [check["tag"] for check in checks if check["status"] == CONFIRMED_VIOLATION]
        package_status = "NO_FLAGS" if overall == "PASS" else "POTENTIAL_ISSUES"

        package_result = {
            "scan_schema_version": "2.0",
            "overall_status": overall,
            "legacy_package_status": package_status,
            "checks": checks,
            "clarification_requests": clarification_requests(checks),
            "confirmed_violation_tags": confirmed_tags,
            "unresolved_tags": unresolved_tags,
            "duplicate_side_hints": duplicate_of,
            "duplicate_match_details": duplicate_match_details,
            "results": results,
            "limitations": [
                "Prototype decision support only; it is not an official certificate, notice, or legal determination.",
                "Rule references and applicability need human legal review before operational use.",
                "Image-derived physical text measurements are not used as legal evidence without calibrated capture.",
            ],
        }

        if existing is None:
            record = ScanRecord(
                user_id=user.id if user else None,
                category=category.name,
                status=package_status,
                result=package_result,
                image_names=[],
                rule_engine_version=RULE_ENGINE_VERSION,
            )
            db.add(record)
            db.flush()
        else:
            record = existing
            record.status = package_status
            record.result = package_result
            record.rule_engine_version = RULE_ENGINE_VERSION

        for item in uploaded:
            record.evidence.append(ScanEvidence(
                filename=item["filename"],
                content_type=item.get("content_type"),
                sha256=hashlib.sha256(item["raw"]).hexdigest(),
                size_bytes=len(item["raw"]),
                payload=item["raw"],
                metadata_json={"dimensions": item["dimensions"], "source": "clarification" if existing is not None else "initial"},
            ))
        record.image_names = [evidence.filename for evidence in record.evidence]
        db.commit()
        db.refresh(record)

        # Per-image fields remain for the current Flutter view, while the
        # package-level checks carry the actual evidence-aware conclusion.
        for result in results:
            result["analysis"]["missing_tags"] = unresolved_tags
            result["analysis"]["status"] = package_status
            result["analysis"]["package_checks"] = checks
        return {
            "status": "SUCCESS",
            "scan_id": record.id,
            "package_status": package_status,
            "overall_status": overall,
            "checks": checks,
            "confirmed_violation_tags": confirmed_tags,
            "unresolved_tags": unresolved_tags,
            "clarification_requests": package_result["clarification_requests"],
            "results": results,
            "limitations": package_result["limitations"],
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="The scan could not be saved. No compliance conclusion was created.") from exc
    finally:
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)
