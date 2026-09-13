from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.cart import Cart, CartItem
from app.models.menu_item import MenuItem
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartOut, CartItemOut

router = APIRouter(prefix="/cart", tags=["cart"])

DELIVERY_FEE = 40.0
TAX_RATE = 0.05  # 5%


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def build_cart_response(cart: Cart, db: Session) -> CartOut:
    items_out = []
    subtotal = 0.0

    for item in cart.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        item_subtotal = menu_item.price * item.quantity
        subtotal += item_subtotal

        items_out.append(CartItemOut(
            id=item.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            item_name=menu_item.name,
            item_price=menu_item.price,
            subtotal=item_subtotal
        ))

    taxes = subtotal * TAX_RATE
    total = subtotal + DELIVERY_FEE + taxes if subtotal > 0 else 0.0

    return CartOut(
        id=cart.id,
        items=items_out,
        subtotal=subtotal,
        delivery_fee=DELIVERY_FEE if subtotal > 0 else 0.0,
        taxes=taxes,
        total=total
    )


@router.get("/", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = get_or_create_cart(db, current_user.id)
    return build_cart_response(cart, db)


@router.post("/items", response_model=CartOut)
def add_item(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    cart = get_or_create_cart(db, current_user.id)

    existing = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.menu_item_id == item.menu_item_id
    ).first()

    if existing:
        existing.quantity += item.quantity
    else:
        new_item = CartItem(cart_id=cart.id, menu_item_id=item.menu_item_id, quantity=item.quantity)
        db.add(new_item)

    db.commit()
    db.refresh(cart)
    return build_cart_response(cart, db)


@router.patch("/items/{id}", response_model=CartOut)
def update_item(
    id: int,
    updated: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)
    item = db.query(CartItem).filter(CartItem.id == id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    item.quantity = updated.quantity
    db.commit()
    db.refresh(cart)
    return build_cart_response(cart, db)


@router.delete("/items/{id}", response_model=CartOut)
def remove_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)
    item = db.query(CartItem).filter(CartItem.id == id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()
    db.refresh(cart)
    return build_cart_response(cart, db)


@router.delete("/")
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = get_or_create_cart(db, current_user.id)
    for item in cart.items:
        db.delete(item)
    db.commit()
    return {"message": "Cart cleared"}