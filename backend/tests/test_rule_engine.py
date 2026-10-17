import unittest

from backend.app.services.ai_engine.rule_engine import (
    CONFIRMED_VIOLATION,
    NOT_APPLICABLE,
    PASS,
    UNRESOLVED,
    evaluate_rules,
    overall_status,
)


class RuleEngineTests(unittest.TestCase):
    def setUp(self):
        self.rules = [
            {"tag": "MRP", "is_mandatory": True, "legal_act_reference": "Rule 6", "review_status": "needs_legal_review"},
            {"tag": "UNIT_SALE_PRICE", "is_mandatory": False, "legal_act_reference": "Rule 6(11)"},
        ]

    def test_missing_ocr_evidence_is_unresolved_not_a_violation(self):
        checks = evaluate_rules(self.rules, [])
        self.assertEqual(UNRESOLVED, checks[0]["status"])
        self.assertEqual(NOT_APPLICABLE, checks[1]["status"])
        self.assertEqual(UNRESOLVED, overall_status(checks))

    def test_readable_declaration_can_pass_presence_check(self):
        checks = evaluate_rules(self.rules, [{"tag": "MRP", "text": "MRP Rs. 105.41", "confidence": 0.91, "image_index": 0}])
        self.assertEqual(PASS, checks[0]["status"])
        self.assertEqual(PASS, overall_status(checks))
        self.assertEqual("needs_legal_review", checks[0]["review_status"])

    def test_evidence_backed_defect_is_a_confirmed_violation(self):
        checks = evaluate_rules(self.rules, [{
            "tag": "MRP",
            "text": "MRP Rs. 105.41",
            "confidence": 0.91,
            "finding_status": CONFIRMED_VIOLATION,
            "failure_reason": "Readable conflicting price declaration.",
        }])
        self.assertEqual(CONFIRMED_VIOLATION, checks[0]["status"])
        self.assertEqual(CONFIRMED_VIOLATION, overall_status(checks))

    def test_institutional_context_does_not_claim_mrp_failure(self):
        checks = evaluate_rules(self.rules, [], {"is_institutional": True})
        self.assertEqual(NOT_APPLICABLE, checks[0]["status"])
        self.assertIn("confirm", checks[0]["reason"].lower())


if __name__ == "__main__":
    unittest.main()
