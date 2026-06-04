<div align="center">
  <h1>⚡ DeltaGrid</h1>
  <p><strong>Paris Agreement NDC pledges vs actual energy trajectory gap analysis</strong></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#development">Development</a> •
    <a href="#deployment">Deployment</a> •
    <a href="#contributing">Contributing</a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
    <img src="https://img.shields.io/badge/tests-105%20passing-brightgreen" alt="105 tests passing">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
    <img src="https://img.shields.io/badge/dependencies-5-lightgrey" alt="5 dependencies">
  </p>
</div>

---

DeltaGrid is an interactive dashboard that calculates the gap between **Paris Agreement NDC pledges** and **actual energy transition trajectories** for 200+ countries. Users adjust slider weights for energy sources (solar, wind, hydro, nuclear, gas, coal) and see countries re-ranked in real time.

**The problem:** NDCs (Nationally Determined Contributions) set emission targets, but tracking progress country-by-country requires comparing apples-to-oranges: intensity targets vs absolute targets, different base years, different sector coverage. DeltaGrid normalizes these into a single 0–100 **Green Score** and computes the gap to each country's pledged trajectory.

---

## Features

- **Green Score** — weighted composite (0–100) from 6 energy shares, normalized to absolute scale
- **Gap Analysis** — actual score vs linear NDC trajectory, per country and year
- **Real-time Re-ranking** — move a slider, the map and tables update immediately
- **World Map** — Plotly choropleth maps for green score and gap
- **Custom Data Upload** — CSV/XLSX with auto-preprocessing: encoding detection, column normalization, ISO code mapping
- **Classification** — countries bucketed into hidden champions, on track, slightly behind, laggards, or no data

---

## Architecture

### Three-layer design

```
┌─────────────────────────────────────────────────┐
│                   app/                           │
│  main.py · 1_gap_analysis.py · 2_rankings.py    │
│  3_methodology.py · sidebar.py · choropleth.py  │
│  tables.py · ui.py                               │
│  ── Streamlit pages + components                 │
├─────────────────────────────────────────────────┤
│                   src/                           │
│  scoring.py · gap.py · ranking.py · pipeline.py │
│  ── Computation, scoring, gap, classification    │
├─────────────────────────────────────────────────┤
│                  src/data/                       │
│  owid.py · climate_watch.py · validators.py      │
│  cache.py · country_codes.py                     │
│  upload_preprocessor.py                          │
│  ── Ingestion, API, caching, preprocessing       │
└─────────────────────────────────────────────────┘
```

### Data flow

```
Sidebar (weights, year)
  │
  ├─→ compute_green_score() ──→ choropleth (main page)
  │
  ├─→ fetch_all_ndcs()
  │     │
  │     └─→ compute_gap() ──→ choropleth + stats (gap analysis page)
  │              │
  │              └─→ classify_countries() ──→ ranking tables (rankings page)
```

### Key design decisions

| Decision | Rationale |
|----------|-----------|
| **5 dependencies only** | streamlit, plotly, pandas, requests, numpy. No geopandas, no paid APIs, no heavy frameworks |
| **Plotly px.choropleth, not geopandas** | GeoJSON bundling is fragile; Plotly's built-in country outlines cover 200+ countries with zero setup |
| **Absolute green score normalization** | `score / total_weight` instead of `score / score.max() * 100`. The old relative normalization made slider changes invisible (top country always scored 100). Absolute scores give meaningful 0–100 values that shift when weights change |
| **No ORM, no database** | The dataset is small enough (4,500 rows) that pandas in memory is faster and simpler than any persistence layer |
| **Disk cache with TTL** | OWID CSV (7 days) and Climate Watch API (24 hours). No Redis, no database cache — just JSON files in `data/cache/` |
| **`@st.cache_data` for Streamlit** | Memoizes scoring, analysis, and choropleth figures across reruns with TTL |

---

## Quick Start

### Prerequisites

- Python **3.10+** (tested on 3.12)
- pip

### Install

```bash
git clone https://github.com/AshayK003/DeltaGrid.git
cd DeltaGrid

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

# Install
pip install -r requirements.txt
pip install -e ".[dev]"      # dev tools (ruff, mypy, pytest)
```

### Run

```bash
streamlit run app/main.py
```

