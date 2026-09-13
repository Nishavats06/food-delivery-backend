from pydantic import BaseModel

class RestaurantCreate(BaseModel):
    name: str
    cuisine: str | None = None
    address: str | None = None

class RestaurantOut(BaseModel):
    id: int
    name: str
    cuisine: str | None
    address: str | None
    owner_id: int
    rating: float

    class Config:
        from_attributes = True