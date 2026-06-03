"""ISO code mapping and aggregate region detection."""

# ISO-3166-1 alpha-3 codes for countries present in OWID dataset.
# This is a representative subset; the full list is loaded from OWID at runtime.
# Aggregates are excluded from per-country analysis.

AGGREGATE_NAMES: set[str] = {
    "Africa",
    "Africa (EI)",
    "Africa (OWID)",
    "Asia",
    "Asia Pacific (EI)",
    "Asia Pacific (OWID)",
    "CIS (OWID)",
    "Central America (EI)",
    "Eastern Africa (UN)",
    "Europe",
    "Europe (other)",
    "European Union (27)",
    "High-income countries",
    "Middle Africa (UN)",
    "Middle East (EI)",
    "Middle East (OWID)",
    "North America",
    "North America (EI)",
    "North America (OWID)",
    "Oceania",
    "OECD (EI)",
    "OECD (OWID)",
    "OPEC (OWID)",
    "Other Africa (EI)",
    "Other Asia & Pacific (EI)",
    "Other CIS (OWID)",
    "Other Caribbean (EI)",
    "Other Middle East (EI)",
    "Other Northern Africa (UN)",
    "Other South America (EI)",
    "Other Southern Africa (UN)",
    "Other Southern Asia (UN)",
    "Pan America (PAHO)",
    "South & Central America (EI)",
    "South America",
    "South Asia (WB)",
    "Sub-Saharan Africa (WB)",
    "World",
    "European Union (28)",
    "High income (WB)",
    "Low income (WB)",
    "Lower middle income (WB)",
    "Upper middle income (WB)",
}


def is_aggregate(name: str) -> bool:
    """Return True if the country name is a regional/global aggregate."""
    return name in AGGREGATE_NAMES


def normalize_iso3(code: str) -> str:
    """Normalize ISO code to uppercase alpha-3."""
    if not code or not isinstance(code, str):
        return ""
    return code.strip().upper()[:3]
