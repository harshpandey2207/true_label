import io
import os
import tempfile
import unittest

from PIL import Image

from backend.app.services.ai_engine.metrology_engine import analyze_product_label, orb_overlap_score


class ImageAnalysisTests(unittest.TestCase):
    def test_unconfigured_ocr_produces_an_unresolved_evidence_result(self):
        image = Image.new("RGB", (120, 100), "white")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output:
            image.save(output, format="PNG")
            path = output.name
        try:
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


if __name__ == "__main__":
    unittest.main()
