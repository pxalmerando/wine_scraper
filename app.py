from scraper.vivino import VivinoScraper
from utils.helper import remove_url_parameters, vivino_replace_country_code, vivino_add_vintage_params
from serp.serp_google import SerperAPIClient
from utils.round_robin_proxies import ProxyRoundRobin

PROXIES_PATH = "E:\MVP file\proxies.txt"
proxy_round_robin = ProxyRoundRobin(PROXIES_PATH)
SERP_API_CLIENT = SerperAPIClient()
vivino_scraper = VivinoScraper(proxy_round_robin.get_proxy())
test_urls = [
    "https://www.vivino.com/US/en/francois-carillon-puligny-montrachet-1er-cru-les-combettes/w/2722342?srsltid=AfmBOooifNCxJjuTX-3ApUcFf11PYGv8l1bYP5N6Rhji7NhzXMM6Js89",
    "https://www.vivino.com/US/en/francois-carillon-puligny-montrachet-1er-cru-les-folatieres/w/1607644?srsltid=AfmBOoqHDA6nvdzw_COgGuyd_07GTd3qwSV-vlHoZTezm_YeVfeUetuy",
    "https://www.vivino.com/US/en/francois-carillon-puligny-montrachet-1er-cru-les-perrieres/w/1461718?srsltid=AfmBOooxm5WIjf4LmPnx1BdNTbbl2TtC2tp-1ONemw_tTWjD96NwbN-t",
    "https://www.vivino.com/US/en/francois-carillon-puligny-montrachet/w/2261443?srsltid=AfmBOoouQzq10N6COf2IoYMNJmx1iVamjVbMR1a0On49CEKZqfpqpyi0",
    "https://www.vivino.com/US/en/francois-carillon-puligny-montrachet/w/2261443?srsltid=AfmBOoouQzq10N6COf2IoYMNJmx1iVamjVbMR1a0On49CEKZqfpqpyi0",
    "https://www.vivino.com/US/en/francois-carillon-bourgogne-chardonnay/w/2064477?srsltid=AfmBOoqRK_ExXWSUz_id0hFPr6B1VHdRJpoBMXk-bb8Rcuxmt0J_wg1g",
    "https://www.vivino.com/US/en/francois-carillon-bourgogne-aligote/w/2682724?srsltid=AfmBOoqScv3IEbPcjAmoLK54VENC2naCDiZESJrtHNN8No-OtKF-sD--",
    "https://www.vivino.com/US/en/francois-carillon-bourgogne-pinot-noir/w/5326950?srsltid=AfmBOorqzq6fo4_67ViqBeZ272yKLQMB0iXwDsEC6PDtSKeH8F32wsna",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-pommard/w/1207562?year=2016&srsltid=AfmBOorXbrzh5dOveWLF7DTla2iB_wwm4FykpWhmz5SKotAuCnaOAoMH",
    "https://www.vivino.com/US/en/vincent-girardin-santenay-1er-cru-beauregard-rouge/w/1301332?year=2016&srsltid=AfmBOorcWLAEITdHa00MLpJOpyUJoM0bnBFc39FZd6GSzZTd5pxHA3pI",
    "https://www.vivino.com/US/en/vincent-girardin-savigny-les-beaune-1er-cru-les-marconnets/w/1862790?srsltid=AfmBOorCMgaqSKjJLfRm4eWLvpbXBteHW9UEnXhY4mrxhvFF18h3UEJH",
    "https://www.vivino.com/US/en/vincent-girardin-bourgogne-cuvee-saint-vincent-rouge/w/41324?srsltid=AfmBOor_loqZK9xDMd4i6TJqLM1a-vCdchlsMwN0U1uAmZWhrpMs-1nK",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-chassagne-montrachet-rouge/w/1218616?year=2017&srsltid=AfmBOoockqOYI4PqHpVUBT301Lb3jNB9SBPsDlFqu1Aua0ukYXDmCei1",
    "https://www.vivino.com/US/en/vincent-girardin-chassagne-montrachet-1er-cru-clos-saint-jean-chassagne-montrachet-clos-saint-jean/w/2373532?srsltid=AfmBOop3UPP7Okv5fuIiSL2hZXKmjBZMKidTtFVCUKPklvTSRfaRO7XT",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-pommard/w/1207562?srsltid=AfmBOootD4MQ8oQ8u8KSpphRCJsiXQe0yn4NJCrmH7QyEGE2vOmQ1o1b",
    "https://www.vivino.com/US/en/vincent-girardin-rully-vieilles-vignes/w/41764?srsltid=AfmBOorVbVE66ZnMgg3jvCsT8cr5BxIPzhRRXz-wj2pWRoTeR5xSjFvB",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-volnay/w/41864?srsltid=AfmBOoqj3qjYOve3A9u9od1NDw_20FL-GU0YGpyM8T1iSRDD9UPTVkZr",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-morey-saint-denis/w/7087027?srsltid=AfmBOoosG3OQen8gRVP5Unezd_gBkvt4lDeY8yHK4bXTGjjbNkFwq4EF",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-pommard/w/1207562?srsltid=AfmBOootD4MQ8oQ8u8KSpphRCJsiXQe0yn4NJCrmH7QyEGE2vOmQ1o1b",
    "https://www.vivino.com/US/en/vincent-girardin-rully-premier-cru-gresigny/w/7507269?srsltid=AfmBOop30ysmQFsIwT5ZKlbAkx05VpuuxChZLXKsMYv6iVc0m1fHitBn",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-santenay-blanc/w/3384452?srsltid=AfmBOopSGcBsU4YTI7T3CMXtQZke7eDvf8jGDxXKu0xVwJIkGfyb2VLb",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-aloxe-corton-aloxe-corton/w/6080877?year=2019&srsltid=AfmBOorIB1E0Ic7TOKZ6MNmJ9RmI3-f8LpfPGFf9KZPXS9T_zv724nnc",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-auxey-duresses-rouge/w/6477730?srsltid=AfmBOoovhPY-lzgs_Tz-U4k_J_5CoQ5w4UxkKnpClmKu_0s7t9UwrqtB",
    "https://www.vivino.com/US/en/vincent-girardin-beaune-1er-cru-les-aigrots/w/9189771?year=2019&srsltid=AfmBOopRV5KT57jrKLrnh1EBAqRBZoSrchgG7aiyjn3Ik_-VkZqNANtC",
    "https://www.vivino.com/US/en/vincent-girardin-charmes-chambertin-grand-cru/w/1568502?srsltid=AfmBOoq3gU4hMAxfUtT_ashZZ-p1hxUHDnduvAr7GJenSwTD-AvT9BuI",
    "https://www.vivino.com/US/en/vincent-girardin-chassagne-montrachet-1er-cru-la-maltroie/w/1815631?srsltid=AfmBOooCT2b0UHtjA5OnifmDciek1AeDwQ81lTLRQMbzYUNQbj3G4whE",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-chassagne-montrachet-rouge/w/1218616?srsltid=AfmBOopWyp2y5wloO2aHDzyD_pGBVHnnqXhBbTcihqC11UNx_uP5JHGA",
    "https://www.vivino.com/US/en/vincent-girardin-chorey-les-beaune-les-beaumonts/w/9435151?srsltid=AfmBOorU0hRmB-Dv5W7iymysbiW8IGJkDIK1xoiVgHMOrfOPwXsEnxS8",
    "https://www.vivino.com/US/en/vincent-girardin-clos-de-vougeot-grand-cru/w/1817082?srsltid=AfmBOoqr0ll3j3rJ4BYNO0e3psuPt8ZmZeL1IG52gzzb8HcQi_bgJGyp",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-morey-saint-denis/w/7087027?srsltid=AfmBOoosG3OQen8gRVP5Unezd_gBkvt4lDeY8yHK4bXTGjjbNkFwq4EF",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-pommard/w/1207562?srsltid=AfmBOootD4MQ8oQ8u8KSpphRCJsiXQe0yn4NJCrmH7QyEGE2vOmQ1o1b",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-pouilly-fuisse/w/1137230?srsltid=AfmBOoqNPSdjNXi3cYUAj8A6CHZ_GshCIXaGixObFAnEuW1zwN8V6Ijt",
    "https://www.vivino.com/US/en/vincent-girardin-santenay-terre-d-enfance/w/1651970?srsltid=AfmBOoqH6qbeWp0ltuw8fdY_IYO9MbB1X_irn7ffE8hiA0hIfVyhrRCV",
    "https://www.vivino.com/BE/en/vincent-girardin-santenay-1er-cru-beauregard-rouge/w/1301332?year=2019&price_id=37263001&bottle_count=1&srsltid=AfmBOors9t7caczIjNDlozwawN2fwZaEZxMoXqrWhzY4oDmAdtePwQWd",
    "https://www.vivino.com/US/en/vincent-girardin-santenay-1er-cru-les-gravieres-rouge/w/85110?srsltid=AfmBOoqDM00ld_EqKV1CVq3Xy4wW2bcOrTHWEiFVAjqxOxb2ac8HD0p4",
    "https://www.vivino.com/US/en/vincent-girardin-volnay-1er-cru-les-pitures/w/4564659?year=2019&srsltid=AfmBOorYy6isWEW9YqSpeJEZBihsJchUVHZNfD8__bo9IHzH8HyD14Jq",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-volnay/w/41864?srsltid=AfmBOopFPA1Hv_xV4BFm6aTXwuFsBSd4CIV7LZWh9g42WAO82OaSTE4M",
    "https://www.vivino.com/US/en/vincent-girardin-beaune-1er-cru-les-aigrots/w/9189771?srsltid=AfmBOop50yUw8bn0KrhrlMDY44fPDUYU4bCmo65De8wbNUbuVwh6sRtk",
    "https://www.vivino.com/US/en/vincent-girardin-charmes-chambertin-grand-cru/w/1568502?srsltid=AfmBOoq3gU4hMAxfUtT_ashZZ-p1hxUHDnduvAr7GJenSwTD-AvT9BuI",
    "https://www.vivino.com/US/en/vincent-girardin-chassagne-montrachet-1er-cru-morgeot-rouge/w/1215955?srsltid=AfmBOorfz9Wle5hmv-qcb2518txq7xiqq-YuQsdImzNS8s78kkm_CMfk",
    "https://www.vivino.com/BR/en/vincent-girardin-les-vieilles-vignes-chassagne-montrachet-rouge/w/1218616?srsltid=AfmBOortGp27IeFZTDIDyHN1_KmVg0ZRd2pE2cHFk4ueDkMRxK08awpy",
    "https://www.vivino.com/US/en/vincent-girardin-chorey-les-beaune-les-beaumonts/w/9435151?srsltid=AfmBOorU0hRmB-Dv5W7iymysbiW8IGJkDIK1xoiVgHMOrfOPwXsEnxS8",
    "https://www.vivino.com/US/en/vincent-girardin-clos-de-vougeot-grand-cru/w/1817082?srsltid=AfmBOorz6x3Sye-CVX5jeuusSG46V9XNAGm3QyNPvowxpLIMfxH7hmQJ",
    "https://www.vivino.com/US/en/vincent-girardin-gevrey-chambertin-vieilles-vignes/w/41594?year=2020&srsltid=AfmBOorgutVuuIRC-HtfSr6c1QyYQ4ti8ANV0FYfd1ibFczZsnNGOIL8",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-macon-fuisse-macon-fuisse/w/2422519?srsltid=AfmBOorvUbYMeHEAM2JuGSGunMOXJGtNI4nRTLeYon8EJ81IrMpCl9fW",
    "https://www.vivino.com/US/en/vincent-girardin-les-vieilles-vignes-morey-saint-denis/w/7087027?srsltid=AfmBOoosG3OQen8gRVP5Unezd_gBkvt4lDeY8yHK4bXTGjjbNkFwq4EF"
]
for test in test_urls:
    
    url = vivino_replace_country_code(test)
    add_vintage = vivino_add_vintage_params(url,2019)
    print(add_vintage)
    # print(vivino_scraper.get_wine(test))