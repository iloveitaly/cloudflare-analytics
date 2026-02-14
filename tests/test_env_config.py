import os
from unittest.mock import patch
import pytest
from cloudflare_analytics import get_analytics_client, client


def test_get_analytics_client_env_var():
    # Clear global state
    client._analytics_client = None

    with patch.dict(os.environ, {"CLOUDFLARE_API_TOKEN": "env_token"}):
        c = get_analytics_client()
        assert c.api_token == "env_token"


def test_get_analytics_client_no_token_raises_error():
    # Clear global state
    client._analytics_client = None

    with patch.dict(os.environ, {}, clear=True):
        if "CLOUDFLARE_API_TOKEN" in os.environ:
            del os.environ["CLOUDFLARE_API_TOKEN"]

        with pytest.raises(ValueError, match="API token must be provided"):
            get_analytics_client()
