# DeltaGrid — AI Agent Context

## Project Overview
DeltaGrid is an interactive Streamlit dashboard that calculates the gap between Paris Agreement NDC pledges and actual energy trajectories for 200+ countries, with a user-configurable "green score" weight slider that re-ranks countries in real-time.

## Tech Stack
- **Framework:** Streamlit 1.57
- **Viz:** Plotly 5.19 (px.choropleth for maps)
- **Data:** pandas 2.2.3, requests 2.31, numpy 2.2.6
- **Runtime:** Python 3.12.10 (Windows)
- **No paid deps, no proprietary cloud**

## Architecture (3 Layers)

```
data/          → raw CSVs, API responses, caching
computation/   → scoring, gap analysis, ranking
presentation/  → Streamlit pages, components
```

### Data Pipeline
1. **OWID Energy Data** → `data/raw/owid-energy-data-2010-2025.csv` (filtered, ~4.5k rows)
2. **Climate Watch NDC API** → `https://www.climatewatchdata.org/api/v1/ndcs` (bulk fetch)
3. **Climate Watch Historical Emissions** → `https://www.climatewatchdata.org/api/v1/data/historical_emissions`

### OWID Key Columns
- Share columns: `solar_share_energy`, `wind_share_energy`, `nuclear_share_energy`, `gas_share_energy`, `coal_share_energy`, `hydro_share_energy`
- Absolute: `primary_energy_consumption`, `solar_consumption`, `wind_consumption`, `hydro_consumption`, `nuclear_consumption`, `gas_consumption`, `coal_consumption`
- Index: `iso_code` (ISO-3166-1 alpha-3), `year`, `country`

### Climate Watch NDC Fields
- `ghg_target`, `ghg_target_type`, `pledge_base_year`, `pledge_target_year`, `conditionality`, `mitigation_contribution_type`
- India is an **intensity target** country (emissions/GDP, not absolute)
- `_parse_ghg_percentage()` handles: "33 to 35 percent", "45%", "47 percent"
- `fetch_all_ndcs()` — single bulk API call for all countries

## Green Score Formula
```
green_score = weighted_sum(energy_share_columns, user_weights) / max(all_weights)
             → absolute 0-100 scale: 100 = 100% from the most-valued source
```

### Default Weights
| Source  | Default |
|---------|---------|
| Solar   | 1.0     |
| Wind    | 1.0     |
| Hydro   | 1.0     |
| Nuclear | 0.5     |
| Gas     | 0.2     |
| Coal    | 0.0     |

## Gap Analysis
```
gap = actual_green_score - expected_trajectory
expected_trajectory = linear_interpolation(base_year, target_year, current_year)
```

## Country Classification
| Class            | Gap Range |
|------------------|-----------|
| hidden_champion  | > 5       |
| on_track         | 0–5       |
| slightly_behind  | -5–0      |
| laggard          | < -5      |
| no_data          | missing   |

## Key Files

```
src/
  config.py                — constants, URLs, column lists, DEFAULT_WEIGHTS
  pipeline.py              — AnalysisResult dataclass, run_analysis() orchestrator
  data/
    owid.py                — OWID CSV ingestion + filtering (cached via @st.cache_data)
    climate_watch.py       — NDC API client + bulk fetch + _parse_ghg_percentage()
    cache.py               — TTL-based disk cache (read/write/clear)
    country_codes.py       — ISO mapping, AGGREGATE_NAMES set, is_aggregate()
    upload_preprocessor.py — CSV/XLSX upload: encoding, column norm, ISO mapping
  models/
    scoring.py             — compute_green_score(weights required)
    gap.py                 — compute_gap() with linear trajectory
    ranking.py             — classify_countries(), get_laggards(), get_hidden_champions()

app/
  main.py                  — entry point, CSS, logging setup, cached scoring
  components/
    sidebar.py             — weight sliders + year selector (2010–2025)
    choropleth.py          — px.choropleth() world map + percentile range
    tables.py              — ranking tables w/ conditional formatting
  pages/
    _shared.py             — cached_analysis() + load_energy_data()
    1_gap_analysis.py      — dual choropleth (green score + gap) + stats
    2_rankings.py          — tabs: laggards, hidden champions, all
    3_methodology.py       — scoring explanation + weight preview
```

## Build Commands
```bash
make install     # pip install -r requirements.txt
make lint        # ruff check src/ app/
make typecheck   # mypy src/ app/
make test        # pytest tests/ -v
make serve       # streamlit run app/main.py
make clean       # remove __pycache__, .pytest_cache
```

## Data Flow
```
Sidebar (weights, year) → compute_green_score() → choropleth
                        → compute_gap()          → choropleth + tables
                        → classify_countries()   → rankings page
```

## Platform Notes
- Repo: `https://github.com/AshayK003/DeltaGrid.git`
- Deploy to Streamlit Community Cloud
- OWID uses ISO-3166-1 alpha-3 (`IND`, not `India`)
- Climate Watch uses `iso_code3` with bulk fetch (single API call)
- OWID CSV filtered to 2010–2025 for faster load

## Known Bugs Fixed
- `" Eastern Africa (UN)"` leading space in AGGREGATE_NAMES → removed
- `"Russia"` in AGGREGATE_NAMES → removed (real country)
- `row.get("green_score", 0.0)` NaN handling → added `pd.notna()` guard
- Empty DataFrame crash in `compute_green_score()` → added early return
- `classify_gap()` NaN → falls through to `"no_data"` instead of `"laggard"`
- `_vectorized_trajectory()` same-year branch fixed (dead code from `valid & (target_years == base_years)` contradiction)
- `render_classification_summary()` only creates columns for classes present in data
- Normalization: changed from `score / data_max * 100` → `score / total_weight` → `score / max(all_weights)`. Final version: 100% from top source = 100, slider changes rescale visibly

## Constraints for Agents
- Only 5 direct dependencies in requirements.txt
- Never commit secrets, API keys, or `data/raw/` large files
- All OWID data must be filtered by `iso_code` not `country` name
- Cache TTL: 24h for API (disk), 1h for OWID CSV (@st.cache_data)
- No `geopandas` — Plotly handles maps natively
- Prefer function composition over inheritance
- No unnecessary abstractions — keep it boring
