# Python Cloudflare Analytics Client

A Python client for interacting with the [Cloudflare GraphQL Analytics API](https://developers.cloudflare.com/analytics/graphql-api/).

> **Note:** The official Cloudflare Python library does not support the GraphQL Analytics API endpoints. This library provides dedicated support for querying Cloudflare analytics data.

## Installation

```bash
uv add cloudflare-analytics
```

## Usage

```python
from cloudflare_analytics import client

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
    },
    api_token="your_cloudflare_api_token"
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
