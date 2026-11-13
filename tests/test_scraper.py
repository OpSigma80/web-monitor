"""Tests for app.services.scraper — CSS/XPath extraction and extract_value.

No network: fetch_with_httpx is replaced with a fake in every
extract_value test, and the extractors run on sample HTML.
"""

import asyncio

from app.services import scraper
from app.services.scraper import extract_by_css, extract_by_xpath, extract_value

HTML = """
<html><body>
  <span class="price">$1,234.56</span>
  <div id="status">In stock</div>
  <span class="empty"></span>
  <a class="link" href="https://example.com/item">Item</a>
</body></html>
"""

PRICE_JSON = '{"data": {"amount": "65432.10", "currency": "USD"}}'


class TestExtractByCss:
    def test_finds_element_text(self):
        assert extract_by_css(HTML, ".price") == "$1,234.56"

    def test_finds_by_id(self):
        assert extract_by_css(HTML, "#status") == "In stock"

    def test_missing_selector_returns_none(self):
        assert extract_by_css(HTML, ".does-not-exist") is None

    def test_empty_element_returns_none(self):
        assert extract_by_css(HTML, ".empty") is None


class TestExtractByXpath:
    def test_text_node(self):
        assert extract_by_xpath(HTML, "//span[@class='price']/text()") == "$1,234.56"

    def test_element(self):
        assert extract_by_xpath(HTML, "//div[@id='status']") == "In stock"

    def test_attribute(self):
        assert extract_by_xpath(HTML, "//a[@class='link']/@href") == "https://example.com/item"

    def test_missing_returns_none(self):
        assert extract_by_xpath(HTML, "//span[@class='nope']") is None


def fake_fetch(html: str):
    async def _fetch(url: str) -> str:
        return html

    return _fetch


class TestExtractValue:
    def test_css_selector(self, monkeypatch):
        monkeypatch.setattr(scraper, "fetch_with_httpx", fake_fetch(HTML))
        value, html = asyncio.run(extract_value("https://example.com", css_selector=".price"))
        assert value == "$1,234.56"
        assert html == HTML

    def test_xpath(self, monkeypatch):
        monkeypatch.setattr(scraper, "fetch_with_httpx", fake_fetch(HTML))
        value, _ = asyncio.run(
            extract_value("https://example.com", xpath="//div[@id='status']")
        )
        assert value == "In stock"

    def test_price_monitor_default_amount(self, monkeypatch):
        monkeypatch.setattr(scraper, "fetch_with_httpx", fake_fetch(PRICE_JSON))
        value, _ = asyncio.run(
            extract_value("https://api.example.com", monitor_type="price")
        )
        assert value == "65432.10"

    def test_price_monitor_dotted_key(self, monkeypatch):
        monkeypatch.setattr(scraper, "fetch_with_httpx", fake_fetch(PRICE_JSON))
        value, _ = asyncio.run(
            extract_value(
                "https://api.example.com",
                css_selector="data.amount",
                monitor_type="price",
            )
        )
        assert value == "65432.10"

    def test_price_monitor_invalid_json_returns_none(self, monkeypatch):
        monkeypatch.setattr(scraper, "fetch_with_httpx", fake_fetch("not json"))
        value, html = asyncio.run(
            extract_value("https://api.example.com", monitor_type="price")
        )
        assert value is None
        assert html == "not json"

    def test_no_selector_returns_none(self, monkeypatch):
        monkeypatch.setattr(scraper, "fetch_with_httpx", fake_fetch(HTML))
        value, _ = asyncio.run(extract_value("https://example.com"))
        assert value is None
