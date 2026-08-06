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

    status = _parse_status(soup)
    last_inspection, next_inspection = _parse_inspection_dates(soup)

    return {
        "status": status,
        "lastInspection": last_inspection,
        "nextInspection": next_inspection,
    }


def _parse_status(soup: BeautifulSoup) -> str | None:
    """Extract 'I trafik: Ja/Nej' from the meta description."""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc = meta_desc["content"] if meta_desc else ""

    match = re.search(r"I trafik:\s*(Ja|Nej)", desc)
    return match.group(1) if match else None


def _parse_inspection_dates(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """Extract 'Besiktad' and 'Besiktas senast' dates.

    car.info renders these as pairs of divs, e.g.:

        <div class="featured_info_item">
          <div class="btn btn-grey cursor_default">
            <span class="text-truncate">2026-07-28</span>
          </div>
          <div class="text-center text-truncate text-muted fs-9">
            Besiktad
          </div>
        </div>

    The value comes BEFORE its label in the markup, so we match each
    "featured_info_item" block and pair its value span with its label div.
    """
    last_inspection = None
    next_inspection = None

    for item in soup.find_all("div", class_="featured_info_item"):
        value_el = item.select_one(".btn .text-truncate")
        label_el = item.select_one(".text-muted.fs-9")

        if not value_el or not label_el:
            continue

        label = label_el.get_text(strip=True)
        value = value_el.get_text(strip=True)

        if label == "Besiktad":
            last_inspection = value
        elif label == "Besiktas senast":
            next_inspection = value

    return last_inspection, next_inspection
