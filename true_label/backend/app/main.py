from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.scan_routes import router as scan_router

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
        "service": "True Label Legal Metrology AI Engine",
        "version": "1.2.0",
        "docs": "/docs"
    }

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "HEALTHY"}

# Mount the routes with a clean prefix
app.include_router(scan_router, prefix="/scan", tags=["Scan"])