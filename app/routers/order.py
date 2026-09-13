from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.cart import Cart, CartItem
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate

router = APIRouter(tags=["orders"])

DELIVERY_FEE = 40.0
TAX_RATE = 0.05


@router.post("/orders", response_model=OrderOut)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Sabhi cart items ek hi restaurant ke honi chahiye
    first_menu_item = db.query(MenuItem).filter(MenuItem.id == cart.items[0].menu_item_id).first()
    restaurant_id = first_menu_item.restaurant_id

    subtotal = 0.0
    order_items_data = []

    for cart_item in cart.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == cart_item.menu_item_id).first()
        if menu_item.restaurant_id != restaurant_id:
            raise HTTPException(status_code=400, detail="All items must be from the same restaurant")

        item_subtotal = menu_item.price * cart_item.quantity
        subtotal += item_subtotal

        order_items_data.append({
            "menu_item_id": menu_item.id,
            "item_name": menu_item.name,
            "item_price": menu_item.price,
            "quantity": cart_item.quantity,
            "subtotal": item_subtotal
        })

    taxes = subtotal * TAX_RATE
    total = subtotal + DELIVERY_FEE + taxes

    new_order = Order(
        user_id=current_user.id,
        restaurant_id=restaurant_id,
        address_id=order_data.address_id,
        status=OrderStatus.PLACED,
        subtotal=subtotal,
        delivery_fee=DELIVERY_FEE,
        taxes=taxes,
        total=total
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item_data in order_items_data:
        order_item = OrderItem(order_id=new_order.id, **item_data)
        db.add(order_item)

    for cart_item in cart.items:
        db.delete(cart_item)

    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("/orders", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.value == "RESTAURANT_OWNER":
        restaurant_ids = [r.id for r in db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).all()]
        return db.query(Order).filter(Order.restaurant_id.in_(restaurant_ids)).all()
    return db.query(Order).filter(Order.user_id == current_user.id).all()


@router.get("/orders/{id}", response_model=OrderOut)
def get_order(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/orders/{id}/status", response_model=OrderOut)
def update_order_status(
    id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the restaurant owner can update order status")

    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order