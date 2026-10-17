# True Label — Codex Master Implementation Brief

## Mission and working style
Transform the existing `true_label` repository into the strongest coherent SIH jury prototype possible for packaged-commodity label screening, compliance analysis, inspection workflows, and corrected label generation.

Work directly in this repository. First inspect the current code, architecture, README, existing UI, API contracts, database models, and deployment configuration. Do not assume the README accurately describes implementation. Verify every important claim against the code.

You have broad discretion to brainstorm, redesign, refactor, replace weak implementations, and improve requirements that are missing from this brief. Optimize for a polished, reliable end-user experience and a coherent end-to-end product—not for preserving a poor implementation or a particular technology. Do the work, run checks, fix root causes, and continue until meaningful completion. Do not stop after producing a plan or a list of TODOs.

Maintain `IMPLEMENTATION_PROGRESS.md` in the repository. Record discoveries, decisions, completed work, commands/tests and actual outcomes, current blockers, and the next steps. Update it regularly so work can resume after context or usage limits.

## Important project constraints
- This is currently an SIH jury/demo prototype, not an officially certified government enforcement system.
- Preserve the easy demo-entry experience for manufacturer, inspector, and admin. Do not introduce mandatory login/signup/token friction that would break the intended jury demo. You may improve role selection and demo safety without making the demo harder to enter.
- Mock data is acceptable for dashboards, analytics, audit history, reports, and simulated payment when live operational data is not available. Clearly label demo/mock/simulated data. Never present fabricated government actions, official notices, real fines, or actual enforcement outcomes as real.
- Current deployment target: Flutter frontend on Vercel and FastAPI backend on Render free tier. Verify actual compatibility. Be mindful of cold starts, RAM/CPU, request timeouts, large model weights, and ephemeral storage. Never assume Render local disk is durable.
- Prefer open-source components and local/self-hostable approaches for the eventual product. Hosted APIs may be used behind replaceable provider interfaces when needed for the demo, but keep secrets out of source control and document production-ready open-source alternatives.
- Do not run destructive commands, delete unrelated files, drop databases, expose secrets, or deploy to production without explicit permission. Limit changes to this project. Preserve existing user work; inspect git status before modifying files.
- Do not claim that a test, build, scan, legal check, or export succeeded unless you actually ran it and observed the result.

## First phase: audit and baseline
1. Inspect repository structure, git status, frontend/backend, dependencies, routes, schemas, database setup, configuration, tests, README and deployment files.
2. Run existing tests, static checks, and builds where feasible before changing anything; record real outcomes.
3. Trace the entire current flow: image upload → quality checks → OCR → field extraction → product category → rule checks → verdict → persisted scan/history → report; and scan/reference input → label draft → validation → SVG/PDF export.
4. Identify broken contracts, disconnected models, incorrect verdicts, misleading UI, insecure secrets, unimplemented controls, and README/code mismatches.
5. Create or update `IMPLEMENTATION_PROGRESS.md` and a concise architecture/audit document. Then fix the most important end-to-end defects before adding breadth.

Known potential problems from a preliminary, unverified review that must be independently checked (do not assume they remain true):
- OCR implementation may use OCR.space despite README describing local PaddleOCR; a key may be hard-coded and an error path may reference undefined names.
- Label generation may use Gemini and return SVG while the frontend expects structured side data; parsing may reference a missing `re` import.
- Rule catalogue may be limited or seeded with only a few rules.
- `ScanHistory` and `ScanRecord` may be disconnected, and scan endpoints may not return stable IDs expected by clients.
- Admin metrics, audit logs, violations, and reports may be static mock data.
Fix verified root causes, not just symptoms.

## Product roles and workflows
Support three clear demo workspaces:
- Manufacturer: create/inspect a label, scan a product, review compliance findings, generate a corrected label, export deliverables, view scan/report history, and see a clearly simulated fine/payment flow if included.
- Inspector: scan products, review findings and evidence, create/view formal reports, access inspection history and analytics, manage profile, and escalate a case to admin.
- Admin: coherent dashboard, violations/cases, rule catalogue, reports, audit logs, profile, and escalation review.

Every visible button, form, tab, and workflow should work meaningfully. If an operation is only simulated, communicate that clearly and make the simulation internally coherent. Ensure dashboard totals, lists, histories, and reports derive from the same persisted or explicitly seeded demo data instead of contradictory numbers. Escalation must create a visible case/status, not just show a snackbar. Keep secondary workflows proportionate to the core scanning and label-generation workflows.

