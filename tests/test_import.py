"""Test cloudflare-analytics."""

import cloudflare_analytics


def test_import() -> None:
    """Test that the  can be imported."""
    assert isinstance(cloudflare_analytics.__name__, str)