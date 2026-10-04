"""Config over hardcoding: every tunable used by detection/drift/ais_scoring
lives here, sourced from environment variables (.env), per the project's
ground rules. Nothing pipeline-specific should be a magic number in module
code — import `settings` instead.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    port: int = 8000

    # DEMO_MODE: when true, hackathon-only shortcuts (e.g. skipping heavy
    # OpenDrift runs in favor of pre-cached results) are allowed to activate.
    # Mirrors node-api's DEMO_MODE flag; keep both in sync.
    demo_mode: bool = True

    # --- Detection module (DATA_SCHEMA.md Part A / C.1) ---
    sar_data_dir: str = "./data/sar-images"
    # Wind-speed gatekeeper window: outside this range, oil is either invisible
    # (too calm) or washed out (too rough) in SAR imagery.
    wind_speed_valid_min_ms: float = 1.5
    wind_speed_valid_max_ms: float = 10.0

    # --- Drift module (DATA_SCHEMA.md Part A / C.2) ---
    ocean_current_data_dir: str = "./data/ocean-currents"
    # 144h = 6 days, matching the Sentinel-1 revisit gap — the maximum
    # realistic backward hindcast window given detection latency.
    drift_duration_hours: int = 144
    drift_particle_count: int = 1000

    # --- AIS scoring module (DATA_SCHEMA.md Part C.3 / Part E) ---
    ais_data_dir: str = "./data/ais"
    # Composite score weights — DATA_SCHEMA.md Part E. A starting judgment
    # call, not derived from data; tune here, not inline in scoring code.
    proximity_weight: float = 0.40
    trajectory_weight: float = 0.35
    anomaly_weight: float = 0.25
    # proximity_score is a normalized inverse of distance, capped at 0 past this radius.
    proximity_max_distance_km: float = 30.0
    # anomaly_score reaches 1.0 once an AIS gap exceeds this duration.
    anomaly_gap_threshold_minutes: float = 60.0


settings = Settings()
