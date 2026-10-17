"""End-to-end API-contract tests using an isolated SQLite database."""

from __future__ import annotations

import io
import os
import unittest
import uuid
from contextlib import contextmanager

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
        os.environ.pop("TRUE_LABEL_ENABLE_LOCAL_OCR", None)

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

        from backend.app.db.database import SessionLocal
        from backend.app.db.models import ScanEvidence, ScanRecord

        session = SessionLocal()
        try:
            record = session.get(ScanRecord, payload["scan_id"])
            self.assertEqual("POTENTIAL_ISSUES", record.status)
            self.assertEqual(1, session.query(ScanEvidence).filter_by(scan_id=record.id).count())
            self.assertEqual(record.user_id, self.user_id)
        finally:
            session.close()

        history = self.client.get("/workspace/scans?limit=10", headers=self.headers)
        self.assertEqual(200, history.status_code, history.text)
        self.assertIn(payload["scan_id"], [row["id"] for row in history.json()["items"]])

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
                "dimensions": "10 cm x 15 cm",
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
        self.assertIn("validation", payload["label_data"])
        label_pdf = self.client.get(payload["pdf_download_url"], headers=self.headers)
        self.assertEqual(200, label_pdf.status_code, label_pdf.text)
        self.assertEqual("application/pdf", label_pdf.headers["content-type"])
        self.assertTrue(label_pdf.content.startswith(b"%PDF-1.4"))
        self.assertIn(b"/MediaBox", label_pdf.content)

        drafts = self.client.get("/workspace/labels", headers=self.headers)
        self.assertEqual(200, drafts.status_code, drafts.text)
        self.assertIn(payload["draft_id"], [row["id"] for row in drafts.json()["items"]])

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
        self.assertIn(b"PRELIMINARY COMPLIANCE REPORT", download.content)
        self.assertIn(b"EVIDENCE MANIFEST", download.content)

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
        updated = self.client.patch(f"/workspace/escalations/{case['id']}", json={"status": "in_review"}, headers=admin_headers)
        self.assertEqual(200, updated.status_code, updated.text)
        self.assertEqual("in_review", updated.json()["status"])

    def test_fixture_declarations_cover_pass_and_confirmed_violation_contracts(self):
        complete = [
            {"tag": tag, "text": tag, "confidence": 0.99, "finding_status": "DETECTED", "box": []}
            for tag in ("MANUFACTURER", "NET_QUANTITY", "MANUFACTURING_DATE", "MRP", "CONSUMER_CARE", "LANGUAGE_CHECK")
        ]
        with _patched_analyser(complete):
            compliant = self.scan(self.image_bytes("#f3fff3"))
        self.assertEqual(200, compliant.status_code, compliant.text)
        self.assertEqual("PASS", compliant.json()["overall_status"])
        self.assertEqual("NO_FLAGS", compliant.json()["package_status"])

        violation = [dict(item) for item in complete]
        violation[1]["finding_status"] = "CONFIRMED_VIOLATION"
        violation[1]["failure_reason"] = "Readable misleading quantity declaration."
        with _patched_analyser(violation):
            flagged = self.scan(self.image_bytes("#fff3f3"))
        self.assertEqual(200, flagged.status_code, flagged.text)
        self.assertEqual("CONFIRMED_VIOLATION", flagged.json()["overall_status"])
        self.assertIn("NET_QUANTITY", flagged.json()["confirmed_violation_tags"])


if __name__ == "__main__":
    unittest.main()
