"""
Configuration management for rTLE.

This module loads and manages the default configuration, which includes
the public TLE data source URL.
"""

DEFAULT_CONFIG = {
    "data_source_url": "https://celestrak.org/NORAD/elements/gp.php?CATNR="
}

def get_config():
    """
    Returns the default configuration dictionary.
    """
    return DEFAULT_CONFIG.copy()

def set_data_source_url(new_url: str):
    """
    Allows runtime modification of the TLE data source URL.
    """
    DEFAULT_CONFIG["data_source_url"] = new_url
