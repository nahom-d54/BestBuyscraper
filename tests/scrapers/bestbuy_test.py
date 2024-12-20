import pytest
from urllib.parse import urlparse


@pytest.fixture
def bestbuy_scraper():
    from app.scrapers.bestbuy.scraper import LocalBestbuyScraper

    return LocalBestbuyScraper(category="mens")


def test_bestbuy_scraper_run(bestbuy_scraper):
    
    bestbuy_scraper.run()

    assert len(bestbuy_scraper.all_products) > 0

    for product in bestbuy_scraper.all_products:
        assert product.get("name") is not None
        assert product.get("url") is not None

        assert urlparse(product.get("url")).scheme in ["http", "https"]