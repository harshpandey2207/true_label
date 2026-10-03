"""Local, data-driven SVG label drafts.

This renderer deliberately does not ask a hosted model to invent statutory text.
Uploaded images are used only to sample a small colour palette; all supplied copy
is escaped before it is placed in the SVG.
"""

from __future__ import annotations

import html
import os
import re
import textwrap
from typing import Any

import cv2
import numpy as np


CATEGORIES = [
    "General Packaged Commodity",
    "Food & Beverages",
    "Electronics & Appliances",
    "Cosmetics, Ointments & Pharma Goods",
    "Apparel & Textiles",
    "Medical Devices",
]

FIELD_LABELS = {
    "manufacturer": "Manufacturer / packer / importer",
    "commodity_name": "Common / generic commodity name",
    "net_quantity": "Net quantity",
    "manufacturing_date": "Manufacturing / packing date",
    "mrp": "MRP (inclusive of taxes)",
    "consumer_care": "Consumer care details",
    "unit_sale_price": "Unit sale price (if applicable)",
    "batch_code": "Batch / lot number",
    "best_before_date": "Best before / expiry",
    "fssai_license": "FSSAI licence / registration",
    "veg_non_veg_logo": "Food symbol / declaration",
    "ingredients": "Ingredients / allergen information",
    "bis_mark": "BIS registration / mark (if applicable)",
    "model": "Model / product ID",
    "country_of_origin": "Country of origin",
    "e_waste_info": "E-waste information (if applicable)",
    "manufacturing_license": "Manufacturing licence",
    "expiry_date": "Expiry date",
    "size": "Size",
    "fibre_content": "Fibre content",
    "serial_number": "Serial number",
    "license_no": "Licence number",
    "sterile_status": "Sterile status",
}

DEFAULT_FIELDS = [
    "manufacturer",
    "commodity_name",
    "net_quantity",
    "manufacturing_date",
    "mrp",
    "consumer_care",
]

CATEGORY_FIELDS = {
    "Food & Beverages": [
        "batch_code", "best_before_date", "fssai_license", "veg_non_veg_logo", "ingredients"
    ],
    "Electronics & Appliances": ["model", "bis_mark", "country_of_origin", "e_waste_info"],
    "Cosmetics, Ointments & Pharma Goods": [
        "batch_code", "expiry_date", "manufacturing_license", "ingredients"
    ],
    "Apparel & Textiles": ["size", "fibre_content", "country_of_origin"],
    "Medical Devices": ["batch_code", "serial_number", "license_no", "sterile_status"],
}


def _escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _normalise_values(values: dict[str, Any]) -> dict[str, str]:
    normalised: dict[str, str] = {}
    for key, value in values.items():
        tag = re.sub(r"[^a-z0-9]+", "_", str(key).strip().lower()).strip("_")
        if not tag or value is None:
            continue
        text = str(value).strip()
        if text:
            normalised[tag] = text[:500]
    return normalised


