import httpx

API_KEY_FU = None  # sätt via secrets eller env om du vill


async def fetch_fu(plate: str) -> dict:
    """
    Hämtar data från Fordonsuppgifter API.
    Justera URL och headers efter verklig dokumentation.
    """
    url = f"https://api.fordonsuppgifter.se/api/v1/vehicle/{plate}"
    headers = {}
    if API_KEY_FU:
        headers["Authorization"] = f"Bearer {API_KEY_FU}"

    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()
