"""Deterministic, editable SVG label drafts for the prototype.

The renderer deliberately does not invent identity assets or legally sensitive
facts. It turns supplied text into editable SVG and marks unknown required
content for review.
"""

from __future__ import annotations

import html
import io
import re
from collections import Counter
from typing import Any

from PIL import Image

CATEGORIES = [
    "General Packaged Commodity",
    "Food & Beverages",
    "Electronics & Appliances",
    "Cosmetics, Ointments & Pharma Goods",
    "Apparel & Textiles",
    "Medical Devices",
]

SIDE_NAMES = ("Front", "Back", "Left", "Right", "Top", "Bottom")
DEFAULT_PALETTE = ("#153B50", "#F7FAFC", "#2F855A")


def _pdf_escape(value: Any) -> str:
    return str(value or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", "replace").decode("latin-1")


def render_label_pdf(label_data: dict[str, Any]) -> bytes:
    """Create a small vector/text PDF with one physical-size page per side.

    SVG remains the editable source of truth. This export maps only supplied
    declaration text and sampled palette values to PDF primitives; it never
    rasterises or invents identity artwork. Printers must still confirm bleed,
    ICC profile, trim and imposed-sheet setup.
    """
    sides = label_data.get("sides", [])
    supplied = label_data.get("supplied_values", {}) or {}
    title = str(label_data.get("source_dimensions") or "Label draft")
    product_name = str(label_data.get("product_name") or "Approved product identity to confirm")
    objects: list[bytes] = [b"", b""]
    page_numbers: list[int] = []
    for index, side in enumerate(sides, start=1):
        dimensions = side.get("physical_dimensions_mm", {})
        width = max(float(dimensions.get("width", 100)), 20) * 72 / 25.4
        height = max(float(dimensions.get("height", 150)), 20) * 72 / 25.4
        primary = str(side.get("sampled_primary_color") or "#153B50").lstrip("#")
        try:
            rgb = tuple(int(primary[position:position + 2], 16) / 255 for position in (0, 2, 4))
        except ValueError:
            rgb = (0.08, 0.23, 0.31)
        y = height - 36
        lines = [
            "BT /F1 16 Tf 18 %0.2f Td (%s) Tj ET" % (y, _pdf_escape(f"{side.get('side_name', 'Panel')} - True Label draft")),
            "BT /F1 12 Tf 18 %0.2f Td (%s) Tj ET" % (y - 19, _pdf_escape(product_name)),
            "%0.3f %0.3f %0.3f rg 18 %0.2f %0.2f 28 re f" % (*rgb, y - 42, max(width - 36, 1)),
            "BT /F1 9 Tf 22 %0.2f Td (Editable SVG source: verify approved artwork, trim, bleed and printer profile.) Tj ET" % (y - 60),
        ]
        row_y = y - 88
        for key, value in list(supplied.items())[:16]:
            if row_y < 26:
                break
            lines.append("BT /F1 9 Tf 22 %0.2f Td (%s: %s) Tj ET" % (row_y, _pdf_escape(str(key).replace("_", " ").title()), _pdf_escape(value)))
            row_y -= 14
        lines.append("BT /F1 7 Tf 18 12 Td (True Label prototype | %s | panel %d of %d) Tj ET" % (_pdf_escape(title), index, len(sides)))
        stream = "\n".join(lines).encode("latin-1", "replace")
        content_number = len(objects) + 1
        objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        page_number = len(objects) + 1
        page_numbers.append(page_number)
        objects.append(("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents %d 0 R >>" % (width, height, content_number)).encode())
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = ("<< /Type /Pages /Kids [" + " ".join(f"{number} 0 R" for number in page_numbers) + f"] /Count {len(page_numbers)} >>").encode()
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, value in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode())
        output.extend(value)
        output.extend(b"\nendobj\n")
    startxref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    output.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:]))
    output.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{startxref}\n%%EOF\n".encode())
    return bytes(output)


def _safe(value: Any) -> str:
    return html.escape(str(value or "").strip(), quote=True)


def _pixel_values(image: Image.Image) -> list[tuple[int, int, int]]:
    flattened = getattr(image, "get_flattened_data", None)
    return list(flattened() if flattened else image.getdata())


