"""Stub route for the drift/hindcast module. Implemented in build order step 3.

NOTE: this request shape is a placeholder assumption for the internal
node-api <-> python-service interface (see the same note in detection.py).
Modeled on DATA_SCHEMA.md's Drift Simulation Parameters schema (Part C.2).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class DriftSimulationRequest(BaseModel):
    start_position: list[float]  # [lng, lat], GeoJSON order per API_CONTRACT.md
    start_time: str
    simulation_mode: str  # "backward" | "forward"
    duration_hours: int
    current_data_path: str
    wind_data_path: str
    particle_count: int


@router.post("/drift")
def run_drift(payload: DriftSimulationRequest):
    # TODO (build order step 3): OpenDrift backward + forward simulation,
    # per DATA_SCHEMA.md Part C.2. Output maps to drift.{backward_path,
    # forward_path, origin_estimate} in API_CONTRACT.md.
    raise HTTPException(
        status_code=501,
        detail="drift module not implemented yet (build order step 3)",
    )
