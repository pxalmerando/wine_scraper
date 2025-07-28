
import unicodedata
import re

def _normalize_text(text):
    """Normalize text but preserve accented letters."""
    if not text:
        return text
    
    # Normalize Unicode (e.g., convert curly quotes to straight quotes)
    text = unicodedata.normalize('NFKC', text.strip().lower())
    
    # Remove control characters but keep accented letters
    cleaned_text = []
    for char in text:
        if unicodedata.category(char) not in ('Cc', 'Cf', 'Co', 'Cn'):  # Skip control chars
            cleaned_text.append(char)
    
    return ''.join(cleaned_text)

def remove_url_parameters(url):
    """
    Remove all parameters from the given URL, returning the base URL without query or fragment.
    """
    # Parse the URL using urlparse
    from urllib.parse import urlparse, urlunparse

    parsed = urlparse(url)
    # Remove query and fragment
    cleaned = parsed._replace(query='', fragment='')
    return urlunparse(cleaned)

def vivino_replace_country_code(url, country="GB"):
    url = remove_url_parameters(url)
    return re.sub(r'/[A-Z]{2}/en/', f'/{country}/en/', url)

def vivino_add_vintage_params(url, year):
    """
    Add or replace the 'year' parameter in the given Vivino URL.
    """
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query['year'] = [str(year)]
    new_query = urlencode(query, doseq=True)
    new_url = urlunparse(parsed._replace(query=new_query))
    return new_url