def register_and_login(client, email="cartuser@example.com"):
    client.post("/auth/register", json={
        "name": "Cart User",
        "email": email,
        "password": "test1234"
    })
    response = client.post("/auth/login", data={
        "username": email,
        "password": "test1234"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def setup_restaurant_owner_with_menu_item(client):
    client.post("/auth/register", json={
        "name": "Owner",
        "email": "owner@example.com",
        "password": "test1234"
    })
    login_res = client.post("/auth/login", data={
        "username": "owner@example.com",
        "password": "test1234"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Directly database mein role update (test ke liye shortcut)
    from tests.conftest import TestingSessionLocal
    from app.models.user import User, UserRole
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "owner@example.com").first()
    user.role = UserRole.RESTAURANT_OWNER
    db.commit()
    db.close()

    # Fresh token lo naye role ke saath
    login_res = client.post("/auth/login", data={
        "username": "owner@example.com",
        "password": "test1234"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    restaurant_res = client.post("/restaurants/", json={
        "name": "Test Restaurant",
        "cuisine": "Test",
        "address": "Test Address"
    }, headers=headers)
    restaurant_id = restaurant_res.json()["id"]

    menu_res = client.post(f"/restaurants/{restaurant_id}/menu", json={
        "name": "Test Pizza",
        "price": 200.0
    }, headers=headers)
    menu_item_id = menu_res.json()["id"]

    return menu_item_id


def test_add_item_to_cart(client):
    headers = register_and_login(client)
    menu_item_id = setup_restaurant_owner_with_menu_item(client)

    response = client.post("/cart/items", json={
        "menu_item_id": menu_item_id,
        "quantity": 2
    }, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == 400.0


def test_cart_requires_login(client):
    response = client.get("/cart/")
    assert response.status_code == 401