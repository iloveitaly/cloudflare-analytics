"""
Cloudflare Analytics GraphQL API client.

API docs: https://developers.cloudflare.com/analytics/graphql-api/
"""

import logging

from .client import CloudflareAnalyticsClient, GraphQLResponse, get_analytics_client

log = logging.getLogger(__name__)

__all__ = [
    "CloudflareAnalyticsClient",
    "GraphQLResponse",
    "get_analytics_client",
]
