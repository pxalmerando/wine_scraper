# Serper API Client

A unified Python client for Serper API services including Google search and webpage scraping.

## Features

- **Unified API Key Management**: Single API key for all Serper services
- **Google Search**: Perform Google searches with customizable parameters
- **Webpage Scraping**: Scrape webpages with markdown support
- **Combined Operations**: Search and scrape in one operation
- **Backward Compatibility**: Existing code continues to work
- **Configuration Management**: Centralized settings

## Quick Start

### Basic Usage

```python
from serp import SerperClient

# Create client with default API key from config
client = SerperClient()

# Or with custom API key
client = SerperClient("your-api-key-here")
```

### Google Search

```python
# Perform a Google search
search_result = client.google_search(
    query="wine searcher",
    keywords="chardonnay",
    country="us"
)

if search_result:
    print(f"Found: {search_result['title']}")
    print(f"URL: {search_result['link']}")
    print(f"Position: {search_result['position']}")
```

### Webpage Scraping

```python
# Scrape a webpage
url = "https://www.wine-searcher.com/find/montaignan+chard+igp+pays+d+oc+de+france"
scraped_content = client.scrape_webpage(url, include_markdown=True)
print(scraped_content)
```

### Combined Search and Scrape

```python
# Search and scrape the first result
combined_result = client.search_and_scrape(
    query="wine searcher",
    keywords="chardonnay",
    country="us",
    include_markdown=True
)

if combined_result:
    print(f"Search result: {combined_result['search_result']['title']}")
    if combined_result['scraped_content']:
        print("Successfully scraped the webpage")
```

## Configuration

Edit `config.py` to customize default settings:

```python
# API Configuration
SERPER_API_KEY = "your-api-key-here"

# Default settings
DEFAULT_COUNTRY = "us"
DEFAULT_INCLUDE_MARKDOWN = True

# API endpoints
GOOGLE_SEARCH_ENDPOINT = "https://google.serper.dev/search"
WEBPAGE_SCRAPE_ENDPOINT = "https://scrape.serper.dev"
```

## Backward Compatibility

Existing code using the old functions will continue to work:

```python
from serp import google_search

# This still works
result = google_search(api_key, query, keywords, country)
```

## Error Handling

The client uses `ExternalAPIException` for error handling:

```python
from serp import SerperClient
from serp.exception import ExternalAPIException

try:
    client = SerperClient()
    result = client.google_search("test query")
except ExternalAPIException as e:
    print(f"API Error: {e}")
```

## Examples

See `example_usage.py` for complete usage examples.

## API Reference

### SerperClient

#### `__init__(api_key=None)`
Initialize the client with an optional API key.

#### `google_search(query, keywords="", country=None)`
Perform a Google search.

#### `scrape_webpage(url, include_markdown=None)`
Scrape a webpage.

#### `search_and_scrape(query, keywords="", country=None, include_markdown=None)`
Perform a search and scrape the first result. 