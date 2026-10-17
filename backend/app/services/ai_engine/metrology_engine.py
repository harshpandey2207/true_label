"""Local, evidence-preserving image analysis for the prototype scanner.

No image is sent to a hosted OCR service from this module. PaddleOCR is
optional and deliberately opt-in because model downloads and inference are not
appropriate for a constrained demo deployment without an operator decision.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Any

from PIL import Image, ImageFilter, ImageOps, ImageStat


def _pixel_values(image: Image.Image) -> list[Any]:
    flattened = getattr(image, "get_flattened_data", None)
    return list(flattened() if flattened else image.getdata())


def _quality_report(image: Image.Image) -> dict[str, Any]:
    gray = image.convert("L")
    pixels = _pixel_values(gray)
    count = max(len(pixels), 1)
    glare_ratio = sum(value >= 245 for value in pixels) / count
    edge_variance = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).var[0]
    warnings: list[str] = []
    if min(image.size) < 700:
        warnings.append("The image is low resolution for small package text. Move closer and keep the text in focus.")
    if glare_ratio > 0.12:
        warnings.append("Strong glare/reflection may hide text. Tilt the package or use softer, indirect light.")
    if edge_variance < 110:
        warnings.append("The image may be blurred or out of focus. Hold still and capture the declaration straight on.")
    if image.width > image.height * 2.5 or image.height > image.width * 2.5:
        warnings.append("The package panel is highly elongated in this frame. Capture a straight-on close-up for better readability.")
    return {
        "width": image.width,
        "height": image.height,
        "glare_ratio": round(glare_ratio, 3),
        "edge_variance": round(edge_variance, 1),
        "warnings": warnings,
    }


def _perceptual_hash(image: Image.Image) -> str:
    """A small deterministic average hash used only for duplicate-side hints."""
    small = image.convert("L").resize((8, 8), Image.Resampling.LANCZOS)
    values = _pixel_values(small)
    average = sum(values) / len(values)
    return "".join("1" if value >= average else "0" for value in values)


def orb_overlap_score(first_path: str, second_path: str) -> dict[str, Any] | None:
    """Return a conservative ORB overlap hint when OpenCV is available.

    This is intentionally evidence-preserving: low texture, glare, or an
    incomplete match produces no conclusion.  It is used only to help an
    operator spot repeated photographs of a package side, never to stitch or
    remove source images.
    """
    try:
        import cv2  # type: ignore

        first = cv2.imread(first_path, cv2.IMREAD_GRAYSCALE)
        second = cv2.imread(second_path, cv2.IMREAD_GRAYSCALE)
        if first is None or second is None:
            return None
        detector = cv2.ORB_create(nfeatures=700)
        first_points, first_descriptors = detector.detectAndCompute(first, None)
        second_points, second_descriptors = detector.detectAndCompute(second, None)
        if first_descriptors is None or second_descriptors is None:
            return {"status": "insufficient_features", "first_keypoints": len(first_points or []), "second_keypoints": len(second_points or [])}
        matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(first_descriptors, second_descriptors)
        good = [match for match in matches if match.distance <= 42]
        denominator = max(min(len(first_points), len(second_points)), 1)
        return {
            "status": "evaluated",
            "first_keypoints": len(first_points),
            "second_keypoints": len(second_points),
            "good_matches": len(good),
            "overlap_ratio": round(len(good) / denominator, 3),
        }
    except Exception:
        return None


@lru_cache(maxsize=1)
def _paddle_ocr() -> Any | None:
    if os.getenv("TRUE_LABEL_ENABLE_LOCAL_OCR", "").strip().lower() not in {"1", "true", "yes"}:
        return None
    try:
        from paddleocr import PaddleOCR  # type: ignore

        return PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    except Exception:
        return None


def _extract_lines(image_path: str) -> tuple[list[tuple[list[list[float]], str, float]], str, list[str]]:
    ocr = _paddle_ocr()
    if ocr is None:
        return [], "unavailable", [
            "Text recognition is not configured in this deployment. The image was saved as evidence, but declarations need a manual confirmation or a deployment with optional local OCR enabled."
        ]
    try:
        result = ocr.ocr(image_path, cls=True)
    except Exception:
        return [], "paddle", ["Local OCR could not read this image. Retake a sharper, glare-free close-up or enter the declaration manually."]
    lines: list[tuple[list[list[float]], str, float]] = []
    for group in result or []:
        if not group:
            continue
        for row in group:
            if not row or len(row) < 2:
                continue
            box, content = row[0], row[1]
            text = str(content[0]).strip()
            if text:
                lines.append((box, text, float(content[1])))
    return lines, "paddle", []


def _tag_declaration(text: str) -> tuple[str, str | None]:
    value = text.lower()
    if re.search(r"(?:m\s*\.?\s*r\s*\.?\s*p|max(?:imum)?\s+retail\s+price|(?:₹|rs\.?|inr)\s*\d)", value):
        return "MRP", None
    if re.search(r"\b(?:net\s*(?:wt|weight|qty|quantity)|\d+(?:\.\d+)?\s*(?:g|gm|gms|kg|ml|l))\b", value) and not re.search(r"\b(?:w/w|usp|\bip\b|%)\b", value):
        if re.search(r"\b(?:minimum|not\s+less\s+than|at\s+least|approximately|approx\.?)\b", value):
            return "NET_QUANTITY", "Potentially misleading quantity expression detected in readable text."
        return "NET_QUANTITY", None
    if re.search(r"\b(?:batch|lot\s*(?:no|number)?|b\.?\s*no\.?)\b", value):
        return "BATCH_CODE", None
    if re.search(r"\b(?:mfg|mfd|manufactur(?:ed|ing)|expiry|exp(?:iry)?|packed\s+on|pkd)\b", value):
        return "MANUFACTURING_DATE", None
    if re.search(r"\b(?:toll\s*free|customer\s*care|consumer\s*(?:care|affairs)|helpline|complaint|feedback|queries|e-?mail)\b", value):
        return "CONSUMER_CARE", None
    if re.search(r"\b(?:marketed\s+by|manufactured\s+by|mfd\.?\s+by|mfg\.?\s+by|manufacturer)\b", value):
        return "MANUFACTURER", None
    if re.search(r"\bfssai\b", value):
        return "FSSAI_LICENSE", None
    return "GENERAL", None


def analyze_product_label(
    image_path: str,
    product_type: str = "package",
    distance_mm: float = 300.0,
    focal_length_px: float = 800.0,
    **_: Any,
) -> dict[str, Any]:
    """Analyse one image without inferring legal failure from missing OCR text."""
    try:
        with Image.open(image_path) as raw:
            image = ImageOps.exif_transpose(raw).convert("RGB")
    except Exception as exc:
        return {"status": "ERROR", "declarations": [], "error": f"Image processing failed: {exc}"}

    quality = _quality_report(image)
    lines, ocr_engine, ocr_warnings = _extract_lines(image_path)
    declarations: list[dict[str, Any]] = []
    for box, text, confidence in lines:
        tag, failure_reason = _tag_declaration(text)
        if tag == "GENERAL":
            continue
        x_values = [float(point[0]) for point in box]
        y_values = [float(point[1]) for point in box]
        scaled_box = [
            [round(min(x_values) / image.width, 4), round(min(y_values) / image.height, 4)],
            [round(max(x_values) / image.width, 4), round(max(y_values) / image.height, 4)],
        ]
        declarations.append({
            "text": text,
            "tag": tag,
            "field": tag.lower(),
            "confidence": round(confidence, 3),
            "box": scaled_box,
            "finding_status": "CONFIRMED_VIOLATION" if failure_reason and confidence >= 0.55 else "DETECTED",
            "failure_reason": failure_reason,
            "message": failure_reason or "Readable declaration detected; rule applicability and presentation still need review.",
        })

    return {
        "status": "UNRESOLVED" if not declarations else "EVIDENCE_CAPTURED",
        "product_type": product_type,
        "declarations": declarations,
        "ocr_engine": ocr_engine,
        "image_quality": quality,
        "warnings": [*quality["warnings"], *ocr_warnings],
        "perceptual_hash": _perceptual_hash(image),
        "measurement": {
            "distance_mm": distance_mm,
            "focal_length_px": focal_length_px,
            "status": "INDICATIVE_ONLY",
            "message": "No calibrated physical text-height conclusion is made from this image.",
        },
    }
