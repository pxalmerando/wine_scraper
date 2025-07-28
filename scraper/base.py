from abc import ABC, abstractmethod
import random
import logging
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from typing import Dict, Optional, Union, List
import requests
import re

class BaseWineScraper(ABC):
    def __init__(self, proxies: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None):
        self.session = requests.Session()
        self.headers = {'User-Agent': UserAgent().random}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if proxies:
            if isinstance(proxies, list):
                self.proxies = proxies
                self.current_proxy_idx = 0
            else:
                self.proxies = [proxies]
                self.current_proxy_idx = 0
        else:
            self.proxies = None

    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_proxy_idx]
        self.current_proxy_idx = (self.current_proxy_idx + 1) % len(self.proxies)
        return proxy

    def get_wine(self, url: str, max_retries: int = 2) -> Optional[Dict[str, str]]:
        try:
            proxy = self.get_next_proxy()
            request_kwargs = {'headers': self.headers, 'timeout': 30}
            if proxy:
                request_kwargs['proxies'] = proxy
                
            response = self.session.get(url, **request_kwargs)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            #404: Looks like we'll need another bottle
            error_header = soup.find('h1', class_='error-page-header')
            if error_header:
                self.logger.warning(f"Error page detected for URL: {url}")
                return self._handle_error_page(url, max_retries)
                
            return self.parse_wine(soup, url)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching wine data from {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error processing {url}: {e}", exc_info=True)
            return None

    def _handle_error_page(self, original_url: str, remaining_retries: int) -> Optional[Dict[str, str]]:
        """Handle error page by trying previous years if year is found in URL"""
        if remaining_retries <= 0:
            self.logger.warning(f"Max retries reached for URL: {original_url}")
            return None
            
        #any 4-digit year from URL
        year_match = re.search(r'/(\d{4})/', original_url)
        if not year_match:
            self.logger.warning(f"No year found in URL to retry: {original_url}")
            return None
            
        original_year = int(year_match.group(1))
        new_year = original_year - 1
            
        new_url = original_url.replace(str(original_year), str(new_year))
        
        self.logger.info(f"Getting Previous Vintage: {new_url}")
        return self.get_wine(new_url, remaining_retries - 1)

    @abstractmethod
    def parse_wine(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        pass