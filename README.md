# True Label

True Label is a prototype for screening package-label images and preparing editable label drafts. It is a decision-support demo, not a legal compliance certificate, regulator portal, or notice/payment system.

## What works in this prototype

- Flutter app for manufacturer, inspector, and admin demo screens.
- FastAPI backend with SQLite by default and optional PostgreSQL via `DATABASE_URL`.
- Package-image text recognition with PaddleOCR and image handling with OpenCV. OCR runs in the backend process; image files are not sent to an OCR SaaS.
- Rule checks use a small seeded prototype catalogue. They do not cover all product-specific rules, exemptions, amendments, or packaging conditions.
- Label Draft Studio creates editable SVG drafts with a local template renderer. Category fields, supplied declarations, extra copy, prompt-based colour/style choices, package shape, and aspect ratio inform the draft. Uploaded images are sampled for colour per side, and filenames such as `front.jpg` or `back.jpg` are used to name sides. Without images, choose two, four, or six sides and describe a design brief.
- Unit sale price is an optional input when applicable; the prototype neither assumes it applies to every package nor calculates it from MRP.
- Manufacturer-entered text is inserted as text; the renderer does not infer or recreate logos, photos, barcodes, or original package artwork. It adds placeholders when the brief requests artwork.
- Displayed text-height numbers are rough estimates from fixed, uncalibrated camera geometry and are not used to determine scan status. Generated drafts and automated screening results need human review before production or business decisions.

## Open-source-first stack

The app uses Flutter/Dart, FastAPI/Python, SQLAlchemy, SQLite or PostgreSQL, OpenCV, PaddleOCR, and SVG. Label drafting does not require Gemini, Groq, Together AI, or another hosted model API. A hosting provider may still be used to publish the app; hosting is separate from the application stack and can be replaced with self-hosted infrastructure.

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

The API is available at `http://127.0.0.1:8000`; interactive API docs are at `/docs`. On the first scan, PaddleOCR may need to download its model weights. Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL to use PostgreSQL; otherwise the app creates `metrology.db` in the working directory. Startup creates missing tables and seeds the initial catalogue without dropping existing records.

### Frontend

```bash
cd frontend
flutter pub get
flutter run -d chrome
```

The frontend defaults to `http://127.0.0.1:8000`. Set `API_BASE_URL` in the Flutter `.env` file to point to a separately hosted backend.

## Review before use

Automated text extraction can miss or misread package text. The seeded checks are a prototype and should be checked against the current official rules and the product's category, intended sale, package dimensions, exemptions, and other applicable requirements. The SVG is a design draft: verify every value, final panel layout, artwork, contrast, and print dimensions before use.

Useful official references for maintaining the rule catalogue:

- [Department of Consumer Affairs: Legal Metrology and Packaged Commodities Rules](https://consumeraffairs.gov.in/pages/legal-metrology-act)
- [FSSAI: Labelling and Display Regulations and amendments](https://fssai.gov.in/food-law/regulations/amendments/labelling-display)
