from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
headers = {'Authorization': 'Bearer token_str'}


def test_create_user():
    data_user = {"full_name": "test11",
                 "email": "test1121@test11.com",
                 "phone": "+78221131264",
                 "password": "Qwerty123!",
                 "password_confirm": ""}
    response = client.post("/users/register", json=data_user)
    print(response.json())
    assert response.status_code == 422


def test_login_user():
    data_user = {"email_or_phone": "test1121@test11.com",
                 "password": "Qwerty123!"}
    response = client.post("/users/login", json=data_user)
    print(response.json())

    #access_token = response.json()["access_token"]
    #headers = {'Authorization': f'Bearer {access_token}'}
    assert response.status_code == 422


def test_verify_send():
    response = client.post("/users/verify_send", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_users_list():
    response = client.get("/users/user_list", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_user_num():
    response = client.get("/users/user/2", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_user_active():
    response = client.post("/users/active/2", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_verify_post():
    data = {"access_token": "string", "token_type": "string"}
    response = client.post("/users/verify_post", json=data, headers=headers)
    print(response.json())
    assert response.status_code == 404


def test_user_staff():

    response = client.post("/users/staff/2", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_user_update():
    data = {"full_name": "string", "email": "user@example.com", "phone": "+74399464198"}
    response = client.put("/users/update/1", json=data, headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_user_delete():
    response = client.post("//users/delete/1", headers=headers)
    print(response.json())
    assert response.status_code == 404


def test_create_product():
    data = {"name": "test", "price": 10, "photo": "test"}
    response = client.post("/product/create_product", json=data, headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_product_list():

    response = client.get("/product/product_list", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_product_get():
    response = client.get("/product/1", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_product_update():
    data = {"name": "test", "price": 10, "photo": "test"}
    response = client.put("/product/1", json=data, headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_product_active():
    response = client.post("/product/1", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_product_delete():
    response = client.delete("/product/1", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_basket_get():
    response = client.get("/product/basket", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_basket_add():
    data = {"product": 1, "count": 10}
    response = client.post("/product/basket", json=data, headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_basket_put():
    response = client.put("/product/basket/1", headers=headers)
    print(response.json())
    assert response.status_code == 403


def test_basket_delete():
    response = client.delete("/product/basket", headers=headers)
    print(response.json())
    assert response.status_code == 403
