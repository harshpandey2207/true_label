# True Label

True Label is a prototype for screening package-label images and preparing editable label drafts. It is a decision-support demo, not a legal compliance certificate, regulator portal, or notice/payment system.

## Live Deployments

- **Web Application (Vercel)**: [https://web-ten-puce-86.vercel.app/](https://web-ten-puce-86.vercel.app/)
- **API Backend (Render)**: [https://true-label-backend.onrender.com/](https://true-label-backend.onrender.com/) (Interactive API docs at `/docs`)

## What works in this prototype

- Flutter app for manufacturer, inspector, and admin demo screens.
- FastAPI backend with SQLite by default and optional PostgreSQL via `DATABASE_URL`.
- Package-image analysis keeps uploads as scan evidence, checks basic resolution/glare/blur signals, and can use optional local PaddleOCR. Local OCR is deliberately disabled by default in the lightweight deployment; without it, the product returns an explicit **unresolved** result and asks for a clearer crop or manual confirmation. Images are never sent to an OCR SaaS by this codebase.
- Rule checks use a small seeded prototype catalogue. They do not cover all product-specific rules, exemptions, amendments, or packaging conditions.
- Label Draft Studio creates editable SVG drafts and a companion vector/text PDF export with a local deterministic template renderer. The PDF uses each declared panel's millimetre dimensions, while the SVG remains the editable source. Category fields, supplied declarations, extra copy, package shape, dimensions, and palette cues from reference images inform the draft. Uploaded filenames such as `front.jpg` or `back.jpg` name panels. The renderer does not reproduce or invent logos, photos, barcodes, certification marks, or legally sensitive values.
- Unit sale price is an optional input when applicable; the prototype neither assumes it applies to every package nor calculates it from MRP.
- Manufacturer-entered text is inserted as text; the renderer does not infer or recreate logos, photos, barcodes, or original package artwork. It adds placeholders when the brief requests artwork.
- Uncalibrated image measurements are explicitly indicative only and are not used to determine scan status. A scan returns `PASS`, `CONFIRMED_VIOLATION`, `UNRESOLVED`, or `NOT_APPLICABLE` per rule; missing OCR evidence is unresolved, not a violation. Generated drafts and automated screening results need human review before production or business decisions.

## Open-source-first stack

The app uses Flutter/Dart, FastAPI/Python, SQLAlchemy, SQLite or PostgreSQL, Pillow, optional PaddleOCR, and SVG. Label drafting does not require Gemini, Groq, Together AI, or another hosted model API. A hosting provider may still be used to publish the app; hosting is separate from the application stack and can be replaced with self-hosted infrastructure.

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

The API is available at `http://127.0.0.1:8000`; interactive API docs are at `/docs`. Set `TRUE_LABEL_ENABLE_LOCAL_OCR=1` only after intentionally installing the optional PaddleOCR runtime (`backend/requirements-paddle.txt`); it may download model weights and is not suited to the free-tier container by default. Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL to use PostgreSQL; otherwise the app creates `metrology.db` in the working directory. Startup creates missing tables and safely adds a small set of compatible SQLite columns without dropping data. See [deployment notes](docs/DEPLOYMENT.md) and [rule coverage](docs/RULE_COVERAGE.md).

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
