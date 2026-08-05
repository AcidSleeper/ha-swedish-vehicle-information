import re
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
}

BASE_URL = "https://www.car.info/sv-se/license-plate/S/"


async def fetch_carinfo(hass, plate: str) -> dict:
    url = f"{BASE_URL}{plate}"

    session = async_get_clientsession(hass)
    r = await session.get(url, headers=HEADERS)
    html = await r.text()

    soup = BeautifulSoup(html, "html.parser")

    # --- TITLE ---
    title = soup.title.string if soup.title else None

    # --- META DESCRIPTION ---
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc = meta_desc["content"] if meta_desc else ""

    # Extract "I trafik: Ja/Nej"
    status_match = re.search(r"I trafik:\s*(Ja|Nej)", desc)
    status = status_match.group(1) if status_match else None

    # --- JSON-LD (contains inspection dates) ---
    json_ld = soup.find("script", type="application/ld+json")
    last_inspection = None
    next_inspection = None

    if json_ld:
        text = json_ld.string

        # Besiktad
        m1 = re.search(r'"dateOfLastInspection"\s*:\s*"([^"]+)"', text)
        if m1:
            last_inspection = m1.group(1)

        # Besiktas senast
        m2 = re.search(r'"dateOfNextInspection"\s*:\s*"([^"]+)"', text)
        if m2:
            next_inspection = m2.group(1)

    return {
        "status": status,
        "lastInspection": last_inspection,
        "nextInspection": next_inspection,
        "raw_html": html,
        "title": title,
        "description": desc,
    }
