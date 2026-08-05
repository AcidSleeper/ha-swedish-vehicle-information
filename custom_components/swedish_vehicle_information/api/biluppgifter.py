import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://biluppgifter.se/fordon/"


async def fetch_bu(plate: str) -> dict:
    url = f"{BASE_URL}{plate}/"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(url, timeout=30)
        r.raise_for_status()
        html = r.text

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
        "raw_html": html
    }
