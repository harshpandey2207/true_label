import io
import unittest
import xml.etree.ElementTree as ET

from PIL import Image

from backend.app.services.ai_engine.label_generator import CATEGORIES, generate_label_draft, render_label_pdf


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
        self.assertIn("100 x 150 mm", side["svg_code"])
        self.assertIn("FRONT - 1/1", side["svg_code"])
        self.assertIn("PRODUCT CATEGORY", side["svg_code"])
        self.assertIn("Cosmetics, Ointments &amp; Pharma Goods", side["svg_code"])
        self.assertLess(
            side["svg_code"].index("100 x 150 mm"),
            side["svg_code"].index("</svg>"),
        )
        self.assertIn('viewBox="0 0 1000 1500.00"', side["svg_code"])
        self.assertNotIn("Approved brand mark", side["svg_code"])
        ET.fromstring(side["svg_code"])
        pdf = render_label_pdf(result["label_data"])
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertIn(b"/MediaBox [0 0 283.46 425.20]", pdf)
        self.assertIn(b"Test & Care", pdf)
        self.assertIn(b"NET QUANTITY", pdf)
        self.assertIn(b"MRP Rs. 105.41", pdf)
        self.assertIn(b"100 x 150 mm", pdf)
        self.assertIn(b"PRODUCT CATEGORY", pdf)
        self.assertIn(b"Cosmetics, Ointments & Pharma Goods", pdf)
        self.assertNotIn("—".encode("utf-8"), pdf)

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

    def test_long_values_wrap_without_losing_physical_dimensions(self):
        result = generate_label_draft(
            product_name="AquaPure Consumer Wellness Product with Extended Name",
            product_category="Food & Beverages",
            shape="bottle",
            dimensions="100 mm x 150 mm",
            custom_prompt="",
            label_values={
                "manufacturer": "A long manufacturing address and customer support detail that must remain readable inside the editable panel.",
                "consumer_care": "Call the approved customer-care number printed on the package.",
            },
            additional_details="Keep sealed and store away from sunlight.",
            images=[],
        )
        front, back = result["label_data"]["sides"]
        svg = back["svg_code"]
        self.assertIn('width="100mm" height="150mm"', svg)
        self.assertIn('preserveAspectRatio="xMidYMid meet"', svg)
        self.assertIn('y="176.0"', svg)
        self.assertNotIn("My Product", svg)
        self.assertGreater(svg.count("<text"), 6)
        self.assertIn("manufacturing address", svg)
        self.assertEqual({}, front["supplied_values"])
        pdf = render_label_pdf(result["label_data"])
        self.assertIn(b"AquaPure Consumer", pdf)
        self.assertIn(b"MANUFACTURER", pdf)
        self.assertIn(b"/Count 2", pdf)

    def test_design_brief_and_package_shape_change_the_local_visual_system(self):
        result = generate_label_draft(
            product_name="Everyday Cleaner",
            product_category="Household Cleaning Products",
            shape="bottle",
            dimensions="120 x 180 mm",
            custom_prompt="minimal navy with a clean premium finish",
            label_values={"net_quantity": "500 ml", "mrp": "Rs. 120"},
            additional_details="",
            images=[],
            side_count=2,
        )
        data = result["label_data"]
        front = data["sides"][0]["svg_code"]
        self.assertEqual("#17324F", data["brand_dna"]["primary_color"])
        self.assertIn("Minimal vector style", data["brand_dna"]["design_aesthetic"])
        self.assertIn('rx="42"', front)
        self.assertIn("NET QUANTITY", front)
        self.assertIn("MAXIMUM RETAIL PRICE", front)

    def test_four_side_draft_distributes_all_supplied_copy_without_invention(self):
        values = {
            "commodity_name": "Sample Face Cream",
            "net_quantity": "50 g",
            "mrp": "Rs. 99",
            "manufacturer": "Example Manufacturer Ltd.",
            "batch_code": "B-204",
            "consumer_care": "care@example.test",
        }
        result = generate_label_draft(
            product_name="Sample",
            product_category="Cosmetics, Ointments & Pharma Goods",
            shape="carton",
            dimensions="100 x 150 mm",
            custom_prompt="",
            label_values=values,
            additional_details="",
            images=[("front.jpg", self._image_bytes()), ("back.jpg", self._image_bytes()), ("left.jpg", self._image_bytes()), ("right.jpg", self._image_bytes())],
            side_count=4,
        )
        sides = result["label_data"]["sides"]
        self.assertEqual(4, len(sides))
        self.assertEqual(["Front", "Back", "Left", "Right"], [side["side_name"] for side in sides])
        for side in sides:
            self.assertIn("100 x 150 mm", side["svg_code"])
        self.assertEqual(set(values), {key for side in sides for key in side["supplied_values"]})
        self.assertEqual({"commodity_name", "net_quantity", "mrp"}, set(sides[0]["supplied_values"]))
        self.assertIn("MAXIMUM RETAIL PRICE", sides[0]["svg_code"])
        self.assertIn("NET QUANTITY", sides[0]["svg_code"])
        self.assertNotIn("Approved brand mark", "".join(side["svg_code"] for side in sides))

    def test_ai_style_spec_changes_editable_art_but_never_writes_copy(self):
        result = generate_label_draft(
            product_name="Cipladine",
            product_category="Cosmetics, Ointments & Pharma Goods",
            shape="carton",
            dimensions="20 cm x 30 cm",
            custom_prompt="clean clinical style",
            label_values={"net_quantity": "30 g", "mrp": "Rs. 105.41", "manufacturer": "Cipla Health Ltd."},
            additional_details="",
            images=[],
            side_count=2,
            design_spec={
                "primary": "#18362F",
                "background": "#FFFDF8",
                "accent": "#C83E4D",
                "style": "clinical",
                "motif": "cross",
                "source": "gemini",
            },
        )
        label_data = result["label_data"]
        front = label_data["sides"][0]["svg_code"]
        self.assertEqual("Gemini AI-assisted vector design direction", result["engine_used"])
        self.assertEqual("#C83E4D", label_data["brand_dna"]["accent_color"])
        self.assertIn("NET QUANTITY", front)
        self.assertIn("MAXIMUM RETAIL PRICE", front)
        self.assertIn("30 g", front)
        self.assertIn("Rs. 105.41", front)
        self.assertIn("PRODUCT CATEGORY", front)
        self.assertIn("#C83E4D", front)
        self.assertIn("AI-assisted design direction controls only colours", " ".join(result["warnings"]))
        pdf = render_label_pdf(label_data)
        self.assertIn(b"NET QUANTITY", pdf)
        self.assertIn(b"MAXIMUM RETAIL PRICE", pdf)
        self.assertIn(b"/MediaBox [0 0 566.93 850.39]", pdf)

    def test_reference_hue_guides_palette_and_small_dimensions_are_flagged(self):
        output = io.BytesIO()
        image = Image.new("RGB", (200, 100), "#9A603A")
        for x in range(28, 172):
            for y in range(12, 88):
                image.putpixel((x, y), (210, 20, 35))
        image.save(output, format="PNG")
        result = generate_label_draft(
            product_name="Sample Product",
            product_category="General Packaged Commodity",
            shape="carton",
            dimensions="25 mm x 30 mm",
            custom_prompt="",
            label_values={"net_quantity": "30 g"},
            additional_details="",
            images=[("front.png", output.getvalue())],
        )
        side = result["label_data"]["sides"][0]
        self.assertEqual(25.0, side["physical_dimensions_mm"]["width"])
        self.assertIn('viewBox="0 0 1000 1200.00"', side["svg_code"])
        self.assertIn("25 x 30 mm", side["svg_code"])
        self.assertEqual("#D84A32", result["label_data"]["brand_dna"]["accent_color"])
        self.assertIn("too small to read at actual print size", " ".join(result["warnings"]))
        self.assertNotIn("#9A603A", side["sampled_primary_color"])

    def test_every_catalog_category_is_accepted_by_label_generator(self):
        self.assertGreaterEqual(len(CATEGORIES), 16)
        for category in CATEGORIES:
            result = generate_label_draft(
                product_name="Catalog sample",
                product_category=category,
                shape="carton",
                dimensions="10 cm x 15 cm",
                custom_prompt="",
                label_values={"mrp": "MRP Rs. 10"},
                additional_details="",
                images=[],
            )
            self.assertEqual(category, result["label_data"]["product_category"])


if __name__ == "__main__":
    unittest.main()
