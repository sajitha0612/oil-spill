from fastapi import FastAPI

from app.config import settings
from app.routers import ais_scoring, detection, drift

app = FastAPI(title="SpillTrace Python Service", version="0.1.0")

app.include_router(detection.router, tags=["detection"])
app.include_router(drift.router, tags=["drift"])
app.include_router(ais_scoring.router, tags=["ais_scoring"])


@app.get("/health")
def health():
    return {"ok": True, "demo_mode": settings.demo_mode}
