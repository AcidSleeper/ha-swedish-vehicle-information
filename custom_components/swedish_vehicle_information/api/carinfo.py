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

    car.info has changed this section twice in November 2026. Both variants
    put the label before the value inside a group_item, but the CSS classes
    differ. Current markup (2026-11-28) has dropped ``text-truncate`` and
    leaves the label in an unclassed div:

        <div class="featured_info_group">
          <div class="group_item">
            <div class="... text-end"><div>Besiktad</div></div>
            <div class="..."><div class="fw-bold text-end">
              2024-07-18
            </div></div>
          </div>
        </div>

    The 2026-11-24 variant used div.text-end.text-truncate for the label and
    div.fw-bold.text-truncate.text-end for the value. Both are accepted so a
    partial rollout on car.info's side cannot break the sensor. The older
    featured_info_item blocks (value before label) are checked last.
    """
    last_inspection = None
    next_inspection = None

    for item in soup.select(".featured_info_group .group_item"):
        # 2026-11-24 markup: explicit classes on both label and value.
        label_el = item.select_one("div.text-end.text-truncate")
        value_el = item.select_one("div.fw-bold.text-truncate.text-end")

        if not label_el or not value_el:
            # 2026-11-28 markup: find the label by its exact text and take
            # the bold div in the same group_item as the value.
            label_el = next(
                (
                    div
                    for div in item.find_all("div")
                    if div.get_text(strip=True)
                    in ("Besiktad", "Besiktas senast")
                ),
                None,
            )
            value_el = item.select_one("div.fw-bold") if label_el else None

        if not label_el or not value_el:
            continue

        label = label_el.get_text(strip=True)
        value = value_el.get_text(strip=True)

        if label == "Besiktad":
            last_inspection = value
        elif label == "Besiktas senast":
            next_inspection = value

    if last_inspection is None or next_inspection is None:
        for item in soup.find_all("div", class_="featured_info_item"):
            value_el = item.select_one(".btn .text-truncate")
            label_el = item.select_one(".text-muted.fs-9")

            if not value_el or not label_el:
                continue

            label = label_el.get_text(strip=True)
            value = value_el.get_text(strip=True)

            if label == "Besiktad" and last_inspection is None:
                last_inspection = value
            elif label == "Besiktas senast" and next_inspection is None:
                next_inspection = value

    return last_inspection, next_inspection


def _parse_make(soup: BeautifulSoup, plate: str) -> str | None:
    """Extract the manufacturer/model name from the page <title>.

    car.info titles follow the pattern "{PLATE} - {FABRIKAT} {resten}", e.g.:

        <title>ABC123 - Volvo V70 2.4 D5 AWD Momentum, 185hk, 2019</title>
        <title>XYZ789 - Kärrsläpet 500 2020</title>

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
    return words[0].capitalize() if words else None
