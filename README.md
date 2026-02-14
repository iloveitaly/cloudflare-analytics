# Python Cloudflare Analytics Client

[![Release Notes](https://img.shields.io/github/release/iloveitaly/cloudflare-analytics)](https://github.com/iloveitaly/cloudflare-analytics/releases)
[![Downloads](https://static.pepy.tech/badge/cloudflare-analytics/month)](https://pepy.tech/project/cloudflare-analytics)
![GitHub CI Status](https://github.com/iloveitaly/cloudflare-analytics/actions/workflows/build_and_publish.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client for interacting with the [Cloudflare GraphQL Analytics API](https://developers.cloudflare.com/analytics/graphql-api/).

> **Note:** The official Cloudflare Python library does not support the GraphQL Analytics API endpoints. This library provides dedicated support for querying Cloudflare analytics data.

## Installation

```bash
uv add cloudflare-analytics
```

## Usage

There are two ways to initialize the client:

### Option 1: Global Client (Recommended)

`get_analytics_client` returns a globally cached singleton instance. It also automatically checks for the `CLOUDFLARE_API_TOKEN` environment variable if no token is passed.

```python
from cloudflare_analytics import get_analytics_client

# Uses CLOUDFLARE_API_TOKEN environment variable by default
client = get_analytics_client()

# Or pass it explicitly
client = get_analytics_client(api_token="your_cloudflare_api_token")
```

### Option 2: Manual Instantiation

Use `CloudflareAnalyticsClient` directly if you need to manage multiple instances with different tokens or prefer to avoid global state.

```python
from cloudflare_analytics import CloudflareAnalyticsClient

client = CloudflareAnalyticsClient(api_token="your_cloudflare_api_token")
```

### Executing a Query

Once you have a client instance, you can execute GraphQL queries:

```python
# Execute a GraphQL query
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
    print(f"Errors: {response.errors}")
elif response.data:
    groups = response.data["viewer"]["accounts"][0]["streamMinutesViewedAdaptiveGroups"]
    for group in groups:
        minutes = group["sum"]["minutesViewed"]
        date = group["dimensions"]["date"]
        print(f"Date: {date}, Minutes: {minutes}")
```

## Features

- Simple, clean API for Cloudflare GraphQL Analytics
- Built-in retry logic with exponential backoff
- Type-safe responses using Pydantic models
- Comprehensive error handling


## [MIT License](LICENSE.md)

---

*This project was created from [iloveitaly/python-package-template](https://github.com/iloveitaly/python-package-template)*
