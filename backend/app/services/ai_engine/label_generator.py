"""Deterministic, editable SVG label drafts for the prototype.

The renderer deliberately does not invent identity assets or legally sensitive
facts. It turns supplied text into editable SVG and marks unknown required
content for review.
"""

from __future__ import annotations

import html
import io
import re
import colorsys
from collections import Counter
from textwrap import wrap
from typing import Any

from PIL import Image

CATEGORIES = [
    "General Packaged Commodity",
    "Food & Beverages",
    "Packaged Drinking Water",
    "Electronics & Appliances",
    "Electrical Cables & Accessories",
    "Cosmetics, Ointments & Pharma Goods",
    "Personal Care Products",
    "Household Cleaning Products",
    "Apparel & Textiles",
    "Footwear & Leather Goods",
    "Toys & Childcare Products",
    "Medical Devices",
    "Automotive Components & Lubricants",
    "Tobacco & Nicotine Products",
    "Stationery & School Supplies",
    "Agricultural Inputs",
    "Other / Custom Packaged Product",
]

SIDE_NAMES = ("Front", "Back", "Left", "Right", "Top", "Bottom")
DEFAULT_PALETTE = ("#153B50", "#F7FAFC", "#2F855A")
FRONT_SUMMARY_KEYS = {"mrp", "net_quantity"}


