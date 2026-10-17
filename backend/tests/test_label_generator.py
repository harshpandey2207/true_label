import io
import unittest
import xml.etree.ElementTree as ET

from PIL import Image

from backend.app.services.ai_engine.label_generator import generate_label_draft, render_label_pdf


class LabelGeneratorTests(unittest.TestCase):
    def _image_bytes(self) -> bytes:
        output = io.BytesIO()
        Image.new("RGB", (80, 60), "#206A5D").save(output, format="PNG")
        return output.getvalue()

    def test_generates_editable_valid_svg_without_a_hosted_key(self):
        result = generate_label_draft(
            product_name="Test & Care",
            product_category="Cosmetics, Ointments & Pharma Goods",
            shape="carton",
            dimensions="10 cm x 15 cm",
            custom_prompt="calm teal style",
            label_values={"mrp": "MRP Rs. 105.41", "net_quantity": "30 g"},
            additional_details="For external use only",
            images=[("front.png", self._image_bytes())],
        )
        self.assertEqual("Local deterministic SVG template renderer", result["engine_used"])
        side = result["label_data"]["sides"][0]
        self.assertEqual("Front", side["side_name"])
        self.assertTrue(side["editable"])
        self.assertEqual(100.0, side["physical_dimensions_mm"]["width"])
        self.assertIn("Test &amp; Care", side["svg_code"])
        ET.fromstring(side["svg_code"])
        pdf = render_label_pdf(result["label_data"])
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertIn(b"/MediaBox [0 0 283.46 425.20]", pdf)
        self.assertIn(b"Test & Care", pdf)

    def test_invalid_dimensions_are_rejected(self):
        with self.assertRaises(ValueError):
            generate_label_draft(
                product_name="Sample",
                product_category="General Packaged Commodity",
                shape="box",
                dimensions="1 mm x 1 mm",
                custom_prompt="",
                label_values={},
                additional_details="",
                images=[],
            )


if __name__ == "__main__":
    unittest.main()
