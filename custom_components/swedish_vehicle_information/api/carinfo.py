from bs4 import BeautifulSoup
from homeassistant.helpers.aiohttp_client import async_get_clientsession

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

BASE_URL = "https://www.car.info/sv-se/license-plate/S/"


async def fetch_carinfo(hass, plate: str) -> dict:
    url = f"{BASE_URL}{plate}"

    session = async_get_clientsession(hass)
    r = await session.get(url, headers=HEADERS)

    html = await r.text()

    # --- NEW: Detect Copilot metadata instead of real HTML ---
    if "edge_all_open_tabs" in html or "WebsiteContent_" in html:
        return {
            "status": "ERROR",
            "lastInspection": None,
            "nextInspection": None,
            "raw_html": "ERROR: Metadata detected instead of Car.info HTML",
        }

    soup = BeautifulSoup(html, "html.parser")

    def find_value(label: str) -> str | None:
        el = soup.find(string=lambda t: isinstance(t, str) and label in t)
        if not el:
            return None

        parent = el.find_parent()
        if not parent:
            return None

        value_el = parent.find_next_sibling("div")
        if value_el:
            return value_el.get_text(strip=True)

        return None

    return {
        "status": find_value("I trafik"),
        "lastInspection": find_value("Besiktad"),
        "nextInspection": find_value("Besiktas senast"),
        "raw_html": html,
    }
