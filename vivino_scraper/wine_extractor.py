from abc import ABC, abstractmethod
from typing import Dict, Any, Union, Optional 
from utils import vivino_build_url_vintage
from bs4 import BeautifulSoup
from price_parser import Price
from .requester import make_request
import json
import unicodedata
import requests
import re
import traceback
class VivinoScraper:

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
    
    def get_wine_info(self, wine_url: str, year: Optional[Union[int, str]] = None, country: Optional[str] = "US", proxies=None) -> Dict[str, Any]:
        if year:
            wine_url = vivino_build_url_vintage(wine_url, year, country)
            vintage = year
        else:
            vintage = "NV"
            wine_url = vivino_build_url_vintage(wine_url, country)
        response = make_request(url = wine_url, proxies=proxies, method="GET")
        text = response.text
        json_wine_data = re.search(
                r"<script[^>]*type=['\"]application/ld\+json['\"][^>]*>(.*?)</script>",
                text,
                re.DOTALL | re.IGNORECASE
            )
        soup = BeautifulSoup(text, 'html.parser')
        price = soup.select_one('span[class*="purchaseAvailability__currentPrice"]')
        if price:
            price = Price.fromstring(price.get_text(strip=True)).amount
        rating = soup.select_one('div[class*="vivinoRating_averageValue"]')
        if rating:
            rating = rating.get_text(strip=True)
        else:
            rating = None
        data = {}
        wine_searcher_name = soup.select_one('div[class*="wineHeadline"]')
        if wine_searcher_name:
            wine_searcher_name = wine_searcher_name.get_text()
            wine_searcher_name = re.sub(r'\d+', '', wine_searcher_name)
        if json_wine_data:
            try:
                ld_json = json.loads(json_wine_data.group(1).strip())
                data['url'] = ld_json.get('url')
                if 'offers' in ld_json:
                    data['price'] = ld_json.get('offers', {}).get('price')
                    data['priceCurrency'] = ld_json.get('offers', {}).get('priceCurrency')
                else:
                    if price is None:
                        data['price'] = None
                        data['priceCurrency'] = None
                    else:
                        data['price'] = price
                        data['priceCurrency'] = getattr(price, 'currency', None)
                data['ratingValue'] = ld_json.get('aggregateRating', {}).get('ratingValue') if 'aggregateRating' in ld_json else rating
                data['name'] = unicodedata.normalize('NFKD', ld_json.get('name')).encode('ascii', 'ignore').decode('ascii')
                data['images'] = ld_json.get('image')
                data['Product'] = ld_json.get('@type')
                data['Product_name'] = unicodedata.normalize('NFKD', ld_json.get('name')).encode('ascii', 'ignore').decode('ascii')
                data['vintage'] = vintage
                print(wine_searcher_name, "wine_searcher_name")
                data['wine_searcher_url'] = f"http://www.wine-searcher.com/find/{wine_searcher_name.lower().rstrip().replace(' ', '+')}/{vintage}"
                data.update(self._get_wine_types(soup))
            except Exception as e:
                traceback.print_exc()
                return None
        print(data,"asdsad")
        return data