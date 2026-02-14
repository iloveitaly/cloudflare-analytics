"""
Cloudflare Analytics GraphQL API client.

API docs: https://developers.cloudflare.com/analytics/graphql-api/
"""

import logging
import os
from typing import Any

import httpx
from pydantic import BaseModel
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

_analytics_client: "CloudflareAnalyticsClient | None" = None


class GraphQLResponse(BaseModel):
    data: dict[str, Any] | None = None
    errors: list[dict[str, Any]] | None = None


class CloudflareAnalyticsClient:
    """
    Client for interacting with the Cloudflare GraphQL Analytics API using httpx.

    There are two ways to initialize the client:

    1. Using the global client (Recommended):
       `get_analytics_client()` returns a globally cached singleton instance and
       automatically checks the `CLOUDFLARE_API_TOKEN` environment variable.

    2. Manual instantiation:
       Use `CloudflareAnalyticsClient(api_token=...)` directly if you need to manage
       multiple instances with different tokens.

    Example usage:

        from cloudflare_analytics import get_analytics_client

        client = get_analytics_client()
        # ... or pass explicitly ...
        # client = get_analytics_client(api_token="your_token")

        query = '''
        query GetStreamMinutes($accountTag: string!, $start: Date, $end: Date) {
          viewer {
            accounts(filter: { accountTag: $accountTag }) {
              streamMinutesViewedAdaptiveGroups(
                filter: { date_geq: $start, date_lt: $end }
                orderBy: [date_ASC]
              ) {
                dimensions { date }
                sum { minutesViewed }
              }
            }
          }
        }
        '''

        response = client.query(
            query,
            variables={
                "accountTag": "your_account_id",
                "start": "2025-10-01",
                "end": "2025-10-28"
            }
        )

        if response.errors:
            logger.error("graphql errors", extra={"errors": response.errors})
        elif response.data:
            groups = response.data["viewer"]["accounts"][0]["streamMinutesViewedAdaptiveGroups"]
            for group in groups:
                minutes = group["sum"]["minutesViewed"]
                date = group["dimensions"]["date"]
                logger.info("stream data", extra={"date": date, "minutes": minutes})
    """

    def __init__(self, api_token: str):
        if not api_token:
            raise ValueError("API token must be provided.")

        self.api_token = api_token
        self.base_url = "https://api.cloudflare.com/client/v4"

    @retry(
        stop=stop_after_attempt(6),
        wait=wait_exponential(multiplier=1, min=0, max=32),
        retry=retry_if_exception_type(httpx.HTTPError),
        before_sleep=before_sleep_log(logger, logging.INFO),
        reraise=True,
    )
    def _make_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Internal method to make the HTTP POST request to the GraphQL endpoint.

        Args:
            payload: Dictionary containing query and optional variables

        Returns:
            The JSON response as a dictionary
        """
        url = f"{self.base_url}/graphql"
        headers = {"Authorization": f"Bearer {self.api_token}"}

        logger.debug(
            "cloudflare graphql request", extra={"url": url, "payload": payload}
        )

        response = httpx.post(url, json=payload, headers=headers)
        response.raise_for_status()

        json_data = response.json()
        logger.info(
            "cloudflare graphql response", extra={"status": response.status_code}
        )

        return json_data

    def query(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> GraphQLResponse:
        """Execute a GraphQL query against the Cloudflare Analytics API.

        Args:
            query: GraphQL query string
            variables: Optional variables for the query

        Returns:
            GraphQLResponse containing data or errors

        Raises:
            httpx.HTTPError: If the request fails after retries
        """
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        json_data = self._make_request(payload)

        return GraphQLResponse(
            data=json_data.get("data"), errors=json_data.get("errors")
        )


def get_analytics_client(api_token: str | None = None) -> CloudflareAnalyticsClient:
    """
    Get or create the global Cloudflare Analytics client instance.

    Args:
        api_token: Cloudflare API token. If not provided, looks for CLOUDFLARE_API_TOKEN env var.

    Returns:
        CloudflareAnalyticsClient: The configured analytics client instance
    """
    global _analytics_client

    if _analytics_client is None:
        token = api_token or os.environ.get("CLOUDFLARE_API_TOKEN")
        if not token:
            raise ValueError(
                "API token must be provided or set via CLOUDFLARE_API_TOKEN environment variable."
            )
        _analytics_client = CloudflareAnalyticsClient(api_token=token)

    return _analytics_client
