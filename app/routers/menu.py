from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.menu_item import MenuItemCreate, MenuItemOut

router = APIRouter(tags=["menu"])


@router.post("/restaurants/{restaurant_id}/menu", response_model=MenuItemOut)
def create_menu_item(
    restaurant_id: int,
    item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this restaurant")

    new_item = MenuItem(**item.model_dump(), restaurant_id=restaurant_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItemOut])
def get_menu(restaurant_id: int, db: Session = Depends(get_db)):
    return db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()


@router.patch("/menu/{id}", response_model=MenuItemOut)
def update_menu_item(
    id: int,
    updated: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(MenuItem).filter(MenuItem.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    restaurant = db.query(Restaurant).filter(Restaurant.id == item.restaurant_id).first()
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this restaurant")

    for key, value in updated.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/menu/{id}")
def delete_menu_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(MenuItem).filter(MenuItem.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    restaurant = db.query(Restaurant).filter(Restaurant.id == item.restaurant_id).first()
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this restaurant")

    db.delete(item)
    db.commit()
    return {"message": "Menu item deleted successfully"}