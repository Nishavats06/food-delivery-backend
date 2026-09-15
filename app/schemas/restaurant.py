from pydantic import BaseModel

class RestaurantCreate(BaseModel):
    name: str
    cuisine: str | None = None
    address_line: str

class RestaurantOut(BaseModel):
    id: int
    name: str
    cuisine: str | None
    address_line: str | None
    formatted_address: str | None
    latitude: float | None
    longitude: float | None
    owner_id: int
    rating: float

    class Config:
        from_attributes = True