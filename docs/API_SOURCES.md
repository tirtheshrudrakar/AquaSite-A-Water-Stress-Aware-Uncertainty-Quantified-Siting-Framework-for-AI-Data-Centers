# APIs

Live API integrations used by GAUGE. Most are called once per candidate site and cached locally — the core pipeline should not depend on repeated live calls at analysis time. See [DATA_SOURCES.md](./DATA_SOURCES.md) for static/bulk datasets.

## Quick Reference

| # | API | Used for |
|---|---|---|
| 1 | Open-Meteo Historical Weather API | Wet-bulb temperature |
| 2 | NASA POWER API | Wet-bulb cross-validation |
| 3 | OpenStreetMap Overpass API | Existing data center locations |
| 4 | Electricity Maps API | Live carbon intensity (demo only) |
| 5 | EIA Open Data API (US) | US generation by fuel/state |
| 6 | USGS Water Data API (US) | Basin supply/withdrawal validation |

---

## 1. Open-Meteo Historical Weather API
**Purpose:** Hourly temperature and humidity (ERA5 reanalysis, from 1940), used to compute wet-bulb temperature, which drives the cooling-technology model.
**Docs:** [open-meteo.com/en/docs/historical-weather-api](https://open-meteo.com/en/docs/historical-weather-api)
**Auth:** None required.
**Limits:** Free for non-commercial use, up to 10,000 calls/day.
**License:** CC BY 4.0 — attribution required ("Weather data by Open-Meteo.com").
**Usage pattern:** Call once per candidate site, cache the result locally — do not re-query on every pipeline run.

## 2. NASA POWER API
**Purpose:** Includes a built-in wet-bulb temperature variable (`T2MWET`), used as a cross-check against the Open-Meteo-derived value.
**Docs:** [power.larc.nasa.gov](https://power.larc.nasa.gov/)
**Auth:** None required.
**Usage pattern:** Validation only, not the primary source — call once per site, cache.

## 3. OpenStreetMap Overpass API
**Purpose:** Existing data center locations worldwide, via the `telecom=data_center` tag.
**Endpoint:** `https://overpass-api.de/api/interpreter`
**Auth:** None required.
**Limits:** Add a country filter to queries, or large/global queries will time out.
**License:** ODbL — attribution required ("Map data © OpenStreetMap contributors").
**Usage pattern:** Query once, cache results — locations don't change frequently enough to justify repeated live calls.

## 4. Electricity Maps API
**Purpose:** Real-time carbon intensity and electricity mix by grid zone.
**Docs:** [app.electricitymaps.com/docs](https://app.electricitymaps.com/docs)
**Auth:** API key required (free tier signup).
**Limits:** Free tier covers **one zone only**, ~50 requests/hour, non-commercial use only.
**Usage pattern:** Too limited for the core multi-region pipeline — use Ember's static bulk data (see DATA_SOURCES.md) for the main analysis. Reserve this API for a single "live conditions" feature in the dashboard demo only.

## 5. EIA Open Data API (US)
**Purpose:** US electricity generation by fuel type and state — useful if the pilot region is scoped to the US.
**Docs:** [eia.gov/opendata](https://www.eia.gov/opendata/)
**Auth:** Free API key, instant signup.
**Usage pattern:** Bulk pull once per pilot region, cache locally.

## 6. USGS Water Data API (US)
**Purpose:** Observed basin-level water supply and withdrawal data, used to validate the basin-capacity numbers used in the cumulative pipeline simulator.
**Docs:** [waterdata.usgs.gov](https://waterdata.usgs.gov/)
**Auth:** None required for basic queries.
**Usage pattern:** US-only; used for validation pulls, not the core pipeline.

---

## General Rules for API Use in This Project

- **Cache everything.** No API in this list should be called more than once per site/region per pipeline run. Store responses in `data/interim/` and re-use them.
- **No live API is required for the core siting score.** If an API is unreachable, the pipeline should still run on previously cached data.
- **Electricity Maps is demo-only.** Do not build the core water/carbon scoring logic around it — its free-tier limits make it unsuitable for a multi-region study.
- **Respect rate limits and attribution requirements** listed above for each API, especially Open-Meteo (CC BY 4.0) and OpenStreetMap (ODbL).

---

## Attribution Requirements

> Weather data by [Open-Meteo.com](https://open-meteo.com/). Map data © OpenStreetMap contributors (ODbL).
