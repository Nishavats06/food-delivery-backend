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

    class Config:
        from_attributes = True