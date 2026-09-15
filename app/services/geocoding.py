import httpx

async def get_coordinates_from_address(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "food-delivery-app"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        data = response.json()

    if not data:
        return None

    result = data[0]
    return {
        "formatted_address": result["display_name"],
        "latitude": float(result["lat"]),
        "longitude": float(result["lon"])
    }


async def search_locations(query: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 5}
    headers = {"User-Agent": "food-delivery-app"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        data = response.json()

    return [
        {
            "formatted_address": item["display_name"],
            "latitude": float(item["lat"]),
            "longitude": float(item["lon"])
        }
        for item in data
    ]


async def reverse_geocode(latitude: float, longitude: float):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": latitude, "lon": longitude, "format": "json"}
    headers = {"User-Agent": "food-delivery-app"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        data = response.json()

    if "error" in data:
        return None

    return {
        "formatted_address": data["display_name"],
        "latitude": float(data["lat"]),
        "longitude": float(data["lon"])
    }