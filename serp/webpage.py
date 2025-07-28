from .serper_client import SerperClient

# Example usage of the new SerperClient class
def scrape_webpage_example(api_key, url, include_markdown=True):
    """
    Example function showing how to use the new SerperClient for webpage scraping.
    """
    client = SerperClient(api_key)
    return client.scrape_webpage(url, include_markdown)

# Example of the original code converted to use the new class
if __name__ == "__main__":
    # Your API key
    api_key = "270af4d1d0390342a75c6b1acec84521a38bede1"
    
    # Create client instance
    client = SerperClient(api_key)
    
    # Example URL to scrape
    url = "https://www.wine-searcher.com/find/montaignan+chard+igp+pays+d+oc+de+france?srsltid=AfmBOoqQifyV1_XdD4ZL2tvRtnLy10yTJaTad_y8JDZtgPntg3A66WDf"
    
    # Scrape the webpage
    result = client.scrape_webpage(url, include_markdown=True)
    print(result)