def _pdf_escape(value: Any) -> str:
    return str(value or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", "replace").decode("latin-1")


def _grid_metrics(row_count: int, view_height: float, grid_top: float) -> tuple[int, float, int, float]:
    """Return a compact, shared SVG/PDF declaration-grid layout."""
    columns = 1 if row_count <= 4 else 2
    footer_y = view_height - (300 if view_height >= 750 else 38)
    available = max(0.0, footer_y - grid_top - 24)
    rows_per_column = max(1, (row_count + columns - 1) // columns)
    minimum_pitch = 84 if view_height >= 750 else 58
    maximum_pitch = (230 if columns == 1 else 145) if view_height >= 750 else 96
    row_pitch = (
        min(maximum_pitch, max(minimum_pitch, available / rows_per_column))
        if available > 0
        else float(minimum_pitch)
    )
    capacity = int(available / row_pitch) * columns
    return columns, float(row_pitch), capacity, available


def render_label_pdf(label_data: dict[str, Any]) -> bytes:
    """Create a polished vector PDF proof, one correctly sized page per side.

    SVG remains the editable source of truth. This small PDF writer avoids an
    extra native rendering dependency and uses only vector paths and supplied
    text. It is a visual proof, not a printer-preflighted production file.
    """
    sides = label_data.get("sides", [])
    supplied = label_data.get("supplied_values", {}) or {}
    product_name = str(label_data.get("product_name") or "Product identity to confirm")
    product_category = str(label_data.get("product_category") or "Product category to confirm")
    objects: list[bytes] = [b"", b""]
    page_numbers: list[int] = []
    for index, side in enumerate(sides, start=1):
        side_index = int(side.get("side_index", index - 1))
        dimensions = side.get("physical_dimensions_mm", {})
        width = max(float(dimensions.get("width", 100)), 20) * 72 / 25.4
        height = max(float(dimensions.get("height", 150)), 20) * 72 / 25.4
        def colour(hex_value: str) -> tuple[float, float, float]:
            value = hex_value.lstrip("#")
            try:
                return tuple(int(value[offset:offset + 2], 16) / 255 for offset in (0, 2, 4))
            except (ValueError, IndexError):
                return (0.08, 0.23, 0.31)

        primary = colour(str(side.get("sampled_primary_color") or "#153B50"))
        accent = colour(str(side.get("sampled_accent_color") or "#2F855A"))
        cream = colour("#FFFDF8")
        card = colour("#F8F7F3")
        ink = colour("#172A25")
        muted = colour("#52615C")
        scale = width / 1000
        view_height = 1000 * height / width
        header_height_units = (
            min(330.0, max(220.0, view_height * 0.25))
            if side_index == 0
            else min(250.0, max(185.0, view_height * 0.18))
        )
        header_top_units = 48.0
        header_bottom_units = header_top_units + header_height_units
        header_y = height - (header_top_units + header_height_units) * scale
        header_height = header_height_units * scale
        margin = 22 * scale
        inner_width = width - margin * 2
        label_font = 17 * scale
        value_font = 21 * scale

        def rectangle(x: float, y: float, w: float, h: float, fill: tuple[float, float, float], stroke: tuple[float, float, float] | None = None) -> str:
            command = f"{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f"
            if stroke is not None:
                command += f"\n{stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG 0.7 w {x:.2f} {y:.2f} {w:.2f} {h:.2f} re S"
            return command

        def text(value: str, x: float, y: float, size: float, fill: tuple[float, float, float], bold: bool = False) -> str:
            font_name = "F2" if bold else "F1"
            return f"BT /{font_name} {size:.2f} Tf {fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg {x:.2f} {y:.2f} Td ({_pdf_escape(value)}) Tj ET"

        def circle(cx_units: float, cy_units: float, radius_units: float, fill: tuple[float, float, float]) -> str:
            cx, cy, radius = cx_units * scale, height - cy_units * scale, radius_units * scale
            handle = radius * 0.55228475
            return (
                f"{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg "
                f"{cx + radius:.2f} {cy:.2f} m "
                f"{cx + radius:.2f} {cy + handle:.2f} {cx + handle:.2f} {cy + radius:.2f} {cx:.2f} {cy + radius:.2f} c "
                f"{cx - handle:.2f} {cy + radius:.2f} {cx - radius:.2f} {cy + handle:.2f} {cx - radius:.2f} {cy:.2f} c "
                f"{cx - radius:.2f} {cy - handle:.2f} {cx - handle:.2f} {cy - radius:.2f} {cx:.2f} {cy - radius:.2f} c "
                f"{cx + handle:.2f} {cy - radius:.2f} {cx + radius:.2f} {cy - handle:.2f} {cx + radius:.2f} {cy:.2f} c f"
            )

        side_name = str(side.get("side_name") or f"Panel {index}")
        side_supplied = side["supplied_values"] if "supplied_values" in side else supplied
        dimension_label = (
            f"{dimensions.get('width', 100):g} x {dimensions.get('height', 150):g} mm"
        )
        commands = [
            rectangle(0, 0, width, height, cream),
            rectangle(22 * scale, height - (view_height - 22) * scale, 956 * scale, (view_height - 44) * scale, cream, colour("#D8D4CB")),
            rectangle(48 * scale, header_y, 904 * scale, header_height, cream, primary),
            rectangle(48 * scale, height - 110 * scale, 904 * scale, 62 * scale, primary),
            rectangle(690 * scale, height - 111 * scale, 232 * scale, 48 * scale, cream),
        ]
        commands.append(text(f"{side_name.upper()}  {index}/{len(sides)}", 94 * scale, height - 94 * scale, 22 * scale, cream, True))
        dimension_x = 806 - len(dimension_label) * 20 * 0.48
        commands.append(text(dimension_label, dimension_x * scale, height - 94 * scale, 20 * scale, primary, True))
        title_lines = wrap(product_name, width=24, break_long_words=True, break_on_hyphens=False) or [product_name]
        title_font_units = 72 if side_index == 0 and header_height_units >= 270 else 38
        title_font = title_font_units * scale
        title_start_units = (
            48 + max(130.0, header_height_units * 0.43)
            if side_index == 0
            else 176.0
        )
        for line_index, title_line in enumerate(title_lines[:2]):
            commands.append(text(title_line, 94 * scale, height - (title_start_units + line_index * (title_font_units + 8)) * scale, title_font, primary, True))
        commodity_copy = str(side_supplied.get("commodity_name") or side_supplied.get("Commodity Name") or "") if side_index == 0 else ""
        subtitle_start_units = title_start_units + len(title_lines[:2]) * (title_font_units + 8) + 12
        for line_index, subtitle in enumerate(wrap(commodity_copy, width=64, break_long_words=True, break_on_hyphens=False)[:2]):
            commands.append(text(subtitle, 96 * scale, height - (subtitle_start_units + line_index * 24) * scale, 21 * scale, ink))
        commands.append(rectangle(78 * scale, height - (header_bottom_units + 1) * scale, 844 * scale, 7 * scale, accent))
        if view_height >= 750:
            commands.append(
                f"{primary[0]:.3f} {primary[1]:.3f} {primary[2]:.3f} rg "
                f"{22 * scale:.2f} {22 * scale:.2f} m "
                f"{22 * scale:.2f} {278 * scale:.2f} l "
                f"{250 * scale:.2f} {340 * scale:.2f} {430 * scale:.2f} {240 * scale:.2f} {660 * scale:.2f} {290 * scale:.2f} c "
                f"{800 * scale:.2f} {340 * scale:.2f} {900 * scale:.2f} {235 * scale:.2f} {978 * scale:.2f} {260 * scale:.2f} c "
                f"{978 * scale:.2f} {22 * scale:.2f} l h f"
            )
            commands.append(
                f"{accent[0]:.3f} {accent[1]:.3f} {accent[2]:.3f} RG {8 * scale:.2f} w "
                f"{22 * scale:.2f} {278 * scale:.2f} m "
                f"{250 * scale:.2f} {340 * scale:.2f} {430 * scale:.2f} {240 * scale:.2f} {660 * scale:.2f} {290 * scale:.2f} c S"
            )
            commands.extend([
                circle(815, view_height - 168, 48, cream),
                circle(815, view_height - 168, 28, accent),
                circle(905, view_height - 123, 18, cream),
            ])

        rows = [(str(key).replace("_", " ").title(), str(value).strip()) for key, value in side_supplied.items() if str(value).strip()]
        summary_rows = _front_summary(rows, side_index)
        display_rows = _display_rows(rows, side_index)
        feature_y_units = header_bottom_units + 22
        if side_index == 0:
            feature_height_units = 94 if view_height >= 750 else 58
            feature_y = height - (feature_y_units + feature_height_units) * scale
            commands.append(rectangle(78 * scale, feature_y, 844 * scale, feature_height_units * scale, colour("#F5F1E9")))
            commands.append(rectangle(78 * scale, feature_y, 12 * scale, feature_height_units * scale, accent))
            pale_primary = tuple(channel * 0.12 + cream[channel] * 0.88 for channel in range(3))
            pale_accent = tuple(channel * 0.14 + cream[channel] * 0.86 for channel in range(3))
            commands.append(circle(865, feature_y_units + feature_height_units / 2, feature_height_units * 0.30, pale_primary))
            commands.append(circle(865, feature_y_units + feature_height_units / 2, feature_height_units * 0.16, pale_accent))
            commands.append(text("PRODUCT CATEGORY", 116 * scale, height - (feature_y_units + 22) * scale, 14 * scale, muted, True))
            for line_index, category_line in enumerate(wrap(product_category, width=50, break_long_words=True, break_on_hyphens=False)[:2]):
                commands.append(text(category_line, 116 * scale, height - (feature_y_units + 45 + line_index * 20) * scale, 19 * scale, ink, True))
            motif = (label_data.get("design_direction") or {}).get("motif", "wave")
            motif_center = feature_y_units + feature_height_units / 2
            if motif == "cross":
                commands.append(rectangle(854 * scale, height - (motif_center + 6) * scale, 38 * scale, 12 * scale, primary))
                commands.append(rectangle(867 * scale, height - (motif_center + 19) * scale, 12 * scale, 38 * scale, primary))
            elif motif == "bubble":
                commands.extend([circle(852, motif_center, 13, primary), circle(879, motif_center - 13, 8, accent), circle(884, motif_center + 13, 4, primary)])
            elif motif == "grid":
                for row in range(3):
                    for column in range(3):
                        x = (847 + column * 16) * scale
                        y = height - (motif_center - 18 + row * 16 + 9) * scale
                        commands.append(rectangle(x, y, 9 * scale, 9 * scale, primary))
            elif motif == "circuit":
                commands.append(
                    f"{primary[0]:.3f} {primary[1]:.3f} {primary[2]:.3f} RG {4 * scale:.2f} w "
                    f"{840 * scale:.2f} {height - (motif_center + 15) * scale:.2f} m "
                    f"{858 * scale:.2f} {height - (motif_center + 15) * scale:.2f} l "
                    f"{858 * scale:.2f} {height - (motif_center - 8) * scale:.2f} l "
                    f"{884 * scale:.2f} {height - (motif_center - 8) * scale:.2f} l S"
                )
                commands.extend([circle(884, motif_center - 8, 5, accent), circle(858, motif_center + 15, 4, accent)])
            else:
                commands.append(
                    f"{primary[0]:.3f} {primary[1]:.3f} {primary[2]:.3f} RG {5 * scale:.2f} w "
                    f"{840 * scale:.2f} {height - (motif_center + 4) * scale:.2f} m "
                    f"{852 * scale:.2f} {height - (motif_center - 16) * scale:.2f} "
                    f"{864 * scale:.2f} {height - (motif_center + 4) * scale:.2f} "
                    f"{876 * scale:.2f} {height - (motif_center + 16) * scale:.2f} "
                    f"{888 * scale:.2f} {height - (motif_center + 4) * scale:.2f} c S"
                )

        grid_top_units = header_bottom_units + (145 if side_index == 0 else 42)
        if summary_rows:
            summary_y_units = grid_top_units
            summary_height_units = 112
            summary_columns = len(summary_rows)
            summary_width_units = 816 if summary_columns == 1 else 398
            for summary_index, (label, value) in enumerate(summary_rows[:2]):
                summary_x_units = 92 + summary_index * 418
                key = _row_key(label)
                summary_label = "MAXIMUM RETAIL PRICE" if key == "mrp" else "NET QUANTITY"
                summary_lines = wrap(
                    value,
                    width=27 if summary_columns > 1 else 56,
                    break_long_words=True,
                    break_on_hyphens=False,
                )[:2]
                summary_y = height - (summary_y_units + summary_height_units) * scale
                commands.append(
                    rectangle(
                        summary_x_units * scale,
                        summary_y,
                        summary_width_units * scale,
                        summary_height_units * scale,
                        primary,
                    )
                )
                commands.append(
                    rectangle(
                        summary_x_units * scale,
                        summary_y,
                        9 * scale,
                        summary_height_units * scale,
                        accent,
                    )
                )
                commands.append(
                    text(
                        summary_label,
                        (summary_x_units + 26) * scale,
                        height - (summary_y_units + 36) * scale,
                        16 * scale,
                        cream,
                        True,
                    )
                )
                for line_index, summary_line in enumerate(summary_lines):
                    commands.append(
                        text(
                            summary_line,
                            (summary_x_units + 26) * scale,
                            height - (summary_y_units + 74 + line_index * 25) * scale,
                            23 * scale,
                            cream,
                            True,
                        )
                    )
            grid_top_units += summary_height_units + 20

        footer_y_units = view_height - (300 if view_height >= 750 else 38)
        columns, row_pitch_units, max_rows, available_height = _grid_metrics(
            len(display_rows), view_height, grid_top_units
        )
        rows_visible = display_rows[:max_rows]
        column_width_units = 816 if columns == 1 else 404
        for row_index, (key, value) in enumerate(rows_visible):
            column = 0 if columns == 1 else row_index % 2
            line_row = row_index if columns == 1 else row_index // 2
            x_units = 92 + column * 414
            card_top_units = grid_top_units + line_row * row_pitch_units
            text_offset = max(20.0, (row_pitch_units - 48) / 2)
            y_units = card_top_units + text_offset
            card_height_units = row_pitch_units - 10
            card_y = height - (card_top_units + card_height_units) * scale
            commands.append(rectangle(x_units * scale, card_y, column_width_units * scale, card_height_units * scale, card))
            commands.append(rectangle((x_units - 12) * scale, card_y, 4 * scale, card_height_units * scale, accent))
            commands.append(text(key.upper(), x_units * scale, height - y_units * scale, 17 * scale, muted, True))
            value_lines = wrap(value, width=36, break_long_words=True, break_on_hyphens=False) or [value]
            for line_index, value_line in enumerate(value_lines[:2]):
                commands.append(text(value_line, x_units * scale, height - (y_units + 27 + line_index * 21) * scale, 21 * scale, ink))
        if len(display_rows) > len(rows_visible):
            commands.append(text(f"{len(display_rows) - len(rows_visible)} supplied item(s) need another side or larger panel.", 92 * scale, height - (footer_y_units - 8) * scale, 17 * scale, muted))
        stream = "\n".join(commands).encode("latin-1", "replace")
        content_number = len(objects) + 1
        objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        page_number = len(objects) + 1
        page_numbers.append(page_number)
        objects.append(("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> /F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> >> >> /Contents %d 0 R >>" % (width, height, content_number)).encode())
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
        return 100.0, 150.0, "100 x 150 mm (draft assumption)"
    first, first_unit, second, second_unit = match.groups()
    unit = first_unit or second_unit or "mm"
    multiplier = {"mm": 1.0, "cm": 10.0, "in": 25.4}[unit]
    width, height = float(first) * multiplier, float(second) * multiplier
    if not 20 <= width <= 1000 or not 20 <= height <= 1000:
        raise ValueError("Finished label dimensions must be between 20 mm and 1000 mm per side.")
    return width, height, f"{width:g} x {height:g} mm"


def _palette_from_images(images: list[tuple[str, bytes]]) -> tuple[str, str, str]:
    saturated: list[tuple[float, tuple[int, int, int]]] = []
    for _, content in images:
        try:
            with Image.open(io.BytesIO(content)) as image:
                rgb = image.convert("RGB")
                # Package photos often contain a large white margin and a
                # hand/table behind the box. A central crop plus saturated
                # colour voting gives the artwork more influence than that
                # background without claiming to identify a brand palette.
                left, top = int(rgb.width * 0.12), int(rgb.height * 0.24)
                right, bottom = int(rgb.width * 0.88), int(rgb.height * 0.76)
                sample = rgb.crop((left, top, right, bottom)).resize(
                    (40, 40), Image.Resampling.LANCZOS
                )
                for pixel in _pixel_values(sample):
                    hue, saturation, value = colorsys.rgb_to_hsv(
                        *(channel / 255 for channel in pixel)
                    )
                    if saturation >= 0.34 and 0.16 <= value <= 0.92:
                        saturated.append((hue, pixel))
        except Exception:
            continue
    if not saturated:
        return DEFAULT_PALETTE

    hue_bins: Counter[int] = Counter()
    for hue, _ in saturated:
        hue_bins[round(hue * 48) % 48] += 1
    dominant_hue = hue_bins.most_common(1)[0][0] / 48
    candidates = [pixel for hue, pixel in saturated if abs((hue - dominant_hue + 0.5) % 1 - 0.5) <= 1 / 24]
    primary = tuple(
        round(sum(pixel[channel] for pixel in candidates) / len(candidates))
        for channel in range(3)
    )
    def hex_colour(value: tuple[int, int, int]) -> str:
        return "#%02X%02X%02X" % value
    primary_hex = hex_colour(primary)
    contrast = "#FFFDF8" if sum(primary) / 3 < 170 else "#17352D"
    if dominant_hue < 0.10 or dominant_hue > 0.92:
        accent = "#D84A32"
    elif 0.18 <= dominant_hue <= 0.46:
        accent = "#D69E2E"
    else:
        accent = "#2F855A"
    return primary_hex, contrast, accent


def sample_reference_palette(images: list[tuple[str, bytes]]) -> tuple[str, str, str]:
    """Return a local-only palette sample for optional design assistance."""
    return _palette_from_images(images)


def _text_rows(label_values: dict[str, Any], additional_details: str) -> list[tuple[str, str]]:
    rows = [(str(key).replace("_", " ").title(), str(value).strip()) for key, value in label_values.items() if str(value).strip()]
    rows.extend(("Additional copy", line.strip()) for line in additional_details.splitlines() if line.strip())
    return rows


def _row_key(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.strip().lower()).strip("_")


def _front_summary(rows: list[tuple[str, str]], side_index: int) -> list[tuple[str, str]]:
    if side_index != 0:
        return []
    return [(label, value) for label, value in rows if _row_key(label) in FRONT_SUMMARY_KEYS]


def _display_rows(rows: list[tuple[str, str]], side_index: int) -> list[tuple[str, str]]:
    return [
        (label, value)
        for label, value in rows
        if not (
            side_index == 0
            and (_row_key(label) == "commodity_name" or _row_key(label) in FRONT_SUMMARY_KEYS)
        )
    ]


def _local_design_direction(category: str, brief: str) -> dict[str, str]:
    """Map user intent and category to renderer-owned visual tokens offline."""
    style_cues = {
        "botanical": ("botanical", "leaf"),
        "herbal": ("botanical", "leaf"),
        "organic": ("botanical", "leaf"),
        "earthy": ("botanical", "leaf"),
        "clinical": ("clinical", "cross"),
        "sterile": ("clinical", "cross"),
        "playful": ("playful", "bubble"),
        "industrial": ("industrial", "circuit"),
        "technical": ("industrial", "circuit"),
        "premium": ("premium", "spark"),
        "luxury": ("premium", "spark"),
        "elegant": ("premium", "spark"),
        "bold": ("bold", "wave"),
        "vibrant": ("bold", "wave"),
        "minimal": ("minimal", "grid"),
        "simple": ("minimal", "grid"),
    }
    matched_cues = [
        (match.start(), direction)
        for cue, direction in style_cues.items()
        if (match := re.search(rf"\b{re.escape(cue)}\b", brief.lower()))
    ]
    if matched_cues:
        _, (style, motif) = min(matched_cues, key=lambda item: item[0])
    else:
        category_text = category.lower()
        if any(token in category_text for token in ("pharma", "medical", "cosmetic", "personal care")):
            style, motif = "clinical", "cross"
        elif any(token in category_text for token in ("food", "beverage", "water", "agricultural")):
            style, motif = "botanical", "leaf"
        elif any(token in category_text for token in ("electronic", "cable", "automotive")):
            style, motif = "industrial", "circuit"
        elif any(token in category_text for token in ("toy", "childcare")):
            style, motif = "playful", "bubble"
        else:
            style, motif = "editorial", "wave"
    return {"style": style, "motif": motif, "source": "local"}


def _palette_from_brief(brief: str, sampled: tuple[str, str, str]) -> tuple[str, str, str]:
    """Honour common explicit colour requests without changing copy or assets."""
    choices = {
        "burgundy": ("#6E1F35", "#FFF8F4", "#C5455D"),
        "maroon": ("#702632", "#FFF8F4", "#C33D4B"),
        "red": ("#7B2638", "#FFF9F6", "#D94352"),
        "green": ("#214B3B", "#F7FAF4", "#72A77B"),
        "teal": ("#155E63", "#F3FAF8", "#54A89B"),
        "blue": ("#173D66", "#F5F8FC", "#4B83C3"),
        "navy": ("#17324F", "#F5F7FA", "#5C8DB5"),
        "purple": ("#4A315F", "#FAF7FC", "#9A70B4"),
        "orange": ("#7C3B1D", "#FFF8F1", "#E6823B"),
        "pink": ("#713C54", "#FFF7FA", "#D887A8"),
        "black": ("#242A2A", "#F7F7F4", "#B28A48"),
        "gold": ("#50401F", "#FBF8EF", "#B28A3A"),
        "earthy": ("#59432C", "#F8F5EC", "#A77847"),
    }
    tokens = re.findall(r"[a-z]+", brief.lower())
    selected = next((choices[token] for token in tokens if token in choices), None)
    return selected or sampled


def _svg_motif(motif: str, center_y: float, primary: str, accent: str) -> str:
    """Small, editable category/design ornament in the front category strip."""
    if motif == "leaf":
        return (
            f'<path d="M844 {center_y + 18:.1f} C846 {center_y - 18:.1f} 882 {center_y - 28:.1f} 887 {center_y + 4:.1f} '
            f'C881 {center_y + 27:.1f} 855 {center_y + 30:.1f} 844 {center_y + 18:.1f} Z" fill="none" stroke="{accent}" stroke-width="5"/>'
            f'<path d="M849 {center_y + 16:.1f} Q864 {center_y + 4:.1f} 880 {center_y - 10:.1f}" fill="none" stroke="{primary}" stroke-width="4" stroke-linecap="round"/>'
        )
    if motif == "cross":
        return f'<path d="M858 {center_y - 22:.1f} H872 V{center_y - 7:.1f} H887 V{center_y + 7:.1f} H872 V{center_y + 22:.1f} H858 V{center_y + 7:.1f} H843 V{center_y - 7:.1f} H858 Z" fill="{primary}"/>'
    if motif == "bubble":
        return (
            f'<circle cx="852" cy="{center_y + 5:.1f}" r="13" fill="none" stroke="{primary}" stroke-width="4"/>'
            f'<circle cx="877" cy="{center_y - 11:.1f}" r="8" fill="{accent}"/>'
            f'<circle cx="881" cy="{center_y + 16:.1f}" r="4" fill="{primary}"/>'
        )
    if motif == "circuit":
        return (
            f'<path d="M840 {center_y + 15:.1f} H858 V{center_y - 8:.1f} H884 M858 {center_y + 4:.1f} H876 V{center_y + 20:.1f}" fill="none" stroke="{primary}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="884" cy="{center_y - 8:.1f}" r="5" fill="{accent}"/><circle cx="876" cy="{center_y + 20:.1f}" r="5" fill="{accent}"/>'
        )
    if motif == "spark":
        return (
            f'<path d="M860 {center_y - 23:.1f} L866 {center_y - 5:.1f} L885 {center_y + 1:.1f} L866 {center_y + 7:.1f} '
            f'L860 {center_y + 26:.1f} L854 {center_y + 7:.1f} L835 {center_y + 1:.1f} L854 {center_y - 5:.1f} Z" fill="{accent}"/>'
            f'<circle cx="888" cy="{center_y - 18:.1f}" r="4" fill="{primary}"/>'
        )
    if motif == "grid":
        return "".join(
            f'<rect x="{847 + column * 16}" y="{center_y - 18 + row * 16:.1f}" width="9" height="9" rx="2" fill="{primary}" opacity="{0.55 + 0.1 * ((row + column) % 3):.2f}"/>'
            for row in range(3) for column in range(3)
        )
    if motif == "wave":
        return (
            f'<path d="M840 {center_y + 5:.1f} Q852 {center_y - 16:.1f} 864 {center_y + 5:.1f} T888 {center_y + 5:.1f}" fill="none" stroke="{primary}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M844 {center_y + 19:.1f} Q856 {center_y + 3:.1f} 868 {center_y + 19:.1f} T892 {center_y + 19:.1f}" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>'
        )
    return ""


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
    design_direction: dict[str, str],
) -> str:
    primary, secondary, accent = palette
    view_height = 1000 * height_mm / width_mm
    header_height = (
        min(330.0, max(220.0, view_height * 0.25))
        if index == 0
        else min(250.0, max(185.0, view_height * 0.18))
    )
    header_bottom = 48 + header_height
    grid_top = header_bottom + (145 if index == 0 else 42)
    footer_y = view_height - (300 if view_height >= 750 else 38)
    # Keep every text run inside the panel's trim area. SVG text does not wrap
    # by itself, so values are explicitly wrapped before being emitted.
    def lines(value: Any, width: int) -> list[str]:
        return wrap(str(value).strip(), width=width, break_long_words=True, break_on_hyphens=False) or [""]

    name_lines = lines(product_name, 24)[:2]
    name_font = 72 if index == 0 and header_height >= 270 else 38
    name_start = 48 + max(130.0, header_height * 0.43) if index == 0 else 176.0
    rendered_name = "".join(
        f'<text x="94" y="{name_start + line_index * (name_font + 8):.1f}" font-family="Arial, sans-serif" font-size="{name_font}" font-weight="700" letter-spacing="0.4" fill="{primary}">{_safe(value)}</text>'
        for line_index, value in enumerate(name_lines)
    )
    commodity_copy = next(
        (value for label, value in rows if label.strip().lower() == "commodity name"),
        "",
    ) if index == 0 else ""
    subtitle_start = name_start + len(name_lines) * (name_font + 8) + 12
    rendered_subtitle = "".join(
        f'<text x="96" y="{subtitle_start + line_index * 24:.1f}" font-family="Arial, sans-serif" font-size="21" fill="#263631">{_safe(value)}</text>'
        for line_index, value in enumerate(lines(commodity_copy, 64)[:2])
    )
    summary_rows = _front_summary(rows, index)
    display_rows = _display_rows(rows, index)
    summary_markup = ""
    if summary_rows:
        summary_y = grid_top
        summary_height = 112
        summary_columns = len(summary_rows)
        summary_width = 816 if summary_columns == 1 else 398
        for summary_index, (label, value) in enumerate(summary_rows[:2]):
            summary_x = 92 + summary_index * 418
            key = _row_key(label)
            label_text = "MAXIMUM RETAIL PRICE" if key == "mrp" else "NET QUANTITY"
            value_lines = lines(value, 27 if summary_columns > 1 else 56)[:2]
            summary_markup += (
                f'<rect x="{summary_x}" y="{summary_y:.1f}" width="{summary_width}" height="{summary_height}" rx="18" fill="{primary}"/>'
                f'<rect x="{summary_x}" y="{summary_y:.1f}" width="9" height="{summary_height}" rx="4" fill="{accent}"/>'
                f'<text x="{summary_x + 26}" y="{summary_y + 32:.1f}" font-family="Arial, sans-serif" font-size="15" font-weight="700" letter-spacing="0.8" fill="{secondary}">{label_text}</text>'
                + "".join(
                    f'<text x="{summary_x + 26}" y="{summary_y + 70 + line_index * 26:.1f}" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="{secondary}">{_safe(value_line)}</text>'
                    for line_index, value_line in enumerate(value_lines)
                )
            )
        grid_top += summary_height + 20

    # Fronts get a restrained decorative band rather than a fake logo or
    # placeholder illustration. It uses only the sampled reference palette.
    feature_band = ""
    if index == 0:
        feature_y = header_bottom + 22
        feature_height = 94 if view_height >= 750 else 58
        category_lines = lines(category, 50)[:2]
        feature_copy = (
            '<text x="116" y="%.1f" font-family="Arial, sans-serif" font-size="14" font-weight="700" '
            'letter-spacing="0.6" fill="#52615C">PRODUCT CATEGORY</text>'
            % (feature_y + 22)
            + "".join(
                f'<text x="116" y="{feature_y + 45 + line_index * 20:.1f}" font-family="Arial, sans-serif" font-size="19" font-weight="700" fill="#172A25">{_safe(value)}</text>'
                for line_index, value in enumerate(category_lines)
            )
        )
        feature_band = (
            f'<rect x="78" y="{feature_y:.1f}" width="844" height="{feature_height:.1f}" rx="18" fill="#F5F1E9"/>'
            f'<rect x="78" y="{feature_y:.1f}" width="12" height="{feature_height:.1f}" rx="6" fill="{accent}"/>'
            f'{feature_copy}'
            f'<circle cx="865" cy="{feature_y + feature_height / 2:.1f}" r="{feature_height * .28:.1f}" fill="{primary}" opacity="0.12"/>'
            f'<circle cx="865" cy="{feature_y + feature_height / 2:.1f}" r="{feature_height * .16:.1f}" fill="{primary}" opacity="0.22"/>'
            f'{_svg_motif(design_direction.get("motif", "wave"), feature_y + feature_height / 2, primary, accent)}'
        )

    footer_art = ""
    if view_height >= 750:
        footer_top = view_height - 278
        footer_art = (
            f'<path d="M22 {footer_top:.1f} C250 {view_height - 340:.1f} 430 {view_height - 240:.1f} 660 {view_height - 290:.1f} '
            f'C800 {view_height - 340:.1f} 900 {view_height - 235:.1f} 978 {view_height - 260:.1f} '
            f'L978 {view_height - 22:.1f} L22 {view_height - 22:.1f} Z" fill="{primary}"/>'
            f'<path d="M22 {footer_top:.1f} C250 {view_height - 340:.1f} 430 {view_height - 240:.1f} 660 {view_height - 290:.1f}" '
            f'fill="none" stroke="{accent}" stroke-width="8" stroke-linecap="round"/>'
            f'<circle cx="815" cy="{footer_top + 110:.1f}" r="48" fill="{secondary}" opacity="0.96"/>'
            f'<circle cx="815" cy="{footer_top + 110:.1f}" r="28" fill="{accent}"/>'
            f'<circle cx="905" cy="{footer_top + 155:.1f}" r="18" fill="{secondary}"/>'
        )

    rendered_rows: list[str] = []
    # A compact two-column declaration grid uses the available physical
    # panel more effectively while keeping every value sourced from the user
    # or OCR. Unfitted copy is reported rather than silently clipped.
    column_width = 404
    columns, row_pitch, max_rows, available_height = _grid_metrics(
        len(display_rows), view_height, grid_top
    )
    rendered_count = min(len(display_rows), max_rows)
    for row_index, (label, value) in enumerate(display_rows[:rendered_count]):
        column = 0 if columns == 1 else row_index % 2
        line_row = row_index if columns == 1 else row_index // 2
        x = 92 + column * 414
        card_top = grid_top + line_row * row_pitch
        text_offset = max(20.0, (row_pitch - 48) / 2)
        y = card_top + text_offset
        value_lines = lines(value, 36)[:2]
        card_height = row_pitch - 10
        rendered_rows.append(
            f'<rect x="{x - 12}" y="{card_top:.1f}" width="{column_width}" height="{card_height:.1f}" rx="10" fill="#F8F7F3"/>'
            f'<rect x="{x - 12}" y="{card_top:.1f}" width="4" height="{card_height:.1f}" rx="2" fill="{accent}" opacity="0.88"/>'
            f'<text x="{x}" y="{y:.1f}" font-family="Arial, sans-serif" font-size="17" font-weight="700" letter-spacing="0.45" fill="#52615C">{_safe(label.upper())}</text>'
        )
        for line_index, value_line in enumerate(value_lines):
            rendered_rows.append(
                f'<text x="{x}" y="{y + 27 + line_index * 21:.1f}" font-family="Arial, sans-serif" font-size="21" fill="#172A25">{_safe(value_line)}</text>'
            )
    remaining = max(0, len(display_rows) - rendered_count)
    remainder = (
        f'<text x="92" y="{footer_y - 8:.1f}" font-family="Arial, sans-serif" font-size="17" fill="#8A5A12">{remaining} supplied item(s) need a larger panel or a separate side.</text>'
        if remaining
        else ""
    )
    shape_lower = shape.lower()
    corner_radius = 42 if any(token in shape_lower for token in ("bottle", "tube", "can")) else 30 if any(token in shape_lower for token in ("pouch", "sachet")) else 22
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width_mm:g}mm" height="{height_mm:g}mm" viewBox="0 0 1000 {view_height:.2f}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Editable {side_name} label draft">
  <rect width="1000" height="{view_height:.2f}" fill="#FFFDF8"/>
  <rect x="22" y="22" width="956" height="{max(1, view_height - 44):.2f}" rx="{corner_radius}" fill="none" stroke="#D8D4CB" stroke-width="3"/>
  <rect x="48" y="48" width="904" height="{header_height:.2f}" rx="{corner_radius}" fill="{secondary}" stroke="{primary}" stroke-width="3"/>
  <rect x="48" y="48" width="904" height="62" rx="{max(12, corner_radius - 4)}" fill="{primary}"/>
  <path d="M750 48 H924 Q952 48 952 76 V{48 + header_height * .32:.1f} Q860 48 750 110 Z" fill="{accent}" opacity="0.42"/>
  <text x="94" y="94" font-family="Arial, sans-serif" font-size="22" font-weight="700" letter-spacing="1.2" fill="{secondary}">{_safe(side_name.upper())} - {index + 1}/{total}</text>
  <rect x="690" y="63" width="232" height="48" rx="24" fill="{secondary}"/>
  <text x="806" y="94" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="{primary}">{_safe(dimensions_text)}</text>
  {rendered_name}
  {rendered_subtitle}
  <rect x="78" y="{header_bottom - 6:.1f}" width="844" height="7" rx="3.5" fill="{accent}"/>
  {footer_art}
  {feature_band}
  {summary_markup}
  {''.join(rendered_rows)}
  {remainder}
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
    design_spec: dict[str, str] | None = None,
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
    design_direction = design_spec or _local_design_direction(product_category, custom_prompt)
    if design_spec:
        palette = (
            design_spec["primary"],
            design_spec["background"],
            design_spec["accent"],
        )
    elif custom_prompt.strip():
        palette = _palette_from_brief(custom_prompt, palette)
    rows = _text_rows(label_values, additional_details)
    view_height = 1000 * height_mm / width_mm
    header_height = min(330.0, max(220.0, view_height * 0.25))
    warnings = [
        "Generated locally from deterministic SVG templates; no hosted generative-design provider was used.",
        "This is not print-ready artwork. Confirm trim, bleed, colour profile, approved identity assets and printer specifications.",
        "Reference photos guide sampled colour and panel naming only. The renderer does not recreate logos or exact artwork, or invent barcodes, photographs, certifications or missing declarations.",
    ]
    front_keys = {"commodity_name", "net_quantity", "mrp"}
    front_rows = [row for row in rows if _row_key(row[0]) in front_keys]
    detail_rows = [row for row in rows if row not in front_rows]
    side_rows: list[list[tuple[str, str]]] = [[] for _ in range(count)]
    if count == 1:
        side_rows[0] = rows
    else:
        side_rows[0] = front_rows
        for row_index, row in enumerate(detail_rows):
            side_rows[1 + row_index % (count - 1)].append(row)
    side_capacities = [
        _grid_metrics(
            len(_display_rows(values, index)),
            view_height,
            48 + header_height + (145 if index == 0 else 42)
            + (132 if index == 0 and _front_summary(values, index) else 0),
        )[2]
        for index, values in enumerate(side_rows)
    ]
    overflowing_capacities = [
        capacity
        for values, capacity in zip(side_rows, side_capacities)
        if len(values) > capacity
    ]
    if overflowing_capacities:
        warnings.append(
            f"At {dimensions_text}, a panel has more supplied text than its readable layout can fit (only {min(overflowing_capacities)} item(s) fit on the tightest panel). Overflow is identified in the artwork; increase the panel size or distribute copy across more sides before printing."
        )
    if min(width_mm, height_mm) < 60:
        warnings.append(
            f"At {dimensions_text}, regulatory copy may be too small to read at actual print size. Verify a 1:1 print proof or enter the correct larger panel dimensions."
        )
    if design_spec:
        warnings.insert(
            0,
            "AI-assisted design direction controls only colours and vector styling. Product copy, package photos and compliance findings were not sent to the provider; all printed text remains manufacturer-supplied.",
        )
    filenames = [filename for filename, _ in images] or ["" for _ in range(count)]
    sides = []
    for index in range(count):
        side_name = _side_name(filenames[index] if index < len(filenames) else "", index)
        side_values = {
            label.strip().lower().replace(" ", "_"): value
            for label, value in side_rows[index]
        }
        sides.append({
            "side_name": side_name,
            "side_index": index,
            "svg_code": _svg_panel(side_name, index, count, product_name, product_category, shape, width_mm, height_mm, dimensions_text, side_rows[index], palette, design_direction),
            "supplied_values": side_values,
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
                "design_aesthetic": f"{design_direction.get('style', 'editorial').title()} vector style with {design_direction.get('motif', 'wave')} motif and a front-facing MRP / quantity panel",
            },
            "design_direction": design_direction,
            "package_shape": shape.strip(),
            "source_dimensions": dimensions_text,
            "supplied_values": {str(key): str(value) for key, value in label_values.items()},
            "design_brief": custom_prompt.strip(),
        },
        "warnings": warnings,
        "engine_used": (
            "Gemini AI-assisted vector design direction"
            if design_spec
            else "Local deterministic SVG template renderer"
        ),
    }
