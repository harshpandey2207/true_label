# Deployment and operational notes

## Environment variables

| Variable | Required | Meaning |
| --- | --- | --- |
| `DATABASE_URL` | No for local demo | SQLAlchemy URL. Defaults to `sqlite:///./metrology.db`. Use managed PostgreSQL for durable deployments. |
| `AUTH_SECRET_KEY` | Yes outside a disposable demo | Signs sessions. When unset, sessions expire after a process restart because an in-memory secret is used. |
| `TRUE_LABEL_ENABLE_LOCAL_OCR` | No | Set to `1` only in an environment where the optional PaddleOCR runtime and model assets have been intentionally provisioned. Default is disabled; no image is sent to an OCR SaaS. |
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

Optional local OCR is intentionally separate because it has substantial model/runtime cost:

```powershell
python -m pip install -r backend\requirements-paddle.txt
$env:TRUE_LABEL_ENABLE_LOCAL_OCR = '1'
```

## Render and Vercel

- The committed Dockerfile installs only `backend/requirements.txt`; it is compatible with the deterministic local SVG renderer and the no-provider OCR fallback.
- Render free-tier local disk is ephemeral. The demo persists uploads in its database to make a clarification scan coherent, but durable deployments must use private object storage, retention controls, and a managed PostgreSQL database. Do not rely on a container-local SQLite file for history or evidence.
- Vercel serves the Flutter web build from `frontend/build/web`. Build the frontend before deployment and provide the deployed backend URL through the frontend environment configuration.
- Label PDF exports are generated locally from supplied draft data and use panel dimensions in millimetres. They are not preflighted print files: production print workflows must validate bleed, trim marks, ICC colour profile, fonts, and printer imposition.
- Restrict CORS to the Vercel origin and set a persistent `AUTH_SECRET_KEY` before any non-demo deployment. The current wide-open CORS is acceptable only for local jury demonstration convenience.

### Existing service update procedure

This repository is configured to update the existing Render service `truelabel-backend` and the existing Vercel static deployment; it does not define duplicate services. Commit only the intended source changes on the production branch used by the connected projects, push through the normal repository workflow, and let the existing integrations deploy. Confirm the Render service retains its current database, secrets, plan and storage settings. Confirm Vercel's build output is regenerated from `frontend/build/web` (or use the existing project build command) and that the generated `assets/.env` points to the Render origin.

The production update has been successfully committed, pushed to `main`, and deployed to both services:
- Vercel frontend: `https://true-label-jade.vercel.app` (served from `frontend/build/web` with `API_BASE_URL=https://true-label-backend.onrender.com`).
- Render backend: `https://true-label-backend.onrender.com` (running version `1.3.0` with 29 active endpoints and universal PostgreSQL column compatibility).
- Live verification: Health check, representative image scanning, clarification upload, scan history, PDF report generation/download, label drafting/PDF download, and inspector escalation/admin review workflows were executed against the live endpoints and verified passing.

## Production boundary

This prototype has no official government integration, payment gateway, native AR measurement, certified rules service, document retention policy, or production-grade authorization design. It must not be presented as a government notice, certificate, fine, or payment system.
