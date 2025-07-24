from services.exception import ExternalAPIException
import requests
import json

def google_search(api_key, query , keywords, country):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query + " " + keywords,
        "gl": country
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
        raise ExternalAPIException(f"Failed to fetch Google search results: {str(e)}")
    
    if response.status_code != 200:
        raise ExternalAPIException(f"Failed to fetch Google search results: {response.status_code} {response.text}")
        
    data = response.json()
    results = [{"title": item["title"], "link": item["link"]} for item in data["organic"][:3]]
    return results





