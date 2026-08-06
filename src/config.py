"""Project constants, URLs, column lists, and default weights."""

from pathlib import Path
from types import MappingProxyType

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CACHE_DIR = DATA_DIR / "cache"
OWID_CSV = RAW_DIR / "owid-energy-data-2010-2025.csv"

# --- URLs ---
OWID_URL = "https://github.com/owid/energy-data/raw/master/owid-energy-data.csv"
CLIMATE_WATCH_NDC_URL = "https://www.climatewatchdata.org/api/v1/ndcs"

# --- Year range ---
YEAR_MIN = 2010
YEAR_MAX = 2025

# --- Default year selection offset ---
DEFAULT_SELECTED_YEAR_OFFSET = 3

# --- OWID columns ---
ISO_COL = "iso_code"
YEAR_COL = "year"
COUNTRY_COL = "country"

ENERGY_SHARE_COLS = [
    "solar_share_energy",
    "wind_share_energy",
    "hydro_share_energy",
    "nuclear_share_energy",
    "gas_share_energy",
    "coal_share_energy",
]

ENERGY_ABSOLUTE_COLS = [
    "primary_energy_consumption",
    "solar_consumption",
    "wind_consumption",
    "hydro_consumption",
    "nuclear_consumption",
    "gas_consumption",
    "coal_consumption",
]

# --- Green score default weights (frozen) ---
DEFAULT_WEIGHTS: MappingProxyType[str, float] = MappingProxyType(
    {
        "solar_share_energy": 1.0,
        "wind_share_energy": 1.0,
        "hydro_share_energy": 1.0,
        "nuclear_share_energy": 0.5,
        "gas_share_energy": 0.2,
        "coal_share_energy": 0.0,
    }
)

# --- Cache TTL (seconds) ---
CACHE_TTL_API = 24 * 60 * 60  # 24 hours
CACHE_TTL_CSV = 7 * 24 * 60 * 60  # 7 days

# --- Gap classification thresholds ---
CLASS_THRESHOLDS = {
    "hidden_champion": 5,
    "on_track": 0,
    "slightly_behind": -5,
}

# --- Classification display ---
CLASS_COLORS = {
    "hidden_champion": "#00C853",
    "on_track": "#4CAF50",
    "slightly_behind": "#FFC107",
    "laggard": "#F44336",
    "no_data": "#9E9E9E",
}

CLASS_LABELS = {
    "hidden_champion": "Hidden Champion",
    "on_track": "On Track",
    "slightly_behind": "Slightly Behind",
    "laggard": "Laggard",
    "no_data": "No Data",
}
