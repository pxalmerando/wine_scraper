from abc import ABC, abstractmethod
from typing import Dict, Any, Union, Optional 
from typing_extensions import Optional
from services.scraper.base import BaseScraper
from services.utils.helper import vivino_build_url_vintage
from bs4 import BeautifulSoup
from price_parser import Price
from services.scraper.requester import make_request
import json
import unicodedata
import requests
import re
class VivinoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
      
    def _get_wine_types(self, soup:BeautifulSoup):
        target_types = {
            "country": "/wine-countries/",
            "region": "/wine-regions/",
            "winery": "/wineries/",
            "winetype": "wine_type_ids[]=",
            "grape": "grape_ids[]=",
        }
        breadcrumbs = {}

        for link in soup.select('.breadCrumbs__breadCrumbs--2pkcX a[href]'):
            href = link['href']
            text = link.get_text(strip=True)
            
            for key, pattern in target_types.items():
                if pattern in href:
                    breadcrumbs[key] = text
        return breadcrumbs
    
    def get_wine_info(self, wine_url: str, year: Optional[Union[int, str]] = None, country: Optional[str] = "US") -> Dict[str, Any]:
        if year:
            wine_url = vivino_build_url_vintage(wine_url, year, country)
            vintage = year
        else:
            vintage = "NV"
            wine_url = vivino_build_url_vintage(wine_url, country)
        response = make_request(wine_url, headers=self.header, method="GET")
        text = response.text
        json_wine_data = re.search(
                r"<script[^>]*type=['\"]application/ld\+json['\"][^>]*>(.*?)</script>",
                text,
                re.DOTALL | re.IGNORECASE
            )
        soup = BeautifulSoup(text, 'html.parser')
        price = soup.select_one('span[class*="purchaseAvailability__currentPrice"]').get_text(strip=True)
        price = Price.fromstring(price)
 
      
        data = {}
        if json_wine_data:
            try:
                ld_json = json.loads(json_wine_data.group(1).strip())
                data['url'] = ld_json.get('url')
                data['price'] = ld_json.get('offers', {}).get('price') if 'offers' in ld_json else price.amount
                data['priceCurrency'] = ld_json.get('offers', {}).get('priceCurrency') if 'offers' in ld_json else price.currency
                data['ratingValue'] = ld_json.get('aggregateRating', {}).get('ratingValue') if 'aggregateRating' in ld_json else None
                data['name'] = unicodedata.normalize('NFKD', ld_json.get('name')).encode('ascii', 'ignore').decode('ascii')
                data['images'] = ld_json.get('image')
                data['Product'] = ld_json.get('@type')
                data['Product_name'] = unicodedata.normalize('NFKD', ld_json.get('name')).encode('ascii', 'ignore').decode('ascii')
                data['vintage'] = vintage
                data.update(self._get_wine_types(soup))
            except:
                return None
        return data