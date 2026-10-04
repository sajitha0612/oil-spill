# API Contract — Oil Spill Detection & AIS Vessel Attribution

This is the single source of truth for every request/response shape between frontend and backend. Both teams must follow this exactly. Any change must be updated here first, then communicated before either side changes code.

**Base URL (local dev):** `http://localhost:5000/api`

**Units convention:**
- Coordinates: `[longitude, latitude]` decimal degrees (GeoJSON standard order — NOT lat/lng)
- Distance: kilometers
- Time: ISO 8601 strings, UTC (e.g., `"2017-08-12T14:30:00Z"`)
- Scores: floats between 0 and 1 (frontend multiplies by 100 for display if needed)
- Area: square kilometers

---

## 1. Get list of available incidents

Used to populate the landing/summary view — pre-loaded demo incidents.

**Request**
```
GET /api/incidents
```

**Response `200`**
```json
{
  "incidents": [
    {
      "id": "chennai-2017",
      "title": "Chennai Coast Oil Spill",
      "date": "2017-01-28",
      "region": "Bay of Bengal, Chennai Coast",
      "thumbnail_url": "/static/thumbnails/chennai-2017.png",
      "status": "analyzed"
    }
  ]
}
```

`status` is one of: `"not_analyzed"`, `"analyzing"`, `"analyzed"`, `"failed"`

---

## 2. Trigger analysis on an incident

This is the "Analyze" button action. Kicks off the full pipeline: detection → hindcast → AIS scoring.

**Request**
```
POST /api/incidents/analyze
Content-Type: application/json

{
  "incident_id": "chennai-2017"
}
```

**Response `202` (analysis started, async)**
```json
{
  "incident_id": "chennai-2017",
  "status": "analyzing",
  "message": "Pipeline started"
}
```

**Frontend behavior:** show loading state with progress steps (`Detecting slick... Calculating drift... Scoring vessels...`). Poll `GET /api/incidents/:id` every 2-3 seconds until `status` becomes `"analyzed"` or `"failed"`, OR use the results endpoint directly if pre-cached (see note at bottom).

---

## 3. Get full incident results

The main data-fetch endpoint. Returns everything needed to render the dashboard in one call.

**Request**
```
GET /api/incidents/:id
```

**Response `200`**
```json
{
  "id": "chennai-2017",
  "status": "analyzed",
  "title": "Chennai Coast Oil Spill",
  "date": "2017-01-28",

  "detection": {
    "detected": true,
    "confidence": 0.87,
    "detected_at": "2017-01-28T05:42:00Z",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[80.28, 13.05], [80.31, 13.06], [80.30, 13.02], [80.28, 13.05]]]
    },
    "centroid": [80.295, 13.043],
    "area_km2": 4.2,
    "perimeter_km": 9.8,
    "elongation_ratio": 3.1,
    "classification": "oil_spill",
    "sar_image_url": "/static/sar/chennai-2017-raw.png",
    "mask_overlay_url": "/static/sar/chennai-2017-mask.png"
  },

  "drift": {
    "origin_estimate": {
      "time_window_start": "2017-01-27T18:00:00Z",
      "time_window_end": "2017-01-27T22:00:00Z",
      "probability_region": {
        "type": "Polygon",
        "coordinates": [[[80.25, 13.10], [80.27, 13.11], [80.26, 13.08], [80.25, 13.10]]]
      },
      "centroid": [80.26, 13.095]
    },
    "conditions": {
      "current_speed_ms": 0.35,
      "current_direction_deg": 145,
      "wind_speed_ms": 4.8,
      "wind_direction_deg": 60,
      "source": "Copernicus Marine Service (historical, pre-downloaded NetCDF)"
    },
    "backward_path": [
      { "time": "2017-01-27T18:00:00Z", "position": [80.26, 13.095] },
      { "time": "2017-01-27T22:00:00Z", "position": [80.28, 13.06] },
      { "time": "2017-01-28T05:42:00Z", "position": [80.295, 13.043] }
    ],
    "forward_path": [
      { "time": "2017-01-28T05:42:00Z", "position": [80.295, 13.043] },
      { "time": "2017-01-28T12:00:00Z", "position": [80.31, 13.01] },
      { "time": "2017-01-28T18:00:00Z", "position": [80.33, 12.98] }
    ]
  },

  "suspects": [
    {
      "vessel_id": "IMO9234567",
      "vessel_name": "MV Example Trader",
      "composite_score": 0.78,
      "sub_scores": {
        "proximity": 0.82,
        "trajectory": 0.75,
        "anomaly": 0.71
      },
      "flags": ["ais_gap_detected"],
      "ais_gap": {
        "gap_start": "2017-01-27T19:10:00Z",
        "gap_end": "2017-01-27T21:40:00Z"
      },
      "track": [
        { "time": "2017-01-27T17:00:00Z", "position": [80.20, 13.15] },
        { "time": "2017-01-27T19:10:00Z", "position": [80.24, 13.11] },
        { "time": "2017-01-27T21:40:00Z", "position": [80.27, 13.07] }
      ]
    }
  ],

  "ais_coverage_gap_detected": true
}
```

