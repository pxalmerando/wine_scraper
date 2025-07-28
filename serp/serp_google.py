import requests
import json
import os
from typing import Optional, Dict, Any

class SerperAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SERPER_API_KEY')
        if not self.api_key:
            raise ValueError("API key not provided")
        self.base_headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

    def google_search(self, query: str, country_code: str = "gb") -> Optional[Dict[str, Any]]:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query, "gl": country_code})
        
        try:
            response = requests.post(url, headers=self.base_headers, data=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Search error: {e}")
            return None

    def get_first_keyword_result(self, query: str, keyword: str) -> Optional[Dict[str, Any]]:
        search_results = self.google_search(query)
        if not search_results or 'organic' not in search_results:
            return None
            
        organic_results = search_results['organic']
        keyword_results = [r for r in organic_results if keyword.lower() in r.get('link', '').lower()]
        
        return keyword_results[0] if keyword_results else organic_results[0] if organic_results else None

    def scrape_webpage(self, url: str) -> Optional[str]:
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://scrape.serper.dev",
                    headers=self.base_headers,
                    data=json.dumps({"url": url}),
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Scraping error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None