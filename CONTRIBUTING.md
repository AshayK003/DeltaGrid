# Contributing to DeltaGrid

Thank you for your interest in contributing to DeltaGrid! This document provides guidelines and workflows for contributing to the project.

## Development Workflow

### Prerequisites

- Python **3.10+** (tested on 3.12)
- pip
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/AshayK003/DeltaGrid.git
cd DeltaGrid

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"      # dev tools (ruff, mypy, pytest)
```

### Development Commands

```bash
make install     # pip install -r requirements.txt + dev extras
make test        # pytest tests/ -v (123 tests)
make lint        # ruff check src/ app/
make typecheck   # mypy src/ app/ (strict mode)
make serve       # streamlit run app/main.py
make clean       # remove __pycache__, .pytest_cache, .mypy_cache, .ruff_cache
```

### Running the Application

```bash
streamlit run app/main.py
```

Open [http://localhost:8501](http://localhost:8501).

## Contribution Process

1. **Read the project structure** — review `src/` and `app/` to understand the architecture before making changes
2. **Open an issue** first for any non-trivial change
3. **Branch** from `master`: `git checkout -b feat/your-feature`
4. **Write tests first** for new functions (fixtures, edge cases, error paths)
5. **Run the full suite** before opening a PR:
   ```bash
   make lint && make typecheck && make test
   ```
6. **Keep dependencies lean** — no new dependency without discussion. The 5-dependency constraint is deliberate

## Picking a Good First Issue (GFI)

Good First Issues are labeled with `good first issue` in the issue tracker. These are ideal for new contributors:

- **Scope**: Small, well-defined changes
- **Impact**: Improves documentation, fixes minor bugs, or adds small features
- **Complexity**: Low risk, minimal dependencies on other parts of the codebase

### How to Claim a GFI

1. Browse issues labeled `good first issue`
2. Comment on the issue to express interest: "I'd like to work on this"
3. Wait for maintainer confirmation
4. Create a branch following the naming convention: `git checkout -b fix/issue-number` or `feat/issue-number`
5. Implement the change with tests
6. Open a PR referencing the issue

## Code Style

- **Ruff linting** (E, F, I, N, W, UP rulesets). Run `make lint` before commit
- **mypy strict mode**. Run `make typecheck` before commit
- **No comments on obvious code** — prefer readable names over explanatory comments
- **Function composition over inheritance**
- **No unnecessary abstractions** — "keep it boring"

## Commit Message Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(scoring): add weighted green score normalization

Fixes #123

The new normalization divides by max(all_weights) instead of
score.max() * 100, ensuring slider changes rescale the entire map.
```

```
fix(data): handle missing ISO codes in upload preprocessor

Previously, missing ISO codes would cause a KeyError. Now they are
logged and skipped with a warning message.
```

```
docs: update contributing guidelines with GFI section

Added section on how to pick and claim Good First Issues.
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run a specific module
pytest tests/test_scoring.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### Test Coverage by Module

| Module | Tests | What it covers |
|--------|-------|----------------|
| `test_scoring.py` | 9 | Empty/NaN/single-row DataFrames, zero weights, range bounds, mutation safety |
| `test_gap.py` | 6 | Positive/negative gaps, missing NDCs, invalid years, NaN scores, empty input |
| `test_ranking.py` | 17 | Boundary classifications (exactly 5, 0, -5), empty results, missing columns |
| `test_climate_watch.py` | 21 | Percent parser (range/dash/float/keyword), network failures, cache behavior |
| `test_cache.py` | 10 | TTL expiry, corrupted JSON, key sanitization, empty dir |
| `test_country_codes.py` | 17 | ISO normalization, aggregates, whitespace, mixed case |
| `test_owid.py` | 4 | Year range, CSV loading, aggregate filtering |
| `test_upload_preprocessor.py` | 33 | Encoding, column normalization, ISO mapping, alternative columns, full pipeline |
| `test_integration.py` | 5 | End-to-end pipeline, weight-specific rankings, NDC-less countries |

### Writing Tests

- Write tests before implementing new features (TDD approach)
- Cover edge cases: empty inputs, NaN values, boundary conditions
- Use fixtures for common test data
- Ensure all tests pass before submitting a PR

## Project Structure

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
│       ├── _shared.py      # Cached analysis wrapper + load_energy_data()
│       ├── 1_gap_analysis.py
│       ├── 2_rankings.py
│       └── 3_methodology.py
├── src/
│   ├── config.py           # Constants, column names, default weights, thresholds
│   ├── pipeline.py         # AnalysisResult dataclass, run_analysis() orchestrator
│   ├── data/
│   │   ├── owid.py         # OWID CSV download and filtering
│   │   ├── climate_watch.py# NDC bulk fetch + _parse_ghg_percentage()
│   │   ├── cache.py        # TTL disk cache (JSON files)
│   │   ├── country_codes.py# ISO normalization, aggregate detection
│   │   └── upload_preprocessor.py
│   └── models/
│       ├── scoring.py      # compute_green_score(weights required)
│       ├── gap.py          # compute_gap() with vectorized interpolation
│       └── ranking.py      # classify_gap(), classify_countries()
├── tests/                  # 123 tests across 9 modules
├── data/
│   ├── raw/                # OWID CSV (gitignored — downloaded on first run)
│   └── cache/              # JSON cache files (gitignored)
└── .streamlit/config.toml  # Dark theme, headless mode
```

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the `question` label
- Start a discussion in the GitHub Discussions tab
- Contact the maintainers

Thank you for contributing to DeltaGrid! 🌍
