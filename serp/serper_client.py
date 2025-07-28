import requests
import json
from .exception import ExternalAPIException
from .config import SERPER_API_KEY, DEFAULT_COUNTRY, DEFAULT_INCLUDE_MARKDOWN, GOOGLE_SEARCH_ENDPOINT, WEBPAGE_SCRAPE_ENDPOINT

class SerperClient:
    """
    A unified client for Serper API services including Google search and webpage scraping.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the SerperClient with an API key.
        
        Args:
            api_key (str, optional): The Serper API key for authentication. 
                                   If not provided, uses the default from config.
        """
        self.api_key = api_key or SERPER_API_KEY
        self.base_headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def google_search(self, query, keywords="", country=None):
        """
        Perform a Google search using Serper API.
        
        Args:
            query (str): The search query
            keywords (str): Additional keywords to append to the query
            country (str): Country code for localized search (default: from config)
            
        Returns:
            dict: Search result with title, link, and position, or None if not found
            
        Raises:
            ExternalAPIException: If the API request fails
        """
        country = country or DEFAULT_COUNTRY
        url = GOOGLE_SEARCH_ENDPOINT
        payload = json.dumps({
            "q": query + " " + keywords if keywords else query,
            "gl": country
        })
        
        try:
            response = requests.post(url, headers=self.base_headers, data=payload)
        except requests.exceptions.RequestException as e:
            raise ExternalAPIException(f"Failed to fetch Google search results: {str(e)}")
        
        if response.status_code != 200:
            raise ExternalAPIException(f"Failed to fetch Google search results: {response.status_code} {response.text}")
        
        data = response.json()
        for item in data.get("organic", []):
            if keywords.lower() in item.get("link", "").lower():
                return {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "position": item.get("position")
                }
        return None
    
    def scrape_webpage(self, url, include_markdown=None):
        """
        Scrape a webpage using Serper API.
        
        Args:
            url (str): The URL to scrape
            include_markdown (bool): Whether to include markdown in the response (default: from config)
            
        Returns:
            dict: The scraped webpage data
            
        Raises:
            ExternalAPIException: If the API request fails
        """
        include_markdown = include_markdown if include_markdown is not None else DEFAULT_INCLUDE_MARKDOWN
        serper_url = WEBPAGE_SCRAPE_ENDPOINT
        payload = json.dumps({
            "url": url,
            "includeMarkdown": include_markdown
        })
        
        try:
            response = requests.post(serper_url, headers=self.base_headers, data=payload)
        except requests.exceptions.RequestException as e:
            raise ExternalAPIException(f"Failed to scrape webpage: {str(e)}")
        
        if response.status_code != 200:
            raise ExternalAPIException(f"Failed to scrape webpage: {response.status_code} {response.text}")
        
        return response.json()
    
    def search_and_scrape(self, query, keywords="", country=None, include_markdown=None):
        """
        Perform a Google search and scrape the first matching result.
        
        Args:
            query (str): The search query
            keywords (str): Additional keywords to filter results
            country (str): Country code for localized search (default: from config)
            include_markdown (bool): Whether to include markdown in the scraped content (default: from config)
            
        Returns:
            dict: Combined search and scrape result, or None if no search result found
            
        Raises:
            ExternalAPIException: If any API request fails
        """
        # First, perform the search
        search_result = self.google_search(query, keywords, country)
        
        if not search_result:
            return None
        
        # Then, scrape the found URL
        try:
            scraped_content = self.scrape_webpage(search_result["link"], include_markdown)
            
            # Combine the results
            return {
                "search_result": search_result,
                "scraped_content": scraped_content
            }
        except ExternalAPIException as e:
            # If scraping fails, still return the search result
            return {
                "search_result": search_result,
                "scraped_content": None,
                "scrape_error": str(e)
            } 