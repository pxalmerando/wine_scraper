"""
Example usage of the unified SerperClient class.
This demonstrates how to use both Google search and webpage scraping with a single API key.
"""

from .serper_client import SerperClient
from .config import SERPER_API_KEY

def main():
    """
    Example usage of the SerperClient class.
    """
    
    # Method 1: Use with default API key from config
    client = SerperClient()
    
    # Method 2: Use with custom API key
    # client = SerperClient("your-api-key-here")
    
    print("=== Google Search Example ===")
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
    else:
        print("No search results found")
    
    print("\n=== Webpage Scraping Example ===")
    # Scrape a specific webpage
    url = "https://www.wine-searcher.com/find/montaignan+chard+igp+pays+d+oc+de+france"
    scraped_content = client.scrape_webpage(url, include_markdown=True)
    print(f"Scraped content length: {len(str(scraped_content))} characters")
    
    print("\n=== Combined Search and Scrape Example ===")
    # Perform search and scrape the first result
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
        else:
            print(f"Scraping failed: {combined_result.get('scrape_error', 'Unknown error')}")
    else:
        print("No search results found")

if __name__ == "__main__":
    main() 