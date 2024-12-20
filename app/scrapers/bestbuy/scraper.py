import httpx
from bs4 import BeautifulSoup as bs
import datetime
import httpx
from typing import Dict, List, TypedDict
import os
import traceback
from dotenv import load_dotenv

load_dotenv()



class ProductType(TypedDict):
    pricing: Dict[str, str]
    category_detail: Dict[str, str]
    id: str
    product_name: str


class BestBuyScraper:
    """
    A scraper for site
    """

    HEADERS = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "https://www.bestbuy.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def __init__(self, category: str, *args, **kwargs) -> None:
        """pass the category as well"""

        self.client = httpx.Client(
            follow_redirects=True,
            timeout=30,
            cookies={"intl_splash": "false"}
        )
        self.category = category
        self.base_url = "https://www.bestbuy.com/site/searchpage.jsp"

        self.max_page = 2

    def get_products(self, page: int = 1, limit: int = 48, retry: int = 0) -> str:
        """
        Fetch products from BestBuy

        Args:
            page_url: Category or search term to look for
            page: Page number to fetch

        Returns:
            HTML content from the response
        """


        try:
            response = self.client.get(self.category, params={"cp": page})
            if response.status_code == 200:
                return response.text
        except httpx.HTTPStatusError as e:
            print(e)
            return ""
        

    def parse_products(
        self, html_content: str, page: int = 1, limit: int = 48
    ) -> List[Dict[str, str]]:
        """
        Parse product information from HTML content.

        Args:
            html_content: HTML content to parse

        Returns:
            List of dictionaries containing product information
        """
        soup = bs(html_content, "html.parser")
        page_list = soup.find("ol", class_="paging-list")
        page_ints = [int(i.text) for i in page_list.find_all("li")]

        self.max_page = max(self.max_page,max(page_ints))

        products = []

        for product in soup.find_all("li", {"class": "sku-item"}):
            product_name = product.find("h4", class_="sku-title")
            id = product.get("data-sku-id")

            category_detail_url = product_name.find("a").get("href")
            category_detail_image = product.find("img", class_="product-image")
            category_detail = {
                "url": category_detail_url,
                "image": category_detail_image.get("src") if category_detail_image else None,
            }

            try:
                customerPrice = product.find("div",class_="priceView-customer-price").find("span", attrs={"aria-hidden":"true"}).text
                regularPrice = product.find("div",class_="pricing-price__regular-price").find("span", attrs={"aria-hidden":"true"}).text.strip("Was ")
            except AttributeError as e:
                customerPrice = None
                regularPrice = None
            pricing = {
                "regularPrice": regularPrice if regularPrice else None,
                "currentPrice": customerPrice if customerPrice else None,
            }

            products.append({
                "id": id,
                "product_name": product_name.text,
                "category_detail": category_detail,
                "pricing": pricing
            })

        

        return products

    def process_product(self, product: ProductType | Dict[str, str]) -> bool:
        """Process individual product and send to SQS.

        Args:
            product (ProductType | Dict[str, str]): Dictionary containing product information

        Returns:
            bool: True if the product was processed successfully, False otherwise
        """

        return True
        

    def run(self) -> int:
        print(f"Running BestBuy scraper for {self.category}")
        page = 1
        limit = 48
        total_products = 0

        print(f'Scraping started for "{self.category}"')
        try:
            while page <= self.max_page:
                html_content = self.get_products(page, limit)
                products = self.parse_products(html_content, page, limit)

                if not products:
                    break

                total_products += len(products)
                for product in products:
                    self.process_product(product)

                print(
                    f"Processed {len(products)} products on page {page} for {self.category}. So far, {total_products} products processed."
                )
                page += 1
        except Exception as e:
            print(f"Error occurred while scraping: {e}")
            traceback.print_exc()

        print(
            f"Finished scraping {self.category}. Total products processed: {total_products}"
        )
        return total_products

    def __del__(self):
        self.client.close()


class LocalBestBuyScraper(BestBuyScraper):
    """For local testing purposes"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.all_products = []

    def process_product(self, product: ProductType | Dict[str, str]) -> bool:
        print(f"Processing item {product}")

        self.all_products.append(product)

        return True


def generate_flow_run_name() -> str:
    now = datetime.datetime.now()

    human_readable = now.strftime("%A, %d %B %Y %I:%M:%S %p")

    return f"BestBuy-scraper-{human_readable}"



def main(categories: list | str, is_local: bool = False):
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    is_local = is_local or ENVIRONMENT == "local"
    if isinstance(categories, str):
        categories = [categories]

    if not categories:
        print("No categories provided")
        return

    report = {}
    if is_local:
        print("Running in local environment for category:", categories[0])
        scraper = LocalBestBuyScraper(categories[0])
        report[categories[0]] = scraper.run()
    else:
        for category in categories:
            try:
                print("Running in production environment for category:", category)
                scraper = BestBuyScraper(category)
                report[category] = scraper.run()
            except Exception as e:
                print(f"Error running scraper for {category}: {e}")

    print("All categories scraped successfully with the following report:")
    for category, count in report.items():
        print(f"{category}: {count} products scraped")


if __name__ == "__main__":
    # use any category you want to scrape
    categories = ["https://www.bestbuy.com/site/small-appliances/fryers/abcat0912013.c?id=abcat0912013"]
    main(categories, is_local=False)




