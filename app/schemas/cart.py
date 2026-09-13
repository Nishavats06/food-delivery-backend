from pydantic import BaseModel

class CartItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    item_name: str
    item_price: float
    subtotal: float

    class Config:
        from_attributes = True

class CartOut(BaseModel):
    id: int
    items: list[CartItemOut]
    subtotal: float
    delivery_fee: float
    taxes: float
    total: float