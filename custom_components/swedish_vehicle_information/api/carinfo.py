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
    make = _parse_make(soup, clean_plate)

    return {
        "status": status,
        "lastInspection": last_inspection,
        "nextInspection": next_inspection,
        "make": make,
    }


def _parse_status(soup: BeautifulSoup) -> str | None:
    """Extract 'I trafik' status (Ja/Nej).

    car.info renders every spec row (I trafik, Svensksåld, Bagagevolym, etc.)
    the same way across vehicle types (car, trailer, motorcycle, ...):

        <div class="sprow ...">
          <span class="sptitle">I trafik</span>
          Ja <span class="icon_check text-success ms-1"></span>
        </div>

    Relying on this instead of the meta description works consistently:
    the meta description is empty on some vehicle types (e.g. trailers).
    """
    for row in soup.select(".sprow"):
        title_el = row.select_one(".sptitle")
        if not title_el:
            continue

        label = title_el.get_text(strip=True)
        if label != "I trafik":
            continue

        full_text = row.get_text(" ", strip=True)
        value = full_text.replace(label, "", 1).strip()
        return value.split()[0] if value else None

    return None


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


def _parse_make(soup: BeautifulSoup, plate: str) -> str | None:
    """Extract the manufacturer/model name from the page <title>.

    car.info titles follow the pattern "{PLATE} - {FABRIKAT} {resten}", e.g.:

        <title>ABC123 - Volvo V90, 2025</title>
        <title>CBA321 - Fogelsta S1938B1000 o Premium</title>

    We take the first word after the plate as the make/manufacturer.
    """
    title_el = soup.find("title")
    if not title_el:
        return None

    title = title_el.get_text(strip=True)

    prefix = f"{plate} - "
    if title.startswith(prefix):
        rest = title[len(prefix):]
    else:
        # Fallback in case the plate casing/spacing differs slightly.
        parts = title.split(" - ", 1)
        rest = parts[1] if len(parts) > 1 else title

    words = rest.split()
    return words[0] if words else None
