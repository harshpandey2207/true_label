import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.api.security import get_optional_user
from backend.app.db.database import get_db
from backend.app.db.models import ComplianceRule, LabelDraftRecord, ProductCategory, ScanRecord, UserAccount
from backend.app.services.ai_engine.label_generator import (
    CATEGORIES,
    generate_label_draft,
    render_label_pdf,
)
from backend.app.services.ai_engine.rule_engine import RULE_ENGINE_VERSION, UNRESOLVED, evaluate_rules, overall_status

router = APIRouter(tags=["Label Generator"])

MAX_IMAGE_BYTES = 8 * 1024 * 1024


@router.get("/categories")
def list_label_categories():
    return {"categories": CATEGORIES}


@router.post("/generate")
async def generate_label(
    images: Optional[List[UploadFile]] = File(default=None),
    product_name: str = Form(..., max_length=120),
    product_category: str = Form("General Packaged Commodity"),
    shape: str = Form("", max_length=80),
    dimensions: str = Form("", max_length=80),
    custom_prompt: str = Form("", max_length=1000),
    missing_tag_values: str = Form("{}"),
    additional_details: str = Form("", max_length=3000),
    side_count: int = Form(2),
    source_scan_id: Optional[int] = Form(None),
    user: Optional[UserAccount] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Generate a local SVG draft from form values and optional reference images."""
    try:
        tag_values: Any = json.loads(missing_tag_values or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Label values must be valid JSON.")
    if not isinstance(tag_values, dict):
        raise HTTPException(status_code=422, detail="Label values must be a JSON object.")
    if len(tag_values) > 80:
        raise HTTPException(status_code=422, detail="Submit no more than 80 declaration fields.")
    if any(len(str(key)) > 100 or len(str(value)) > 500 for key, value in tag_values.items()):
        raise HTTPException(status_code=422, detail="Declaration names must be 100 characters or fewer and values 500 characters or fewer.")

    image_inputs: list[tuple[str, bytes]] = []
    uploaded_images = images or []
    if len(uploaded_images) > 6:
        raise HTTPException(status_code=413, detail="Upload no more than six package-side images.")
    for image in uploaded_images:
        data = await image.read(MAX_IMAGE_BYTES + 1)
        if not data:
            raise HTTPException(status_code=422, detail="An uploaded image is empty.")
        if len(data) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="Each reference image must be 8 MB or smaller.")
        image_inputs.append((image.filename or "", data))

    source_scan = None
    if source_scan_id is not None:
        source_scan = db.query(ScanRecord).filter(ScanRecord.id == source_scan_id).first()
        if source_scan is None:
            raise HTTPException(status_code=404, detail="The source scan no longer exists.")
        if source_scan.user_id is not None and source_scan.user_id != (user.id if user else None):
            raise HTTPException(status_code=404, detail="The source scan no longer exists.")
        if source_scan.category != product_category:
            raise HTTPException(status_code=422, detail="The selected source scan belongs to a different product category.")
        if not image_inputs:
            image_inputs = [(evidence.filename, evidence.payload) for evidence in source_scan.evidence]

    try:
        result = generate_label_draft(
            product_name=product_name,
            product_category=product_category,
            shape=shape,
            dimensions=dimensions,
            custom_prompt=custom_prompt,
            label_values=tag_values,
            additional_details=additional_details,
            images=image_inputs,
            side_count=side_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="The local renderer could not create this label draft.")

    category = db.query(ProductCategory).filter(ProductCategory.name == product_category).first()
    rules = db.query(ComplianceRule).filter(ComplianceRule.category_id == category.id).all() if category else []
    value_evidence = [
        {"tag": str(key).upper(), "text": str(value), "confidence": 1.0, "image_index": None}
        for key, value in tag_values.items() if str(value).strip()
    ]
    validation = evaluate_rules(rules, value_evidence)
    result["label_data"]["validation"] = {
        "rule_engine_version": RULE_ENGINE_VERSION,
        "overall_status": overall_status(validation),
        "checks": validation,
    }
    unresolved = [check["tag"] for check in validation if check["status"] == UNRESOLVED]
    if unresolved:
        result["warnings"].append("Draft still needs confirmed values or review for: " + ", ".join(unresolved) + ".")

    draft = LabelDraftRecord(
        user_id=user.id if user else None,
        product_name=product_name.strip(),
        category=product_category,
        source_scan_id=str(source_scan.id) if source_scan is not None else None,
        label_data=result["label_data"],
        warnings=result["warnings"],
        pdf_payload=render_label_pdf(result["label_data"]),
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return {"success": True, "draft_id": draft.id, "pdf_download_url": f"/label/drafts/{draft.id}/download", **result}


@router.get("/drafts/{draft_id}/download")
def download_label_pdf(draft_id: int, user: Optional[UserAccount] = Depends(get_optional_user), db: Session = Depends(get_db)):
    draft = db.query(LabelDraftRecord).filter(LabelDraftRecord.id == draft_id).first()
    if draft is None or (draft.user_id is not None and draft.user_id != (user.id if user else None)):
        raise HTTPException(status_code=404, detail="Label draft not found.")
    if not draft.pdf_payload:
        raise HTTPException(status_code=409, detail="This legacy draft has no PDF export. Generate a new draft to create one.")
    return Response(draft.pdf_payload, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="true-label-draft-{draft.id}.pdf"'})
