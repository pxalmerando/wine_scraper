import keyword
from utils import get_keyword_column_A_to_F_with_index, update_cell_in_file
from vivino_scraper.wine_extractor import VivinoScraper
from serp.google import google_search
from multi_login.api.auth import TokenAuth
from multi_login.api.profile import ProfileManager
from multi_login.api.launcher import BrowserLauncher
from multi_login.api.workspaces import WorkspaceManager
from multi_login.api.cookies import MultiloginCookieManager
from wine_searcher.pages.product import RequestWine
from wine_searcher.wine_url_builder import WineUrlBuilder
from serp.serper_client import SerperClient
from utils import encode_url
import random
import uuid
import traceback
ML_EMAIL = "almerando2@gmail.com"
ML_PASSWORD = "Thanos_12345@"
token = TokenAuth(ML_EMAIL, ML_PASSWORD)
COOKIES_FILE = r"E:\MVP file\cookies.json"
def get_cookies():
    with open(COOKIES_FILE, "r") as file:
        cookies_string = file.read()
    return cookies_string
def create_browser(url,vintage, highest_price=False):
    profile_manager = ProfileManager(token)
    workspace_manager = WorkspaceManager(token_auth=token)
    folder_id = workspace_manager.create_workspace(workspace_name=f"testing")
    profile_result = profile_manager.create_profile(profile_name=f"testing", folder_id=folder_id, proxy=get_random_proxy())
    profile_id = profile_result if isinstance(profile_result, str) else str(profile_result)
    cookie_manager = MultiloginCookieManager(profile_manager=profile_manager, profile_id=profile_id)
    cookie_manager.import_cookies_to_browser(cookies=get_cookies(), folder_id=folder_id)
    browser = BrowserLauncher(profile_manager=profile_manager, profile_id=profile_id)
    launch = browser.start_profile(folder_id=folder_id, automation_type="selenium", headless_mode=False)
    wine_request = RequestWine(command_executor=f"http://localhost:{launch}", url=url)
    wine = wine_request.get_wine_info(url,vintage, highest_price)
    return wine, browser
# Load proxies from proxies.txt
def load_proxies_from_file(filepath="proxies.txt"):
    proxies = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                proxy_url = line.strip()
                if proxy_url:
                    proxies.append(proxy_url)
    except Exception as e:
        print(f"Error loading proxies: {e}")
    return proxies
def parse_proxy_line(line):
    """Convert a proxy URL string into the desired dictionary format"""
    # Remove http:// prefix
    no_prefix = line.replace("http://", "")
    
    # Split into auth and host parts
    auth_part, host_part = no_prefix.split("@")
    
    # Get username and password
    username, password = auth_part.split(":")
    
    # Get host and port
    host, port = host_part.split(":")
    
    return {
        "host": host,
        "type": "http",
        "port": int(port),
        "username": username,
        "password": password,
        "save_traffic": False
    }
proxy_list = [parse_proxy_line(line) for line in load_proxies_from_file("proxies.txt")]
proxies_list = [parse_proxy_line(line) for line in load_proxies_from_file("proxies.txt")]
def get_random_proxy():
    """Return a randomly selected proxy in the desired format"""
    return random.choice(proxies_list)


PATH_TO_SAVE = r"E:\MVP file\Input\Joanne - Sheet1.csv"
PATH = r"E:\MVP file\Input"
API_KEY = "270af4d1d0390342a75c6b1acec84521a38bede1"
def get_vivino_wine_info_with_proxies(wine_url, year=None, country="GB", proxies=None, max_retries=3):
    """
    Fetch wine info from Vivino using VivinoScraper, with optional proxies and retry on error.

    Args:
        wine_url (str): The Vivino wine URL.
        year (int or str, optional): The vintage year.
        country (str, optional): Country code, default "GB".
        proxies (dict, optional): Proxies dictionary for requests.
        max_retries (int, optional): Number of retries on error.

    Returns:
        dict: Wine information dictionary, or None if all retries fail.
    """
    for attempt in range(1, max_retries + 1):
        try:
            scraper = VivinoScraper()
            # Set proxies if provided
            if proxies:
                return scraper.get_wine_info(wine_url, year, country, proxies)
            else:
                return scraper.get_wine_info(wine_url, year, country)
        except Exception as e:
            traceback.print_exc()
            print(f"Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                print("All retries failed.")
                return None

# google_search
#   get_vivino_wine_info_with_proxies()
serp = SerperClient()
def get_vivino_wine_info():
    for key, value in get_keyword_column_A_to_F_with_index(PATH).items():
        for item in value:
            producer, wine_name, country, region, vintage, wine_color  = item[1]
            keyword = f"{producer} {wine_name} {country} {region} {vintage} {wine_color}"
            print(keyword, "keyword")
            url = serp.google_search(keyword, "vivino", "GB")

            if url:
                    url = url.get("link")    
                    result = get_vivino_wine_info_with_proxies(url, vintage, "GB", random.choice(proxies_list))
                    if result:
                        update_cell_in_file(PATH_TO_SAVE,item[0],"Vivino rating",result.get("ratingValue"))
                        update_cell_in_file(PATH_TO_SAVE,item[0],"Vivino URL",result.get("url"))
    
def get_wine_searcher():
    for key, value in get_keyword_column_A_to_F_with_index(PATH).items():
        for item in value:
            producer, wine_name, country, region, vintage, wine_color, price, abv, vivino_rating, vivino_url  = item[1]
            print(vivino_url, "vivino_url")
            print( random.choice(proxy_list), "proxy")

            if vivino_url:
                result = get_vivino_wine_info_with_proxies(vivino_url, vintage, "GB", random.choice(proxy_list))
                ws_url = serp.scrape_webpage(result.get("wine_searcher_url"), include_markdown=False)
                print(ws_url, "ws_url")
                if "no results for" not in ws_url.get('text').lower():
                    update_cell_in_file(PATH_TO_SAVE,item[0],"Wine Searcher URL",result.get("wine_searcher_url"))

                    # wine_url_builder = WineUrlBuilder()
                    # uk_urls = wine_url_builder.get_url_variations(original_url=encode_url(ws_url),
                    #                                                 vintage=vintage,
                    #                                                 region="UK")
                
                # ws_result = []
                # for key,url in uk_urls.items():
                #     WS, browser = create_browser(url, vintage, highest_price=True)
                #     if WS is None:
                #         browser.stop_profile(profile_id=browser.profile_id)
                #         break
                #     if WS:
                #         ws_result.append(WS)
                #         ws_result.append(create_browser(url, vintage, highest_price=False))

                # if len(ws_result) == 0:
                # else:
                #     update_cell_in_file(PATH_TO_SAVE,item[0],"Wine Searcher URL",ws_result)
                #     if ws_result[-1]:
                #         update_cell_in_file(PATH_TO_SAVE,item[0],"Uk seller same vintage lowest",ws_result[-1].get("lowest_price"))
                #     if ws_result[-2]:
                #         update_cell_in_file(PATH_TO_SAVE,item[0],"Uk seller same vintage highest",ws_result[-2].get("highest_price"))
get_wine_searcher() 