def _image_palette(image_bytes: bytes) -> list[str]:
    raw = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("One of the uploaded files is not a readable image.")
    image_height, image_width = image.shape[:2]
    if image_width * image_height > 40_000_000 or max(image_width, image_height) > 12_000:
        raise ValueError("Reference images must be no larger than 40 megapixels.")

    sample = cv2.resize(image, (64, 64), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(sample, cv2.COLOR_BGR2RGB).reshape(-1, 3)
    # Coarse colour quantisation is stable and cheap, and keeps the image local.
    buckets = (rgb // 32).clip(0, 7)
    ids = buckets[:, 0] * 64 + buckets[:, 1] * 8 + buckets[:, 2]
    counts = np.bincount(ids, minlength=512)
    order = np.argsort(counts)[::-1]
    colors: list[str] = []
    for bucket_id in order:
        if counts[bucket_id] == 0:
            break
        red_bin = bucket_id // 64
        green_bin = (bucket_id % 64) // 8
        blue_bin = bucket_id % 8
        color = tuple(min(255, index * 32 + 16) for index in (red_bin, green_bin, blue_bin))
        # Ignore near white/black when a more useful brand colour is available.
        if (min(color) > 238 or max(color) < 24) and len(colors) < 2:
            continue
        hex_color = "#%02X%02X%02X" % color
        if hex_color not in colors:
            colors.append(hex_color)
        if len(colors) == 3:
            break
    return colors or ["#1B4332", "#F5F3E8", "#D4A373"]


def _prompt_palette(prompt: str, extracted: list[str]) -> tuple[str, str, str, str]:
    text = prompt.lower()
    choices = {
        "earthy": ("#6B705C", "#F4F1DE", "#CB997E", "Earthy"),
        "natural": ("#386641", "#F2E8CF", "#A7C957", "Natural"),
        "minimal": ("#263238", "#FFFFFF", "#78909C", "Minimal"),
        "premium": ("#18212B", "#F8F4EA", "#C8A96B", "Premium"),
        "luxury": ("#18212B", "#F8F4EA", "#C8A96B", "Luxury"),
        "bright": ("#0B6E69", "#FFFDF5", "#F4A261", "Bright"),
        "playful": ("#5A189A", "#FFF9F0", "#FF8500", "Playful"),
        "retro": ("#9B4A38", "#F4E7C5", "#D89B35", "Retro"),
        "vintage": ("#9B4A38", "#F4E7C5", "#D89B35", "Vintage"),
        "monochrome": ("#222222", "#FFFFFF", "#8A8A8A", "Monochrome"),
        "blue": ("#174A7E", "#F4F8FC", "#55A6D9", "Blue"),
        "green": ("#1B4332", "#F5F3E8", "#74A57F", "Green"),
        "red": ("#8C1C13", "#FFF7F0", "#E09F3E", "Red"),
        "orange": ("#9C3D10", "#FFF5E8", "#F2A541", "Orange"),
        "yellow": ("#544B00", "#FFFBE6", "#F2C14E", "Yellow"),
        "purple": ("#4B2673", "#F8F3FC", "#B28DCC", "Purple"),
        "pink": ("#8D365B", "#FFF5F8", "#E9A3B5", "Pink"),
        "black": ("#202020", "#F7F7F7", "#AAAAAA", "Black and white"),
    }
    selected = next((entry for keyword, entry in choices.items() if keyword in text), None)
    if selected:
        return selected
    primary = extracted[0] if extracted else "#1B4332"
    secondary = extracted[1] if len(extracted) > 1 else "#F5F3E8"
    accent = extracted[2] if len(extracted) > 2 else "#74A57F"
    return primary, secondary, accent, "Sampled from reference image"


def _side_name(filename: str, index: int) -> str:
    name = os.path.splitext(os.path.basename(filename or ""))[0].lower()
    for side in ("front", "back", "left", "right", "top", "bottom"):
        if re.search(rf"(^|[^a-z]){side}([^a-z]|$)", name):
            return side.title()
    defaults = ["Front", "Back", "Left", "Right", "Top", "Bottom"]
    return defaults[index] if index < len(defaults) else f"Side {index + 1}"


def _text_lines(value: str, limit: int = 46) -> list[str]:
    return textwrap.wrap(value, width=limit, break_long_words=True, break_on_hyphens=True) or [""]


def _dimensions(dimensions: str) -> tuple[int, int]:
    numbers = re.findall(r"\d+(?:\.\d+)?", dimensions or "")
    if len(numbers) < 2:
        return 800, 1200
    width_cm, height_cm = map(float, numbers[:2])
    if width_cm <= 0 or height_cm <= 0:
        return 800, 1200
    ratio = max(0.45, min(2.0, width_cm / height_cm))
    width = 800
    return width, int(width / ratio)


def _render_side(
    *,
    side_name: str,
    product_name: str,
    category: str,
    package_shape: str,
    values: dict[str, str],
    additional_details: list[str],
    custom_prompt: str,
    palette: tuple[str, str, str, str],
    width: int,
    base_height: int,
) -> str:
    primary, secondary, accent, _aesthetic = palette
    shape_text = package_shape.lower()
    corner_radius = 42 if any(word in shape_text for word in ("bottle", "jar", "can", "tube")) else (
        12 if any(word in shape_text for word in ("box", "carton", "rectangular")) else 24
    )
    rgb = tuple(int(primary[index:index + 2], 16) for index in (1, 3, 5))
    luminance = (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])
    header_text_color = "#202020" if luminance > 155 else "#FFFFFF"
    ordered_keys = list(dict.fromkeys(DEFAULT_FIELDS + CATEGORY_FIELDS.get(category, []) + list(values)))
    details: list[tuple[str, str]] = []
    for key in ordered_keys:
        label = FIELD_LABELS.get(key, key.replace("_", " ").title())
        details.append((label, values.get(key, f"[ADD {label.upper()}]")))
    for index, detail in enumerate(additional_details, start=1):
        details.append((f"Additional detail {index}", detail))

    # Keep a clear, editable placeholder where a user asks to retain artwork.
    needs_artwork_slot = any(word in custom_prompt.lower() for word in ("logo", "artwork", "barcode", "qr", "photo"))
    # Measure with the same line wrapping and vertical increments used below so
    # long declarations cannot collide with the artwork box or footer.
    detail_height = sum(
        22 + 21 * len(_text_lines(value, 38)) + 7
        for _, value in details
    )
    artwork_y = 330 + detail_height + 28 if needs_artwork_slot else 0
    height = max(base_height, 330 + detail_height + (155 if needs_artwork_slot else 90))
    safe_side = _escape(side_name)
    safe_product = _escape(product_name)
    title_lines = _text_lines(product_name, 25)[:3]
    title_font_size = 43 if len(title_lines) == 1 else (37 if len(title_lines) == 2 else 32)
    title_line_gap = 44 if len(title_lines) == 2 else 38
    title_tspans = "".join(
        f'<tspan x="48" dy="{0 if index == 0 else title_line_gap}">{_escape(line)}</tspan>'
        for index, line in enumerate(title_lines)
    )
    accent_y = 183 if len(title_lines) == 1 else (222 if len(title_lines) == 2 else 235)
    subtitle_y = 230 if len(title_lines) == 1 else (250 if len(title_lines) == 2 else 260)
    art_block = ""
    if needs_artwork_slot:
        art_block = (
            f'<rect x="42" y="{artwork_y}" width="{width - 84}" height="70" rx="10" '
            f'fill="none" stroke="{accent}" stroke-width="2" stroke-dasharray="8 6"/>'
            f'<text x="{width / 2}" y="{artwork_y + 43}" text-anchor="middle" '
            f'font-family="Arial,sans-serif" font-size="20" fill="{primary}">Replace with approved logo / artwork</text>'
        )

    detail_svg: list[str] = []
    y = 330
    for label, value in details:
        lines = _text_lines(value, 38)
        detail_svg.append(
            f'<text x="48" y="{y}" font-family="Arial,sans-serif" font-size="17" '
            f'font-weight="700" fill="{primary}">{_escape(label)}</text>'
        )
        y += 22
        for line in lines:
            detail_svg.append(
                f'<text x="48" y="{y}" font-family="Arial,sans-serif" font-size="18" '
                f'fill="#202020">{_escape(line)}</text>'
            )
            y += 21
        y += 7

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{safe_side} label draft for {safe_product}">'
        f'<rect width="{width}" height="{height}" fill="{secondary}"/>'
        f'<rect x="18" y="18" width="{width - 36}" height="{height - 36}" rx="{corner_radius}" '
        f'fill="none" stroke="{primary}" stroke-width="4"/>'
        f'<path d="M20 38 Q20 20 40 20 H{width - 40} Q{width - 20} 20 {width - 20} 40 '
        f'V270 H20Z" fill="{primary}"/>'
        f'<text x="48" y="70" font-family="Arial,sans-serif" font-size="19" '
        f'font-weight="700" letter-spacing="2" fill="{header_text_color}">{safe_side.upper()} SIDE</text>'
        f'<text x="48" y="150" font-family="Arial,sans-serif" font-size="{title_font_size}" '
        f'font-weight="700" fill="{header_text_color}">{title_tspans}</text>'
        f'<rect x="48" y="{accent_y}" width="130" height="6" rx="3" fill="{accent}"/>'
        f'<text x="48" y="{subtitle_y}" font-family="Arial,sans-serif" font-size="18" '
        f'fill="{header_text_color}">Packaging label draft</text>'
        f'<text x="48" y="303" font-family="Arial,sans-serif" font-size="18" '
        f'font-weight="700" fill="{primary}">PRODUCT DECLARATIONS</text>'
        f'{"".join(detail_svg)}{art_block}'
        f'<text x="48" y="{height - 42}" font-family="Arial,sans-serif" font-size="14" '
        f'fill="#555555">Draft artwork • Verify text, dimensions and current rules before printing</text>'
        f'</svg>'
    )


