import httpx
from bs4 import BeautifulSoup

TS_URL = "https://fordon-fu-regnr.transportstyrelsen.se/UppgifterAnnatFordon/Fordonsuppgifter"


async def fetch_ts(plate: str) -> dict:
    payload = {
        "Registreringsnummer": plate,
        "recaptchaClientToken": "",
        "Captcha_CaptchaResponse": ""
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.post(TS_URL, data=payload, timeout=30)
        r.raise_for_status()
        html = r.text

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
