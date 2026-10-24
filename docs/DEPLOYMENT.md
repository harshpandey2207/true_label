# Deployment and operational notes

## Environment variables

| Variable | Required | Meaning |
| --- | --- | --- |
| `DATABASE_URL` | No for local demo | SQLAlchemy URL. Defaults to `sqlite:///./metrology.db`. Use managed PostgreSQL for durable deployments. |
| `AUTH_SECRET_KEY` | Yes outside a disposable demo | Signs sessions. When unset, sessions expire after a process restart because an in-memory secret is used. |
| `TRUE_LABEL_ENABLE_LOCAL_OCR` | No | Installed local OCR is auto-detected when unset. Set to `1` to force enable or `0` to disable. The lightweight deployment omits both optional OCR packages, so it asks for manual confirmation. No image is sent to an OCR SaaS. |
| `TRUE_LABEL_OCR_ENGINE` | No | `rapidocr` (default) or `paddle`. When `paddle` is selected and cannot initialise, RapidOCR is attempted automatically. |
| `TRUE_LABEL_GEMINI_API_KEY` | No | Backend-only key for the explicitly opted-in Gemini label visual-direction feature. Never place it in the Flutter/browser `.env`; it is not returned by the API. With no key, the local vector renderer remains available. |
| `TRUE_LABEL_GEMINI_MODEL` | No | Gemini model identifier for constrained JSON visual-direction output. Defaults to `gemini-3.5-flash-lite`; check Google's current model availability before changing it. |
| `API_BASE_URL` | Frontend deployment | Backend origin compiled into the Flutter web app through `frontend/.env`. The checked-in Flutter fallback targets the existing Render service (`https://true-label-backend.onrender.com`); use `http://127.0.0.1:8000` explicitly in a developer-only `.env` for local work. |

## Local run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.app.main:app --reload

cd frontend
flutter pub get
flutter run -d chrome
```

Optional local OCR is separate from the base container. Install RapidOCR on a workstation and the normal local server command detects it automatically. To force local OCR on explicitly:

```powershell
python -m pip install -r backend\requirements-ocr.txt
$env:TRUE_LABEL_ENABLE_LOCAL_OCR = '1'
# Optional: prefer Paddle first, then fall back to RapidOCR.
# $env:TRUE_LABEL_OCR_ENGINE = 'paddle'
python -m uvicorn backend.app.main:app --reload
```

For a Windows workstation with the optional runtime installed, the repository
also includes `..\run_local_ocr.ps1`. It sets the process-scoped OCR flags and
starts RapidOCR without changing deployment configuration; pass `-Port 8011`
if port 8000 is already in use.

PaddleOCR can still be installed from `backend\requirements-paddle.txt` when its
model assets are available. If both engines are unavailable, scans retain the
image and expose an `UNRESOLVED` result; they never infer a missing declaration
from an empty OCR result.

### Optional AI-assisted label styling

The label renderer remains local and produces the SVG/PDF. To enable its
opt-in visual-direction assistant for a local API process, set the key in that
backend process before launch (PowerShell example):

```powershell
$env:TRUE_LABEL_GEMINI_API_KEY = '<your Google AI Studio key>'
$env:TRUE_LABEL_GEMINI_MODEL = 'gemini-3.5-flash-lite'
python -m uvicorn backend.app.main:app --reload
```

The manufacturer UI checks `/label/design-status` and enables the AI switch
only when the backend reports that a key is configured. A request is sent only
after the manufacturer turns the switch on. The AI prompt includes the
category, package shape, dimensions, design brief and locally sampled HEX
palette. It excludes package photos, product name, OCR text, declaration
values and compliance results. The response is constrained to a palette,
visual style and motif; the local renderer ignores AI-authored copy because
the provider is not asked to generate any. Google's Gemini REST API supports
constrained JSON outputs and the documented `gemini-3.5-flash-lite` model;
provider availability, account access, rate limits and charges remain subject
to Google's current service terms. If the key is absent or a request fails, the
AI option is unavailable or returns a visible error and the deterministic
local renderer remains usable.

## Render and Vercel

- The committed Dockerfile installs only `backend/requirements.txt`; it is compatible with the deterministic local SVG renderer and the no-provider OCR fallback.
- Render free-tier local disk is ephemeral. The demo persists uploads in its database to make a clarification scan coherent, but durable deployments must use private object storage, retention controls, and a managed PostgreSQL database. Do not rely on a container-local SQLite file for history or evidence.
- Vercel serves the Flutter web build from `frontend/build/web`. From the repository root, run `./frontend/build_vercel.ps1` before deployment. It builds the Flutter release bundle and writes the Render origin into the generated `assets/.env`, while leaving `frontend/.env` set up for local development.
- Label PDF exports are generated locally from supplied draft data and use panel dimensions in millimetres. They are not preflighted print files: production print workflows must validate bleed, trim marks, ICC colour profile, fonts, and printer imposition.
- Restrict CORS to the Vercel origin and set a persistent `AUTH_SECRET_KEY` before any non-demo deployment. The current wide-open CORS is acceptable only for local jury demonstration convenience.

### Existing service update procedure

This repository is configured to update the existing Render service `truelabel-backend` and the existing Vercel static deployment; it does not define duplicate services. Commit only the intended source changes on the production branch used by the connected projects, push through the normal repository workflow, and let the existing integrations deploy. Confirm the Render service retains its current database, secrets, plan and storage settings. Confirm Vercel's build output is regenerated from `frontend/build/web` (or use the existing project build command) and that the generated `assets/.env` points to the Render origin.

The production system is fully connected and deployed:
- Vercel frontend: `https://web-ten-puce-86.vercel.app` (served from `frontend/build/web` with `API_BASE_URL=https://true-label-backend.onrender.com`).
- Render backend: `https://true-label-backend.onrender.com` (running version `1.3.0` with 29 active endpoints and connection resilience).
- Managed Database: Permanent cloud PostgreSQL on Supabase (`aws-0-ap-south-1.pooler.supabase.com` session pooler) replaces Render's expiring trial database.
- Live verification: Health check confirms PostgreSQL connection to Supabase pooler; live end-to-end tests (auth, scan, history, clarification, report download, label draft, escalation) pass completely.

## Production boundary

This prototype has no official government integration, payment gateway, native AR measurement, certified rules service, document retention policy, or production-grade authorization design. It must not be presented as a government notice, certificate, fine, or payment system.
