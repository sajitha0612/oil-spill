"""Stub route for the detection module. Implemented in build order step 2.

NOTE: this request shape is a placeholder assumption for the internal
node-api <-> python-service interface, not something either API_CONTRACT.md
(external contract only) or DATA_SCHEMA.md (internal data, not internal
routes) actually specifies. Modeled loosely on DATA_SCHEMA.md's SAR Scene
schema (Part B.1) — confirm/adjust before step 2 implements the real logic.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class SARSceneRequest(BaseModel):
    scene_id: str
    acquisition_time: str
    polarization: str = "VV"
    mode: str = "IW"
    image_path: str
    bounding_box: dict
    wind_speed_ms: float
    wind_source: str | None = None


@router.post("/detect")
def detect(payload: SARSceneRequest):
    # TODO (build order step 2): calibration -> speckle filtering -> segmentation
    # -> geometry/confidence output, per DATA_SCHEMA.md Part C.1.
    raise HTTPException(
        status_code=501,
        detail="detection module not implemented yet (build order step 2)",
    )
