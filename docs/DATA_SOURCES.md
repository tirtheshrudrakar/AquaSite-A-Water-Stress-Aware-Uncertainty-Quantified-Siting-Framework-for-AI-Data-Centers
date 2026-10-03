# Data Sources

Static/bulk datasets used by GAUGE. These are downloaded once and cached locally in `data/raw/` — the core pipeline does not depend on live API calls for any of these. See [APIS.md](./APIS.md) for live API integrations.

## Quick Reference

| # | Source | Used for |
|---|---|---|
| 1 | WRI Aqueduct 4.0 | Water stress (core layer) |
| 2 | HydroBASINS / HydroSHEDS | Basin boundaries |
| 3 | LBNL 2024 Data Center Energy Usage Report | WUE/PUE parameter ranges |
| 4 | Ember Global Electricity Data | Grid mix → indirect water |
| 5 | EPA eGRID (US) | Water/emission intensity by sub-region |
| 6 | IM3 Open Source Data Center Atlas (US) | Pre-built US facility dataset |
| 7 | Manually curated list | Planned/announced facilities |

---

## 1. WRI Aqueduct 4.0
**Purpose:** Core water-stress layer — baseline annual, baseline monthly, and future-scenario water stress by location.
**Access:** [wri.org/aqueduct](https://www.wri.org/aqueduct) — direct download, no account required.
**Data dictionary:** [github.com/wri/Aqueduct40](https://github.com/wri/Aqueduct40)
**Storage:** `data/raw/aqueduct/`
**Notes:** The non-negotiable foundation of the whole project. Monthly columns (e.g. `bws_01_raw` = January baseline water stress) feed the temporal-weighting logic directly.

## 2. HydroBASINS / HydroSHEDS
**Purpose:** Basin polygon boundaries — needed to assign every candidate site (and every power plant supplying it) to a specific hydrological basin, for two-basin accounting and cumulative basin-capacity analysis.
**Access:** [hydrosheds.org](https://www.hydrosheds.org/) — free shapefile download.
**Storage:** `data/raw/hydrobasins/`
**Notes:** Required before any basin-level math is possible — set this up alongside Aqueduct, not later.

## 3. LBNL 2024 United States Data Center Energy Usage Report
**Purpose:** Source of WUE/PUE ranges by cooling technology (air-cooled, evaporative, direct-to-chip liquid, etc.) — feeds the Pareto optimizer's parameter ranges directly.
**Access:** [eta.lbl.gov/publications/2024-lbnl-data-center-energy-usage-report](https://eta.lbl.gov/publications/2024-lbnl-data-center-energy-usage-report)
**Notes:** Not an API — read once, manually extract the parameter ranges into `docs/ASSUMPTIONS.md`.

## 4. Ember — Global Electricity Data
**Purpose:** Country/region-level electricity generation mix, used to compute indirect water consumption via the grid.
**Access:** [ember-energy.org/data](https://ember-energy.org/data/) — free bulk CSV download, no key.
**Notes:** Preferred over a live carbon-intensity API for the core global pipeline, since it covers all regions at once rather than one zone at a time (see APIS.md, Electricity Maps).

## 5. EPA eGRID (US)
**Purpose:** Emission factors and water-intensity factors by grid sub-region — sharpens the indirect-water conversion for US sites specifically.
**Access:** [epa.gov/egrid](https://www.epa.gov/egrid) — free annual release download.

## 6. IM3 Open Source Data Center Atlas (US)
**Purpose:** Pre-built US dataset of facility locations with area and county-level detail — a faster starting point than building from OpenStreetMap alone for a US pilot.
**Access:** [osti.gov/biblio/2550666](https://www.osti.gov/biblio/2550666) — free.

## 7. Planned / Announced Facilities (manually curated)
**Purpose:** The cumulative basin-pipeline simulator needs to know which *new* facilities are planned for a basin, not just which already exist — **no dataset or API currently provides this.**
**Source:** News coverage, company press releases, and state/local permitting filings, tracked manually.
**Notes:** This is an acknowledged data-collection limitation, not a solved problem — document it honestly in the paper's Limitations section rather than overstating coverage.

---

## Build Order (recommended)

1. WRI Aqueduct 4.0 — foundation layer
2. HydroBASINS — basin assignment, needed immediately alongside #1
3. Ember bulk data — grid mix for indirect water
4. LBNL report — WUE/PUE parameter ranges
5. IM3 Atlas — US pilot site locations

**Deferred / add later if time permits:** EPA eGRID — sharpens US-specific accuracy but isn't required for a first working version.

---

## Attribution Requirements

> Water stress data © World Resources Institute (Aqueduct). Map data © OpenStreetMap contributors (ODbL), where OSM-derived datasets (e.g. IM3 Atlas) are used.
