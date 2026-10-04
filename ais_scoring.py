"""Stub route for the AIS scoring module. Implemented in build order step 4.

NOTE: this request shape is a placeholder assumption for the internal
node-api <-> python-service interface (see the same note in detection.py).
Modeled on DATA_SCHEMA.md's AIS Raw Record schema (Part B.3).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AISRecord(BaseModel):
    vessel_id: str
    vessel_name: str
    vessel_type: str | None = None
    timestamp: str
    position: list[float]  # [lng, lat]
    speed_knots: float
    heading_deg: float


class AISScoringRequest(BaseModel):
    origin_position: list[float]  # [lng, lat]
    origin_time_window_start: str
    origin_time_window_end: str
    ais_records: list[AISRecord]


@router.post("/score-ais")
def score_ais(payload: AISScoringRequest):
    # TODO (build order step 4): filter to origin space-time window, compute
    # per-vessel proximity/trajectory/anomaly features (DATA_SCHEMA.md Part
    # C.3), then composite_score via the Part E formula (weights come from
    # app.config.settings, not hardcoded here).
    raise HTTPException(
        status_code=501,
        detail="AIS scoring module not implemented yet (build order step 4)",
    )
