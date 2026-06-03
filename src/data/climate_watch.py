"""Climate Watch NDC API client."""

import re

import requests

from src.config import CACHE_TTL_API, CLIMATE_WATCH_NDC_URL
from src.data.cache import read_cache, write_cache
from src.data.country_codes import normalize_iso3


def _parse_ghg_percentage(text: str) -> float | None:
    """Extract numeric percentage from NDC target text.

    Handles formats like:
      - "33 to 35 percent"
      - "45%"
      - "47 percent"
      - "40 per cent"
    Returns the midpoint for ranges, or the single value.
    """
    if not text or not isinstance(text, str):
        return None

    # Range: "33 to 35 percent"
    range_pattern = r"(\d+\.?\d*)\s*(?:to|-)\s*(\d+\.?\d*)\s*(?:percent|per\s*cent|%)"
    range_match = re.search(range_pattern, text, re.IGNORECASE)
    if range_match:
        low, high = float(range_match.group(1)), float(range_match.group(2))
        return (low + high) / 2

    # Single: "45%", "47 percent", "40 per cent"
    single_pattern = r"(\d+\.?\d*)\s*(?:percent|per\s*cent|%)"
    single_match = re.search(single_pattern, text, re.IGNORECASE)
    if single_match:
        return float(single_match.group(1))

    # Bare number with "percent" context nearby
    bare_match = re.search(r"(\d+\.?\d*)", text)
    keywords = ["percent", "per cent", "%", "reduction", "mitigate"]
    if bare_match and any(kw in text.lower() for kw in keywords):
        return float(bare_match.group(1))

    return None


def fetch_ndc(iso3: str) -> dict | None:
    """Fetch NDC data for a country from Climate Watch API.

    Returns dict with keys:
      ghg_target, ghg_target_type, pledge_base_year, pledge_target_year,
      conditionality, mitigation_contribution_type, raw_text
    Or None if no data.
    """
    code = normalize_iso3(iso3)
    cache_key = f"ndc_{code}"
    cached = read_cache(cache_key, CACHE_TTL_API)
    if cached is not None:
        return cached

    try:
        resp = requests.get(
            CLIMATE_WATCH_NDC_URL,
            params={"location": code},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    results = data.get("data", [])
    if not results:
        return None

    # Take the first (most recent) entry
    entry = results[0]

    # Extract key fields
    ndc_info: dict = {
        "iso_code": code,
        "raw_text": entry.get("ndc_text", ""),
        "ghg_target": None,
        "ghg_target_type": None,
        "pledge_base_year": None,
        "pledge_target_year": None,
        "conditionality": None,
        "mitigation_contribution_type": None,
    }

    # Parse indicators from the NDC data
    indicators = entry.get("indicators", [])
    for ind in indicators:
        name = ind.get("name", "").lower()
        value = ind.get("value", "")
        if "ghg" in name and "target" in name:
            parsed = _parse_ghg_percentage(value) if isinstance(value, str) else value
            ndc_info["ghg_target"] = parsed
        elif "target" in name and "type" in name:
            ndc_info["ghg_target_type"] = value
        elif "base" in name and "year" in name:
            ndc_info["pledge_base_year"] = value
        elif "target" in name and "year" in name:
            ndc_info["pledge_target_year"] = value
        elif "conditionality" in name:
            ndc_info["conditionality"] = value
        elif "mitigation" in name and "contribution" in name:
            ndc_info["mitigation_contribution_type"] = value

    write_cache(cache_key, ndc_info)
    return ndc_info


def get_all_ndc_iso_codes() -> list[str]:
    """Return list of all countries with NDC submissions."""
    cache_key = "ndc_all_iso"
    cached = read_cache(cache_key, CACHE_TTL_API)
    if cached is not None:
        return cached

    try:
        resp = requests.get(CLIMATE_WATCH_NDC_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    codes = [
        normalize_iso3(entry.get("iso_code3", ""))
        for entry in data.get("data", [])
        if entry.get("iso_code3")
    ]
    write_cache(cache_key, codes)
    return codes


def _parse_ndc_entry(entry: dict, code: str) -> dict | None:
    """Parse a single NDC API entry into our dict format."""
    indicators = entry.get("indicators", [])
    if not indicators:
        return None

    ndc_info: dict = {
        "iso_code": code,
        "raw_text": entry.get("ndc_text", ""),
        "ghg_target": None,
        "ghg_target_type": None,
        "pledge_base_year": None,
        "pledge_target_year": None,
        "conditionality": None,
        "mitigation_contribution_type": None,
    }

    for ind in indicators:
        name = ind.get("name", "").lower()
        value = ind.get("value", "")
        if "ghg" in name and "target" in name:
            parsed = _parse_ghg_percentage(value) if isinstance(value, str) else value
            ndc_info["ghg_target"] = parsed
        elif "target" in name and "type" in name:
            ndc_info["ghg_target_type"] = value
        elif "base" in name and "year" in name:
            ndc_info["pledge_base_year"] = value
        elif "target" in name and "year" in name:
            ndc_info["pledge_target_year"] = value
        elif "conditionality" in name:
            ndc_info["conditionality"] = value
        elif "mitigation" in name and "contribution" in name:
            ndc_info["mitigation_contribution_type"] = value

    return ndc_info


def fetch_all_ndcs() -> dict[str, dict]:
    """Fetch all NDCs in a single API call. Returns dict of iso3 → ndc_info."""
    cache_key = "ndc_all_bulk"
    cached = read_cache(cache_key, CACHE_TTL_API)
    if cached is not None:
        return cached

    try:
        resp = requests.get(CLIMATE_WATCH_NDC_URL, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return {}

    result: dict[str, dict] = {}
    for entry in data.get("data", []):
        iso3 = normalize_iso3(entry.get("iso_code3", ""))
        if not iso3:
            continue
        ndc = _parse_ndc_entry(entry, iso3)
        if ndc:
            result[iso3] = ndc
            write_cache(f"ndc_{iso3}", ndc)

    write_cache(cache_key, result)
    return result
