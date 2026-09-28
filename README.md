# AquaSite: A Water-Stress-Aware, Uncertainty-Quantified Siting Framework for AI Data Centers

> A fully software-based, from-scratch research project. Original code, original indices, original models. Only open data and public APIs are used as inputs.

---

## 1. Problem Statement

AI data centers consume water directly (evaporative cooling) and indirectly (water used by power plants that supply their electricity). Public reporting suggests that new facilities are increasingly built in water-stressed regions, and that water is often the last factor considered in siting decisions. Existing analyses are mostly proprietary, static (annual averages), single-objective, and deterministic.

**AquaSite** is an open, reproducible framework that scores candidate locations for data center siting using *seasonal* water stress, *direct + indirect* water demand, carbon intensity, and *uncertainty*, then simulates the *cumulative basin-level impact* of a planned data center pipeline.

## 2. Research Gaps Addressed

| # | Gap observed in current work | AquaSite contribution |
|---|---|---|
| G1 | Siting screens use **annual** water stress; cooling demand peaks in hot months when monthly stress may also peak | **Temporal Water Coincidence Index (TWCI)**: monthly stress weighted by monthly cooling demand |
| G2 | Analyses look at the **site basin only**; indirect water sits in a *different* basin (the power plant's) | **Two-basin water accounting**: direct water in the site basin plus indirect water via the grid mix |
| G3 | **Site and cooling technology are studied separately**; air cooling saves water but raises power use, and power carries indirect water and carbon | **Joint site x cooling-tech Pareto optimization** across water, carbon, and power burden |
| G4 | Results are **deterministic** even though cooling type, WUE, and load are unknown for most facilities | **Monte Carlo uncertainty propagation** with confidence bands on every score |
| G5 | Facilities are assessed **one at a time** | **Cumulative pipeline simulator**: all announced facilities in a basin against basin supply capacity |
| G6 | Strong analyses rely on **proprietary data**, so they cannot be reproduced | Fully **open-data, reproducible** pipeline with published methodology |

> **Important:** These gaps come from a targeted literature scan, not a systematic review. Before you claim novelty in a paper, run a proper search on Google Scholar, Scopus, and arXiv (see Section 12) and confirm each gap still holds.

## 3. Objectives

1. Build a monthly **Water Stress Exposure** layer for a global candidate grid.
2. Build a parametric **direct water model** (WUE as a function of wet-bulb temperature and cooling technology).
3. Build an **indirect water and carbon model** from regional electricity mix.
4. Combine these into a **multi-objective siting score** with uncertainty bands.
5. Simulate **cumulative basin burden** for planned facilities.
6. Expose everything through a **REST API** and an **interactive map dashboard**.
7. Validate against known cases and publish the methodology.

## 4. System Architecture

```
            +-------------------------- DATA LAYER --------------------------+
            | WRI Aqueduct | Open-Meteo/NASA POWER | Electricity Maps/Ember  |
            | OSM/IM3 data-center locations | LBNL WUE/PUE ranges            |
            +---------------------------------+------------------------------+
                                              |
                               ingestion + cleaning (Python)
                                              |
                        +---------------------v---------------------+
                        |  SPATIAL GRID  (hexagonal cells, e.g. H3) |
                        |  one row per cell x month                 |
                        +---------------------+---------------------+
                                              |
     +-----------------+----------------------+---------------------+-----------------+
     |                 |                      |                     |                 |
 Stress module    Direct water module   Indirect water &     Uncertainty       Pipeline
 (monthly WSEI)   (WUE model)           carbon module        (Monte Carlo)     simulator
     |                 |                      |                     |                 |
     +-----------------+----------+-----------+---------------------+-----------------+
                                  |
                     Multi-objective optimizer (Pareto front)
                                  |
                     +------------+-------------+
                     |                          |
                FastAPI service          Map dashboard
```

## 5. Data Sources

### 5.1 Water stress (core)

| Dataset | Use | Link |
|---|---|---|
| WRI Aqueduct 4.0 (baseline annual, baseline monthly, future annual) | Water stress, depletion, drought, seasonal variability | https://www.wri.org/aqueduct |
| Aqueduct 4.0 docs and data dictionary | Column definitions (for example `bws_01_raw` is baseline water stress for January) | https://github.com/wri/Aqueduct40 |
| Aqueduct 4.0 technical note | Methodology to cite | https://www.wri.org/research/aqueduct-40-updated-decision-relevant-global-water-risk-indicators |

### 5.2 Data center locations

| Dataset | Use | Link |
|---|---|---|
| OpenStreetMap `telecom=data_center` via Overpass API | Free, global, continuously updated | https://wiki.openstreetmap.org/wiki/Tag:telecom=data_center |
| IM3 Open Source Data Center Atlas (US) | Locations plus facility area and county | https://www.osti.gov/biblio/2550666 |
| ATLAS open data center dataset (18,110 facilities, 116 countries) | Cross-check and coverage gaps (**verify the current license and attribution terms before use**) | https://github.com/Ringmast4r/Global-Data-Center-Map |

### 5.3 Energy, WUE, and PUE parameters

| Dataset | Use | Link |
|---|---|---|
| LBNL 2024 US Data Center Energy Usage Report | Cooling-system types, PUE and WUE ranges, direct and indirect water estimates | https://eta.lbl.gov/publications/2024-lbnl-data-center-energy-usage-report |
| Company sustainability reports (Google, Microsoft, Meta, AWS) | Reported site WUE/PUE for calibration | Each company's environmental report page |

### 5.4 Additional datasets worth adding (not re-verified during this session; check terms before use)

| Dataset | Use |
|---|---|
| Ember open electricity data | Country-level carbon intensity and mix |
| EIA Open Data (US) | US electricity generation by fuel and state |
| EPA eGRID (US) | Emission factors by sub-region |
| HydroSHEDS / HydroBASINS | Basin polygons for basin-level accounting |
| USGS water data (US) | Validation against observed water availability |
| Copernicus ERA5 (Climate Data Store) | Bulk historical climate if you outgrow API limits |
| Published literature on water intensity of electricity by fuel type | Convert generation mix to indirect water |

## 6. APIs

| API | Purpose | Notes |
|---|---|---|
| **Open-Meteo Historical Weather API** | Hourly temperature and humidity (ERA5 from 1940) to derive wet-bulb temperature | No key needed; free for non-commercial use up to 10,000 calls/day; data under CC BY 4.0 (attribution required). Docs: https://open-meteo.com/en/docs/historical-weather-api |
| **Electricity Maps API** | Carbon intensity, electricity mix, forecasts | Free tier is limited to one zone and about 50 requests/hour, non-commercial. For many zones use bulk open data (Ember) instead. Docs: https://app.electricitymaps.com/docs |
| **OSM Overpass API** | Data center locations | Free; endpoint `https://overpass-api.de/api/interpreter`; add a country filter to avoid timeouts |
| **NASA POWER API** | Includes a wet-bulb temperature variable (`T2MWET`); good cross-check for Open-Meteo | https://power.larc.nasa.gov/ |

**Design tip:** Because the Electricity Maps free tier covers only one zone, do not depend on live API calls for your global analysis. Download static open datasets, cache everything locally, and use live APIs only for a small demo feature.

## 7. Methodology (what you build yourself)

### 7.1 Spatial grid
Tile the study area into hexagonal cells. For each cell compute or look up: monthly water stress, monthly wet-bulb temperature, grid carbon intensity, indirect water factor, basin ID, and basin supply capacity.

### 7.2 Monthly Water Stress Exposure (WSEI)
Normalize the monthly baseline water stress for each cell to [0, 1] using a documented rule (for example quantile scaling within region).

### 7.3 Direct water model
Model site WUE as a function of wet-bulb temperature *T_wb* and cooling technology *c*:

```
WUE_direct(m, c) = f_c(T_wb(m))
```

Fit each `f_c` as a documented parametric curve (for example piecewise-linear) whose range is calibrated to the LBNL cooling-system WUE ranges. Air-cooled chillers sit near zero site water, while water-cooled chillers without economizers can exceed 1 L/kWh. Document every assumption.

### 7.4 Temporal Water Coincidence Index (TWCI, G1)
```
TWCI = sum_m ( w_m * WSEI_m ),    w_m = cooling_demand_m / sum(cooling_demand)
```
A site with moderate annual stress but severe stress in the same months when cooling demand peaks scores worse than an annual average suggests.

### 7.5 Two-basin accounting (G2)
```
Water_total = E * WUE_direct  (site basin)  +  E * PUE * I_grid  (generation basins)
```
`E` is IT energy, `PUE` depends on cooling tech and climate, and `I_grid` is the water intensity of the local grid mix. Report both components separately and attribute each to its own basin stress.

### 7.6 Joint site x cooling optimization (G3)
For each cell and cooling technology, compute three objectives: water burden, carbon, and power-system burden. Implement your own non-dominated sorting to obtain the **Pareto front**, and report the trade-off (for example, dry sunny sites may be low carbon but high water stress, and dry cooling then raises power use).

### 7.7 Uncertainty propagation (G4)
Treat WUE, PUE, load, and cooling technology as distributions (triangular or beta, bounded by literature ranges). Run Monte Carlo sampling (for example 1,000 to 10,000 draws) and report medians and 5th to 95th percentile bands. Add a sensitivity analysis (one-at-a-time or Sobol-style) to show which assumptions matter most.

### 7.8 Cumulative pipeline simulator (G5)
Assign announced or planned facilities to basins, sum expected water demand under scenarios, and compare with basin supply capacity. Output a **basin burden ratio** and the year when it crosses chosen thresholds.

## 8. Tech Stack

| Layer | Suggested tools |
|---|---|
| Language | Python 3.11+ |
| Data | pandas, geopandas, xarray, rasterio, pyarrow |
| Spatial indexing | H3 (library only; you write the logic) |
| Modeling | numpy, scipy (own Monte Carlo and Pareto code) |
| API | FastAPI, uvicorn, pydantic |
| Dashboard | Streamlit, or React with MapLibre GL |
| Storage | Parquet files first; PostgreSQL/PostGIS later if needed |
| Testing | pytest |
| Reproducibility | Makefile or DVC, pinned `requirements.txt`, Docker |

Using open-source libraries is normal and expected; the "from scratch" part is the *methodology, indices, and models*.

## 9. Repository Structure

```
aquasite/
  README.md
  requirements.txt
  Makefile
  data/
    raw/            # untouched downloads (git-ignored, with fetch scripts)
    interim/
    processed/
  src/aquasite/
    ingest/         # aqueduct.py, weather.py, grid.py, datacenters.py
    grid/           # hexagonal grid builder
    models/         # stress.py, direct_water.py, indirect_water.py, twci.py
    optimize/       # pareto.py
    uncertainty/    # montecarlo.py, sensitivity.py
    pipeline/       # cumulative_simulator.py
    api/            # main.py, schemas.py
  dashboard/
  notebooks/        # exploration and figures
  tests/
  docs/             # methodology, assumptions log, paper drafts
```

## 10. Step-by-Step Roadmap (about 16 weeks)

| Phase | Weeks | Tasks | Deliverable |
|---|---|---|---|
| **0. Setup** | 1 | Read Aqueduct 4.0 technical note and the LBNL report; set up repo, environment, and assumptions log | Project skeleton, reading notes |
| **1. Literature review** | 1-2 | Systematic search (keywords in Section 12); build a table of prior work; confirm G1-G6 | Gap-confirmation table |
| **2. Data ingestion** | 3-4 | Download Aqueduct, build ingestion scripts, pull locations, fetch weather for sample cells | Clean, documented datasets |
| **3. Spatial grid and stress layer** | 5 | Build the hexagonal grid; join monthly stress; compute WSEI | Global/regional stress map |
| **4. Direct and indirect water models** | 6-8 | Wet-bulb calculation, WUE curves, indirect water factors, carbon; unit tests | Model modules plus calibration notes |
| **5. TWCI and two-basin accounting** | 9 | Implement G1 and G2; compare against annual-only scoring | First novel result |
| **6. Optimization and uncertainty** | 10-11 | Pareto front (G3); Monte Carlo and sensitivity (G4) | Pareto plots, confidence bands |
| **7. Pipeline simulator** | 12 | Basin assignment; cumulative scenarios (G5) | Basin burden results |
| **8. API and dashboard** | 13-14 | FastAPI endpoints; interactive map with sliders (cooling tech, load, scenario) | Working demo |
| **9. Validation** | 15 | Compare against reported facility water use, published rankings, and known controversial sites | Validation chapter |
| **10. Writing and release** | 16 | Paper draft, final report, open-source release with data-fetch scripts | Paper and repository |

## 11. Evaluation and Validation

- **Ablation:** compare annual-only scoring vs. TWCI; single-basin vs. two-basin accounting; deterministic vs. uncertain results. Show where rankings change.
- **Validation:** check that the model reproduces the *order of magnitude* of reported facility water use, and that it flags sites widely reported as water-stressed.
- **Sensitivity:** identify which inputs drive most of the output variance.
- **Reproducibility:** one command should rebuild all results from raw data.
- **Metrics to report:** rank correlation between scoring variants, share of sites whose category changes, width of uncertainty bands, and Pareto front size.

## 12. Publishing a Research Paper

**Yes, this can be published**, as long as it makes a defensible new contribution (G1-G6 are the candidates) and is rigorous about assumptions and validation.

**Suggested paper structure:** Abstract, Introduction, Related Work, Data, Methodology, Results, Validation, Sensitivity and Limitations, Policy Implications, Conclusion, Data and Code Availability.

**Venue options (check current scope, deadlines, and fees before submitting):**

- **Preprint first:** arXiv (for example cs.CY or related sustainability categories) to establish priority.
- **Journals in this area:** Environmental Research Letters, Journal of Cleaner Production, Resources Conservation and Recycling, Sustainable Computing: Informatics and Systems, Environmental Modelling and Software.
- **Conferences and workshops:** ACM HotCarbon, ACM e-Energy, and Climate Change AI workshops at major ML conferences.
- If you are in a university program, also ask your supervisor about recognized IEEE or Springer conferences that count toward your degree.

**Search keywords for the literature review:** "data center" AND ("water stress" OR "water scarcity") AND ("siting" OR "site selection"); "water usage effectiveness" AND "climate"; "indirect water" AND "electricity" AND "data center"; "Aqueduct" AND "data center"; "cumulative" AND "basin" AND "data center".

**Tips to raise acceptance chances:** state assumptions explicitly, release code and processed data, include uncertainty everywhere, avoid overclaiming causal impact, and be transparent about the limits of proprietary or missing facility-level data.

## 13. Risks and Mitigation

| Risk | Mitigation |
|---|---|
| Facility-level water data is scarce | Use ranges and Monte Carlo instead of point values; say so clearly |
| Aqueduct resolution or basin definition limits accuracy | Report resolution limits; use basin-level not street-level claims |
| API rate limits | Cache data; use static bulk datasets for analysis |
| Dataset license terms | Track every license in `docs/DATA_LICENSES.md`; attribute properly |
| Scope creep | Ship one region first (for example a single country), then generalize |
| Overclaiming novelty | Complete the systematic literature review before writing claims |

## 14. Ethical and Responsible-Use Notes

This tool supports planning and transparency. It should not be presented as an authoritative ruling on whether a specific real-world project should proceed. Communicate uncertainty, do not target named companies or communities with unverified claims, and cite sources for every input.

## 15. Key References to Read First

1. Kuzma et al. (2023). *Aqueduct 4.0: Updated decision-relevant global water risk indicators.* WRI Technical Note. https://www.wri.org/research/aqueduct-40-updated-decision-relevant-global-water-risk-indicators
2. Shehabi et al. (2024). *2024 United States Data Center Energy Usage Report.* Lawrence Berkeley National Laboratory. https://eta.lbl.gov/publications/2024-lbnl-data-center-energy-usage-report
3. Privette et al. (2026). *Data Centers Water Footprint: The Need for More Transparency.* AGU Advances. https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2025AV002140
4. *AI Data Centers and the Water Use Feedback Loop* (arXiv 2606.21760). https://arxiv.org/pdf/2606.21760
5. MSCI (2025). *When AI Meets Water Scarcity: Data Centers in a Thirsty World.* https://www.msci.com/research-and-insights/blog-post/when-ai-meets-water-scarcity-data-centers-in-a-thirsty-world
6. Chen et al. *Concentrated siting of AI data centers drives regional power-system stress* (arXiv 2604.06198). https://arxiv.org/pdf/2604.06198
7. Brookings (2025). *AI, data centers, and water.* https://www.brookings.edu/articles/ai-data-centers-and-water/

## 16. Getting Started Today (first 5 actions)

1. Create the repository and a `docs/ASSUMPTIONS.md` file.
2. Read the Aqueduct 4.0 technical note and data dictionary.
3. Download the Aqueduct baseline monthly data and open it in Python.
4. Write your own hexagonal-grid builder and join one month of stress data.
5. Query Open-Meteo for one sample location and compute wet-bulb temperature by hand from temperature and humidity, then verify against the NASA POWER wet-bulb value.

---

*Weather data by Open-Meteo.com. Map data (c) OpenStreetMap contributors (ODbL). Aqueduct data (c) World Resources Institute; follow its license terms.*
