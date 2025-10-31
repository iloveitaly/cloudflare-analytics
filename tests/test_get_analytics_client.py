"""Tests for get_analytics_client helper function."""

from cloudflare_analytics import get_analytics_client, CloudflareAnalyticsClient


def test_get_analytics_client_creates_instance():
    """Test that get_analytics_client creates a client instance."""
    import cloudflare_analytics.client

    cloudflare_analytics.client._analytics_client = None

    client = get_analytics_client(api_token="test_token")

    assert isinstance(client, CloudflareAnalyticsClient)
    assert client.api_token == "test_token"


def test_get_analytics_client_returns_singleton():
    """Test that get_analytics_client returns the same instance."""
    import cloudflare_analytics.client

    cloudflare_analytics.client._analytics_client = None

    client1 = get_analytics_client(api_token="test_token")
    client2 = get_analytics_client(api_token="different_token")

    assert client1 is client2
    assert client1.api_token == "test_token"
