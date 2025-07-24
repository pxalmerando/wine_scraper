import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

logging.basicConfig(
    level=logging.DEBUG,  # or INFO, as needed
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs.txt", mode='a', encoding='utf-8'),
        logging.StreamHandler()  # Optional: also log to console
    ]
)

logger = logging.getLogger("vivino.helper")
logger.addHandler(logging.NullHandler())

def remove_all_url_parameters(url: str) -> str:
    logger.debug(f"Removing all URL parameters from: {url}")
    parsed_url = urlparse(url)
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        '',
        parsed_url.fragment
    ))
    logger.debug(f"URL after removing parameters: {new_url}")
    return new_url

def vivino_build_url_vintage(base_url, vintage=None, country=None):
    """Add or replace the 'year' query param in the URL."""
    logger.debug(f"Building Vivino URL for vintage. Base: {base_url}, Vintage: {vintage}, Country: {country}")
    if country:
        base_url = vivino_replace_country_code(base_url, country)
        logger.debug(f"Base URL after country code replacement: {base_url}")
    if isinstance(base_url, tuple):
        base_url = base_url[-1] 
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    if vintage: 
        qs['year'] = [str(vintage)]
        logger.debug(f"Set 'year' query param to: {vintage}")
    new_query = urlencode(qs, doseq=True)
    logger.debug(f"New query: {new_query}")
    result_url = urlunparse(parsed._replace(query=new_query))
    logger.debug(f"Final Vivino URL with vintage: {result_url}")
    return result_url

def vivino_replace_country_code(url, replace_with=None):
    logger.debug(f"Replacing country code in URL: {url} with: {replace_with}")
    url = remove_all_url_parameters(url)
    if isinstance(url, tuple):
        url = url[0]
    parsed = urlparse(url)
    path_parts = parsed.path.lstrip('/').split('/')
    if len(path_parts) > 0:
        country = path_parts[0]
        if replace_with:
            path_parts[0] = replace_with
            new_path = '/' + '/'.join(path_parts)
            new_url = urlunparse(parsed._replace(path=new_path))
            logger.debug(f"Country code replaced. New URL: {new_url}")
            return replace_with, new_url
        logger.debug(f"Extracted country code: {country}")
        return country
    logger.debug("No country code found in URL.")
    return None
