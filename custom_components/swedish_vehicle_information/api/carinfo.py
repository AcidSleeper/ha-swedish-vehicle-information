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

# OBS: landskoden "S" (Sverige) MÅSTE vara med i URL:en, annars svarar
# car.info med fel sida och all data blir None.
# Exempel: https://www.car.info/sv-se/license-plate/S/DGE290
BASE_URL = "https://www.car.info/sv-se/license-plate/S/"


async def fetch_carinfo(hass, plate: str) -> dict:
    """Fetch and parse vehicle info for a single registration plate."""
    clean_plate = plate.strip().upper().replace(" ", "")
    url = f"{BASE_URL}{clean_plate}"

    session = async_get_clientsession(hass)
    response = await session.get(url, headers=HEADERS)
    html = await response.text()

    soup = BeautifulSoup(html, "html.parser")

    # META DESCRIPTION
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc = meta_desc["content"] if meta_desc else ""

    # I trafik: Ja/Nej (med eller utan punkt)
    status_match = re.search(r"I trafik:\s*(Ja|Nej)", desc)
    status = status_match.group(1) if status_match else None

    # JSON-LD
    json_ld = soup.find("script", type="application/ld+json")
    last_inspection = None
    next_inspection = None

    if json_ld and json_ld.string:
        text = json_ld.string
        m1 = re.search(r'"dateOfLastInspection"\s*:\s*"([^"]+)"', text)
        if m1:
            last_inspection = m1.group(1)

        m2 = re.search(r'"dateOfNextInspection"\s*:\s*"([^"]+)"', text)
        if m2:
            next_inspection = m2.group(1)

    return {
        "status": status,
        "lastInspection": last_inspection,
        "nextInspection": next_inspection,
        "raw_html": html,
    }