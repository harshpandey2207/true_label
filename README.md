# True Label

True Label is a prototype for screening package-label images and preparing editable label drafts. It is a decision-support demo, not a legal compliance certificate, regulator portal, or notice/payment system.

## Live Deployments

- **Web Application (Vercel)**: [https://web-ten-puce-86.vercel.app/](https://web-ten-puce-86.vercel.app/)
- **API Backend (Render)**: [https://true-label-backend.onrender.com/](https://true-label-backend.onrender.com/) (Interactive API docs at `/docs`)

## What works in this prototype

- Flutter app for manufacturer, inspector, and admin demo screens.
- FastAPI backend with SQLite by default and optional PostgreSQL via `DATABASE_URL`.
- Package-image analysis keeps uploads as scan evidence, checks basic resolution/glare/blur signals, and uses local RapidOCR automatically when its optional runtime is installed (PaddleOCR is also supported). The lightweight deployment does not install an OCR runtime, so it returns an explicit **unresolved** result and asks for manual confirmation. Images are never sent to an OCR SaaS by this codebase.
- Rule checks use a small seeded prototype catalogue. They do not cover all product-specific rules, exemptions, amendments, or packaging conditions.
- Label Draft Studio creates editable SVG drafts and one exact-physical-size PDF page per package side. Front panels give supplied MRP and net quantity stronger prominence; category and design brief guide locally rendered visual styling, while reference photos are used locally for colour and side-name cues. The optional Gemini design assistant can suggest only a constrained style, motif and palette; it cannot write printed copy. When explicitly enabled, the backend sends only category, shape, dimensions, the design brief and locally sampled colour values. Package photos, product name, OCR text, declaration values and compliance results remain local. Without a backend key, the editable local renderer works without AI. Neither path invents legal declarations, logos, barcodes or certifications. A 200 x 300 mm label is naturally close to A4 proportions, but its PDF media box remains 200 x 300 mm; choose actual size / 100% when printing rather than fit-to-page.
- Unit sale price is an optional input when applicable; the prototype neither assumes it applies to every package nor calculates it from MRP.
- Manufacturer-entered text is inserted as editable text; the renderer does not infer or recreate logos, photos, barcodes, or original package artwork. Manufacturers should supply approved identity artwork separately and confirm all label copy and print specifications.
- Uncalibrated image measurements are explicitly indicative only and are not used to determine scan status. A scan returns `PASS`, `CONFIRMED_VIOLATION`, `UNRESOLVED`, or `NOT_APPLICABLE` per rule; missing OCR evidence is unresolved, not a violation. Generated drafts and automated screening results need human review before production or business decisions.

## Open-source-first stack

The app uses Flutter/Dart, FastAPI/Python, SQLAlchemy, SQLite or PostgreSQL, Pillow, optional PaddleOCR, and SVG. Label drafting works without a hosted model; Gemini visual direction is opt-in and is limited to validated renderer settings, not copy or compliance decisions. A hosting provider may still be used to publish the app; hosting is separate from the application stack and can be replaced with self-hosted infrastructure.

## Run locally

### Backend

From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive API docs are at `/docs`. For local text extraction, install `backend/requirements-ocr.txt`; installed RapidOCR is detected and enabled automatically. Set `TRUE_LABEL_OCR_ENGINE=paddle` to prefer PaddleOCR (RapidOCR remains the fallback), or explicitly set `TRUE_LABEL_ENABLE_LOCAL_OCR=0` to disable local OCR. Without an installed runtime, the image is retained as evidence and the result remains unresolved rather than being treated as a missing declaration. Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL to use PostgreSQL; otherwise the app creates `metrology.db` in the working directory. Startup creates missing tables and safely adds a small set of compatible SQLite columns without dropping data. See [deployment notes](docs/DEPLOYMENT.md) and [rule coverage](docs/RULE_COVERAGE.md).

Optional AI design direction requires a Google AI Studio API key configured only in the backend process as `TRUE_LABEL_GEMINI_API_KEY`; `TRUE_LABEL_GEMINI_MODEL` can select another supported model and defaults to `gemini-3.5-flash-lite`. Do not put this key in Flutter's `.env` or browser bundle. The UI displays whether the backend is configured, and AI use is opt-in per label draft. The provider uses Gemini's structured JSON output to choose a small set of safe visual tokens, then the local renderer creates the actual editable SVG and dimensioned PDF. This is AI-assisted styling—not image generation, automated label-copy authoring, or regulatory approval.

On Windows, use `.\run_local_ocr.ps1` to start the API with the repository's Python environment and RapidOCR. Use `.\run_local_ocr.ps1 -Port 8011` when another local API already owns port 8000. A normal launch also detects OCR when run from an environment that has the optional runtime installed. This does not change the lightweight deployment's dependencies or send images to a hosted OCR service.

### Frontend

```bash
cd frontend
flutter pub get
flutter run -d chrome
```

The frontend defaults to `http://127.0.0.1:8000`. Set `API_BASE_URL` in the Flutter `.env` file to point to a separately hosted backend.

## Review before use

Automated text extraction can miss or misread package text. The seeded checks are a prototype and should be checked against the current official rules and the product's category, intended sale, package dimensions, exemptions, and other applicable requirements. SVG and PDF outputs are design drafts: verify every value, final panel layout, artwork, trim, bleed, colour profile, contrast, printer setup, and print dimensions before use.

Useful official references for maintaining the rule catalogue:

- [Department of Consumer Affairs: Legal Metrology and Packaged Commodities Rules](https://consumeraffairs.gov.in/pages/legal-metrology-act)
- [FSSAI: Labelling and Display Regulations and amendments](https://fssai.gov.in/food-law/regulations/amendments/labelling-display)
