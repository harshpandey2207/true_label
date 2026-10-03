import json
from typing import Any, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.app.services.ai_engine.label_generator import (
    CATEGORIES,
    generate_label_draft,
)

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

    return {"success": True, **result}
