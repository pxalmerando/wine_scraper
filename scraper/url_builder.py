from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

class VivinoUrlBuilder:
    def __init__(self):
        pass

    def add_country_to_url(self, url: str, country: str = 'GB/en') -> str:
        """
        Replaces any existing country/lang (e.g. BE/en, GB/en, US/en, etc.) at the start of the path
        with the new country/lang. If not present, prepends the country/lang.
        """
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]

        # If the first two parts look like a country/lang (e.g. BE/en, GB/en, US/en, etc.), replace them
        if len(path_parts) >= 2 and len(path_parts[0]) == 2 and len(path_parts[1]) == 2:
            path_parts = [country.split('/')[0], country.split('/')[1]] + path_parts[2:]
        else:
            # Prepend the country/lang
            path_parts = [country.split('/')[0], country.split('/')[1]] + path_parts

        new_path = '/' + '/'.join(path_parts)
        existing_params = parse_qs(parsed_url.query)
        query_params = dict(existing_params)

        updated_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            new_path,
            '',  
            urlencode(query_params, doseq=True),
            ''
        ))
        return updated_url

    def add_vintage_param(self, url: str, vintage: str) -> str:
        """
        Adds or updates the 'year' parameter in the query string of the given URL.
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params['year'] = [vintage]
        new_query = urlencode(query_params, doseq=True)
        updated_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        return updated_url
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

class VivinoUrlBuilder:
    def __init__(self):
        pass

    def add_country_to_url(self, url: str, country: str = 'GB/en') -> str:
        """
        Replaces any existing country/lang (e.g. BE/en, GB/en, US/en, etc.) at the start of the path
        with the new country/lang. If not present, prepends the country/lang.
        """
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]

        # If the first two parts look like a country/lang (e.g. BE/en, GB/en, US/en, etc.), replace them
        if len(path_parts) >= 2 and len(path_parts[0]) == 2 and len(path_parts[1]) == 2:
            path_parts = [country.split('/')[0], country.split('/')[1]] + path_parts[2:]
        else:
            # Prepend the country/lang
            path_parts = [country.split('/')[0], country.split('/')[1]] + path_parts

        new_path = '/' + '/'.join(path_parts)
        existing_params = parse_qs(parsed_url.query)
        query_params = dict(existing_params)

        updated_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            new_path,
            '',  
            urlencode(query_params, doseq=True),
            ''
        ))
        return updated_url

    def add_vintage_param(self, url: str, vintage: str) -> str:
        """
        Adds or updates the 'year' parameter in the query string of the given URL.
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params['year'] = [vintage]
        new_query = urlencode(query_params, doseq=True)
        updated_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        return updated_url

class WineSearcherUrlBuilder:
    def __init__(self, country: str = 'UK'):
        """
        Initialize the WineSearcherUrlBuilder with an optional country code.
        """
        self.country = country.upper() if country else 'UK'
        # US state to abbreviation mapping
        self.us_state_abbreviations = {
            'alabama': 'al', 'alaska': 'ak', 'arizona': 'az', 'arkansas': 'ar',
            'california': 'ca', 'colorado': 'co', 'connecticut': 'ct',
            'delaware': 'de', 'florida': 'fl', 'georgia': 'ga', 'hawaii': 'hi',
            'idaho': 'id', 'illinois': 'il', 'indiana': 'in', 'iowa': 'ia',
            'kansas': 'ks', 'kentucky': 'ky', 'louisiana': 'la', 'maine': 'me',
            'maryland': 'md', 'massachusetts': 'ma', 'michigan': 'mi',
            'minnesota': 'mn', 'mississippi': 'ms', 'missouri': 'mo',
            'montana': 'mt', 'nebraska': 'ne', 'nevada': 'nv', 'new hampshire': 'nh',
            'new jersey': 'nj', 'new mexico': 'nm', 'new york': 'ny',
            'north carolina': 'nc', 'north dakota': 'nd', 'ohio': 'oh',
            'oklahoma': 'ok', 'oregon': 'or', 'pennsylvania': 'pa',
            'rhode island': 'ri', 'south carolina': 'sc', 'south dakota': 'sd',
            'tennessee': 'tn', 'texas': 'tx', 'utah': 'ut', 'vermont': 'vt',
            'virginia': 'va', 'washington': 'wa', 'west virginia': 'wv',
            'wisconsin': 'wi', 'wyoming': 'wz'
        }
    def _get_state_abbrev(self, state_input: str) -> str:
        """Convert state name or abbreviation to proper 2-letter lowercase abbreviation"""
        if not state_input:
            return None
        
        state_input = state_input.strip().lower()
        
        # If already a 2-letter code
        if len(state_input) == 2 and state_input in self.us_state_abbreviations.values():
            return state_input
        
        # If full state name
        if state_input in self.us_state_abbreviations:
            return self.us_state_abbreviations[state_input]
        
        return None
    
    def add_shop_location(self, url: str, state: str = None, 
                        bottle_size: str = 'Bottle', currency: str = 'GBP', 
                        sort_order: str = 'lowest', vintage: int = None) -> str:
        """
        Adds shop location and other parameters to the WineSearcher URL.
        
        Args:
            url: The base URL to modify
            country: Country code (default 'US')
            state: State name or 2-letter code (only for US)
            bottle_size: Bottle size (default 'Bottle')
            currency: Currency code (default 'USD')
            sort_order: 'lowest' or 'highest' price sorting
            vintage: Vintage year (optional)
            
        Returns:
            The modified URL with parameters
        """
        # Validate country is uppercase
        country = self.country.upper()
        
        # Add vintage to the wine name path if specified
        if vintage is not None:
            url = f"{url}/{vintage}/"
        elif vintage is None:
            # Add base path (1/ for non-vintage)
            base_path = "1/"
            url = f"{url}/{base_path}"
        
        # Add country/region path
        if country == 'US':
            # Only process state if country is US
            state_abbrev = self._get_state_abbrev(state) if state else None
            if state_abbrev:
                url = f"{url}usa-{state_abbrev}-y/-/ndbipe"
            else:
                url = f"{url}usa/-/ndbipe"
        else:
            # For non-US countries, ignore state parameter
            url = f"{url}{country.lower()}/-/ndbipe"
        
        # Add query parameters
        params = []
        
        # Add bottle size parameter
        params.append(f"Xbottle_size={bottle_size}")
        
        # Add currency parameter
        params.append(f"Xcurrencycode={currency.upper()}")
        
        # Add sort order
        if sort_order.lower() == 'highest':
            params.append("Xsort_order=E")
        else:
            params.append("Xsort_order=e")
        
        # Combine parameters
        if '?' in url:
            url += "&" + "&".join(params)
        else:
            url += "?" + "&".join(params)
            
        return url
