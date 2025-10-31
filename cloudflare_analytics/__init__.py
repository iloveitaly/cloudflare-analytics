"""
Cloudflare Analytics GraphQL API client.

API docs: https://developers.cloudflare.com/analytics/graphql-api/
"""

import logging
import os

from .client import CloudflareAnalyticsClient, GraphQLResponse, get_analytics_client

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
)

logger = logging.getLogger(__name__)

__all__ = [
    "CloudflareAnalyticsClient",
    "GraphQLResponse",
    "get_analytics_client",
]


def main():
    logger.info("Cloudflare Analytics Client - use as a library")
