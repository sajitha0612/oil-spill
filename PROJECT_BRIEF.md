# Project Brief — Oil Spill Detection & AIS Vessel Attribution

## 1. Problem Statement (Original)

Marine oil spills inflict significant damage on marine ecosystems and often remain un-attributable to the vessel responsible. Leveraging satellite imagery (SAR/EO) along with AIS (Automatic Identification System) vessel-tracking data can enable both detection of oil spills and identification of the vessel responsible.

The core challenge: design an intelligent automated pipeline to (a) detect and characterize oil spills from satellite imagery, (b) trace the slick backward to its origin point/time and predict its future drift using oceanographic/meteorological data, and (c) attribute the spill to a vessel by reconstructing historical AIS traffic around the origin window and scoring suspect vessels by proximity, trajectory, and behavioral anomalies.

## 2. Real-World Purpose

Oil spill accountability is currently a weak link, especially in India. Europe's CleanSeaNet system proves this kind of detection + attribution pipeline works operationally, but it relies on trained human analysts and is EU-only. India has the raw ingredients — SAR satellites (EOS-4, RISAT), a GIS platform (Bhuvan), and an emerging private-sector detection effort (PierSight) — but no integrated, automated pipeline that closes the loop from detection through to AIS-based vessel attribution. This project targets that specific gap: turning "a spill happened, no one to blame" into a traceable, investigable event.

## 3. Target Audience

Primary (operators): Indian Coast Guard, MoEFCC, port authorities, Directorate General of Shipping — institutions that would review the system's output and act on it.

Secondary (beneficiaries): coastal fishing communities, marine conservation bodies, maritime insurers, coastal tourism economies — groups who bear the cost of unattributed spills.

This is a B2G / institutional decision-support tool, not a consumer-facing app.

## 4. Our Solution (Scoped Version)

One-line pitch: A decision-support pipeline — not an autonomous system — that detects oil slicks from archival SAR imagery, hindcasts their likely origin using drift modeling, and produces a confidence-scored suspect-vessel shortlist from AIS data, validated against a real historical spill, with every unsolved limitation named upfront.

The pipeline has three sequential stages, wrapped in a map-based visual dashboard:

- **Detection** — segment oil slicks from SAR imagery, classify against look-alikes, compute geometry and confidence
- **Drift/Hindcast** — use OpenDrift to backtrack the slick to a probable origin time/location (as an uncertainty region, not a pinpoint), and forward-project its future spread
- **AIS Attribution** — filter historical AIS traffic to the origin's space-time window, score remaining vessels on proximity/trajectory/behavioral anomalies, and output a ranked suspect shortlist

Output is explicitly framed as an investigative lead for human review, not proof or a verdict.

## 5. Scope — V1 (What We ARE Building)

- Oil slick detection and segmentation from archival Sentinel-1 SAR scenes (KSAT/OSD labeled datasets)
- Look-alike filtering (oil spill vs. algal bloom / low-wind zone / other false positives)
- Geometric property calculation: area, perimeter, elongation, confidence score
- Backward drift hindcast using OpenDrift, producing an origin-time window + probability region
- Forward drift prediction using the same tool
- AIS data filtering to the estimated origin's spatiotemporal window
- Suspect vessel scoring: proximity, trajectory alignment, behavioral anomalies (AIS gaps, route deviation, loitering)
- Ranked, confidence-scored suspect shortlist output
- Map-based visual dashboard: slick overlay, drift paths, origin uncertainty region, color-coded suspect markers, timeline slider
- End-to-end pipeline validation against one real, documented historical spill incident (2017 Chennai spill)

## 6. Out of Scope — V1

