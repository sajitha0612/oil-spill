# Data Schema — Oil Spill Detection & AIS Vessel Attribution

This document defines every data structure used inside the pipeline — inputs to each module, internal working data, and outputs. It is the third pillar alongside `PROJECT_BRIEF.md` and `API_CONTRACT.md`. **All output field names and shapes here match `API_CONTRACT.md` exactly** — this document exists to define what feeds INTO those outputs, and to justify which parameters we're actually using versus explicitly excluding, given a ~2-day build window.

---

## Part A: Critical Parameter Review (read this first)

Oil spill detection science pulls in a lot of possible inputs — full current fields, wave spectra, sea surface temperature, salinity, dual/quad polarization, slick thickness, weathering chemistry. **Almost none of this is necessary or achievable for a 2-day hackathon build**, and including it would be false precision, not real signal. Below is the honest cut: what stays, what's dropped, and why.

### For DETECTION (oil slick vs. algal bloom / look-alike)

| Parameter | Include? | Why |
|---|---|---|
| **Backscatter contrast** (dB drop of slick vs. surrounding water) | Include | This is the fundamental physical signal SAR detection is based on — oil dampens capillary waves, lowering backscatter. Non-negotiable, this is the core detection signal. |
| **Shape geometry** (area, perimeter, elongation ratio) | Include | Oil slicks from vessels are frequently linear/elongated (a ship's wake trail); biogenic slicks and low-wind zones tend to be more irregular or diffuse. Cheap to compute, genuinely discriminative. |
| **Edge sharpness / boundary irregularity** | Include | Real oil slicks tend to have sharper, more defined edges than natural films or wind-shadow zones, which fade gradually. Directly computable from the segmentation mask contour. |
| **Texture homogeneity** (variance within the detected patch) | Include | Oil slicks are often more visually uniform inside their boundary; biogenic look-alikes are patchier. Cheap statistical feature (standard deviation of pixel intensity within mask). |
| **Wind speed at acquisition time** | Include, but simplified | Critical gatekeeper, not a fine-grained feature. Detection is only physically valid in a roughly 1.5–10 m/s wind window — outside that, oil is invisible (too calm) or washed out (too rough). We use ONE wind speed value per scene (from public reanalysis data, e.g. ERA5/NOAA point value at scene center/time) — not a full wind field — just to flag "this image is in a valid detection window" and as one input feature to the classifier. |
| **Dual-polarization (VV+VH)** | Exclude | Genuinely improves look-alike discrimination in the literature, but adds real preprocessing complexity and dataset availability constraints. Single VV polarization (the standard, freely available mode) is sufficient for a defensible prototype. State as future improvement. |
| **Slick thickness / oil age proxies** | Exclude | Scientifically unresolved even in production systems (already excluded in Project Brief). Not attempted. |
| **Sea surface temperature, salinity** | Exclude | Marginal-value inputs for detection specifically (more relevant to weathering/chemistry modeling, which we're not doing). Would add data-sourcing overhead for no meaningful accuracy gain in our timeframe. |
| **Multi-temporal comparison** (same location, prior/later passes) | Exclude | Valuable in production (algae blooms persist differently than oil over time) but requires multiple time-separated images of the same location, which our archival single-scene approach doesn't support. Flag as future work. |

**Bottom line for detection:** four real, computable signals — **backscatter contrast, shape geometry, edge sharpness, texture homogeneity** — plus **one gatekeeper value, wind speed** — are what the model/classifier actually uses. Everything else is future-scope, not silently dropped but explicitly named as out of scope (consistent with `PROJECT_BRIEF.md` Section 6).

### For DRIFT/HINDCAST

| Parameter | Include? | Why |
|---|---|---|
| **Surface current speed + direction** | Include | Primary driver of slick transport. Required, non-negotiable for OpenDrift to function at all. |
| **Wind speed + direction** | Include | Needed for windage (wind-driven surface drift component) — OpenDrift's standard oil module uses this directly. |
| **Detection point + timestamp** | Include | The starting point for the simulation — this is just our own detection output. |
| **Stokes drift / wave-driven transport** | Exclude | Refines accuracy but is a secondary correction on top of current+wind. OpenDrift can run a basic simulation without it. Adding it means sourcing wave spectra data, real added complexity for marginal gain in a prototype. |
| **Water temperature, salinity, density stratification** | Exclude | These affect oil weathering (evaporation, emulsification) which we're explicitly not modeling (no age estimation, per Project Brief). Not needed for basic transport simulation. |
| **Tidal currents specifically** | Exclude | Regional current datasets (Copernicus) already include net currents; separating tidal component out is unnecessary complexity for our purposes. |

**Bottom line for drift:** just **current (speed+direction) and wind (speed+direction)**, at the detection point and time, run through OpenDrift's basic ocean-drift module. This is genuinely sufficient for a defensible backward/forward simulation.

### For AIS SCORING

| Parameter | Include? | Why |
|---|---|---|
| **Vessel position (lat/lon) + timestamp** | Include | Core requirement — this is what "proximity" and "trajectory" are computed from. |
| **Vessel speed + course/heading** | Include | Needed to compute trajectory alignment (is the vessel's path consistent with passing through the origin area). |
| **AIS signal continuity** (gaps in reporting) | Include | This is your "dark vessel" / anomaly flag — directly computable by looking for time gaps between consecutive AIS pings for the same vessel ID. |
| **Vessel type/size** | Exclude for scoring, Include for display only | Interesting context for a human reviewer (e.g., tanker vs. fishing boat) but not something we're scoring on — including it as a scoring factor would need domain calibration we don't have time for. Show it in the UI as metadata, don't weight it. |
| **Vessel cargo/manifest data** | Exclude | Not available in standard AIS broadcast data, would require a separate registry lookup — out of scope entirely. |
| **Historical violation records** | Exclude | Would meaningfully improve real-world scoring (repeat offenders) but no accessible dataset exists for this in our timeframe. Worth naming as a future enhancement in the pitch. |

**Bottom line for AIS scoring:** **position, timestamp, speed, heading, and signal-gap detection** — five fields, all standard AIS broadcast fields, nothing exotic needed.

---

## Part B: Input Data Schemas

### B.1 SAR Scene (input to Detection module)

```json
{
  "scene_id": "S1A_IW_GRDH_chennai_20170128",
  "acquisition_time": "2017-01-28T05:42:00Z",
  "polarization": "VV",
  "mode": "IW",
  "image_path": "/data/sar-images/chennai-2017-raw.tif",
  "bounding_box": {
    "type": "Polygon",
    "coordinates": [[[80.10, 12.90], [80.45, 12.90], [80.45, 13.20], [80.10, 13.20], [80.10, 12.90]]]
  },
  "wind_speed_ms": 4.8,
  "wind_source": "ERA5 reanalysis, point value at scene center/time"
}
```

### B.2 Ocean/Wind Data Record (input to Drift module)

Kept minimal — one representative value set per simulation run, not a full gridded field, for hackathon scope.

```json
{
  "region": "Bay of Bengal - Chennai coastal",
  "date_range": { "start": "2017-01-27T00:00:00Z", "end": "2017-01-29T00:00:00Z" },
  "source": "Copernicus Marine Service (historical, pre-downloaded NetCDF)",
  "current_speed_ms": 0.35,
  "current_direction_deg": 145,
  "wind_speed_ms": 4.8,
  "wind_direction_deg": 60
}
```

*Note: OpenDrift itself consumes the raw NetCDF file directly (gridded, time-varying) — the simplified record above is for display purposes in the UI ("conditions used for this simulation"). The four numeric fields (`current_speed_ms`, `current_direction_deg`, `wind_speed_ms`, `wind_direction_deg`) plus `source` are surfaced as-is via `drift.conditions` in API_CONTRACT.md's `GET /incidents/:id` response — no separate endpoint.*

### B.3 AIS Raw Record (input to AIS Scoring module)

```json
{
  "vessel_id": "IMO9234567",
  "vessel_name": "MV Example Trader",
  "vessel_type": "Cargo",
  "timestamp": "2017-01-27T19:10:00Z",
  "position": [80.24, 13.11],
  "speed_knots": 12.4,
  "heading_deg": 210
}
```

A full AIS dataset is a time-series of these records per vessel; the scoring module groups by `vessel_id` and sorts by `timestamp` to reconstruct each vessel's track.

---

## Part C: Internal Processing Schemas

### C.1 Detection Feature Set (internal, feeds the classifier)

```json
{
  "backscatter_contrast_db": -8.4,
  "area_km2": 4.2,
  "perimeter_km": 9.8,
  "elongation_ratio": 3.1,
  "edge_irregularity_index": 0.22,
  "texture_variance": 0.15,
  "wind_speed_ms": 4.8,
  "wind_in_valid_range": true
}
```

This is what the classifier actually consumes to decide `oil_spill` vs. `look_alike` vs. `uncertain`. Only fields from Part A's "include" list appear here — nothing else feeds the decision.

### C.2 Drift Simulation Parameters (internal, feeds OpenDrift)

```json
{
  "start_position": [80.295, 13.043],
  "start_time": "2017-01-28T05:42:00Z",
  "simulation_mode": "backward",
  "duration_hours": 144,
  "current_data_path": "/data/ocean-currents/chennai-jan2017.nc",
  "wind_data_path": "/data/ocean-currents/chennai-jan2017-wind.nc",
  "particle_count": 1000
}
```

`duration_hours: 144` = 6 days, matching the Sentinel-1 revisit gap we scoped around — this is the maximum realistic backward window given detection latency.

### C.3 AIS Scoring Feature Set (internal, per candidate vessel)

```json
{
  "vessel_id": "IMO9234567",
  "distance_to_origin_km": 6.2,
  "time_delta_hours": 1.3,
  "trajectory_alignment_score": 0.75,
  "ais_gap_detected": true,
  "gap_duration_minutes": 150
}
```

This feeds directly into the `sub_scores` object in the API contract's output — `proximity` derives from `distance_to_origin_km`, `trajectory` from `trajectory_alignment_score`, `anomaly` from `ais_gap_detected`/`gap_duration_minutes`.

---

## Part D: Output Schemas (reference only — see API_CONTRACT.md for full detail)

Output shapes are fully defined in `API_CONTRACT.md` and are not repeated in full here to avoid duplication/drift between documents. Summary of what each internal schema above maps to:

| Internal schema | Maps to API contract field |
|---|---|
| Detection Feature Set (C.1) + classifier output | `detection.{confidence, area_km2, perimeter_km, elongation_ratio, classification}` |
| Drift Simulation output (particle trajectories) | `drift.{backward_path, forward_path, origin_estimate}` |
| Ocean/Wind Data Record (B.2), passed through as-is | `drift.conditions` |
| AIS Scoring Feature Set (C.3), aggregated per vessel | `suspects[].{composite_score, sub_scores, flags, track}` |

**Consistency rule:** if a field needs to change in either document, update both in the same commit. `API_CONTRACT.md` is the external-facing contract (frontend depends on it); this document is the internal justification for where those values come from.

---

## Part E: Composite Scoring Formula (AIS attribution)

Explicit, so it's defensible in Q&A rather than a black box:

```
composite_score = (0.40 × proximity_score) + (0.35 × trajectory_score) + (0.25 × anomaly_score)
```

- `proximity_score` = normalized inverse of `distance_to_origin_km` (closer = higher, capped at 0 past 30 km)
- `trajectory_score` = `trajectory_alignment_score` from C.3, directly (already 0–1 normalized)
- `anomaly_score` = 1.0 if `ais_gap_detected` with `gap_duration_minutes` > 60, scaled down for shorter/no gaps

These weights are a starting judgment call, not derived from data (state this plainly if asked) — they can be tuned, but the formula itself is fully transparent and explainable, which matters more than the specific weights being "optimal."