def _side_name(filename: str, index: int) -> str:
    lowered = filename.lower()
    for side in SIDE_NAMES:
        if side.lower() in lowered:
            return side
    return SIDE_NAMES[index] if index < len(SIDE_NAMES) else f"Panel {index + 1}"


def _parse_dimensions(raw: str) -> tuple[float, float, str]:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(mm|cm|in)?\s*[x×]\s*(\d+(?:\.\d+)?)\s*(mm|cm|in)?", raw.lower())
    if not match:
        return 100.0, 150.0, "100 × 150 mm (draft assumption)"
    first, first_unit, second, second_unit = match.groups()
    unit = first_unit or second_unit or "mm"
    multiplier = {"mm": 1.0, "cm": 10.0, "in": 25.4}[unit]
    width, height = float(first) * multiplier, float(second) * multiplier
    if not 20 <= width <= 1000 or not 20 <= height <= 1000:
        raise ValueError("Finished label dimensions must be between 20 mm and 1000 mm per side.")
    return width, height, f"{width:g} × {height:g} mm"


def _palette_from_images(images: list[tuple[str, bytes]]) -> tuple[str, str, str]:
    swatches: list[tuple[int, int, int]] = []
    for _, content in images:
        try:
            with Image.open(io.BytesIO(content)) as image:
                small = image.convert("RGB").resize((32, 32), Image.Resampling.LANCZOS)
                swatches.extend(_pixel_values(small))
        except Exception:
            continue
    if not swatches:
        return DEFAULT_PALETTE
    # Avoid using near-white / near-black background pixels for the identity hue.
    candidates = [colour for colour in swatches if 35 < sum(colour) / 3 < 220]
    primary = Counter(candidates or swatches).most_common(1)[0][0]
    def hex_colour(value: tuple[int, int, int]) -> str:
        return "#%02X%02X%02X" % value
    primary_hex = hex_colour(primary)
    contrast = "#FFFFFF" if sum(primary) / 3 < 140 else "#102A43"
    accent = "#D69E2E" if primary[1] > primary[0] else "#2F855A"
    return primary_hex, contrast, accent


def _text_rows(label_values: dict[str, Any], additional_details: str) -> list[tuple[str, str]]:
    rows = [(str(key).replace("_", " ").title(), str(value).strip()) for key, value in label_values.items() if str(value).strip()]
    rows.extend(("Additional copy", line.strip()) for line in additional_details.splitlines() if line.strip())
    return rows


