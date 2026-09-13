def test_register_user(client):
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "test1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data


def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "test1234"
    })
    response = client.post("/auth/register", json={
        "name": "Another User",
        "email": "test@example.com",
        "password": "test5678"
    })
    assert response.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "test1234"
    })
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "test1234"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "test1234"
    })
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401