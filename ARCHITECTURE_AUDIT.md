# True Label architecture audit

Audited on 2026-10-17 against `TRUE_LABEL_CODEX_MASTER_BRIEF.md`.

## Original audited flow (fixed in the working tree)

The original repository routed Flutter uploads through OCR.space and wrote a legacy `ScanHistory` row while workspace history queried a separate `ScanRecord` model. Label generation depended on Gemini and had no durable draft contract. Those statements describe the baseline audit, not the current implementation.

## Implemented flow

`Flutter image picker` -> `POST /scan/analyze-ar` -> image decoding/orientation and quality guidance -> optional, explicitly enabled local PaddleOCR -> structured evidence extraction -> versioned evidence-aware rule checks -> persisted `ScanRecord` + original `ScanEvidence` -> stable scan response/history. A clarification crop uses the same `scan_id`, retains prior evidence, and re-evaluates the aggregate package. Perceptual hashes and conservative OpenCV ORB overlap scores only flag possible duplicate sides; no original is silently merged or deleted.

The label endpoint reuses source-scan evidence when supplied, produces deterministic editable SVG side layouts, validates draft declarations with the same rules, and persists `LabelDraftRecord`. Persisted report records are created/downloaded through `/reports`; inspector escalations are persistent `/workspace/escalations` cases rather than snackbar-only events.

## Priority defects

1. **Evidence integrity:** no OCR result is treated as a compliance failure, rather than an unresolved analysis. The response does not distinguish confirmed violations, unclear fields, not-applicable checks, and passes.
2. **Operational reliability:** the OCR implementation depends on an external provider despite local-OCR documentation, carries undefined fallback variables, and its error handling hides the failure.
3. **Persistence/API mismatch:** scan routes do not produce `ScanRecord` data or a stable ID; workspace endpoints reference model fields that do not exist in the checked-in model.
4. **Label-generator mismatch:** it needs an undeclared hosted key, has a parsing defect, and does not guarantee valid, sanitized editable SVG or side metadata.
5. **Rule-data limitations:** rules are seeded in Python, omit source/version/effective-date/evidence metadata, and current references should be marked for legal review instead of treated as authoritative automation.

## Design decisions for this implementation

- A scan will use four explicit outcomes: `PASS`, `CONFIRMED_VIOLATION`, `UNRESOLVED`, and `NOT_APPLICABLE`. An overall scan is `PASS` only when all applicable checks have affirmative evidence. Missing/low-confidence evidence remains unresolved.
- Image bytes will be retained as bounded, local scan evidence in the demo database. This supports a stable scan ID and clarification/reanalysis within the same scan. Render deployments still need external object storage because local disk is ephemeral.
- OCR will be provider-optional. A local deterministic text/evidence path permits tests and clear user messaging when no OCR backend is configured; no hosted API key is embedded in source.
- Rule configuration will gain version/source/effective-date/evidence metadata while retaining existing seeded records for compatibility. Legal citations remain review-required until linked to verified authoritative material.

## Verification limitations at audit time

The active Python installation lacks the project dependencies and pytest. Flutter did not finish a command inside the available command time window. These are environment limitations, not passing checks.

## Post-audit implementation status (2026-10-17)

The initial defects above have been addressed in the working tree. The current flow is `Flutter multipart upload` -> persisted `ScanRecord` and `ScanEvidence` -> local quality assessment -> optional local PaddleOCR when explicitly enabled -> evidence-aware rule evaluation -> stable scan response/history -> optional clarification upload on the same scan. The default no-OCR path remains `UNRESOLVED` and makes no compliance finding.

The label endpoint now produces deterministic editable SVG data, can reuse stored source-scan evidence, validates entered values through the same rule evaluator, and persists `LabelDraftRecord` rows. A report endpoint persists and serves a dependency-free, searchable PDF report containing checks, source metadata, evidence manifest, caveats and clarification requests.

FastAPI integration tests now cover authenticated multipart scans, evidence persistence, stable IDs, clarification, workspace history, source-scan label drafts, pass/violation fixtures, and report download. Flutter formatter validation is available, but full Dart analysis remains blocked by the local Windows sandbox preventing the analysis-server subprocess and by unresolved Flutter package resolution.
