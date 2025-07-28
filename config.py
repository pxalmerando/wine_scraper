from dotenv import load_dotenv
import os
from dataclasses import dataclass
from typing import Dict, List

load_dotenv()

@dataclass
class OutputConfig:
    COOKIES_FILE: str = "cookies/wine_searcher_cookies.json"
    SCREENSHOT_FILE_AUTH_WINE_SEARCHER: str = "process_tracker_img/authentication/login.png"
    LOG_FILE: str = "wine.logs"

@dataclass
class BrowserOptions:
    HEADLESS: bool = False
    BLOCK_IMAGE: bool = True
    SELENIUM_WAIT: int = 10
    UK: bool = False
    VIVINO_PROXIES:str = os.getenv("VIVINO_PROXIES")




class AppConfig:
    def __init__(self):
        # API Configuration
        self.ZENROW_API_KEY = os.getenv("ZENROWS_API_KEY")
        self.SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # Add SerpAPI key
        self.ZENROW_BASE_URL = "https://api.zenrows.com/v1/"
        self.PROXY_COUNTRY = "gb"
        self.SESSION_ID = "1"

        # Wine Searcher Credentials
        self.WINE_SEARCHER_USERNAME = os.getenv("WINE_SEARCHER_USERNAME")
        self.WINE_SEARCHER_PASSWORD = os.getenv("WINE_SEARCHER_PASSWORD")
        self.WINE_SEARCHER_URL = "https://www.wine-searcher.com"
        self.SERPAPI_KEY = os.getenv("SERP_API_KEY")
        # Output Configuration
        self.OUTPUT = OutputConfig()

        # Browser Configuration
        self.BROWSER_OPTIONS = BrowserOptions()

    def validate(self):
        """Validate required configuration"""
        if not self.ZENROW_API_KEY:
            raise ValueError("ZENROW_API_KEY is not set in environment variables")
        if not self.WINE_SEARCHER_USERNAME or not self.WINE_SEARCHER_PASSWORD:
            raise ValueError("Wine Searcher credentials are not set in environment variables")
