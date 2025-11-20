"""
Core logic for fetching TLE data from public sources.

This module fetches TLE data for one or more NORAD IDs using the configured
data source URL. It returns a dictionary with NORAD IDs as keys and their
corresponding TLE tuples as values.
"""

import requests
from .config import get_config
from .exceptions import NoNoradProvidedError, TLEFetchError

def extract_tle(text: str):
    """
    Extracts TLE lines from plain text returned by CelesTrak.
    Returns a tuple (line1, line2) or None if not found.
    """
    lines = text.strip().splitlines()
    # find first line starting with '1' and next starting with '2'
    for i, line in enumerate(lines):
        if line.startswith("1") and i + 1 < len(lines) and lines[i + 1].startswith("2"):
            return lines[i], lines[i + 1]
    return None

def fetch_tle(norad_ids):
    """
    Fetches TLE data for the given list of NORAD IDs.

    Parameters
    ----------
    norad_ids : list[int]
        One or more NORAD catalog numbers.

    Returns
    -------
    dict
        A dictionary mapping each NORAD ID to a (line1, line2) tuple.

    Raises
    ------
    NoNoradProvidedError
        If the list is empty.
    TLEFetchError
        If the TLE could not be extracted from the source.
    """
    if not norad_ids:
        raise NoNoradProvidedError("No NORAD ID provided.")

    config = get_config()
    base_url = config["data_source_url"]

    results = {}

    for norad in norad_ids:
        url = f"{base_url}{norad}&FORMAT=TLE"  # garante que o formato seja TLE

        try:
            response = requests.get(url, timeout=10)
        except Exception as e:
            raise TLEFetchError(f"Failed to request NORAD {norad}: {e}")

        if response.status_code != 200:
            raise TLEFetchError(
                f"Failed to fetch TLE for NORAD {norad}. HTTP {response.status_code}"
            )

        tle = extract_tle(response.text)
        if tle is None:
            raise TLEFetchError(f"No TLE found for NORAD {norad}.")

        results[norad] = tle

    return results
