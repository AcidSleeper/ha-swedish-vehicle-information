from bs4 import BeautifulSoup
from homeassistant.helpers.aiohttp_client import async_get_clientsession

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

BASE_URL = "https://www.car.info/sv-se/license-plate/S/"


async def fetch_carinfo(hass, plate: str) -> dict:
    url = f"{BASE_URL}{plate}"

    session = async_get_clientsession(hass)
    r = await session.get(url, headers=HEADERS)
    html = await r.text()

    soup = BeautifulSoup(html, "html.parser")

    def find_value(label: str) -> str | None:
        """Finds the value next to a label on Car.info pages."""
        el = soup.find(string=lambda t: isinstance(t, str) and label in t)
        if not el:
            return None

        parent = el.find_parent()
        if not parent:
            return None

        # Value is usually in the next sibling <div>
        value_el = parent.find_next_sibling("div")
        if value_el:
            return value_el.get_text(strip=True)

        return None

    return {
        "status": find_value("I trafik"),
        "lastInspection": find_value("Besiktad"),        # ← ändrad här
        "nextInspection": find_value("Besiktas senast"),
        "raw_html": html,
    }
