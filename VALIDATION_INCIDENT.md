# Validation Incident — 2017 Ennore (Chennai) Oil Spill

This is the real, documented event our pipeline will be validated against. Detection, hindcast, and AIS attribution outputs should be checked for plausibility against these known facts — not expected to match perfectly, but should be in the right ballpark and not contradict established facts.

---

## Incident Summary

On 28 January 2017, at 4:00 AM local time, the outbound tanker BW Maple collided with the inbound tanker Dawn Kanchipuram just outside Kamarajar Port in Ennore, near Chennai, Tamil Nadu. The collision occurred roughly two miles from the port, at coordinates 13°13'41.4"N, 80°21'48.0"E.

**Vessels involved:**
- **MT Dawn Kanchipuram** — Indian-flagged tanker, carrying 32,813 tonnes of petroleum, oil, and lubricants; it suffered a rupture after the collision.
- **MT BW Maple** — UK-flagged (Isle of Man) liquid petroleum gas carrier, reported to be empty/unladen at the time.

**Cause of spill:** Later official assessment concluded the spill was caused by engine/bunker fuel oil leaking from the damaged vessel, not the petroleum cargo itself — had the cargo leaked, the disaster would have been substantially larger.

## Spill Volume (note: sources vary — use as a range, not a single figure)

Reported figures differ across sources, which is itself realistic and worth noting in your pitch as a demonstration of real-world attribution ambiguity:
- One case study reports approximately 75 metric tons of oil released.
- An IEEE-published assessment estimates approximately 196 metric tons of bunker fuel (Grade 6) spilled.
- Coast Guard officials described it as a "major accident but a minor spill," estimating the affected sea area at approximately 34,000 square meters.

**For your pipeline's detection module:** use the Coast Guard's ~34,000 m² (0.034 km²) initial affected-area estimate as your rough sanity-check reference for the detected slick's early geometry — note this is much smaller than the multi-km² figures discussed generally for large spills, consistent with this being officially characterized as a comparatively minor spill.

## Geographic Spread

Within 48 hours, the oil spill contaminated approximately 25 miles (40 km) of coastline, extending from Ennore in the north to Thiruvanmiyur in the south. Coast Guard reporting described impact extending roughly 72 km along the coast from Ennore Port to Mahabalipuram, with the most concentrated slick impact covering about 12 km and the worst-hit stretch around 250 meters in the RK Nagar Kuppam area. Marina Beach and a stretch near Thiruvalluvar were also affected.

**For your drift/hindcast module:** this gives you a real backward AND forward validation reference — the spill originated near Ennore (13.228°N, 80.363°E) and spread south along the coast over the following days. Your forward-drift simulation, if run from the origin point, should plausibly show southward coastal spreading consistent with this reported path.

## Response Timeline

- Collision: 4:00 AM, 28 January 2017.
- Coast Guard was notified within two hours of the incident by Kamarajar Port authorities.
- By afternoon of the same day, oil sheen was visible on the water with reports of dead turtles washing ashore.
- By the following Tuesday, cleanup crews had collected roughly 40 tonnes of oil sludge and 27 tonnes of an oil-water mixture.
- Six days after the incident, cleanup was still actively ongoing across the affected coastline.

**For your pipeline's overall framing:** this timeline is useful evidence for the revisit-latency limitation you've already scoped — even with immediate Coast Guard notification (within 2 hours), the spill had already visibly spread and reached shore before any systematic satellite-based tracking could have meaningfully intervened. This real event supports your "hindcast, not live-catch" framing.

## Legal/Attribution Outcome (real-world precedent for your "investigative lead, not proof" framing)

Police registered cases against the managements of both vessels under six sections, including provisions on marine pollution, and summoned the captains of both MT Dawn Kanchipuram and MT BW Maple. Both vessels were detained by the Tamil Nadu Coastal Security Group pending further orders, and the Directorate General of Shipping conducted a formal inquiry. A separate government inquiry examined a two-day delay in securing the damaged vessel, which port authorities were criticized for not addressing sooner.

**Relevance to your project:** in this real case, attribution was straightforward because the collision was witnessed/reported directly, not because of a forensic satellite+AIS investigation — this is actually a good example of "the easy case." Your pipeline is aimed at the harder, more common case: spills with no witnessed collision, where a vessel discharges (deliberately or accidentally) and simply leaves, which is exactly why AIS-based reconstruction matters — there was no need for it here, but there would be for a genuinely unattributed spill.

---

## How to use this incident in your build

1. **Detection module test input:** if you can source an actual Sentinel-1 scene covering this date/region (check if it's included in any of your KSAT/OSD dataset samples, or search Copernicus Open Access Hub archives directly for late-Jan 2017 over 13.0–13.3°N, 80.2–80.5°E), use it as your primary real-world test case.
2. **Drift module test input:** origin point `[80.363, 13.228]`, origin time `2017-01-28T04:00:00Z`. Run forward drift and check that the simulated path plausibly trends south along the coast toward Thiruvanmiyur/Mahabalipuram, consistent with the real reported spread.
3. **AIS module test input:** the "suspects" here are already publicly known (MT Dawn Kanchipuram, MT BW Maple) — this is actually a good sanity check for your scoring logic: if you can source any historical AIS data for this date/region, your scoring model should rank vessels involved in an actual collision very highly on proximity and, ideally, show an anomaly (a collision itself would likely produce erratic speed/heading data right at the incident time).
4. **In your pitch:** be transparent that this incident's attribution didn't actually require your kind of system (it was a witnessed collision) — frame it as "we validated our pipeline's mechanics against a real, well-documented event, even though this particular case was solved through direct incident reporting rather than forensic reconstruction. Our system targets the more common, harder case: spills with no witnessed origin."

---

## Sources
- ScienceDirect case study: Environmental impacts of the Chennai oil spill accident
- IEEE Xplore: Assessment of Ennore Oil Spill 2017 on Chennai Coastal Water and Biota
- Wikipedia: 2017 Ennore oil spill
- The Hans India, Deccan Herald, Tribune India, The Indian Express — contemporary news coverage
