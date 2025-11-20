"""
Custom exceptions used in the rTLE package.
"""

class RTLEError(Exception):
    """Base exception for rTLE package."""
    pass

class NoNoradProvidedError(RTLEError):
    """Raised when no NORAD ID is provided."""
    pass

class TLEFetchError(RTLEError):
    """Raised when TLE data cannot be retrieved."""
    pass