## Core scanning and compliance workflow
Build a reliable, explainable pipeline for multiple package images:
1. Accept multiple images and preserve originals.
2. Check blur, glare, reflections, resolution, cropping, orientation, and readability. Give targeted guidance and distinguish image-quality problems from compliance findings.
3. Identify likely package sides and group repeated photographs of the same side. Six photos may represent four sides with repeated angles; do not assume each photo is a unique side.
4. Apply OCR and structured extraction with confidence/evidence tracking. Keep extracted text linked to source image and location where feasible.
5. Determine product category and which legal checks apply. If category or a required fact is uncertain, ask a focused question instead of guessing.
6. Evaluate each applicable declaration as one of: pass, confirmed violation, unresolved/unclear, or not applicable. Distinguish a proven violation from OCR uncertainty or missing evidence. Do not mark a product non-compliant solely because OCR failed to read a field.
7. For unclear fields, ask specifically, e.g. “The MRP section is unclear. Please upload a clear image of that section.” Accept a crop/replacement image, attach it to the same scan, preserve all previous evidence, and re-run affected checks and dependent checks without asking the user to upload every image again.
8. Persist a stable scan ID, images/evidence, extracted fields, category, rule-engine version, findings, user corrections, timestamps, and report references. Manufacturer and inspector history must use the same coherent underlying records where appropriate.
9. Return an understandable overall result with confidence and unresolved checks. Do not force a binary verdict when evidence is insufficient.

## Legal and rule-engine integrity
- The project concerns the Legal Metrology (Packaged Commodities) Rules, 2011, subsequent amendments, and other category-specific requirements where applicable (for example, relevant FSSAI requirements for food products).
- Build a structured, versioned, category-aware rule engine. Support conditions, exemptions, exceptions, applicability dates, and evidence requirements rather than applying every rule to every product.
- Ground legal text, exact rule/sub-rule/clause references, and thresholds in authoritative sources. Provide source URLs, effective dates/version metadata, and a rule coverage matrix. Never invent a rule or legal citation to make a result look complete.
- If authoritative sources cannot be verified, mark the rule as needing legal review and state the limitation. Include human-review boundaries and do not claim 100% legal correctness or official certification.
- Show the exact missing/incorrect declaration in red only when supported by evidence; use a distinct warning style for unclear/unresolved checks and neutral styling for not-applicable checks.
- Keep rule data separate from application logic and make it maintainable/testable. Include unit tests for conditions, exemptions, dates, and boundary cases.

## Computer vision and measurement
- Use OpenCV and SIFT/ORB meaningfully for image similarity, duplicate-side detection, keypoint matching, perspective alignment, and stitching/flattening only when quality and overlap support it. Avoid blindly stitching unrelated or unreliable images; surface uncertainty and preserve source images.
- Assess glare, blur, reflection, skew, perspective distortion, and readability. Give actionable re-capture guidance.
- Explore native ARCore/ARKit measurement if feasible for the mobile app. Do not pretend a web browser has native AR support. Provide a transparent manual/reference-object fallback (such as a coin) when native measurement is unavailable.
- Uncalibrated visual size estimates must not be treated as legally reliable font-size/label-height evidence. Clearly state assumptions, calibration needs, uncertainty, and whether the measurement is only indicative.

## Compliance reports
Create a professional, formal, structured PDF report with a preview and download action. Include as applicable:
- unique report/scan ID, date/time, product/category and analysis version;
- overall status with clear caveat that this is a prototype analysis, not an official government certificate or notice;
- applicable checks and outcomes (pass, confirmed violation, unresolved, not applicable);
- exact rule/sub-rule/clause and source for each finding;
- extracted values, expected requirements, evidence images/crops, confidence, and reasoning;
- all violations, unresolved items, limitations, corrective actions, and human-review notes;
- traceable link to the persisted scan and source images.
Inspect generated PDF rendering and pagination. Avoid clipping, illegible text, missing images, and unsupported legal claims.

