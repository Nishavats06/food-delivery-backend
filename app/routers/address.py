from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.address import Address
from app.models.user import User
from app.schemas.address import AddressCreate, AddressOut
from app.services.geocoding import get_coordinates_from_address

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("/", response_model=AddressOut)
async def create_address(
    address: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    full_address_text = f"{address.address_line}, {address.city}, {address.pincode}"
    geo_data = await get_coordinates_from_address(full_address_text)

    new_address = Address(
        **address.model_dump(),
        user_id=current_user.id,
        formatted_address=geo_data["formatted_address"] if geo_data else None,
        latitude=geo_data["latitude"] if geo_data else None,
        longitude=geo_data["longitude"] if geo_data else None
    )
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


@router.get("/", response_model=list[AddressOut])
def list_addresses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Address).filter(Address.user_id == current_user.id).all()