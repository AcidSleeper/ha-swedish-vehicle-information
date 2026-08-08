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

# Exempel: https://biluppgifter.se/fordon/znm11c/
BASE_URL = "https://biluppgifter.se/fordon/"


async def fetch_biluppgifter(hass, plate: str) -> dict:
    """Fetch and parse vehicle info for a single registration plate."""
    clean_plate = plate.strip().upper().replace(" ", "")
    url = f"{BASE_URL}{clean_plate.lower()}/"

    session = async_get_clientsession(hass)
    response = await session.get(url, headers=HEADERS)
    html = await response.text()

    soup = BeautifulSoup(html, "html.parser")

    fields = _parse_label_value_fields(soup)

    status = _normalize_status(fields.get("Status"))
    last_inspection = fields.get("Senast besiktigad")
    next_inspection = fields.get("Nästa besiktning senast")

    # biluppgifter.se har ett dedikerat "Fabrikat"-fält (till skillnad från
    # car.info, vars <title>-baserade märke visat sig trunkera vissa märken,
    # t.ex. mopeder). Faller tillbaka till title-parsning bara om fältet
    # oväntat skulle saknas.
    make = fields.get("Fabrikat")
    if make:
        make = make.strip().capitalize()
    else:
        make = _parse_make(soup, clean_plate)

    return {
        "status": status,
        "lastInspection": last_inspection,
        "nextInspection": next_inspection,
        "make": make,
    }


def _normalize_status(raw_status: str | None) -> str | None:
    """Normalisera biluppgifter.se's statustext till samma Ja/Nej-format
    som car.info använder, så båda källorna alltid ger samma svar oavsett
    vilken av dem som faktiskt hämtade datan.

    biluppgifter.se skriver beskrivande text som "I Trafik", "Avställd"
    eller "Avregistrerad". Bara "I Trafik" innebär att fordonet får köras.
    """
    if not raw_status:
        return None
    return "Ja" if "trafik" in raw_status.lower() else "Nej"


def _parse_label_value_fields(soup: BeautifulSoup) -> dict[str, str]:
    """Collect every label/value pair on the page into a dict.

    biluppgifter.se renders nearly all vehicle facts the same way:

        <li>
          <span class="label">Status</span>
          <span class="value">I Trafik</span>
        </li>

    so instead of writing one regex per field, we build a
    {label: value} lookup once and read whatever fields we need from it.
    """
    fields: dict[str, str] = {}

    for row in soup.find_all("li"):
        label_el = row.find("span", class_="label")
        value_el = row.find("span", class_="value")

        if not label_el or not value_el:
            continue

        label = label_el.get_text(strip=True)
        value = value_el.get_text(strip=True)
        fields[label] = value

    return fields


def _parse_make(soup: BeautifulSoup, plate: str) -> str | None:
    """Extract the manufacturer/model name from the page <title>.

    biluppgifter.se titles follow the pattern
    "{PLATE} {FABRIKAT} {resten} - Biluppgifter.se", e.g.:

        <title>ABC123 Volvo V70 2.4 D5 AWD Blå 2019 - Biluppgifter.se</title>

    We strip the trailing " - Biluppgifter.se" and take the first word
    after the plate as the make/manufacturer.
    """
    title_el = soup.find("title")
    if not title_el:
        return None

    title = title_el.get_text(strip=True)

    # Strip the trailing " - Biluppgifter.se" site suffix.
    if " - " in title:
        title = title.rsplit(" - ", 1)[0]

    prefix = f"{plate} "
    rest = title[len(prefix):] if title.startswith(prefix) else title

    words = rest.split()
    return words[0].capitalize() if words else None