Open [http://localhost:8501](http://localhost:8501). The first load downloads the OWID energy CSV (~45 MB) and caches it locally.

---

## Development

### Commands

```bash
make install     # pip install -r requirements.txt + dev extras
make test        # pytest tests/ -v (105 tests)
make lint        # ruff check src/ app/
make typecheck   # mypy src/ app/ (strict mode)
make serve       # streamlit run app/main.py
make clean       # remove __pycache__, .pytest_cache, .mypy_cache, .ruff_cache
```

### Project structure

```
DeltaGrid/
├── app/                    # Streamlit application
│   ├── main.py             # Entry point, cached scoring, CSS, metrics
│   ├── components/
│   │   ├── sidebar.py      # Weight sliders, year selector, file upload
│   │   ├── choropleth.py   # Plotly world map component
│   │   ├── tables.py       # Ranking tables with conditional formatting
│   │   └── ui.py           # Shared UI: headers, errors, badges, footer
│   └── pages/
│       ├── _shared.py      # Cached analysis wrapper (underscore = hidden from Streamlit)
│       ├── 1_gap_analysis.py
│       ├── 2_rankings.py
│       └── 3_methodology.py
├── src/
│   ├── config.py           # Constants, column names, default weights, thresholds
│   ├── pipeline.py         # AnalysisResult dataclass, run_analysis() orchestrator
│   ├── data/
│   │   ├── owid.py         # OWID CSV download, filter, cache read/write
│   │   ├── climate_watch.py# NDC bulk fetch + _parse_ghg_percentage()
│   │   ├── cache.py        # TTL disk cache (JSON files)
│   │   ├── country_codes.py# ISO normalization, aggregate detection
│   │   ├── validators.py   # Schema validation, energy/NDC merge
│   │   └── upload_preprocessor.py
│   └── models/
│       ├── scoring.py      # compute_green_score()
│       ├── gap.py          # compute_gap() with vectorized interpolation
│       └── ranking.py      # classify_gap(), classify_countries()
├── tests/                  # 105 tests across 9 modules
├── data/
│   ├── raw/                # OWID CSV (gitignored — downloaded on first run)
│   └── cache/              # JSON cache files (gitignored)
├── .streamlit/config.toml  # Dark theme, headless mode
└── Makefile                 # Dev workflow commands
```

### Data sources

| Source | What | Access |
|--------|------|--------|
| [Our World in Data — Energy](https://github.com/owid/energy-data) | Country-level energy mix (1900–2025) | CSV download, cached 7 days |
| [Climate Watch — NDC API](https://www.climatewatchdata.org/api/v1/ndcs) | GHG targets, base/target years, conditionality | REST API (bulk fetch), cached 24 hours |

### Green Score formula

```
green_score = Σ(share_i × weight_i) / Σ(weight_i)
```

- **share_i**: energy source as percentage of total (0–100)
- **weight_i**: user-adjustable slider (0.0–2.0, default per source)
- Output is **absolute 0–100** (not relative to data max)

#### Default weights

| Source | Default | Why |
|--------|---------|-----|
| Solar | 1.0 | Zero-emission, fastest-growing |
| Wind | 1.0 | Zero-emission, rapidly scaling |
| Hydro | 1.0 | Zero-emission, established baseload |
| Nuclear | 0.5 | Low-carbon but controversial |
| Gas | 0.2 | Fossil (bridge fuel) |
| Coal | 0.0 | Highest-emission fossil |

### Gap formula

```
gap = actual_green_score - expected_trajectory

expected_trajectory = linear_interpolation(
    base_value=0,
    target_value=NDC_ghg_target_percent,
    base_year=NDC_pledge_base_year,
    target_year=NDC_pledge_target_year,
    current_year=selected_year,
)
```

#### Classification thresholds

| Class | Gap | Meaning |
|-------|-----|---------|
| Hidden Champion | > 5 | Significantly ahead of NDC trajectory |
| On Track | 0 to 5 | Meeting or slightly ahead |
| Slightly Behind | -5 to 0 | Within striking distance |
| Laggard | < -5 | Far behind trajectory |
| No Data | missing | No NDC data available |

---

## Testing

```bash
# Run all tests
make test

# Run a specific module
pytest tests/test_scoring.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**Test coverage by module:**

| Module | Tests | What it covers |
|--------|-------|----------------|
| `test_scoring.py` | 9 | Empty/NaN/single-row DataFrames, zero weights, range bounds, mutation safety |
| `test_gap.py` | 6 | Positive/negative gaps, missing NDCs, invalid years, NaN scores, empty input |
| `test_ranking.py` | 17 | Boundary classifications (exactly 5, 0, -5), empty results, missing columns |
| `test_climate_watch.py` | 21 | Percent parser (range/dash/float/keyword), network failures, cache behavior |
| `test_cache.py` | 10 | TTL expiry, corrupted JSON, key sanitization, empty dir |
| `test_country_codes.py` | 17 | ISO normalization, aggregates, whitespace, mixed case |
| `test_validators.py` | 12 | Missing fields, partial overlap, empty dicts |
| `test_owid.py` | 4 | Year range, cache hit/miss |
| `test_integration.py` | 8 | End-to-end pipeline, weight-specific rankings, NDC-less countries |

---

## Deployment

### Streamlit Community Cloud (recommended)

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo, set **Main file path** to `app/main.py`
4. Deploy — no additional config needed

### Manual server

```bash
streamlit run app/main.py --server.port 80 --server.address 0.0.0.0
```

### Environment

No environment variables, secrets, or API keys required. All data sources are public. The app runs entirely on:

- OWID energy CSV (CC BY 4.0)
- Climate Watch NDC API (open access)

---

## Custom data upload

The sidebar accepts CSV or XLSX files. Required columns:

| Column | Description |
|--------|-------------|
| `iso_code` | ISO-3166-1 alpha-3 (e.g., `IND`, `USA`) |
| `year` | Integer year |

Optional columns (for green score computation):

| Column | Alias alternatives |
|--------|-------------------|
| `solar_share_energy` | `solar`, `solar_share`, `solar_pct` |
| `wind_share_energy` | `wind`, `wind_share`, `wind_pct` |
| `hydro_share_energy` | `hydro`, `hydro_share`, `hydro_pct` |
| `nuclear_share_energy` | `nuclear`, `nuclear_share` |
| `gas_share_energy` | `gas`, `gas_share`, `natural_gas` |
| `coal_share_energy` | `coal`, `coal_share` |

Column names are normalized (lowercased, snake_cased). Missing ISO codes and aggregate regions (e.g., "World", "Africa") are removed automatically.

---

## Contributing

1. **Read AGENTS.md** — contains the full agent context with all conventions, bug history, and design rationale
2. **Open an issue** first for any non-trivial change
3. **Branch** from `master`: `git checkout -b feat/your-feature`
4. **Write tests first** for new functions (fixtures, edge cases, error paths)
5. **Run the full suite** before opening a PR:
   ```bash
   make lint && make typecheck && make test
   ```
6. **Keep dependencies lean** — no new dependency without discussion. The 5-dependency constraint is deliberate

### Code style

- Ruff linting (E, F, I, N, W, UP rulesets). Run `make lint` before commit
- mypy strict mode. Run `make typecheck` before commit
- No comments on obvious code — prefer readable names over explanatory comments
- Function composition over inheritance
- No unnecessary abstractions — "keep it boring"

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `ImportError: cannot import name 'X'` | Stale `__pycache__` | `make clean` |
| Map is all one color | Fixed color range (vmin/vmax) was too wide for data range | Removed in v0.1.3 — now auto-scales |
| Slider changes don't affect map | Old normalization (`score / max * 100`) compressed all scores to 0–100 regardless of weights | Fixed in v0.1.3 — now uses `score / total_weight` |
| OWID CSV fails to download | Network issue or GitHub rate limit | CSV is cached in `data/raw/` after first successful download |
| NDC API returns empty | Network issue or API downtime | App continues with gap = green_score for all countries |
| Uploaded file columns not recognized | Column names don't match expected patterns | Check normalization: names are lowercased, underscores for spaces. Check `_detect_alternative_columns()` in `upload_preprocessor.py` |

---

## License

MIT — see [LICENSE](LICENSE) (or the [MIT template](https://opensource.org/licenses/MIT)).

---

<div align="center">
  <sub>Data from <a href="https://github.com/owid/energy-data">Our World in Data</a> and <a href="https://www.climatewatchdata.org/">Climate Watch</a>.</sub>
</div>
