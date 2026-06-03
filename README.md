# DeltaGrid

Interactive Streamlit dashboard that calculates the gap between Paris Agreement NDC pledges and actual energy trajectories for 200+ countries.

## Features

- **Green Score** — weighted composite score (0–100) based on solar, wind, hydro, nuclear, gas, and coal energy shares
- **Gap Analysis** — compares actual green score against linear NDC pledge trajectory
- **Country Rankings** — laggards, hidden champions, and full sortable table
- **Interactive Weights** — sidebar sliders to adjust energy source importance in real-time
- **World Map** — choropleth visualization of green scores and gaps by country
- **Custom Data Upload** — upload your own CSV/XLSX with automatic preprocessing (encoding detection, column normalization, ISO mapping)
- **Methodology** — transparent scoring formula and data source documentation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app/main.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Data Sources

| Source | Description | Update Frequency |
|--------|-------------|-----------------|
| [Our World in Data](https://github.com/owid/energy-data) | Energy mix by country (1900–2024) | Annual |
| [Climate Watch](https://www.climatewatchdata.org/) | NDC pledges (120+ countries) | Per submission |

## How It Works

1. **Green Score** — weighted sum of energy share columns, normalized to 0–100
2. **Gap** — difference between actual green score and expected NDC trajectory
3. **Classification** — hidden champion (>5), on track (0–5), slightly behind (-5–0), laggard (<-5)

## Project Structure

```
src/
  config.py              — constants and URLs
  data/
    owid.py              — OWID CSV ingestion
    climate_watch.py     — NDC API client
    validators.py        — data validation
    cache.py             — TTL disk cache
    country_codes.py     — ISO mapping
    upload_preprocessor.py — CSV/XLSX upload preprocessing pipeline
  models/
    scoring.py           — green score computation
    gap.py               — gap analysis
    ranking.py           — country classification
app/
  main.py                — entry point
  components/            — sidebar, choropleth, tables
  pages/                 — gap analysis, rankings, methodology
tests/                   — 121 tests (unit + integration)
```

## Development

```bash
make install    # install deps + dev tools
make test       # run 122 tests
make lint       # check code style
make serve      # start dev server
```

## License

MIT
