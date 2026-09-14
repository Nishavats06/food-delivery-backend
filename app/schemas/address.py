from pydantic import BaseModel

class AddressCreate(BaseModel):
    address_line: str
    city: str
    pincode: str

class AddressOut(BaseModel):
    id: int
    address_line: str
    city: str
    pincode: str
    formatted_address: str | None
    latitude: float | None
    longitude: float | None

    class Config:
        from_attributes = True