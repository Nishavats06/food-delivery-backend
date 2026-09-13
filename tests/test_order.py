def test_place_order(client):
    # Customer register/login
    client.post("/auth/register", json={
        "name": "Order User",
        "email": "orderuser@example.com",
        "password": "test1234"
    })
    login_res = client.post("/auth/login", data={
        "username": "orderuser@example.com",
        "password": "test1234"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Owner register/login + role update
    client.post("/auth/register", json={
        "name": "Owner",
        "email": "owner2@example.com",
        "password": "test1234"
    })
    from tests.conftest import TestingSessionLocal
    from app.models.user import User, UserRole
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "owner2@example.com").first()
    user.role = UserRole.RESTAURANT_OWNER
    db.commit()
    db.close()

    owner_login = client.post("/auth/login", data={
        "username": "owner2@example.com",
        "password": "test1234"
    })
    owner_headers = {"Authorization": f"Bearer {owner_login.json()['access_token']}"}

    # Restaurant + menu item banao
    restaurant_res = client.post("/restaurants/", json={
        "name": "Order Test Restaurant",
        "cuisine": "Test",
        "address": "Test Address"
    }, headers=owner_headers)
    restaurant_id = restaurant_res.json()["id"]

    menu_res = client.post(f"/restaurants/{restaurant_id}/menu", json={
        "name": "Burger",
        "price": 150.0
    }, headers=owner_headers)
    menu_item_id = menu_res.json()["id"]

    # Address banao
    address_res = client.post("/addresses/", json={
        "address_line": "123 Test Street",
        "city": "Test City",
        "pincode": "123456"
    }, headers=headers)
    address_id = address_res.json()["id"]

    # Cart mein add karo
    client.post("/cart/items", json={
        "menu_item_id": menu_item_id,
        "quantity": 3
    }, headers=headers)

    # Order place karo
    order_res = client.post("/orders", json={
        "address_id": address_id
    }, headers=headers)

    assert order_res.status_code == 200
    order_data = order_res.json()
    assert order_data["status"] == "PLACED"
    assert order_data["subtotal"] == 450.0  # 150 x 3

    # Cart empty ho gaya hoga
    cart_res = client.get("/cart/", headers=headers)
    assert cart_res.json()["items"] == []


def test_order_status_update_by_owner(client):
    # (Isi tarah ka setup jaisa upar, phir status update test karo)
    pass