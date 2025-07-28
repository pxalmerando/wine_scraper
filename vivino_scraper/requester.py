import requests
from fake_useragent import UserAgent
from typing import Optional, Dict, Any


def make_request(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    proxies: Optional[Dict[str, str]] = None,
    timeout: int = 10,
    method: str = "GET",
    **kwargs: Any
) -> requests.Response:
    """
    Make an HTTP request with optional proxies and randomized user agent.

    Args:
        url: The URL to request.
        headers: Optional HTTP headers to send. Will be merged with default headers.
        proxies: Either a proxy dictionary or a proxy URL string.
                 If string, will be converted to {'http': url, 'https': url}.
        timeout: Timeout in seconds.
        method: HTTP method, default is 'GET'.
        **kwargs: Additional arguments for requests.request.

    Returns:
        The response object.

    Raises:
        requests.RequestException: If the request fails.
        ValueError: If proxies argument is invalid.
    """
    # Default headers
    default_headers = {
        "User-Agent": UserAgent().chrome,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }
    
    # Merge provided headers with defaults
    final_headers = {**default_headers, **(headers or {})}

    # Handle proxy conversion if a string is provided
    final_proxies = None
    if proxies is not None:
        if isinstance(proxies, str):
            final_proxies = {
                "http": proxies,
                "https": proxies
            }
        elif isinstance(proxies, dict):
            final_proxies = proxies
        else:
            raise ValueError("proxies must be either a dictionary or a string")

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=final_headers,
            proxies=final_proxies,
            timeout=timeout,
            **kwargs
        )
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        # You might want to add logging here
        # Example: logger.error(f"Request failed for {url}: {str(e)}")
        raise