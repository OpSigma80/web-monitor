"""
Extractor de valores de páginas web.
Usa httpx para casos simples y Playwright cuando se necesita JS.
"""

from typing import Optional
import httpx
import json
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_with_httpx(url: str) -> str:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


async def fetch_with_playwright(url: str, wait_selector: Optional[str] = None) -> str:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            locale="es-ES",
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=15000)
            content = await page.content()
            return content
        finally:
            await browser.close()


def extract_by_css(html: str, selector: str) -> Optional[str]:
    soup = BeautifulSoup(html, "lxml")
    element = soup.select_one(selector)
    if element is None:
        return None
    text = element.get_text(strip=True)
    return text if text else None


def extract_by_xpath(html: str, xpath: str) -> Optional[str]:
    from lxml import html as lxml_html

    tree = lxml_html.fromstring(html)
    results = tree.xpath(xpath)
    if not results:
        return None
    first = results[0]
    if hasattr(first, "text_content"):
        return first.text_content().strip()
    return str(first).strip()


async def extract_value(
    url: str,
    css_selector: Optional[str] = None,
    xpath: Optional[str] = None,
    use_playwright: bool = False,
    monitor_type: Optional[str] = None,
) -> tuple[Optional[str], str]:
    if use_playwright:
        html = await fetch_with_playwright(url, wait_selector=css_selector)
    else:
        html = await fetch_with_httpx(url)

    value = None
    if monitor_type == "price":
        try:
            payload = json.loads(html)
            if css_selector:
                value = payload
                for key in css_selector.split("."):
                    value = value[key] if isinstance(value, dict) else None
            elif isinstance(payload, dict) and "data" in payload:
                data = payload["data"]
                value = data.get("amount") if isinstance(data, dict) else None
            if value is not None:
                value = str(value)
        except (json.JSONDecodeError, KeyError, TypeError):
            value = None
    elif css_selector:
        value = extract_by_css(html, css_selector)
    elif xpath:
        value = extract_by_xpath(html, xpath)

    return value, html