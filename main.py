from bestbuy.scraper import Scraper
from urllib.parse import urlparse
from json import dump


scraper = Scraper()

url = "https://www.bestbuy.com/site/searchpage.jsp?st=cheap+laptops"

parsed_url = urlparse(url)

page = 1

prpducts = scraper.get_products(url, page=page)

with open(f"Bestbuy_{parsed_url.query}_{page}.json", "w") as f:
    dump(prpducts, f, indent=4)