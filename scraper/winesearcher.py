import requests
from typing import Dict, Optional, Union, List, Any
from bs4 import BeautifulSoup
from .base import BaseWineScraper
from price_parser import Price
from .url_builder import WineSearcherUrlBuilder
from dotenv import load_dotenv
from ..utils.helper import get_cookie_header
import os
load_dotenv()
class WineSearcherScraper(BaseWineScraper):
    def __init__(
        self,
        cookies: Optional[List[Dict[str, Any]]] = None,
        country: Optional[str] = 'UK',
        proxies: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
    ):
        """Create a new WineSearcherScraper.

        Args:
            cookies: Optional cookies to forward to Wine-Searcher via ZenRows.
            proxies: Optional proxy or list of proxies to rotate through (passed to
                     BaseWineScraper for parity with other scrapers).
        """

        # Initialise the base class first so that ``session``, ``headers`` and
        # logging are correctly configured.
        super().__init__(proxies)

        # Instance-specific attributes.
        self.cookies = cookies
        if country.lower() == "uk":
            self.url_builder = WineSearcherUrlBuilder(country="gb")
        else:
            self.url_builder = WineSearcherUrlBuilder(country="us")
        # Store original parameters for rebuilding URLs when running the
        # vintage-fallback logic.
        self.original_params: Dict[str, str] = {}

        # Cache the ZenRows API key so we can quickly validate presence without
        # repeatedly hitting the environment on every request.
        self.apikey: Optional[str] = os.getenv("ZENROW_API_TOKEN")


    # ---------------------------------------------------------------------
    # Abstract method implementation
    # ---------------------------------------------------------------------

    def parse_wine(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """Concrete implementation required by ``BaseWineScraper``.

        This scraper overrides :py:meth:`get_wine` entirely, so *normally* this
        method is not invoked.  Nevertheless, the abstract base class mandates
        its presence.  We therefore delegate to the internal page-parsing logic
        with no specific vintage so that, should it ever be used, it will still
        return meaningful data.
        """

        return self._parse_wine_page(soup, url, None)

    def _make_request(self, url: str) -> BeautifulSoup:
        """Helper method to make the actual API request"""
        params = {
            'url': url,
            'proxy_country': self.url_builder.country.lower(),
            'apikey': os.getenv("ZENROW_API_TOKEN"),
            'custom_headers': 'true',
            'js_render': 'true',
            'premium_proxy': 'true',
        }
        headers = {
          
        }
        if self.cookies:
            headers['Cookie'] = get_cookie_header(self.cookies)
        response = requests.get('https://api.zenrows.com/v1/', params=params, headers=headers)
        return BeautifulSoup(response.text, "html.parser")

    def get_wine(self, url: str, vintage: Optional[str] = None, **kwargs) -> Dict[str, str]:
        """Fetch and parse wine data from Wine-Searcher via the ZenRows API.

        The method supports automatic fallback to previous or non-vintage wines
        when the requested vintage is unavailable.
        """

        # ------------------------------------------------------------------
        # Prepare parameters for URL construction
        # ------------------------------------------------------------------

        # WineSearcherUrlBuilder only supports the arguments below.  Strip out
        # any unsupported keys (e.g. "country") provided by the caller to
        # avoid unexpected keyword-argument errors.
        supported_builder_keys = {"state", "bottle_size", "currency", "sort_order"}
        builder_kwargs = {k: v for k, v in kwargs.items() if k in supported_builder_keys}
        # Keep a copy of the *original* parameters so that the vintage-fallback
        # logic can reconstruct alternative URLs later.
        self.original_params = {
            "url": url,
            **builder_kwargs,
        }

        if vintage is not None:
            self.original_params["vintage"] = vintage

        # ------------------------------------------------------------------
        # Build the final URL and perform the request
        # ------------------------------------------------------------------

        final_url = self.url_builder.add_shop_location(**self.original_params)
        # Validate prerequisites before making the external request.
        if not final_url or not self.apikey:
            raise ValueError("Both a valid 'url' and the 'ZENROWS_API_KEY' environment variable must be provided.")

        soup = self._make_request(final_url)
        wine_data = self._parse_wine_with_vintage_fallback(soup, final_url, vintage)
        return wine_data

    def _parse_wine_with_vintage_fallback(self, soup: BeautifulSoup, current_url: str, requested_vintage: Optional[str]) -> Dict[str, str]:
        """Handle vintage fallback logic and return parsed wine data"""
        available_vintages = self._get_available_vintages(soup)
        wine_data = {}
        new_params = self.original_params.copy()
        # Update country code if present
        if 'country' in new_params:
            country = new_params['country'].strip().lower()
            if country == 'gb':
                new_params['country'] = 'uk'
            elif country == 'us':
                new_params['country'] = 'usa'
        print(f"[DEBUG] Entered _parse_wine_with_vintage_fallback")
        print(f"[DEBUG] available_vintages: {available_vintages}")
        print(f"[DEBUG] requested_vintage: {requested_vintage}")
        
        # Case 1: No specific vintage requested - just parse what's available
        if not requested_vintage:
            print("[DEBUG] No specific vintage requested, parsing what's available (all vintage)")
            wine_data = self._parse_wine_page(soup, current_url, None)
            wine_data['benchMarkType'] = 'all vintage'
            print(f"[DEBUG] Returning wine_data (all vintage): {wine_data}")
            return wine_data if wine_data else {}

        # Case 2: Requested vintage is available
        if requested_vintage in available_vintages:
            print(f"[DEBUG] Requested vintage {requested_vintage} is available, parsing same vintage")
            wine_data = self._parse_wine_page(soup, current_url, requested_vintage)
            if wine_data:
                wine_data['benchMarkType'] = 'same vintage'
                print(f"[DEBUG] Returning wine_data (same vintage): {wine_data}")
                return wine_data

        # Case 3: Try previous vintage (year-1)
        try:
            previous_vintage = str(int(requested_vintage) - 1)
        except Exception as e:
            print(f"[DEBUG] Could not compute previous vintage from {requested_vintage}: {e}")
            previous_vintage = None

        if previous_vintage and previous_vintage in available_vintages:
            print(f"[DEBUG] Previous vintage {previous_vintage} is available, trying previous vintage")
            # Rebuild URL with previous vintage
            
            new_params['vintage'] = previous_vintage
            new_url = self.url_builder.add_shop_location(**new_params)
            print(f"[DEBUG] Requesting previous vintage URL: {new_url}")
            
            # Make new request with previous vintage
            new_soup = self._make_request(new_url)
            wine_data = self._parse_wine_page(new_soup, new_url, previous_vintage)
            if wine_data:
                wine_data['benchMarkType'] = 'previous vintage'
                print(f"[DEBUG] Returning wine_data (previous vintage): {wine_data}")
                return wine_data

        # Case 4: Try non-vintage version
        if "NV" in available_vintages:
            print("[DEBUG] NV (non-vintage) is available, trying NV")
            # Rebuild URL with NV
            
            new_params['vintage'] = "NV"
            new_url = self.url_builder.add_shop_location(**new_params)
            print(f"[DEBUG] Requesting NV vintage URL: {new_url}")
            
            # Make new request with NV
            new_soup = self._make_request(new_url)
            wine_data = self._parse_wine_page(new_soup, new_url, "NV")
            if wine_data:
                wine_data['benchMarkType'] = 'NV vintage'
                print(f"[DEBUG] Returning wine_data (NV vintage): {wine_data}")
                return wine_data

        # Case 5: Last option get All vintages
        if 'All' in available_vintages:
            country_code = 'usa' if 'us' in current_url else 'uk'
            all_vintages_url = current_url.replace(
                f'/{requested_vintage}/',
                f''
            ).replace('gb/-/', '/1/uk/-/').replace('us/-/', '/1/usa/-/')
            new_soup = self._make_request(all_vintages_url)
            print(all_vintages_url)
            wine_data = self._parse_wine_page(new_soup, all_vintages_url, None)
            if wine_data:
                wine_data['benchMarkType'] = 'all vintage'
                print(f"[DEBUG] Returning wine_data (all vintage): {wine_data}")
                return wine_data
            
    
        
        print("[DEBUG] No wine data found for any fallback case, returning empty dict")
        return {}

    def _get_lowest_price_offer(self, offers) -> Optional[Dict[str, Any]]:
        """Get the offer with the lowest price from a list of wine offers"""
        try:
            return min(
                (o for o in offers if o and isinstance(o, dict) and 'price' in o),
                key=lambda o: float(o['price'])
            ) if offers else None
        except (ValueError, TypeError):
            return None
    
    def _get_highest_price_offer(self, offers) -> Optional[Dict[str, Any]]:
        """Get the offer with the lowest price from a list of wine offers"""
        try:
            return max(
                (o for o in offers if o and isinstance(o, dict) and 'price' in o),
                key=lambda o: float(o['price'])
            ) if offers else None
        except (ValueError, TypeError):
            return None

    def _parse_wine_page(self, soup: BeautifulSoup, url: str, vintage: Optional[str]) -> Dict[str, str]:
        """Parse a wine page and return data if found"""
        wine_data = []
        shop_locations = soup.select("div.js-offers-container div.offer-card__container")
        if self.url_builder.country.lower() == 'gb':
            address_criteria ="uk"
        else:
            address_criteria ="usa"
        for shop_location in shop_locations:
            address = self._get_address(shop_location)
            if address and address_criteria in address.lower():
                price, currency = self._get_price(shop_location)
                if price and currency:
                    wine_data.append({
                        'price': price,
                        'currency': currency,
                        'url': url,
                        'vintage': vintage,
                        'wineName': self._get_wine_name(soup),
                        'taxStatus': self._get_tax_status(shop_location),
                        'offerType': self._data_type_offer(shop_location),
                    })
        lowest_price_offer = self._get_lowest_price_offer(wine_data)
        highest_price_offer = self._get_highest_price_offer(wine_data)
        print(lowest_price_offer,highest_price_offer)
        # Get the sort_order param from add_shop if present
        sort_order = None
        if hasattr(self, 'original_params') and isinstance(self.original_params, dict):
            sort_order = self.original_params.get('sort_order', None)
        elif hasattr(self, 'original_params') and hasattr(self.original_params, 'get'):
            sort_order = self.original_params.get('sort_order', None)
        if sort_order == 'lowest':
            return lowest_price_offer
        elif sort_order == 'highest':
            return highest_price_offer
        return wine_data

    def _get_available_vintages(self, soup: BeautifulSoup) -> List[str]:
        available_vintages = soup.select('div[class*="vintages-list"] a[class="btn btn-outline-primary"]')
        vintages = [vintage.get_text(strip=True) for vintage in available_vintages]
        return vintages
     

    def _get_price(self, soup: BeautifulSoup) -> tuple:
        price = soup.select_one("div.price__detail_main")
        if price:
            price = price.get_text(strip=True)
            price_obj = Price.fromstring(price)
            return price_obj.amount_float, price_obj.currency
        return None, None

    def _get_address(self, soup: BeautifulSoup) -> str:
        address = soup.select_one("div.offer-card__location-address")
        return address.get_text(strip=True) if address else None

    def _get_tax_status(self, soup: BeautifulSoup) -> str:
        tax_status = soup.select_one("div.price__tax-status")
        return tax_status.get_text(strip=True) if tax_status else None 
    
    def _data_type_offer(self, soup: BeautifulSoup) -> str:
        data_type_offer = soup.select("div[data-offer-type]")
        return ','.join([offer.get_text(strip=True) for offer in data_type_offer]) if data_type_offer else None

    def _get_wine_name(self, soup: BeautifulSoup) -> str:
        wine_name = soup.select_one("h1[data-name-id]")
        return wine_name.get_text(strip=True) if wine_name else None