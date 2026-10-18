"""Opt-in Gemini design direction for editable, manufacturer-reviewed labels.

Only the category, pack geometry, dimensions, requested style, and locally
sampled colour palette are sent to the provider. Product identity, label copy,
package images, OCR output, and compliance findings never leave the local API.
The model returns a small constrained design specification, not SVG or text.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

DEFAULT_MODEL = "gemini-3.5-flash-lite"
STYLES = {"editorial", "bold", "botanical", "clinical", "playful", "industrial", "minimal", "premium"}
MOTIFS = {"leaf", "cross", "bubble", "circuit", "spark", "wave", "grid", "none"}
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
MODEL_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")


class DesignAssistantError(RuntimeError):
    """A safe-to-display failure from the optional remote design provider."""


def _config() -> tuple[str, str]:
    key = os.getenv("TRUE_LABEL_GEMINI_API_KEY", "").strip()
    model = os.getenv("TRUE_LABEL_GEMINI_MODEL", DEFAULT_MODEL).strip()
    if not MODEL_NAME.fullmatch(model):
        model = DEFAULT_MODEL
    return key, model


def design_assistant_status() -> dict[str, Any]:
    key, model = _config()
    return {
        "configured": bool(key),
        "provider": "Google Gemini",
        "model": model,
        "scope": "Design direction only; package photos, product identity, declarations and compliance findings stay local.",
    }


def _luminance(hex_color: str) -> float:
    channels = [int(hex_color[position:position + 2], 16) / 255 for position in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    light, dark = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def validate_design_spec(value: Any) -> dict[str, str]:
    """Keep model output to renderer-owned, non-text visual tokens."""
    if not isinstance(value, dict):
        raise DesignAssistantError("The design assistant returned an invalid response.")
    palette = value.get("palette")
    style = value.get("style")
    motif = value.get("motif")
    if not isinstance(palette, dict) or style not in STYLES or motif not in MOTIFS:
        raise DesignAssistantError("The design assistant returned an unsupported design direction.")
    primary = str(palette.get("primary", ""))
    background = str(palette.get("background", ""))
    accent = str(palette.get("accent", ""))
    if not all(HEX_COLOR.fullmatch(color) for color in (primary, background, accent)):
        raise DesignAssistantError("The design assistant returned an invalid colour palette.")
    if _luminance(background) < 0.72 or _contrast_ratio(primary, background) < 4.5:
        raise DesignAssistantError("The design assistant returned colours with insufficient text contrast.")
    return {
        "primary": primary.upper(),
        "background": background.upper(),
        "accent": accent.upper(),
        "style": style,
        "motif": motif,
        "source": "gemini",
    }


async def generate_design_direction(
    *,
    category: str,
    shape: str,
    dimensions: str,
    design_brief: str,
    sampled_palette: tuple[str, str, str],
) -> dict[str, str]:
    key, model = _config()
    if not key:
        raise DesignAssistantError(
            "AI label design is not configured. Set TRUE_LABEL_GEMINI_API_KEY in the backend environment, restart the API, then retry."
        )

    # Never include product name, package photos, OCR text, declarations, or
    # compliance results in this request. The provider may only direct style.
    prompt = (
        "Create a restrained, print-legible visual design direction for an editable package label. "
        "Return only the constrained JSON schema. Do not write product copy, legal claims, logos, "
        "certifications, barcodes, or any text to print. Choose a dark primary, very light background, "
        "one accent, a style, and one simple decorative motif. Keep a clear area for supplied declarations.\n"
        f"Category: {category[:100]}\n"
        f"Package geometry: {shape[:80]}\n"
        f"Finished panel dimensions: {dimensions[:80]}\n"
        f"Manufacturer design brief: {design_brief[:800]}\n"
        f"Locally sampled reference palette (HEX): {', '.join(sampled_palette)}"
    )
    schema = {
        "type": "OBJECT",
        "properties": {
            "palette": {
                "type": "OBJECT",
                "properties": {
                    "primary": {"type": "STRING", "description": "Dark foreground HEX colour, such as #17352D."},
                    "background": {"type": "STRING", "description": "Very light background HEX colour."},
                    "accent": {"type": "STRING", "description": "Single accent HEX colour."},
                },
                "required": ["primary", "background", "accent"],
            },
            "style": {"type": "STRING", "enum": sorted(STYLES)},
            "motif": {"type": "STRING", "enum": sorted(MOTIFS)},
        },
        "required": ["palette", "style", "motif"],
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    request = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema,
            "temperature": 0.65,
            "maxOutputTokens": 400,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(18.0, connect=5.0)) as client:
            response = await client.post(
                url,
                headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                json=request,
            )
            response.raise_for_status()
            body = response.json()
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        return validate_design_spec(json.loads(text))
    except DesignAssistantError:
        raise
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        raise DesignAssistantError(
            "The AI design service could not return a valid design. Check the local API connection and Gemini key, or turn off AI design to use the local vector renderer."
        ) from None
