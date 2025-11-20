"""
Utility functions used internally by rTLE.
"""

import re

def extract_tle(text: str):
    """
    Extracts TLE lines from raw HTML or text response.
    This is a very simple regex-based extraction.
    """
    tle_pattern = r"(1\s[0-9A-Z ]{68})\s*(2\s[0-9A-Z ]{68})"
    match = re.search(tle_pattern, text)
    if match:
        return match.group(1), match.group(2)
    return None
