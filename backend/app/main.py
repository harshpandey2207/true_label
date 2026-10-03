from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.scan_routes import router as scan_router
from backend.app.api.label_routes import router as label_router
from backend.app.api.auth_routes import router as auth_router
from backend.app.api.workspace_routes import router as workspace_router


# Database imports
from backend.app.db.database import SessionLocal, engine
from backend.app.db.init_db import init_db

app = FastAPI(title="True Label Legal Metrology API")

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    init_db(db)
    db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {
        "status": "ONLINE",
        "service": "True Label Package Label Screening API",
        "version": "1.2.0",
        "docs": "/docs"
    }

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "HEALTHY"}

# Mount the routes with a clean prefix
app.include_router(scan_router, prefix="/scan", tags=["Scan"])
app.include_router(label_router, prefix="/label", tags=["Label Generator"])
app.include_router(auth_router, prefix="/auth", tags=["Accounts"])
app.include_router(workspace_router, prefix="/workspace", tags=["Workspace"])

