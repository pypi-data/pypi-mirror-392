# tests/test_settings.py

from wefact.config import DEFAULT_API_URL

def test_default_api_url():
    assert DEFAULT_API_URL == "https://api.mijnwefact.nl/v2/"