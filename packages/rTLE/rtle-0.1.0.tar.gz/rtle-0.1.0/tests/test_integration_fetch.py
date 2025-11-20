# tests/test_integration_fetch.py
import pytest
from rtle import fetch_tle
from rtle.exceptions import NoNoradProvidedError, TLEFetchError

def test_no_norad_raises():
    with pytest.raises(NoNoradProvidedError):
        fetch_tle([])

def test_fetch_iss_real():
    # this test will perform a real HTTP request; may fail if network/site blocks
    result = fetch_tle([39634])
    assert 39634 in result
    line1, line2 = result[39634]
    assert line1.startswith("1 "), "Line 1 looks wrong"
    assert line2.startswith("2 "), "Line 2 looks wrong"
