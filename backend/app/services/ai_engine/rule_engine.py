"""Evidence-aware prototype compliance evaluation.

This module deliberately separates rule outcomes from OCR availability. It is
not a legal opinion: seeded rule records must retain a review status and an
authoritative source before being used for an operational decision.
"""

from __future__ import annotations

from typing import Any, Iterable


PASS = "PASS"
CONFIRMED_VIOLATION = "CONFIRMED_VIOLATION"
UNRESOLVED = "UNRESOLVED"
NOT_APPLICABLE = "NOT_APPLICABLE"
RULE_ENGINE_VERSION = "prototype-2026-10"


def _normalise_tag(value: Any) -> str:
    return str(value or "").strip().upper()


def _rule_payload(rule: Any) -> dict[str, Any]:
    """Accept an ORM rule or a plain mapping to keep evaluator tests simple."""
    if isinstance(rule, dict):
        return rule
    return {
        "tag": getattr(rule, "tag", ""),
        "is_mandatory": getattr(rule, "is_mandatory", False),
        "legal_act_reference": getattr(rule, "legal_act_reference", None),
        "source_url": getattr(rule, "source_url", None),
        "rule_version": getattr(rule, "rule_version", None),
        "effective_from": getattr(rule, "effective_from", None),
        "review_status": getattr(rule, "review_status", "needs_legal_review"),
        "evidence_requirement": getattr(rule, "evidence_requirement", None),
    }


def evaluate_rules(
    rules: Iterable[Any], declarations: Iterable[dict[str, Any]], context: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Evaluate rule presence without mistaking absent OCR for a violation."""
    context = context or {}
    observations: dict[str, list[dict[str, Any]]] = {}
    for declaration in declarations:
        observations.setdefault(_normalise_tag(declaration.get("tag")), []).append(declaration)

    checks: list[dict[str, Any]] = []
    for raw_rule in rules:
        rule = _rule_payload(raw_rule)
        tag = _normalise_tag(rule.get("tag"))
        if not tag:
            continue
        mandatory = bool(rule.get("is_mandatory"))
        base = {
            "tag": tag,
            "required": mandatory,
            "legal_reference": rule.get("legal_act_reference"),
            "source_url": rule.get("source_url"),
            "rule_version": rule.get("rule_version") or RULE_ENGINE_VERSION,
            "effective_from": rule.get("effective_from"),
            "review_status": rule.get("review_status") or "needs_legal_review",
            "evidence_requirement": rule.get("evidence_requirement") or "Readable declaration text or a manual confirmation",
            "evidence": [],
        }

        # These exemptions are not independently certified here. Their purpose
        # is to avoid an unsupported negative finding when the demo operator
        # states that an exception could apply.
        if tag in {"MRP", "UNIT_SALE_PRICE"} and context.get("is_institutional"):
            checks.append({**base, "status": NOT_APPLICABLE, "reason": "Institutional-consumer context was supplied; confirm the exemption and required declaration manually."})
            continue
        if context.get("weight_under_10g") and not context.get("is_tobacco"):
            checks.append({**base, "status": NOT_APPLICABLE, "reason": "Small-package context was supplied. Applicability and any exception require human legal review."})
            continue
        if not mandatory:
            checks.append({**base, "status": NOT_APPLICABLE, "reason": "This seeded prototype rule is conditional; applicability was not established from the submitted evidence."})
            continue

        evidence = observations.get(tag, [])
        base["evidence"] = [
            {
                "text": item.get("text", ""),
                "confidence": item.get("confidence"),
                "image_index": item.get("image_index"),
                "box": item.get("box"),
            }
            for item in evidence
        ]
        violations = [item for item in evidence if item.get("finding_status") == CONFIRMED_VIOLATION]
        reliable = [item for item in evidence if float(item.get("confidence") or 0) >= 0.55]
        if violations:
            checks.append({**base, "status": CONFIRMED_VIOLATION, "reason": violations[0].get("failure_reason") or "A readable declaration has an evidence-backed defect."})
        elif reliable:
            checks.append({**base, "status": PASS, "reason": "A readable declaration was detected. Formatting, prominence and current legal applicability still need review."})
        else:
            checks.append({**base, "status": UNRESOLVED, "reason": "The required declaration was not read with enough confidence. Upload a clear crop of this declaration or confirm it manually."})
    return checks


def overall_status(checks: Iterable[dict[str, Any]]) -> str:
    values = {check.get("status") for check in checks}
    if CONFIRMED_VIOLATION in values:
        return CONFIRMED_VIOLATION
    if UNRESOLVED in values:
        return UNRESOLVED
    return PASS


def clarification_requests(checks: Iterable[dict[str, Any]]) -> list[str]:
    return [
        f"The {check['tag'].replace('_', ' ').title()} section is unclear. Upload a clear close-up of that section or confirm the value manually."
        for check in checks
        if check.get("status") == UNRESOLVED
    ]
