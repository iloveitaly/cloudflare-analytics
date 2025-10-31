"""Tests for CloudflareAnalyticsClient."""

import pytest
from unittest.mock import Mock, patch
import httpx
from cloudflare_analytics import CloudflareAnalyticsClient, GraphQLResponse


def test_client_initialization():
    """Test client initialization with valid token."""
    client = CloudflareAnalyticsClient(api_token="test_token")
    assert client.api_token == "test_token"
    assert client.base_url == "https://api.cloudflare.com/client/v4"


def test_client_initialization_without_token():
    """Test client initialization fails without token."""
    with pytest.raises(ValueError, match="API token must be provided"):
        CloudflareAnalyticsClient(api_token="")


def test_graphql_response_model():
    """Test GraphQLResponse model."""
    response = GraphQLResponse(data={"viewer": {}}, errors=None)
    assert response.data == {"viewer": {}}
    assert response.errors is None

    error_response = GraphQLResponse(data=None, errors=[{"message": "error"}])
    assert error_response.data is None
    assert error_response.errors == [{"message": "error"}]


@patch("httpx.post")
def test_query_success(mock_post):
    """Test successful GraphQL query."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"viewer": {"accounts": []}},
        "errors": None,
    }
    mock_post.return_value = mock_response

    client = CloudflareAnalyticsClient(api_token="test_token")
    query = "query { viewer { accounts { id } } }"

    response = client.query(query)

    assert response.data == {"viewer": {"accounts": []}}
    assert response.errors is None
    mock_post.assert_called_once()


@patch("httpx.post")
def test_query_with_variables(mock_post):
    """Test GraphQL query with variables."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"viewer": {"accounts": [{"id": "123"}]}},
        "errors": None,
    }
    mock_post.return_value = mock_response

    client = CloudflareAnalyticsClient(api_token="test_token")
    query = "query GetAccount($id: String!) { viewer { accounts(filter: {id: $id}) { id } } }"
    variables = {"id": "123"}

    response = client.query(query, variables=variables)

    assert response.data == {"viewer": {"accounts": [{"id": "123"}]}}
    call_args = mock_post.call_args
    assert call_args[1]["json"]["variables"] == variables


@patch("httpx.post")
def test_query_with_errors(mock_post):
    """Test GraphQL query that returns errors."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": None,
        "errors": [{"message": "Authentication required"}],
    }
    mock_post.return_value = mock_response

    client = CloudflareAnalyticsClient(api_token="test_token")
    query = "query { viewer { accounts { id } } }"

    response = client.query(query)

    assert response.data is None
    assert response.errors == [{"message": "Authentication required"}]


@patch("httpx.post")
def test_query_http_error(mock_post):
    """Test query handles HTTP errors with retry."""
    mock_post.side_effect = httpx.HTTPStatusError(
        "500 Server Error", request=Mock(), response=Mock(status_code=500)
    )

    client = CloudflareAnalyticsClient(api_token="test_token")
    query = "query { viewer { accounts { id } } }"

    with pytest.raises(httpx.HTTPStatusError):
        client.query(query)

    assert mock_post.call_count == 6


@patch("httpx.post")
def test_request_headers(mock_post):
    """Test that proper headers are sent with requests."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {}, "errors": None}
    mock_post.return_value = mock_response

    client = CloudflareAnalyticsClient(api_token="test_token_123")
    client.query("query { viewer { accounts { id } } }")

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer test_token_123"


@patch("httpx.post")
def test_request_url(mock_post):
    """Test that requests are sent to correct URL."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {}, "errors": None}
    mock_post.return_value = mock_response

    client = CloudflareAnalyticsClient(api_token="test_token")
    client.query("query { viewer { accounts { id } } }")

    call_args = mock_post.call_args
    assert call_args[0][0] == "https://api.cloudflare.com/client/v4/graphql"
