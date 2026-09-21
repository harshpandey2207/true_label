from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.scan_routes import router as scan_router

app = FastAPI(title="True Label Legal Metrology API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "service": "True Label Legal Metrology AI Engine",
        "docs": "/docs"
    }

# Mount the routes with a clean prefix
app.include_router(scan_router, prefix="/scan", tags=["Scan"])