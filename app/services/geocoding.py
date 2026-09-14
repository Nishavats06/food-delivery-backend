
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



# import httpx
# from app.config import settings

# async def get_coordinates_from_address(address: str):
#     url = "https://maps.googleapis.com/maps/api/geocode/json"
#     params = {"address": address, "key": settings.GOOGLE_MAPS_API_KEY}

#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, params=params)
#         data = response.json()

#     print("GOOGLE API RESPONSE:", data)  # DEBUG LINE - temporary

#     if data["status"] != "OK":
#         return None

#     result = data["results"][0]
#     location = result["geometry"]["location"]

#     return {
#         "formatted_address": result["formatted_address"],
#         "latitude": location["lat"],
#         "longitude": location["lng"]
#     }