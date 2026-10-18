from __future__ import annotations

import asyncio
import json
import os
import unittest
from unittest.mock import patch

from backend.app.services.ai_engine import design_assistant
from backend.app.services.ai_engine.design_assistant import (
    DesignAssistantError,
    design_assistant_status,
    generate_design_direction,
    validate_design_spec,
)


class _Response:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "candidates": [{
                "content": {"parts": [{
                    "text": json.dumps({
                        "palette": {
                            "primary": "#18362F",
                            "background": "#FFFDF8",
                            "accent": "#C83E4D",
                        },
                        "style": "clinical",
                        "motif": "cross",
                    })
                }]}
            }]
        }


class _MockAsyncClient:
    last_request = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, *, headers, json):
        type(self).last_request = {"url": url, "headers": headers, "json": json}
        return _Response()


class DesignAssistantTests(unittest.TestCase):
    def test_status_does_not_expose_api_key(self):
        with patch.dict(os.environ, {"TRUE_LABEL_GEMINI_API_KEY": "private-test-key"}):
            status = design_assistant_status()
        self.assertTrue(status["configured"])
        self.assertNotIn("private-test-key", str(status))

    def test_ai_spec_rejects_unsafe_or_low_contrast_output(self):
        with self.assertRaises(DesignAssistantError):
            validate_design_spec({
                "palette": {"primary": "url(x)", "background": "#FFFFFF", "accent": "#FF0000"},
                "style": "clinical",
                "motif": "cross",
            })
        with self.assertRaises(DesignAssistantError):
            validate_design_spec({
                "palette": {"primary": "#FFFFFF", "background": "#FFFFFF", "accent": "#FF0000"},
                "style": "clinical",
                "motif": "cross",
            })

    def test_provider_request_contains_style_inputs_only_and_validates_response(self):
        with patch.dict(os.environ, {
            "TRUE_LABEL_GEMINI_API_KEY": "private-test-key",
            "TRUE_LABEL_GEMINI_MODEL": "gemini-3.5-flash-lite",
        }), patch.object(design_assistant.httpx, "AsyncClient", _MockAsyncClient):
            result = asyncio.run(generate_design_direction(
                category="Cosmetics, Ointments & Pharma Goods",
                shape="carton",
                dimensions="200 x 300 mm",
                design_brief="deep green, confident and clinical",
                sampled_palette=("#153B50", "#FFFDF8", "#C83E4D"),
            ))
        self.assertEqual("#18362F", result["primary"])
        self.assertEqual("cross", result["motif"])
        request = _MockAsyncClient.last_request
        self.assertEqual("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent", request["url"])
        self.assertEqual("private-test-key", request["headers"]["x-goog-api-key"])
        prompt = request["json"]["contents"][0]["parts"][0]["text"]
        self.assertIn("design brief", prompt.lower())
        self.assertNotIn("Cipladine", prompt)
        self.assertNotIn("30 g", prompt)
        self.assertNotIn("package photos", prompt.lower())

    def test_ai_mode_requires_a_configured_key(self):
        with patch.dict(os.environ, {"TRUE_LABEL_GEMINI_API_KEY": ""}):
            with self.assertRaisesRegex(DesignAssistantError, "not configured"):
                asyncio.run(generate_design_direction(
                    category="Food & Beverages",
                    shape="pouch",
                    dimensions="120 x 180 mm",
                    design_brief="earthy",
                    sampled_palette=("#153B50", "#FFFDF8", "#2F855A"),
                ))


if __name__ == "__main__":
    unittest.main()
