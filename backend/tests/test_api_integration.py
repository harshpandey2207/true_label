"""End-to-end API-contract tests using an isolated SQLite database."""

from __future__ import annotations

import io
import os
import unittest
import uuid
from contextlib import contextmanager
from unittest.mock import AsyncMock, patch

from PIL import Image


@contextmanager
def _patched_analyser(declarations):
    from backend.app.api import scan_routes

    original = scan_routes.analyze_product_label
    scan_routes.analyze_product_label = lambda **_: {
        "status": "EVIDENCE_CAPTURED",
        "declarations": declarations,
        "ocr_engine": "fixture",
        "image_quality": {"width": 900, "height": 900, "warnings": []},
        "warnings": [],
        "perceptual_hash": "10101010",
        "measurement": {"status": "INDICATIVE_ONLY"},
    }
    try:
        yield
    finally:
        scan_routes.analyze_product_label = original


class ApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A fixed project-local database avoids OS temp-directory restrictions
        # in sandboxed Windows runners. It is intentionally never used by the
        # application and is excluded from source control.
        cls.database_path = os.path.join(os.getcwd(), "true_label_integration_test.db")
        os.environ["DATABASE_URL"] = "sqlite:///" + cls.database_path.replace("\\", "/")
        # Test the explicit no-OCR fallback even when optional OCR wheels are
        # installed in the developer's local environment.
        os.environ["TRUE_LABEL_ENABLE_LOCAL_OCR"] = "0"

        from fastapi.testclient import TestClient
        from backend.app.main import app

        cls.client = TestClient(app)
        cls.client.__enter__()
        registered = cls.client.post("/auth/register", json={
            "full_name": "Integration Tester",
            "email": "integration-" + uuid.uuid4().hex + "@example.test",
            "password": "safe-demo-password",
            "role": "business_owner",
            "organization_name": "True Label Test Lab",
        })
        assert registered.status_code == 201, registered.text
        account = registered.json()
        cls.headers = {"Authorization": "Bearer " + account["access_token"]}
        cls.user_id = account["user"]["id"]

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    @staticmethod
    def image_bytes(colour="white"):
        output = io.BytesIO()
        Image.new("RGB", (900, 900), colour).save(output, format="PNG")
        return output.getvalue()

    def scan(self, image, *, scan_id=None):
        fields = {
            "distance_mm": "300",
            "focal_length_px": "1050",
            "category_name": "General Packaged Commodity",
        }
        if scan_id is not None:
            fields["scan_id"] = str(scan_id)
        return self.client.post(
            "/scan/analyze-ar",
            data=fields,
            files=[("images", ("package-side.png", image, "image/png"))],
            headers=self.headers,
        )

    def test_unconfigured_ocr_creates_a_persisted_unresolved_scan(self):
        response = self.scan(self.image_bytes())
        self.assertEqual(200, response.status_code, response.text)
        payload = response.json()
        self.assertEqual("SUCCESS", payload["status"])
        self.assertIsInstance(payload["scan_id"], int)
        self.assertEqual("UNRESOLVED", payload["overall_status"])
        self.assertEqual("POTENTIAL_ISSUES", payload["package_status"])
        self.assertTrue(payload["clarification_requests"])
        self.assertEqual("unavailable", payload["results"][0]["analysis"]["ocr_engine"])
        self.assertEqual([], payload["results"][0]["analysis"]["missing_tags"])
        self.assertIn("MRP", payload["results"][0]["analysis"]["unresolved_tags"])
        self.assertEqual([], payload["confirmed_violation_tags"])

        from backend.app.db.database import SessionLocal
        from backend.app.db.models import ScanEvidence, ScanRecord

        session = SessionLocal()
        try:
            record = session.get(ScanRecord, payload["scan_id"])
            self.assertEqual("POTENTIAL_ISSUES", record.status)
            self.assertEqual(1, session.query(ScanEvidence).filter_by(scan_id=record.id).count())
            self.assertEqual(record.user_id, self.user_id)
            stored_side = record.result["results"][0]["analysis"]
            self.assertEqual([], stored_side["missing_tags"])
            self.assertIn("MRP", stored_side["unresolved_tags"])
        finally:
            session.close()

        history = self.client.get("/workspace/scans?limit=10", headers=self.headers)
        self.assertEqual(200, history.status_code, history.text)
        self.assertIn(payload["scan_id"], [row["id"] for row in history.json()["items"]])

    def test_category_catalog_exposes_every_seeded_product_profile(self):
        response = self.client.get("/label/categories")
        self.assertEqual(200, response.status_code, response.text)
        categories = response.json()["categories"]
        self.assertGreaterEqual(len(categories), 16)
        self.assertIn("Food & Beverages", categories)
        self.assertIn("Medical Devices", categories)
        self.assertIn("Agricultural Inputs", categories)
        self.assertIn("Other / Custom Packaged Product", categories)

    def test_clarification_reuses_stable_scan_id_and_prior_evidence(self):
        initial = self.scan(self.image_bytes("white")).json()
        clarification = self.scan(self.image_bytes("#dfdfdf"), scan_id=initial["scan_id"])
        self.assertEqual(200, clarification.status_code, clarification.text)
        payload = clarification.json()
        self.assertEqual(initial["scan_id"], payload["scan_id"])
        self.assertEqual(2, len(payload["results"]))

        from backend.app.db.database import SessionLocal
        from backend.app.db.models import ScanEvidence

        session = SessionLocal()
        try:
            self.assertEqual(2, session.query(ScanEvidence).filter_by(scan_id=initial["scan_id"]).count())
        finally:
            session.close()

    def test_authenticated_label_draft_is_persisted_from_a_source_scan(self):
        scan = self.scan(self.image_bytes("#e6f4ea")).json()
        response = self.client.post(
            "/label/generate",
            data={
                "product_name": "Demo Ointment",
                "product_category": "General Packaged Commodity",
                "dimensions": "20 cm x 30 cm",
                "side_count": "2",
                "missing_tag_values": '{"mrp":"MRP Rs. 105.41","net_quantity":"30 g"}',
                "source_scan_id": str(scan["scan_id"]),
            },
            headers=self.headers,
        )
        self.assertEqual(200, response.status_code, response.text)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIsInstance(payload["draft_id"], int)
        self.assertEqual("Local deterministic SVG template renderer", payload["engine_used"])
        self.assertTrue(payload["label_data"]["sides"][0]["svg_code"].startswith("<svg"))
        self.assertEqual(
            {"width": 200.0, "height": 300.0},
            payload["label_data"]["sides"][0]["physical_dimensions_mm"],
        )
        self.assertIn('width="200mm" height="300mm"', payload["label_data"]["sides"][0]["svg_code"])
        self.assertIn("validation", payload["label_data"])
        label_pdf = self.client.get(payload["pdf_download_url"], headers=self.headers)
        self.assertEqual(200, label_pdf.status_code, label_pdf.text)
        self.assertEqual("application/pdf", label_pdf.headers["content-type"])
        self.assertTrue(label_pdf.content.startswith(b"%PDF-1.4"))
        self.assertIn(b"/MediaBox [0 0 566.93 850.39]", label_pdf.content)

        drafts = self.client.get("/workspace/labels", headers=self.headers)
        self.assertEqual(200, drafts.status_code, drafts.text)
        self.assertIn(payload["draft_id"], [row["id"] for row in drafts.json()["items"]])

    def test_ai_label_design_requires_opt_in_and_a_backend_key(self):
        with patch.dict(os.environ, {"TRUE_LABEL_GEMINI_API_KEY": ""}):
            status = self.client.get("/label/design-status")
            self.assertEqual(200, status.status_code, status.text)
            self.assertFalse(status.json()["configured"])
            response = self.client.post("/label/generate", data={
                "product_name": "Private local product",
                "product_category": "Food & Beverages",
                "dimensions": "100 x 150 mm",
                "use_ai_design": "true",
            }, headers=self.headers)
        self.assertEqual(503, response.status_code, response.text)
        self.assertIn("TRUE_LABEL_GEMINI_API_KEY", response.json()["detail"])

    def test_ai_label_design_is_constrained_and_keeps_product_copy_local(self):
        design = {
            "primary": "#18362F",
            "background": "#FFFDF8",
            "accent": "#C83E4D",
            "style": "clinical",
            "motif": "cross",
            "source": "gemini",
        }
        assistant = AsyncMock(return_value=design)
        with patch.dict(os.environ, {"TRUE_LABEL_GEMINI_API_KEY": "configured-test-key"}), patch(
            "backend.app.api.label_routes.generate_design_direction", assistant
        ):
            unauthenticated = self.client.post("/label/generate", data={
                "product_name": "Private local product",
                "product_category": "Cosmetics, Ointments & Pharma Goods",
                "dimensions": "20 cm x 30 cm",
                "use_ai_design": "true",
            })
            self.assertEqual(401, unauthenticated.status_code, unauthenticated.text)
            response = self.client.post("/label/generate", data={
                "product_name": "Private local product",
                "product_category": "Cosmetics, Ointments & Pharma Goods",
                "shape": "carton",
                "dimensions": "20 cm x 30 cm",
                "custom_prompt": "clinical red and cream",
                "missing_tag_values": '{"net_quantity":"30 g","mrp":"Rs. 105.41"}',
                "use_ai_design": "true",
            }, headers=self.headers)
        self.assertEqual(200, response.status_code, response.text)
        payload = response.json()
        self.assertEqual("Gemini AI-assisted vector design direction", payload["engine_used"])
        self.assertEqual("#C83E4D", payload["label_data"]["brand_dna"]["accent_color"])
        assistant.assert_awaited_once()
        call = assistant.await_args.kwargs
        self.assertEqual("Cosmetics, Ointments & Pharma Goods", call["category"])
        self.assertEqual("20 cm x 30 cm", call["dimensions"])
        self.assertNotIn("Private local product", str(call))
        self.assertNotIn("30 g", str(call))
        self.assertNotIn("Rs. 105.41", str(call))

    def test_report_is_generated_from_persisted_checks_and_evidence(self):
        scan = self.scan(self.image_bytes("#f6f6f6")).json()
        created = self.client.post(f"/reports/scans/{scan['scan_id']}", headers=self.headers)
        self.assertEqual(201, created.status_code, created.text)
        report = created.json()
        self.assertEqual(scan["scan_id"], report["scan_id"])
        self.assertGreaterEqual(report["check_count"], 1)
        self.assertEqual(1, report["evidence_count"])
        self.assertGreaterEqual(report["page_count"], 1)

        download = self.client.get(report["download_url"], headers=self.headers)
        self.assertEqual(200, download.status_code, download.text)
        self.assertEqual("application/pdf", download.headers["content-type"])
        self.assertTrue(download.content.startswith(b"%PDF-1.4"))
        self.assertIn(b"OFFICIAL PRODUCT COMPLIANCE INSPECTION REPORT", download.content)
        self.assertIn(b"PRELIMINARY COMPLIANCE REPORT", download.content)
        self.assertIn(b"2. EXECUTIVE CONCLUSION", download.content)
        self.assertIn(b"6. IMAGE EVIDENCE RECORD", download.content)
        self.assertIn(b"EVIDENCE MANIFEST", download.content)
        self.assertIn(b"Prototype decision support only -", download.content)
        self.assertEqual("officer-compliance-v2", report["template"])

        second = self.client.post(f"/reports/scans/{scan['scan_id']}", headers=self.headers)
        self.assertEqual(201, second.status_code, second.text)
        self.assertNotEqual(report["report_code"], second.json()["report_code"])

        history = self.client.get("/reports?limit=10", headers=self.headers)
        self.assertEqual(200, history.status_code, history.text)
        self.assertIn(report["id"], [item["id"] for item in history.json()["items"]])

    def test_inspector_escalation_creates_persistent_case_and_admin_can_update_it(self):
        scan = self.scan(self.image_bytes("#faf0e6")).json()
        inspector_registered = self.client.post("/auth/register", json={
            "full_name": "Inspector Tester",
            "email": "inspector-" + uuid.uuid4().hex + "@example.test",
            "password": "safe-demo-password",
            "role": "inspector",
            "organization_name": "True Label Test Lab",
        })
        self.assertEqual(201, inspector_registered.status_code, inspector_registered.text)
        inspector_headers = {"Authorization": "Bearer " + inspector_registered.json()["access_token"]}
        created = self.client.post("/workspace/escalations", json={"scan_id": scan["scan_id"], "note": "Readable evidence needs review."}, headers=inspector_headers)
        self.assertEqual(201, created.status_code, created.text)
        case = created.json()
        self.assertEqual("open", case["status"])
        self.assertEqual(scan["scan_id"], case["scan_id"])
        listed = self.client.get("/workspace/escalations", headers=inspector_headers)
        self.assertEqual(200, listed.status_code, listed.text)
        self.assertIn(case["id"], [item["id"] for item in listed.json()["items"]])
        admin_registered = self.client.post("/auth/register", json={
            "full_name": "Admin Tester",
            "email": "admin-" + uuid.uuid4().hex + "@example.test",
            "password": "safe-demo-password",
            "role": "admin",
            "organization_name": "True Label Test Lab",
        })
        self.assertEqual(201, admin_registered.status_code, admin_registered.text)
        admin_headers = {"Authorization": "Bearer " + admin_registered.json()["access_token"]}
        overview = self.client.get("/workspace/admin/overview", headers=admin_headers)
        self.assertEqual(200, overview.status_code, overview.text)
        overview_payload = overview.json()
        self.assertGreaterEqual(overview_payload["category_count"], 16)
        self.assertGreaterEqual(overview_payload["rule_count"], 169)
        self.assertGreaterEqual(overview_payload["scan_count"], 1)
        self.assertIn("by_category", overview_payload)
        updated = self.client.patch(f"/workspace/escalations/{case['id']}", json={"status": "in_review"}, headers=admin_headers)
        self.assertEqual(200, updated.status_code, updated.text)
        self.assertEqual("in_review", updated.json()["status"])

    def test_fixture_declarations_cover_pass_and_confirmed_violation_contracts(self):
        complete = [
            {"tag": tag, "text": tag, "confidence": 0.99, "finding_status": "DETECTED", "box": []}
            for tag in ("COMMODITY_NAME", "MANUFACTURER", "NET_QUANTITY", "MANUFACTURING_DATE", "MRP", "CONSUMER_CARE", "LANGUAGE_CHECK")
        ]
        with _patched_analyser(complete):
            compliant = self.scan(self.image_bytes("#f3fff3"))
        self.assertEqual(200, compliant.status_code, compliant.text)
        self.assertEqual("PASS", compliant.json()["overall_status"])
        self.assertEqual("NO_FLAGS", compliant.json()["package_status"])

        violation = [dict(item) for item in complete]
        quantity = next(item for item in violation if item["tag"] == "NET_QUANTITY")
        quantity["finding_status"] = "CONFIRMED_VIOLATION"
        quantity["failure_reason"] = "Readable misleading quantity declaration."
        with _patched_analyser(violation):
            flagged = self.scan(self.image_bytes("#fff3f3"))
        self.assertEqual(200, flagged.status_code, flagged.text)
        self.assertEqual("CONFIRMED_VIOLATION", flagged.json()["overall_status"])
        self.assertIn("NET_QUANTITY", flagged.json()["confirmed_violation_tags"])

    def test_legacy_history_result_does_not_reclassify_unresolved_tags_as_missing(self):
        from backend.app.api.workspace_routes import _normalise_scan_result

        normalised = _normalise_scan_result({
            "unresolved_tags": ["MRP"],
            "confirmed_violation_tags": [],
            "results": [{"analysis": {"missing_tags": ["MRP"]}}],
        })
        analysis = normalised["results"][0]["analysis"]
        self.assertEqual([], analysis["missing_tags"])
        self.assertEqual(["MRP"], analysis["unresolved_tags"])


if __name__ == "__main__":
    unittest.main()
