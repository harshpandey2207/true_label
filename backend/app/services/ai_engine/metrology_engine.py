"""Local, evidence-preserving image analysis for the prototype scanner.

No image is sent to a hosted OCR service from this module. Local OCR is
explicitly opt-in. RapidOCR is preferred because its ONNX models are bundled
with the optional runtime and do not require the Paddle model downloader;
PaddleOCR remains available as an explicitly selectable engine and fallback.
"""

from __future__ import annotations

import os
import re
import tempfile
from importlib.util import find_spec
from functools import lru_cache
from typing import Any

from PIL import Image, ImageFilter, ImageOps, ImageStat


def _local_ocr_enabled() -> bool:
    """Enable installed local OCR by default; allow explicit operator opt-out.

    The lightweight deployment does not install either optional OCR package,
    so it remains manual-confirmation only. A developer workstation that has
    installed RapidOCR should work with the normal app launch command.
    """
    setting = os.getenv("TRUE_LABEL_ENABLE_LOCAL_OCR", "").strip().lower()
    if setting in {"0", "false", "no", "off", "disabled"}:
        return False
    if setting in {"1", "true", "yes", "on", "enabled"}:
        return True
    try:
        return find_spec("rapidocr_onnxruntime") is not None or find_spec("paddleocr") is not None
    except (ImportError, ValueError):
        return False


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
    if not _local_ocr_enabled():
        return None
    try:
        from paddleocr import PaddleOCR  # type: ignore

        return PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    except Exception:
        return None


@lru_cache(maxsize=1)
def _rapid_ocr() -> Any | None:
    if not _local_ocr_enabled():
        return None
    try:
        from rapidocr_onnxruntime import RapidOCR  # type: ignore

        return RapidOCR()
    except Exception:
        return None


def _rapid_lines(result: Any) -> list[tuple[list[list[float]], str, float]]:
    """Normalise RapidOCR's ``(boxes, text, confidence)`` rows."""
    if isinstance(result, tuple):
        result = result[0]
    lines: list[tuple[list[list[float]], str, float]] = []
    for row in result or []:
        if not row or len(row) < 3:
            continue
        box, text, confidence = row[0], row[1], row[2]
        text = str(text).strip()
        if text:
            lines.append((box, text, float(confidence)))
    return lines


def _rotate_box_to_original(box: list[list[float]], width: int, height: int, angle: int) -> list[list[float]]:
    """Map a box detected on a PIL-rotated image back to original pixels."""
    transformed: list[list[float]] = []
    for point in box:
        x, y = float(point[0]), float(point[1])
        if angle == 90:
            transformed.append([height - y, x])
        elif angle == 270:
            transformed.append([y, width - x])
        else:  # 180 degrees
            transformed.append([width - x, height - y])
    return transformed


