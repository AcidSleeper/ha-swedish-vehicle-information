import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://fordon-fu-regnr.transportstyrelsen.se/UppgifterAnnatFordon/Fordonsuppgifter"


async def fetch_ts(plate: str) -> dict:
    """
    Hämtar fordonsuppgifter från Transportstyrelsen via HTML-sidan.
    Detta är en generell scraper – justera selectors efter verklig HTML.
    """

    # Antag att sidan accepterar regnr via query-param eller form.
    # Här gör vi en enkel GET med regnr som query-param.
    params = {"regnr": plate}

    async with httpx.AsyncClient() as client:
        r = await client.get(BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        html = r.text

    soup = BeautifulSoup(html, "html.parser")

    # Exempel: plocka ut tabellrader med etiketter
    def get_text_by_label(label: str) -> str | None:
        el = soup.find(string=lambda t: isinstance(t, str) and label in t)
        if not el:
            return None
        # anta att värdet står i nästa <td> eller liknande
        td = el.find_parent("tr")
        if not td:
            return None
        cells = td.find_all("td")
        if len(cells) >= 2:
            return cells[1].get_text(strip=True)
        return None

    status = get_text_by_label("Fordonsstatus") or get_text_by_label("Status")
    last_inspection = get_text_by_label("Senaste besiktning")
    next_inspection = get_text_by_label("Nästa besiktning")
    tax = get_text_by_label("Fordonsskatt")

    return {
        "status": status,
        "lastInspection": last_inspection,
        "nextInspection": next_inspection,
        "tax": tax,
        "raw_html": html,
    }
