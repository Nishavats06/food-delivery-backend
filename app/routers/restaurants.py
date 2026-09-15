from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.schemas.restaurant import RestaurantCreate, RestaurantOut
from app.services.geocoding import get_coordinates_from_address

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("/", response_model=list[RestaurantOut])
def list_restaurants(
    search: str | None = None,
    cuisine: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Restaurant)

    if search:
        query = query.filter(Restaurant.name.ilike(f"%{search}%"))
    if cuisine:
        query = query.filter(Restaurant.cuisine == cuisine)

    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=RestaurantOut)
async def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.RESTAURANT_OWNER:
        raise HTTPException(status_code=403, detail="Only restaurant owners can create restaurants")

    geo_data = await get_coordinates_from_address(restaurant.address_line)

    new_restaurant = Restaurant(
        name=restaurant.name,
        cuisine=restaurant.cuisine,
        address_line=restaurant.address_line,
        formatted_address=geo_data["formatted_address"] if geo_data else None,
        latitude=geo_data["latitude"] if geo_data else None,
        longitude=geo_data["longitude"] if geo_data else None,
        owner_id=current_user.id
    )
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)
    return new_restaurant


@router.get("/{id}", response_model=RestaurantOut)
def get_restaurant(id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.patch("/{id}", response_model=RestaurantOut)
async def update_restaurant(
    id: int,
    updated: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this restaurant")

    geo_data = await get_coordinates_from_address(updated.address_line)

    restaurant.name = updated.name
    restaurant.cuisine = updated.cuisine
    restaurant.address_line = updated.address_line
    restaurant.formatted_address = geo_data["formatted_address"] if geo_data else None
    restaurant.latitude = geo_data["latitude"] if geo_data else None
    restaurant.longitude = geo_data["longitude"] if geo_data else None

    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.delete("/{id}")
def delete_restaurant(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this restaurant")

    db.delete(restaurant)
    db.commit()
    return {"message": "Restaurant deleted successfully"}