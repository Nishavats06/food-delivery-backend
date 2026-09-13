from pydantic import BaseModel
from app.models.order import OrderStatus

class OrderCreate(BaseModel):
    address_id: int

class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    item_name: str
    item_price: float
    quantity: int
    subtotal: float

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    restaurant_id: int
    status: OrderStatus
    subtotal: float
    delivery_fee: float
    taxes: float
    total: float
    items: list[OrderItemOut]

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus