from bs4 import BeautifulSoup
from homeassistant.helpers.aiohttp_client import async_get_clientsession

BASE_URL = "https://biluppgifter.se/fordon/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def is_blocked(html: str) -> bool:
    """Detect if Biluppgifter returned a blocked or empty page."""
    html_lower = html.lower()
    return (
        "blockerad" in html_lower
        or "javascript" in html_lower
        or "captcha" in html_lower
        or "ingen information" in html_lower
        or "logga in" in html_lower
    )


async def fetch_bu(hass, plate: str) -> dict:
    url = f"{BASE_URL}{plate}/"

    session = async_get_clientsession(hass)
    r = await session.get(url, headers=HEADERS)
    html = await r.text()

    # Blocked or unusable HTML → return empty but include raw_html
    if is_blocked(html):
        return {
            "status": None,
            "lastInspection": None,
            "nextInspection": None,
            "tax": None,
            "owner": None,
            "vehicle_type": None,
            "raw_html": html,
        }

    soup = BeautifulSoup(html, "html.parser")

    def find_value(label: str) -> str | None:
        th = soup.find("th", string=lambda t: isinstance(t, str) and label in t)
        if not th:
            return None

        row = th.find_parent("tr")
        if not row:
            return None

        td = row.find("td")
        if td:
            return td.get_text(strip=True)

        return None

    return {
        "status": find_value("Status"),
        "lastInspection": find_value("Senaste besiktning"),
        "nextInspection": find_value("Nästa besiktning"),
        "tax": find_value("Skatt"),
        "owner": find_value("Ägare"),
        "vehicle_type": find_value("Fordonstyp"),
        "raw_html": html,
    }