def _run_rapid_ocr(ocr: Any, image_path: str) -> list[tuple[list[list[float]], str, float]]:
    """Run RapidOCR and retry rotated package photos when no text is found."""
    try:
        lines = _rapid_lines(ocr(image_path))
    except Exception:
        lines = []
    if lines:
        return lines

    try:
        with Image.open(image_path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            width, height = image.size
            for angle in (90, 270, 180):
                rotated = image.rotate(angle, expand=True)
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as handle:
                    rotated.save(handle, format="JPEG", quality=92)
                    rotated_path = handle.name
                try:
                    rotated_lines = _rapid_lines(ocr(rotated_path))
                finally:
                    if os.path.exists(rotated_path):
                        os.remove(rotated_path)
                if rotated_lines:
                    return [(_rotate_box_to_original(box, width, height, angle), text, confidence) for box, text, confidence in rotated_lines]
    except Exception:
        return []
    return []


def _paddle_lines(result: Any) -> list[tuple[list[list[float]], str, float]]:
    """Normalise PaddleOCR's nested ``[box, [text, confidence]]`` rows."""
    lines: list[tuple[list[list[float]], str, float]] = []
    for group in result or []:
        if not group:
            continue
        for row in group:
            if not row or len(row) < 2:
                continue
            box, content = row[0], row[1]
            if not content or len(content) < 2:
                continue
            text = str(content[0]).strip()
            if text:
                lines.append((box, text, float(content[1])))
    return lines


def _extract_lines(image_path: str) -> tuple[list[tuple[list[list[float]], str, float]], str, list[str]]:
    if not _local_ocr_enabled():
        return [], "unavailable", [
            "No local OCR runtime is installed or local OCR was explicitly disabled. The image was saved as evidence, but declarations need manual confirmation."
        ]

    preference = os.getenv("TRUE_LABEL_OCR_ENGINE", "rapidocr").strip().lower()
    engines: list[tuple[str, Any]] = []
    if preference in {"paddle", "paddleocr"}:
        engines.extend([("paddle", _paddle_ocr), ("rapidocr", _rapid_ocr)])
    else:
        engines.extend([("rapidocr", _rapid_ocr), ("paddle", _paddle_ocr)])

    attempted: list[str] = []
    for name, factory in engines:
        ocr = factory()
        if ocr is None:
            continue
        attempted.append(name)
        try:
            if name == "paddle":
                lines = _paddle_lines(ocr.ocr(image_path, cls=True))
            else:
                lines = _run_rapid_ocr(ocr, image_path)
            if lines:
                return lines, name, []
        except Exception:
            continue

    if attempted:
        return [], attempted[-1], [
            "Local OCR could not read this image. Retake a sharper, glare-free close-up or enter the declaration manually."
        ]
    return [], "unavailable", [
        "No local OCR runtime is available. Install the optional RapidOCR runtime (or PaddleOCR); until then, declarations require manual confirmation."
    ]


def _tag_declaration(text: str) -> tuple[str, str | None]:
    value = text.lower()
    if re.search(r"\b(?:fssai|lic(?:ence|ense)\s*(?:no|number)|registration\s*(?:no|number))\b", value) and "fssai" in value:
        return "FSSAI_LICENSE", None
    if re.search(r"(?:m\s*\.?\s*r\s*\.?\s*p|max(?:imum)?\s+retail\s+price|(?:₹|rs\.?|inr)\s*\d)", value):
        return "MRP", None
    if re.search(r"\b(?:net\s*(?:wt|weight|qty|quantity)|\d+(?:\.\d+)?\s*(?:g|gm|gms|kg|ml|l))\b", value) and not re.search(r"\b(?:w/w|usp|\bip\b|%)\b", value):
        if re.search(r"\b(?:minimum|not\s+less\s+than|at\s+least|approximately|approx\.?)\b", value):
            return "NET_QUANTITY", "Potentially misleading quantity expression detected in readable text."
        return "NET_QUANTITY", None
    if re.search(r"\b(?:batch|lot\s*(?:no|number)?|b\.?\s*no\.?)\b", value):
        return "BATCH_CODE", None
    if re.search(r"\b(?:best\s+before|use\s+by|consume\s+before)\b", value):
        return "BEST_BEFORE_DATE", None
    # Small package photos frequently turn "Mfg. Date" into variants such as
    # "Mig.Date" or "Mfg Dafe". These are still readable date-label evidence;
    # do not discard them just because one character was misread.
    if re.search(r"\b(?:mfg|mfd|mig|manufactur\w*)\b", value) and re.search(
        r"\b(?:date|dat|dafe|oate)\b", value
    ):
        return "MANUFACTURING_DATE", None
    if re.search(r"\bexp\w*\b", value) and re.search(r"\b(?:date|dat|dafe|oate)\b", value):
        return "EXPIRY_DATE", None
    if re.search(r"\b(?:expiry|exp\.?\s*date|use\s*before)\b", value):
        return "EXPIRY_DATE", None
    if re.search(r"\b(?:licen[cs]e|lic\.)\s*(?:no|number|#)\b", value):
        return "LICENSE_NO", None
    if re.search(r"\b(?:toll\s*free|customer\s*care|consumer\s*(?:care|affairs)|helpline|complaint|feedback|queries|e-?mail)\b", value):
        return "CONSUMER_CARE", None
    if re.search(r"\b(?:marketed\s*by|manufactured\s*by|mfd\.?\s*by|mfg\.?\s*by|manufacturer)\b", value):
        return "MANUFACTURER", None
    if re.search(r"\b(?:expiry|exp(?:iry)?|packed\s+on|pkd)\b", value) or re.search(
        r"\b(?:mfg|mfd|manufactured)\b.*(?:date|month|year|\d{1,2}[/-](?:\d{1,2}[/-])?\d{4})", value
    ):
        return "MANUFACTURING_DATE", None
    if re.search(r"\b(?:ingredients?|composition|contains)\b", value):
        return "INGREDIENTS", None
    if re.search(r"\b(?:green\s+dot|brown\s+dot|vegetarian|non[-\s]?vegetarian|veg\.?|non[-\s]?veg\.?)\b", value):
        return "VEG_NON_VEG_LOGO", None
    if re.search(r"\b(?:bis|isi|is\s*\d{3,})\b", value):
        return "BIS_MARK", None
    if re.search(r"\b(?:e[-\s]?waste|recycle|dispose|battery\s+disposal)\b", value):
        return "E_WASTE_INFO", None
    if re.search(r"\b(?:country\s+of\s+origin|made\s+in|imported\s+from|origin:)\b", value):
        return "COUNTRY_OF_ORIGIN", None
    if re.search(r"\b(?:model|item|product)\s*(?:no|number|#|id)\b", value):
        return "MODEL", None
    if re.search(r"\b(?:serial|s\.?n\.?)\s*(?:no|number|#)?\b", value):
        return "SERIAL_NUMBER", None
    if re.search(r"\b(?:sterile|non[-\s]?sterile)\b", value):
        return "STERILE_STATUS", None
    if re.search(r"\b(?:health\s+warning|smoking|tobacco\s+causes|nicotine)\b", value):
        return "HEALTH_WARNING", None
    if re.search(r"\b(?:warning|caution|keep\s+out\s+of\s+reach|flammable|hazard)\b", value):
        return "HAZARD_WARNING", None
    if re.search(r"\b(?:age\s*\d+|\d+\s*\+\s*years?|ages?)\b", value):
        return "AGE_GROUP", None
    if re.search(r"\b(?:size|uk\s*\d+|eu\s*\d+|us\s*\d+)\b", value):
        return "SIZE", None
    if re.search(r"\b(?:cotton|polyester|nylon|viscose|fibre|fiber)\b", value):
        return "FIBRE_CONTENT", None
    if re.search(r"\b(?:leather|synthetic|upper|material)\b", value):
        return "MATERIAL", None
    if re.search(r"\b(?:source|drawn|spring)\b.*\b(?:water|well|river)\b", value):
        return "SOURCE_NAME", None
    if re.search(r"\b(?:common|generic|commodity)\s+(?:name|description)\b", value):
        return "COMMODITY_NAME", None

    # A prominent all-capital title is useful product-name evidence (for
    # example, CIPLADINE on the supplied package). Keep this conservative so
    # warnings, dates, quantities and legal marks are not promoted to a
    # commodity name merely because OCR rendered them in capitals.
    compact = re.sub(r"[^A-Za-z0-9 ]+", " ", text).strip()
    letters = [character for character in compact if character.isalpha()]
    blocked_title_words = {
        "BATCH", "DATE", "EXPIRY", "MRP", "COMPOSITION", "WARNING", "CAUTION",
        "EXTERNAL", "ONLY", "STORE", "KEEP", "PROTECT", "REGISTERED", "TRADEMARK",
        "EFFECTIVE", "AGAINST", "CUTS", "WOUNDS", "BURNS", "INFECTIONS",
    }
    compact_title = compact.upper().replace(" ", "")
    blocked_title_fragments = (
        "EXTERNALUSEONLY", "KEEPOUT", "STOREBELOW", "PROTECTFROM", "REGISTEREDTRADEMARK",
        "EFFECTIVEAGAINST", "MULTIPURPOSE", "COMPOSITION",
    )
    if (
        len(letters) >= 5
        and not any(character.isdigit() for character in compact)
        and sum(character.isupper() for character in letters) / len(letters) >= 0.8
        and not (set(compact.upper().split()) & blocked_title_words)
        and not any(fragment in compact_title for fragment in blocked_title_fragments)
    ):
        return "COMMODITY_NAME", None
    return "GENERAL", None


def _looks_like_date_value(text: str) -> bool:
    """Recognise common OCR forms of month/year and day/month/year values."""
    compact = re.sub(r"\s+", "", text.lower())
    return bool(
        re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", compact)
        or re.search(r"\b\d{1,2}[/-]\d{4}\b", compact)
        or re.search(r"\b\d{6,8}\b", compact)
    )


def _looks_like_price_value(text: str) -> bool:
    """Return true only for a standalone two-decimal price candidate."""
    return bool(re.fullmatch(r"\s*\d{1,7}[.,]\d{2}\s*", text))


def _looks_like_batch_value(text: str) -> bool:
    """Recognise a compact batch identifier only when a batch label exists."""
    compact = re.sub(r"[^A-Za-z0-9-]", "", text).upper()
    return (
        5 <= len(compact) <= 24
        and any(character.isalpha() for character in compact)
        and any(character.isdigit() for character in compact)
    )


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
    recognized_labels: dict[str, list[tuple[list[list[float]], str]]] = {
        "MANUFACTURING_DATE": [], "EXPIRY_DATE": [], "MRP": [], "BATCH_CODE": [],
    }
    for candidate_box, candidate_text, _candidate_confidence in lines:
        candidate_tag, _ = _tag_declaration(candidate_text)
        if candidate_tag in recognized_labels:
            recognized_labels[candidate_tag].append((candidate_box, candidate_text))

    def _box_center(candidate_box: list[list[float]]) -> tuple[float, float]:
        return (
            sum(float(point[0]) for point in candidate_box) / max(len(candidate_box), 1),
            sum(float(point[1]) for point in candidate_box) / max(len(candidate_box), 1),
        )

    def _associate_rows(
        labels: list[tuple[list[list[float]], str]],
        value_indexes: list[int],
    ) -> list[tuple[int, str]]:
        """Associate separate OCR value lines with nearby labels conservatively.

        Perspective can skew the baselines enough that independent nearest
        matching swaps expiry and MRP values. When a panel has the same number
        of labels and values, preserve their top-to-bottom row order; otherwise
        use nearest geometry and require a reasonable distance.
        """
        if not labels or not value_indexes:
            return []
        ordered_labels = sorted(labels, key=lambda item: _box_center(item[0])[1])
        ordered_values = sorted(value_indexes, key=lambda index: _box_center(lines[index][0])[1])
        if len(ordered_labels) == len(ordered_values):
            return [
                (value_index, _tag_declaration(label_text)[0])
                for (label_box, label_text), value_index in zip(ordered_labels, ordered_values)
            ]

        pairs: list[tuple[int, str]] = []
        unmatched_labels = list(ordered_labels)
        for value_index in ordered_values:
            value_box = lines[value_index][0]
            value_center = _box_center(value_box)
            if not unmatched_labels:
                break
            distances = [
                ((value_center[0] - _box_center(label_box)[0]) ** 2 + (value_center[1] - _box_center(label_box)[1]) ** 2, position)
                for position, (label_box, _label_text) in enumerate(unmatched_labels)
            ]
            distance_squared, position = min(distances)
            if distance_squared > (max(image.size) * 0.4) ** 2:
                continue
            _label_box, label_text = unmatched_labels.pop(position)
            pairs.append((value_index, _tag_declaration(label_text)[0]))
        return pairs

    date_value_indexes = [index for index, (_box, text, _confidence) in enumerate(lines) if _looks_like_date_value(text)]
    price_value_indexes = [index for index, (_box, text, _confidence) in enumerate(lines) if _looks_like_price_value(text)]
    batch_value_indexes = [index for index, (_box, text, _confidence) in enumerate(lines) if _looks_like_batch_value(text)]
    associated_tags: dict[int, str] = {}
    date_labels = [*recognized_labels["MANUFACTURING_DATE"], *recognized_labels["EXPIRY_DATE"]]
    for candidate_indexes, candidate_labels in (
        (date_value_indexes, date_labels),
        (price_value_indexes, recognized_labels["MRP"]),
        (batch_value_indexes, recognized_labels["BATCH_CODE"]),
    ):
        for value_index, tag in _associate_rows(candidate_labels, candidate_indexes):
            if tag and tag != "GENERAL":
                associated_tags[value_index] = tag

    for line_index, (box, text, confidence) in enumerate(lines):
        tag, failure_reason = _tag_declaration(text)
        if tag == "GENERAL":
            tag = associated_tags.get(line_index, tag)
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
            # Kept for older clients; absence of a declaration is never
            # represented here. A value is compliant only when a readable
            # declaration itself did not produce an evidence-backed finding.
            "is_compliant": not (failure_reason and confidence >= 0.55),
            "failure_reason": failure_reason,
            "message": failure_reason or "Readable declaration detected; rule applicability and presentation still need review.",
        })

    # Language is evaluated as evidence, not as a guessed compliance claim:
    # only readable OCR text with a usable confidence can support this check.
    if not any(item.get("tag") == "LANGUAGE_CHECK" for item in declarations):
        language_evidence = next(
            (
                (box, text, confidence)
                for box, text, confidence in lines
                if confidence >= 0.55 and re.search(r"[A-Za-z\u0900-\u097F]", text)
            ),
            None,
        )
        if language_evidence:
            box, text, confidence = language_evidence
            x_values = [float(point[0]) for point in box]
            y_values = [float(point[1]) for point in box]
            declarations.append({
                "text": text,
                "tag": "LANGUAGE_CHECK",
                "field": "language_check",
                "confidence": round(confidence, 3),
                "box": [
                    [round(min(x_values) / image.width, 4), round(min(y_values) / image.height, 4)],
                    [round(max(x_values) / image.width, 4), round(max(y_values) / image.height, 4)],
                ],
                "finding_status": "DETECTED",
                "is_compliant": True,
                "failure_reason": None,
                "message": "Readable English or Hindi label text was detected; complete language and prominence review remains manual.",
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
