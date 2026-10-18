import io
import os
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from backend.app.services.ai_engine.metrology_engine import _local_ocr_enabled, _tag_declaration, analyze_product_label, orb_overlap_score


class ImageAnalysisTests(unittest.TestCase):
    def test_local_ocr_auto_enables_when_a_runtime_is_installed(self):
        with patch.dict(os.environ, {"TRUE_LABEL_ENABLE_LOCAL_OCR": ""}, clear=False), \
            patch("backend.app.services.ai_engine.metrology_engine.find_spec", side_effect=lambda name: object() if name == "rapidocr_onnxruntime" else None):
            self.assertTrue(_local_ocr_enabled())

        with patch.dict(os.environ, {"TRUE_LABEL_ENABLE_LOCAL_OCR": "0"}, clear=False):
            self.assertFalse(_local_ocr_enabled())

    def test_local_ocr_stays_off_when_no_runtime_is_installed(self):
        with patch.dict(os.environ, {"TRUE_LABEL_ENABLE_LOCAL_OCR": ""}, clear=False), \
            patch("backend.app.services.ai_engine.metrology_engine.find_spec", return_value=None):
            self.assertFalse(_local_ocr_enabled())

    def test_unconfigured_ocr_produces_an_unresolved_evidence_result(self):
        image = Image.new("RGB", (120, 100), "white")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output:
            image.save(output, format="PNG")
            path = output.name
        try:
            with patch.dict(os.environ, {"TRUE_LABEL_ENABLE_LOCAL_OCR": "0"}, clear=False):
                result = analyze_product_label(path)
        finally:
            os.remove(path)
        self.assertEqual("UNRESOLVED", result["status"])
        self.assertEqual("unavailable", result["ocr_engine"])
        self.assertTrue(result["warnings"])
        self.assertEqual("INDICATIVE_ONLY", result["measurement"]["status"])

    def test_orb_overlap_is_advisory_and_handles_feature_poor_images(self):
        image = Image.new("RGB", (120, 100), "white")
        paths = []
        try:
            for _ in range(2):
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output:
                    image.save(output, format="PNG")
                    paths.append(output.name)
            result = orb_overlap_score(paths[0], paths[1])
            self.assertTrue(result is None or result["status"] in {"evaluated", "insufficient_features"})
        finally:
            for path in paths:
                os.remove(path)

    def test_rapidocr_fallback_normalises_local_text_and_confidence(self):
        image = Image.new("RGB", (900, 900), "white")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output:
            image.save(output, format="PNG")
            path = output.name

        class FakeRapidOCR:
            def __call__(self, _: str):
                return ([
                    ([[10, 20], [210, 20], [210, 60], [10, 60]], "MRP Rs. 105", 0.97),
                ], [0.0, 0.0, 0.0])

        try:
            with patch.dict(os.environ, {"TRUE_LABEL_ENABLE_LOCAL_OCR": "1", "TRUE_LABEL_OCR_ENGINE": "rapidocr"}, clear=False), \
                patch("backend.app.services.ai_engine.metrology_engine._rapid_ocr", return_value=FakeRapidOCR()), \
                patch("backend.app.services.ai_engine.metrology_engine._paddle_ocr", return_value=None):
                result = analyze_product_label(path)
        finally:
            os.remove(path)
        self.assertEqual("rapidocr", result["ocr_engine"])
        self.assertEqual("MRP", result["declarations"][0]["tag"])
        self.assertEqual(0.97, result["declarations"][0]["confidence"])

    def test_paddle_failure_falls_back_to_rapidocr(self):
        image = Image.new("RGB", (900, 900), "white")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output:
            image.save(output, format="PNG")
            path = output.name

        class BrokenPaddle:
            def ocr(self, *_args, **_kwargs):
                raise RuntimeError("model weights unavailable")

        class WorkingRapidOCR:
            def __call__(self, _: str):
                return ([
                    ([[10, 20], [210, 20], [210, 60], [10, 60]], "Batch No. K123", 0.94),
                ], [0.0, 0.0, 0.0])

        try:
            with patch.dict(os.environ, {"TRUE_LABEL_ENABLE_LOCAL_OCR": "1", "TRUE_LABEL_OCR_ENGINE": "paddle"}, clear=False), \
                patch("backend.app.services.ai_engine.metrology_engine._rapid_ocr", return_value=WorkingRapidOCR()), \
                patch("backend.app.services.ai_engine.metrology_engine._paddle_ocr", return_value=BrokenPaddle()):
                result = analyze_product_label(path)
        finally:
            os.remove(path)
        self.assertEqual("rapidocr", result["ocr_engine"])
        self.assertEqual("BATCH_CODE", result["declarations"][0]["tag"])

    def test_manufacturer_text_is_not_misclassified_as_a_date(self):
        self.assertEqual("MANUFACTURER", _tag_declaration("Mfd.by: Nanz Med Science Pharma Pvt. Ltd.")[0])
        self.assertEqual("MANUFACTURER", _tag_declaration("Marketedby Cipla Health Ltd.")[0])
        self.assertEqual("MANUFACTURING_DATE", _tag_declaration("Mfd. 06/2025")[0])

    def test_common_ocr_variants_keep_date_and_title_evidence(self):
        self.assertEqual("MANUFACTURING_DATE", _tag_declaration("Mig.Date")[0])
        self.assertEqual("EXPIRY_DATE", _tag_declaration("Expiny Date")[0])
        self.assertEqual("COMMODITY_NAME", _tag_declaration("CIPLADINE")[0])
        self.assertEqual("GENERAL", _tag_declaration("FOREXTERNALUSEONLY")[0])

    def test_date_values_are_associated_with_nearest_readable_date_label(self):
        image = Image.new("RGB", (1200, 900), "white")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output:
            image.save(output, format="PNG")
            path = output.name

        class FakeRapidOCR:
            def __call__(self, _: str):
                return ([
                    ([[100, 100], [240, 100], [240, 140], [100, 140]], "CIPLADINE", 0.96),
                    ([[300, 280], [440, 280], [440, 320], [300, 320]], "Batch No", 0.91),
                    ([[600, 275], [760, 275], [760, 315], [600, 315]], "N0250507", 0.94),
                    ([[600, 100], [760, 100], [760, 140], [600, 140]], "Mig.Date", 0.91),
                    ([[600, 150], [760, 150], [760, 190], [600, 190]], "06/2025", 0.94),
                    ([[900, 100], [1060, 100], [1060, 140], [900, 140]], "Expiny Date", 0.90),
                    ([[900, 150], [1060, 150], [1060, 190], [900, 190]], "05/2027", 0.94),
                    ([[300, 380], [440, 380], [440, 420], [300, 420]], "MRP.Rs", 0.92),
                    ([[600, 380], [760, 380], [760, 420], [600, 420]], "105.41", 0.98),
                ], [0.0] * 9)

        try:
            with patch.dict(os.environ, {"TRUE_LABEL_ENABLE_LOCAL_OCR": "1", "TRUE_LABEL_OCR_ENGINE": "rapidocr"}, clear=False), \
                patch("backend.app.services.ai_engine.metrology_engine._rapid_ocr", return_value=FakeRapidOCR()), \
                patch("backend.app.services.ai_engine.metrology_engine._paddle_ocr", return_value=None):
                result = analyze_product_label(path)
        finally:
            os.remove(path)

        self.assertIn("COMMODITY_NAME", {item["tag"] for item in result["declarations"]})
        date_tags = {item["tag"] for item in result["declarations"] if item["text"] in {"06/2025", "05/2027"}}
        self.assertEqual({"MANUFACTURING_DATE", "EXPIRY_DATE"}, date_tags)
        recognized_fields = {(item["tag"], item["text"]) for item in result["declarations"]}
        self.assertIn(("BATCH_CODE", "N0250507"), recognized_fields)
        self.assertIn(("MRP", "105.41"), recognized_fields)


if __name__ == "__main__":
    unittest.main()
