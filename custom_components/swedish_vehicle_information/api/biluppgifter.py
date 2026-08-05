import httpx

API_KEY_BU = None  # sätt via secrets eller env


async def fetch_bu(plate: str) -> dict:
    """
    Hämtar data från Biluppgifter API.
    Justera URL och headers efter verklig dokumentation.
    """
    url = f"https://api.biluppgifter.se/api/v1/vehicle/{plate}"
    headers = {}
    if API_KEY_BU:
        headers["Authorization"] = f"Bearer {API_KEY_BU}"

    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()