**Field notes:**
- `flags` is an array of strings; possible values: `"ais_gap_detected"`, `"route_deviation"`, `"loitering"`, `"erratic_movement_at_origin_time"` — frontend uses these to show badges on suspect cards
- `"erratic_movement_at_origin_time"` is distinct from `"ais_gap_detected"`: it's for a sudden speed/heading anomaly right at the origin time (e.g. a collision), not a silent AIS gap. A vessel should carry one or the other, not both, for the same event.
- `suspects` array is pre-sorted descending by `composite_score` — frontend should NOT re-sort, just render in order
- `ais_gap` is only present if `"ais_gap_detected"` is in that vessel's `flags`
- If detection finds nothing, `detection.detected` is `false` and `drift`/`suspects` will be `null`
- `drift.conditions` is the single representative current/wind reading used for that simulation run (see DATA_SCHEMA.md Part B.2) — display-only, not a gridded field; `source` is a free-text string for UI attribution, not a machine-readable enum

---

## 4. Get detection detail (for the modal)

Separate endpoint so the full-res SAR image isn't loaded until the user actually opens the detail view.

**Request**
```
GET /api/incidents/:id/detection-detail
```

**Response `200`**
```json
{
  "sar_image_url": "/static/sar/chennai-2017-raw-fullres.png",
  "mask_overlay_url": "/static/sar/chennai-2017-mask-fullres.png",
  "confidence": 0.87,
  "area_km2": 4.2,
  "perimeter_km": 9.8,
  "elongation_ratio": 3.1,
  "look_alike_check": {
    "classification": "oil_spill",
    "look_alike_probability": 0.05
  }
}
```

---

## 5. Error response format (applies to all endpoints)

**Response `4xx` / `5xx`**
```json
{
  "error": true,
  "code": "INCIDENT_NOT_FOUND",
  "message": "No incident found with id 'xyz'"
}
```

Common `code` values: `INCIDENT_NOT_FOUND`, `ANALYSIS_FAILED`, `INVALID_REQUEST`

---

## Data-to-UI mapping (quick reference for frontend)

| API field | Rendered where | Format |
|---|---|---|
| `detection.geometry` | Map — slick polygon overlay | GeoJSON polygon, filled shape |
| `detection.confidence` | Map tooltip / detail modal | Percentage |
| `drift.origin_estimate.probability_region` | Map — shaded ellipse, NOT a pin | GeoJSON polygon, semi-transparent fill |
| `drift.backward_path` | Map — dotted trail | Line, animated by timeline slider |
| `drift.forward_path` | Map — gradient/solid projected path | Line, animated by timeline slider |
| `suspects[].composite_score` | Suspect card — colored bar + % | 0-1 float → percentage; color: red >0.7, amber 0.4-0.7, grey <0.4 |
| `suspects[].sub_scores` | Suspect card — expandable breakdown | Three small bars/values |
| `suspects[].flags` | Suspect card — badge icons | Map flag string → icon + tooltip text |
| `suspects[].track` | Map — vessel path, shown on click | Line, only rendered when that suspect is selected |
| `ais_coverage_gap_detected` | Dashboard banner/notice | Boolean → show/hide "possible dark vessel activity" notice |
| `drift.conditions` | Overview tab — wind compass card | `wind_speed_ms`/`wind_direction_deg` drive a compass pointer; `current_speed_ms`/`current_direction_deg` shown as secondary text |

---

## Notes for demo reliability

Given time constraints, results for pre-loaded demo incidents (`chennai-2017`, etc.) should be **pre-computed and cached** rather than run live during the actual demo. `POST /analyze` can still exist and technically work end-to-end, but for the live pitch, `GET /api/incidents/:id` should return an already-cached result instantly rather than triggering a fresh multi-second pipeline run in front of judges.

---

## Open items to confirm together before building

- [ ] Confirm coordinate order convention (this doc assumes `[lng, lat]` — GeoJSON standard, NOT `[lat, lng]`)
- [ ] Confirm which 2-3 incidents you're pre-loading as demo data
- [ ] Confirm color thresholds for suspect score bands (red/amber/grey cutoffs shown above are a starting suggestion)
- [ ] Decide if `POST /analyze` is sync (waits and returns full result) or async (returns immediately, frontend polls) — this doc assumes async, simpler to do sync if demo-only
