from .base import BaseWineScraper
from bs4 import BeautifulSoup
from typing import Dict, Optional
from price_parser import Price
from utils.helper import _normalize_text
import re
from dotenv import load_dotenv
import os

load_dotenv()

class VivinoScraper(BaseWineScraper):
    def __init__(self, proxy: Optional[Dict[str, str]] = None):
        super().__init__(proxy)  # Now accepts single proxy dict instead of list

    def parse_wine(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        wine_data = {}

        # Extract headline information
        headline_element = soup.select_one('div[class*="wineHeadline"]')
        headline_name = _normalize_text(headline_element.get_text(strip=True)) if headline_element else ""
        
        # Extract vintage year
        vintage = re.search(r'\d{4}', headline_name) if headline_name else None
        wine_data['vintage'] = int(vintage.group()) if vintage else "NV"

        # Extract producer name
        producer_element = soup.select_one('div[class*="wineHeadline"] a[href*="wineries"]')
        wine_data['producerName'] = _normalize_text(producer_element.get_text(strip=True)) if producer_element else None

        # Extract wine name
        wine_name_element = soup.select_one('title')
        if wine_name_element:
            producer_name = wine_data.get('producerName') or ""
            wine_name_text = wine_name_element.get_text(strip=True)
            if producer_name:
                wine_name_text = wine_name_text.replace(producer_name, "")
            wine_name_no_year = re.sub(r'\b\d{4}\b', '', wine_name_text.strip().split("|")[0]).strip()
            wine_data['wineName'] = _normalize_text(wine_name_no_year)
        else:
            wine_data['wineName'] = None

        # Extract rating
        rating_element = soup.select_one('div[class*="vivinoRating_averageValue"]')
        wine_data['rating'] = rating_element.get_text(strip=True) if rating_element else None

        # Extract image
        image_element = soup.select_one('picture img')
        wine_data['image'] = f"https:{image_element['src']}" if image_element else None

        # Generate Wine Searcher URL
        if wine_data.get('wineName'):
            wine_data['wineSearcherUrl'] = f"https://www.wine-searcher.com/find/{wine_data['wineName'].replace(' ','+')}"
        else:
            wine_data['wineSearcherUrl'] = None

        # Extract price
        price_data = self._get_price(soup)
        wine_data['price'] = {
            'amount': price_data[0] if price_data else None,
            'currency': price_data[1] if price_data else None
        }

        # Add wine type information
        wine_data.update(self._get_wine_types(soup))
        
        wine_data['url'] = url
        return wine_data

    def _get_price(self, soup: BeautifulSoup) -> Optional[tuple]:
        price = soup.select_one('span[class*="purchaseAvailability"]')
        if price is None:
            return None
        price_text = price.get_text(strip=True)
        price_obj = Price.fromstring(price_text)
        return (price_obj.amount_float, price_obj.currency)

    def _get_wine_types(self, soup: BeautifulSoup) -> Dict:
        breadcrumbs = {}
        target_types = {
            "country": "/wine-countries/",
            "region": "/wine-regions/",
            "winery": "/wineries/",
            "winetype": "wine_type_ids[]=",
            "grape": "grape_ids[]=",
        }

        for link in soup.select('div[class*="breadCrumbs__breadCrumbs"] a[href]'):
            href = link['href']
            text = link.get_text(strip=True)
            
            for key, pattern in target_types.items():
                if key == "winetype":
                    breadcrumbs[key] = _normalize_text(text.replace("wine","").strip().title())
                if pattern in href:
                    breadcrumbs[key] = _normalize_text(text.title())
        return breadcrumbs