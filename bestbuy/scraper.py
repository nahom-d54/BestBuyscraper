import httpx
from bs4 import BeautifulSoup as bs
from urllib.parse import urlencode
import json
import re
import time


class Scraper:
    def __init__(self):
        self.base_url = "https://www.bestbuy.com/"
        self.headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Referer": self.base_url,
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-US,en;q=0.9"

                    }
        self.client = httpx.Client(headers=self.headers, cookies={"intl_splash": "false"})
    
    def get_page_number(self, response):
        soup = bs(response.text, "html.parser")
        page_numbers = soup.find("ol", class_="paging-list")
        current_page = page_numbers.find("li", class_="current-page-number")
        next_page =current_page.next_sibling

        return {
            "current_page": current_page.text,
            "next_page": next_page.text if next_page else None
        }
    



    def get_products_by_json(self, url, page = 1, no_format = False):
        try:
            response = self.client.get(url, params={"cp": page})
        except httpx.HTTPStatusError as e:
            print(e)
            return []
        soup = bs(response.text, "html.parser")

        finding_by_id = re.compile("^pricing-price-")
        script_details = map(lambda x: json.loads(x.text), soup.find_all("script", {"type": "application/json", "id": finding_by_id}))

        script_detais_hashmap = {}

        for script in script_details:
            if script.get("app"):
                script_detais_hashmap[script.get("app").get("skuId")] = script.get("app")

        script_metas = []

        script_tags = soup.find_all("script", {"type": False, "id": False})

        for script in script_tags:
            if script.string: 
                pattern = r'const.+state\s*=\s*(.*?)}}}";'
                match = re.search(pattern, script.string)

                if match:
                    state_value = match.group(1)
                    try:
                        state_value = state_value+'}}}"'
                        json_parsed = json.loads(json.loads(state_value))
                        script_metas.append(json_parsed)
                    except json.JSONDecodeError as e:
                        print(e)
                        continue

        products = []

        for script in script_metas:
            sku = script.get("sku")
            if sku:
                product_name = sku.get("name")
                id = sku.get("skuId")
                category_detail = sku.get("categoryDetail")
                pricing = {
                    "regularPrice": script_detais_hashmap.get(id, {}).get("priceDomain", {}).get("regularPrice"),
                    "currentPrice": script_detais_hashmap.get(id, {}).get("priceDomain", {}).get("currentPrice"),
                }

                products.append({
                    "id": id,
                    "product_name": product_name,
                    "category_detail": category_detail,
                    "pricing": pricing
                })

        if no_format:
            return products

        return_format = {
            "products": products,
            "product_count": len(products),
        }

        return return_format

    def get_products_by_html(self, url, page = 1, no_format = False, query = None):
        try:
            response = self.client.get(url, params={"cp": page})
        except httpx.HTTPStatusError as e:
            print(e)
            return []
        soup = bs(response.text, "html.parser")
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

        if no_format:
            return products
        
        return_format = {
            "products": products,
            "product_count": len(products)
        }

        return return_format

    def get_products_by_page_range(self, start_page, end_page, url, by_json = False, sleep = 0):
        products = []
        for page in range(start_page, end_page):
            if by_json:
                products.extend(self.get_products_by_json(url, page=page, no_format=True))
            else:
                products.extend(self.get_products_by_html(url, page=page, no_format=True))
            
            time.sleep(sleep)

        return {
            "products": products,
            "product_count": len(products)
        }
    def get_products(self, url, page = 1 , by_json = False, no_format = False):
        if by_json:
            return self.get_products_by_json(url, page, no_format=no_format)
        return self.get_products_by_html(url, page, no_format=no_format)


