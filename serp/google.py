from .serper_client import SerperClient

# For backward compatibility, you can still use the function approach
def google_search(api_key, query, keywords, country):
    """
    Legacy function for backward compatibility.
    Consider using SerperClient directly for new code.
    """
    client = SerperClient(api_key)
    return client.google_search(query, keywords, country)




