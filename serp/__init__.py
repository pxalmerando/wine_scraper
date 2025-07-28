"""
Serper API client package for Google search and webpage scraping.
"""

from .serper_client import SerperClient
from .google import google_search
from .webpage import scrape_webpage_example
from .config import SERPER_API_KEY

__all__ = [
    'SerperClient',
    'google_search',
    'scrape_webpage_example',
    'SERPER_API_KEY'
]
