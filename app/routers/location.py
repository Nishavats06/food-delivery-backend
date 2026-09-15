from fastapi import APIRouter, HTTPException, Query
from app.services.geocoding import search_locations, reverse_geocode

router = APIRouter(prefix="/location", tags=["location"])


@router.get("/search")
async def location_search(query: str = Query(..., min_length=2)):
    results = await search_locations(query)
    if not results:
        raise HTTPException(status_code=404, detail="No locations found")
    return results


@router.get("/geocode")
async def location_geocode(lat: float, lng: float):
    result = await reverse_geocode(lat, lng)
    if not result:
        raise HTTPException(status_code=404, detail="Location not found for given coordinates")
    return result