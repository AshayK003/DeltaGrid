"""Climate Watch NDC API client."""

import logging
import re

import requests

from src.config import CACHE_TTL_API, CLIMATE_WATCH_NDC_URL
from src.data.cache import read_cache, write_cache
from src.data.country_codes import normalize_iso3

logger = logging.getLogger(__name__)


def _parse_ghg_percentage(text: str) -> float | None:
    """Extract numeric percentage from NDC target text.

    Handles: "33 to 35 percent", "45%", "47 percent", "40 per cent"
    Returns the midpoint for ranges, or the single value.
    """
    if not text or not isinstance(text, str):
        return None

    # Range: "33 to 35 percent"
    range_pattern = (
        r"(\d+\.?\d*)\s*(?:to|-)\s*(\d+\.?\d*)\s*"
        r"(?:percent|per\s*cent|%)"
    )
    range_match = re.search(range_pattern, text, re.IGNORECASE)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
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
            if isinstance(value, str):
                ndc_info["ghg_target"] = _parse_ghg_percentage(value)
            elif isinstance(value, (int, float)):
                ndc_info["ghg_target"] = float(value)
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
    """Fetch all NDCs in a single API call. Returns iso3 → ndc_info."""
    cache_key = "ndc_all_bulk"
    cached = read_cache(cache_key, CACHE_TTL_API)
    if cached is not None:
        logger.info("Loaded NDCs from cache (%d countries)", len(cached))
        return cached

    logger.info("Fetching all NDCs from Climate Watch API")
    try:
        resp = requests.get(CLIMATE_WATCH_NDC_URL, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        logger.error("Failed to fetch NDCs: %s", e)
        return {}
    except ValueError as e:
        logger.error("Failed to parse NDC response: %s", e)
        return {}

    result: dict[str, dict] = {}
    for entry in data.get("data", []):
        iso3 = normalize_iso3(entry.get("iso_code3", ""))
        if not iso3:
            continue
        ndc = _parse_ndc_entry(entry, iso3)
        if ndc:
            result[iso3] = ndc

    logger.info("Parsed NDCs for %d countries", len(result))
    write_cache(cache_key, result)
    return result