## Label generator: major product capability
Make the generator genuinely useful, not a text-only mockup.
- Start from an existing scan when possible. Reuse its images, extracted fields, category, package-side grouping, dimensions, and evidence instead of asking the user to start over.
- Permit an optional reference image for theme/design guidance.
- Infer likely sides and dimensions from evidence only when reliable. Ask focused follow-up questions for uncertain side count, physical dimensions, missing values, or print requirements. After the user answers, continue and ask another question only if a material ambiguity remains.
- Preserve the original visual identity as far as possible: brand theme, colours, typography, logo, product photography, barcodes, and non-violating content. Change only what is needed to address identified issues. Never fabricate a logo, barcode, certification mark, manufacturer details, MRP, net quantity, batch/date values, or other legally sensitive facts. Use explicit placeholders and ask the user when required values are unknown.
- Produce editable vector artwork (SVG or an equivalent editable format) and a print-oriented PDF with separate package-side layouts and exact physical dimensions. Handle margins, safe areas, bleed, text legibility, and colour assumptions where supported. Do not claim production/print readiness without the relevant printer specifications.
- Validate the generated artwork through the same applicable rule engine. Show remaining unresolved fields and compliance issues; do not silently claim the draft is compliant.
- Provide a useful preview, side switching, editing of confirmed values, and downloadable artifacts. Ensure SVG is valid/sanitized and export is not just a raster image with an SVG extension.
- Use a clear structured data contract between backend and frontend. Fix any mismatch between generated SVG, side metadata, and UI expectations.

## UI/UX quality
Review the existing Flutter UI and redesign where useful. Aim for a modern, minimal, attractive, professional, accessible, responsive interface with clear information hierarchy and consistent components across roles. Use purposeful status colours: red for evidence-backed violations, amber for unresolved/warnings, and neutral/green for appropriate statuses. Include useful empty, loading, error, retry, and success states. Do not sacrifice correctness or accessibility for visual effects. Avoid dead buttons, misleading charts, placeholder copy, inconsistent navigation, and screens that look complete but do nothing.

## Demo payment and security
- Any manufacturer fine/payment feature must be a clearly simulated demo gateway only. Never initiate real transactions or claim integration with BharatKosh or a government payment system unless genuinely implemented and authorized.
- Keep API keys and secrets in environment configuration. Remove hard-coded credentials and rotate/revoke exposed keys where appropriate if possible; document the required action rather than printing secrets.
- Preserve easy demo access. Do not introduce a production authentication redesign that blocks jury testing. Clearly separate demo mode from future production requirements, including proper authentication, authorization, auditability, privacy, data retention, and security controls.

## Testing and autonomous debugging
Build and use a representative test corpus and manifest. Use controlled synthetic fixtures for known conditions and publicly available example package images where appropriate; do not assume an image found online is legally compliant. Record source/licensing where relevant and expected outcomes.
Test the end-to-end pipeline:
- readable compliant examples, known missing/incorrect declarations, unclear/low-confidence fields;
- multiple package categories and category-specific applicability/exemptions;
- blur, glare, reflection, skew, rotated/cropped images;
- duplicate photos of the same side and distinct sides;
- user-provided clarification/crop and re-analysis;
- persistence and history consistency;
- report content and PDF rendering;
- generated label structure, dimensions, SVG validity, PDF export, and post-generation rule checks;
- manufacturer/inspector/admin workflows and escalation;
- frontend/backend API contract and error handling.
Run backend tests, formatting/lint/type checks, frontend checks/build, and end-to-end tests where the environment supports them. Fix root causes and rerun failing tests. Never fabricate test results or mark an unsupported check as passed. If dependencies, devices, network access, credentials, or compute are unavailable, implement a safe fallback and clearly document what could not be verified. Do not download massive models or exceed free-tier constraints without assessing impact.

## Documentation, deployment, and completion
Update README and deployment/configuration docs to reflect actual implementation, not aspirations. Document environment variables without secrets, local run/test/build steps, Vercel/Render setup, storage persistence limitations, provider choices, resource requirements, demo-vs-production boundaries, legal/human-review limitations, and known gaps. Add a rule-source/coverage document and testing instructions. Do not claim native AR, local OCR, official integration, or print readiness unless verified.

Work in priority order:
1. baseline and end-to-end correctness;
2. core scan/evidence/clarification/persistence;
3. legal rule engine and truthful verdicts;
4. report/PDF;
5. useful label generation and export;
6. role workflows and dashboard consistency;
7. UI polish, docs, deployment hardening, and broader tests.

At completion, provide a concise summary of:
- major implemented features;
- important bugs and root causes fixed;
- actual commands run and their real results;
- artifacts/docs created;
- exact local run/build/deployment steps and environment variables;
- known limitations, anything not verified, and the next highest-priority work.
Do not say “everything is complete” if meaningful tests or legal validation remain outstanding.