- Live/real-time satellite monitoring or tasked acquisitions (using archival data only)
- Spill age estimation from imagery (scientifically unresolved; replaced by hindcasted origin-time window instead)
- India-calibrated detection accuracy (model trained on globally available datasets, not validated specifically on Indian coastal conditions)
- Real Indian historical AIS data access (no public archive exists; using MarineCadastre US data or clearly-labeled synthetic data as proof-of-concept)
- Identifying dark vessels (AIS deliberately turned off) — system flags AIS-coverage gaps as a risk indicator only, cannot unmask a fully dark vessel by identity
- Any definitive "guilty vessel" verdict or legal/evidentiary claim
- Live oceanographic/meteorological data feeds (using historical data for the validated incident instead)
- Any claim of sub-6-day detection latency (acknowledged constraint of free Sentinel-1 access)
- Multi-sensor fusion (optical/EO imagery, radar ship detection independent of AIS) — SAR + AIS only for V1

## 7. Data Flow & User Experience (Completed Product)

User action: User selects a pre-loaded demo incident on the dashboard and clicks "Analyze."

Behind the scenes (three-stage pipeline, orchestrated by the backend):

1. Detection module processes the SAR image (calibration → speckle filtering → segmentation → geometry/confidence output)
2. Drift module takes the detection's location/time, runs OpenDrift backward (origin estimate) and forward (future spread)
3. AIS module filters vessel traffic to the origin's space-time window and scores/ranks suspects

All three outputs are aggregated into one response and cached against the incident ID, so repeat views are instant.

What the user sees:

- A dark, map-first dashboard (instrument-panel style, not consumer app aesthetic) showing the detected slick as a polygon overlay, a dotted backward-drift trail leading into a shaded origin-probability region (never a sharp pin, to reflect real uncertainty), and a forward-projected drift path
- Ranked suspect vessels as color-coded markers on the map and as cards in a side panel, each showing a composite score and a proximity/trajectory/anomaly breakdown, with a badge for any detected AIS coverage gap
- A timeline slider to scrub through and animate the drift path over time
- A detail view (on clicking the slick) showing the original SAR image beside its detection mask, with geometry and confidence stats
- A visible "how this works" panel stating the system's limitations plainly, reinforcing that outputs are investigative leads, not proof

Interaction principle: the expensive pipeline computation happens once per incident, on "Analyze." Everything afterward — timeline scrubbing, clicking a vessel, opening the detail modal — is a fast, client-side interaction against already-fetched data, not a new backend call.

## 8. Limitations & Constraints (Stated Upfront, Not Hidden)

| Limitation | Our framing |
|---|---|
| Satellite revisit gap (~6 days for Sentinel-1) | Spill has likely drifted/weathered by detection time; this is exactly why hindcasting (not live tracking) is the core mechanism |
| Look-alike false positives (algal blooms, low-wind zones) | Mitigated via classifier trained on labeled look-alike data; low-confidence cases flagged for human review, not auto-confirmed |
| No spill-age estimation | Scientifically unresolved even in production systems; hindcasted origin-time window used as a physics-grounded proxy instead |
| No India-specific training/validation data | Architecture designed to be fine-tunable on Indian SAR data as it becomes available (ISRO EOS-4/RISAT archives, NISAR in future) |
| No public Indian historical AIS archive | Demonstrated on MarineCadastre (US) or synthetic Indian-region data; explicitly disclosed as a proof-of-concept substitution |
| Dark vessels (AIS deliberately disabled) | Hardest unsolved piece; system flags the AIS-coverage gap itself as a risk signal but cannot identify a fully dark vessel |
| Small spills (<7 tons) are hardest to detect | Disclosed as a known limitation — ironically these represent a large share of real illegal discharge events |
| Output is not legal proof | Framed throughout as an investigative lead / confidence-scored shortlist for human analyst review, matching how CleanSeaNet actually operates (human-in-the-loop, not autonomous) |
| Existing prior art (CleanSeaNet, PierSight) | Positioned as bringing an automated, India-scoped version of a proven concept to a market where no integrated system currently exists |

## 9. Validation Approach

The full pipeline will be run end-to-end against one real, documented historical spill incident (2017 Ennore/Chennai). Pipeline outputs (detected slick location/geometry, hindcasted origin estimate, top suspect vessels if any real record exists) will be compared against whatever public record is available for that incident, and any divergence will be documented honestly rather than hidden.