def generate_label_draft(
    *,
    product_name: str,
    product_category: str,
    shape: str,
    dimensions: str,
    custom_prompt: str,
    label_values: dict[str, Any],
    additional_details: str,
    images: list[tuple[str, bytes]],
    side_count: int,
) -> dict[str, Any]:
    if product_category not in CATEGORIES:
        raise ValueError("Choose a supported product category.")
    if not product_name.strip():
        raise ValueError("Product name is required.")
    if len(images) > 6:
        raise ValueError("Upload no more than six package-side images.")

    values = _normalise_values(label_values)
    colors_by_image = [_image_palette(content) for _, content in images]
    colors = _prompt_palette(custom_prompt, colors_by_image[0] if colors_by_image else [])
    width, base_height = _dimensions(dimensions)
    names = [filename for filename, _ in images]
    if names:
        side_names = [_side_name(filename, index) for index, filename in enumerate(names)]
    else:
        side_count = side_count if side_count in (2, 4, 6) else 2
        side_names = ["Front", "Back", "Left", "Right", "Top", "Bottom"][:side_count]

    extra = [line.strip()[:240] for line in additional_details.splitlines() if line.strip()][:12]
    sides = []
    for index, side_name in enumerate(side_names):
        side_palette = _prompt_palette(
            custom_prompt,
            colors_by_image[index] if index < len(colors_by_image) else (colors_by_image[0] if colors_by_image else []),
        )
        sides.append({
            "side_name": side_name,
            "sampled_primary_color": side_palette[0],
            "sampled_secondary_color": side_palette[1],
            "sampled_accent_color": side_palette[2],
            "svg_code": _render_side(
                side_name=side_name,
                product_name=product_name.strip()[:120],
                category=product_category,
                package_shape=shape,
                values=values,
                additional_details=extra,
                custom_prompt=custom_prompt[:1000],
                palette=side_palette,
                width=width,
                base_height=base_height,
            ),
        })

    missing_core = [FIELD_LABELS[key] for key in DEFAULT_FIELDS if key not in values]
    warnings = [
        "This is a visual label draft, not a legal compliance determination. Review all declarations against current rules and product-specific requirements before printing.",
        "The renderer samples colours only; it does not reconstruct logos, photographs, barcodes or the exact uploaded artwork. Add approved artwork in a design editor before production.",
    ]
    if missing_core:
        warnings.append("Fields still left as placeholders: " + ", ".join(missing_core) + ".")
    if shape.strip():
        warnings.append("Confirm the die-line and print dimensions for the actual package shape before production.")

    return {
        "label_data": {
            "brand_dna": {
                "primary_color": colors[0],
                "secondary_color": colors[1],
                "accent_color": colors[2],
                "font_style": "Arial / sans-serif system font",
                "design_aesthetic": colors[3],
            },
            "sides": sides,
        },
        "warnings": warnings,
        "engine_used": "Local SVG template renderer and OpenCV colour sampling",
    }
