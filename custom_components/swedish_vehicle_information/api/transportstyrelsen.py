from bs4 import BeautifulSoup
from homeassistant.helpers.aiohttp_client import async_get_clientsession

TS_URL = "https://fordon-fu-regnr.transportstyrelsen.se/UppgifterAnnatFordon/Fordonsuppgifter"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def is_captcha(html: str) -> bool:
    """Detect if Transportstyrelsen returned a CAPTCHA or robot page."""
    html_lower = html.lower()
    return (
        "captcha" in html_lower
        or "robot" in html_lower
        or "skyddad" in html_lower
        or "kontrollera" in html_lower
    )


async def fetch_ts(hass, plate: str) -> dict:
    payload = {
        "Registreringsnummer": plate,
        "recaptchaClientToken": "",
        "Captcha_CaptchaResponse": ""
    }

    session = async_get_clientsession(hass)
    r = await session.post(TS_URL, data=payload, headers=HEADERS)
    html = await r.text()

    # CAPTCHA detected → return empty but include raw_html for debugging
    if is_captcha(html):
        return {
            "status": None,
            "lastInspection": None,
            "nextInspection": None,
            "tax": None,
            "raw_html": html,
        }

    soup = BeautifulSoup(html, "html.parser")

    def find_value(label: str) -> str | None:
        el = soup.find(string=lambda t: isinstance(t, str) and label in t)
        if not el:
            return None

        row = el.find_parent("tr")
        if not row:
            return None

        cells = row.find_all("td")
        if len(cells) >= 2:
            return cells[1].get_text(strip=True)

        return None

    return {
        "status": find_value("Fordonsstatus"),
        "lastInspection": find_value("Senaste besiktning"),
        "nextInspection": find_value("Nästa besiktning"),
        "tax": find_value("Fordonsskatt"),
        "raw_html": html,
    }
