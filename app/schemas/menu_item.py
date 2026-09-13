from pydantic import BaseModel

class MenuItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    image_url: str | None = None
    category_id: int | None = None
    is_available: bool = True

class MenuItemOut(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: str | None
    price: float
    image_url: str | None
    category_id: int | None
    is_available: bool

    class Config:
        from_attributes = True