def _svg_panel(
    side_name: str,
    index: int,
    total: int,
    product_name: str,
    category: str,
    shape: str,
    width_mm: float,
    height_mm: float,
    dimensions_text: str,
    rows: list[tuple[str, str]],
    palette: tuple[str, str, str],
) -> str:
    primary, secondary, accent = palette
    escaped_name, escaped_category = _safe(product_name), _safe(category)
    start_y = 470
    rendered_rows = []
    for row_index, (label, value) in enumerate(rows[:13]):
        y = start_y + row_index * 68
        rendered_rows.append(
            f'<text x="92" y="{y}" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#102A43">{_safe(label)}</text>'
            f'<text x="92" y="{y + 29}" font-family="Arial, sans-serif" font-size="22" fill="#1A202C">{_safe(value)}</text>'
            f'<line x1="90" y1="{y + 42}" x2="910" y2="{y + 42}" stroke="#CBD5E0" stroke-width="1"/>'
        )
    remaining = max(0, len(rows) - 13)
    remainder = f'<text x="92" y="1410" font-family="Arial, sans-serif" font-size="18" fill="#744210">+ {remaining} additional supplied item(s): review in editor</text>' if remaining else ""
    front_copy = (
        f'<rect x="90" y="420" width="820" height="112" rx="16" fill="{secondary}" opacity="0.15"/>'
        f'<text x="120" y="470" font-family="Arial, sans-serif" font-size="27" fill="{secondary}">Approved brand mark / product artwork goes here</text>'
        f'<text x="120" y="510" font-family="Arial, sans-serif" font-size="18" fill="{secondary}">Placeholder only — no logo, barcode or product photography has been fabricated.</text>'
    ) if index == 0 else ""
    if not rows:
        rendered_rows.append('<text x="92" y="555" font-family="Arial, sans-serif" font-size="28" fill="#744210">REVIEW REQUIRED: add the approved declaration text before use.</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width_mm:g}mm" height="{height_mm:g}mm" viewBox="0 0 1000 1500" role="img" aria-label="Editable {side_name} label draft">
  <rect width="1000" height="1500" fill="#FFFFFF"/>
  <rect x="35" y="35" width="930" height="1430" rx="18" fill="none" stroke="#A0AEC0" stroke-width="2" stroke-dasharray="12 8"/>
  <rect x="65" y="65" width="870" height="260" rx="20" fill="{primary}"/>
  <text x="92" y="148" font-family="Arial, sans-serif" font-size="25" font-weight="700" fill="{secondary}">{_safe(side_name)} PANEL · {index + 1}/{total}</text>
  <text x="92" y="220" font-family="Arial, sans-serif" font-size="54" font-weight="700" fill="{secondary}">{escaped_name}</text>
  <text x="92" y="270" font-family="Arial, sans-serif" font-size="24" fill="{secondary}">{escaped_category} · {_safe(shape or 'Package shape to confirm')} · {_safe(dimensions_text)}</text>
  <rect x="90" y="360" width="820" height="8" fill="{accent}"/>
  {front_copy}
  {''.join(rendered_rows)}
  {remainder}
  <text x="92" y="1450" font-family="Arial, sans-serif" font-size="16" fill="#4A5568">Prototype editable SVG. Verify dimensions, safe area, bleed, rules and approved artwork before printing.</text>
</svg>'''


def generate_label_draft(
    product_name: str,
    product_category: str,
    shape: str,
    dimensions: str,
    custom_prompt: str,
    label_values: dict[str, Any],
    additional_details: str,
    images: list[tuple[str, bytes]],
    side_count: int = 2,
) -> dict[str, Any]:
    if product_category not in CATEGORIES:
        raise ValueError("Choose one of the supported product categories.")
    if not product_name.strip():
        raise ValueError("Enter a product name before generating a draft.")
    if side_count not in {2, 4, 6}:
        raise ValueError("Choose two, four or six package sides.")
    width_mm, height_mm, dimensions_text = _parse_dimensions(dimensions)
    count = len(images) if images else side_count
    count = min(max(count, 1), 6)
    palette = _palette_from_images(images)
    rows = _text_rows(label_values, additional_details)
    filenames = [filename for filename, _ in images] or ["" for _ in range(count)]
    sides = []
    for index in range(count):
        side_name = _side_name(filenames[index] if index < len(filenames) else "", index)
        sides.append({
            "side_name": side_name,
            "side_index": index,
            "svg_code": _svg_panel(side_name, index, count, product_name, product_category, shape, width_mm, height_mm, dimensions_text, rows, palette),
            "sampled_primary_color": palette[0],
            "sampled_secondary_color": palette[1],
            "sampled_accent_color": palette[2],
            "physical_dimensions_mm": {"width": width_mm, "height": height_mm},
            "safe_area_mm": 3,
            "bleed_mm": None,
            "editable": True,
        })
    return {
        "label_data": {
            "schema_version": "2.0",
            "product_name": product_name.strip(),
            "product_category": product_category,
            "sides": sides,
            "brand_dna": {
                "primary_color": palette[0],
                "secondary_color": palette[1],
                "accent_color": palette[2],
                "font_style": "Arial / system sans-serif",
                "design_aesthetic": "Structured editable prototype layout",
            },
            "source_dimensions": dimensions_text,
            "supplied_values": {str(key): str(value) for key, value in label_values.items()},
            "design_brief": custom_prompt.strip(),
        },
        "warnings": [
            "Generated locally from deterministic SVG templates; no hosted generative-design provider was used.",
            "This is not print-ready artwork. Confirm trim, bleed, colour profile, approved identity assets and printer specifications.",
            "The renderer preserves supplied text and palette cues only; it does not reproduce or invent logos, barcodes, photographs, certifications or missing declarations.",
        ],
        "engine_used": "Local deterministic SVG template renderer",
    }
