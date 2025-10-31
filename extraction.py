"""
Cloudflare Analytics GraphQL API client.

API docs: https://developers.cloudflare.com/analytics/graphql-api/
"""

import logging
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

from app import log

_analytics_client: "CloudflareAnalyticsClient | None" = None


class GraphQLResponse(BaseModel):
    data: dict[str, Any] | None = None
    errors: list[dict[str, Any]] | None = None


class CloudflareAnalyticsClient:
    """
    Client for interacting with the Cloudflare GraphQL Analytics API using httpx.

    Example usage:

        from app.lib.cloudflare import get_analytics_client

        client = get_analytics_client()

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
            log.error("graphql errors", errors=response.errors)
        elif response.data:
            groups = response.data["viewer"]["accounts"][0]["streamMinutesViewedAdaptiveGroups"]
            for group in groups:
                minutes = group["sum"]["minutesViewed"]
                date = group["dimensions"]["date"]
                log.info("stream data", date=date, minutes=minutes)
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
        before_sleep=before_sleep_log(logging.getLogger(__name__), logging.INFO),
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

        log.debug("cloudflare graphql request", url=url, payload=payload)

        response = httpx.post(url, json=payload, headers=headers)
        response.raise_for_status()

        json_data = response.json()
        log.info("cloudflare graphql response", status=response.status_code)

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
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        json_data = self._make_request(payload)

        return GraphQLResponse(
            data=json_data.get("data"), errors=json_data.get("errors")
        )


def get_analytics_client() -> CloudflareAnalyticsClient:
    """
    Get or create the global Cloudflare Analytics client instance.

    Returns:
        CloudflareAnalyticsClient: The configured analytics client instance
    """
    global _analytics_client

    if _analytics_client is None:
        from app.configuration.cloudflare import CLOUDFLARE_API_TOKEN

        _analytics_client = CloudflareAnalyticsClient(api_token=CLOUDFLARE_API_TOKEN)

    return _analytics_client