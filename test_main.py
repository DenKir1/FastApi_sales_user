import asyncio
import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from main import app
from users.models import User

headers_admin = {'Authorization': 'Bearer token_str'}
headers_user = {'Authorization': 'Bearer token_str'}

u_id = 1
u2_id = 1
p_id = 1
p2_id = 1
d_id = 1
d2_id = 1

test_user = {"full_name": "test",
             "email": "testadmin@test.com",
             "phone": "+79998887766",
             "password": "Qwerty123!",
             "password_confirm": "Qwerty123!"}

test_user_2 = {"full_name": "test2",
               "email": "test_not_admin2@test.com",
               "phone": "+79918687762",
               "password": "Qwerty123!",
               "password_confirm": "Qwerty123!"}

test_user_phone = {"full_name": "test_wrong",
                   "email": "test_wrong@test.com",
                   "phone": "+71",
                   "password": "Qwerty123!",
                   "password_confirm": "Qwerty123!"}

test_user_email = {"full_name": "test27",
                   "email": "test.com",
                   "phone": "+79917777762",
                   "password": "Qwerty123!",
                   "password_confirm": "Qwerty123!"}

test_user_passw = {"full_name": "test27",
                   "email": "t@est.com",
                   "phone": "+79917777762",
                   "password": "Qwerty123!",
                   "password_confirm": "Qwerty1234!"}


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as c:
            yield c


@pytest.mark.anyio
async def test_create_user(client: AsyncClient):
    response = await client.post("/users/register", json=test_user)
    global u_id
    u_id = response.json()["id"]
    assert response.status_code == 200
    # Create superuser for tests
    test_user_admin = await User.get(id=u_id)
    test_user_admin.is_staff = True
    test_user_admin.is_superuser = True
    await test_user_admin.save()

    response_2 = await client.post("/users/register", json=test_user_2)
    global u2_id
    u2_id = response_2.json()["id"]
    assert response_2.status_code == 200

    response_3 = await client.post("/users/register", json=test_user_2)
    assert response_3.status_code == 400

    response_4 = await client.post("/users/register", json=test_user_phone)
    assert response_4.status_code == 422

    response_5 = await client.post("/users/register", json=test_user_email)
    assert response_5.status_code == 422

    response_6 = await client.post("/users/register", json=test_user_passw)
    assert response_6.status_code == 400


@pytest.mark.anyio
async def test_login_user(client: AsyncClient):
    data_superuser = {"email_or_phone": test_user["email"],
                      "password": test_user["password"]}
    response = await client.post("/users/login", json=data_superuser)
    access_token = response.json()["access_token"]
    global headers_admin
    headers_admin = {'Authorization': f'Bearer {access_token}'}
    assert response.status_code == 200

    data_user_2 = {"email_or_phone": test_user["phone"],
                   "password": test_user["password"]}
    response_2 = await client.post("/users/login", json=data_user_2)
    assert response_2.status_code == 200

    data_user_test = {"email_or_phone": test_user_2["email"],
                      "password": test_user_2["password"]}
    response_3 = await client.post("/users/login", json=data_user_test)
    access_token_2 = response_3.json()["access_token"]
    global headers_user
    headers_user = {'Authorization': f'Bearer {access_token_2}'}
    print(headers_admin)
    print(headers_user)
    assert response_3.status_code == 200


@pytest.mark.anyio
async def test_verify_send(client: AsyncClient):
    response = await client.post("/users/verify_send", headers=headers_admin)
    assert response.status_code == 200

    response_2 = await client.post("/users/verify_send", headers=headers_user)
    assert response_2.status_code == 200


@pytest.mark.anyio
async def test_verify_post(client: AsyncClient):
    data = {"access_token": "token_from_email", "token_type": "string"}
    response = await client.post("/users/verify_post", json=data, headers=headers_admin)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_product(client: AsyncClient):
    data = {"name": "test221", "price": 102, "photo": "test221"}
    response = await client.post("/product/create_product", json=data, headers=headers_admin)
    print(response.json())
    global p_id
    p_id = response.json()["id"]
    assert response.status_code == 200

    data_2 = {"name": "test2212", "price": 1022, "photo": "test2221"}
    response_2 = await client.post("/product/create_product", json=data_2, headers=headers_admin)
    global p2_id
    p2_id = response_2.json()["id"]
    assert response_2.status_code == 200

    response_3 = await client.post("/product/create_product", json=data_2, headers=headers_user)
    assert response_3.status_code == 403


@pytest.mark.anyio
async def test_users_list(client: AsyncClient):
    response_2 = await client.get("/users/user_list", headers=headers_user)
    assert response_2.status_code == 403

    response = await client.get("/users/user_list", headers=headers_admin)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_user_num(client: AsyncClient):
    response = await client.get(f"/users/user/{u_id}", headers=headers_admin)
    assert response.status_code == 200

    response = await client.get(f"/users/user/{u_id}", headers=headers_user)
    assert response.status_code == 403


@pytest.mark.anyio
async def test_user_update(client: AsyncClient):
    data = {"full_name": "for_delete", "phone": "+71992998877"}
    response = await client.put(f"/users/update/{u2_id}", json=data, headers=headers_admin)
    assert response.status_code == 200

    data = {"full_name": "for_delete_", "phone": "+72992998877"}
    response_2 = await client.put(f"/users/update/{u2_id}", json=data, headers=headers_user)
    assert response_2.status_code == 200

    response_3 = await client.put(f"/users/update/{u_id}", json=data, headers=headers_user)
    assert response_3.status_code == 403


@pytest.mark.anyio
async def test_product_list(client: AsyncClient):
    response = await client.get("/product/product_list", headers=headers_admin)
    assert response.status_code == 200

    response_2 = await client.get("/product/product_list", headers=headers_user)
    assert response_2.status_code == 200


@pytest.mark.anyio
async def test_product_get(client: AsyncClient):
    response = await client.get(f"/product/{p_id}", headers=headers_admin)
    assert response.status_code == 200

    response = await client.get(f"/product/{p_id}", headers=headers_user)
    assert response.status_code == 200

    response = await client.get(f"/product/1000", headers=headers_user)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_product_update(client: AsyncClient):
    data = {"name": "test_for_delete", "price": 103, "photo": "test32"}
    response = await client.put(f"/product/{p2_id}", json=data, headers=headers_admin)
    assert response.status_code == 200

    data = {"name": "test_for_delete_", "price": 1035, "photo": "test325"}
    response = await client.put(f"/product/{p2_id}", json=data, headers=headers_user)
    assert response.status_code == 403


@pytest.mark.anyio
async def test_product_active(client: AsyncClient):
    response = await client.post(f"/product/{p2_id}", headers=headers_admin)
    assert response.status_code == 200

    response = await client.post(f"/product/1000", headers=headers_admin)
    assert response.status_code == 404

    response = await client.post(f"/product/{p2_id}", headers=headers_user)
    assert response.status_code == 403


@pytest.mark.anyio
async def test_basket_add(client: AsyncClient):
    response = await client.post(f"/product/deal/{p_id}&5", headers=headers_admin)
    global d_id
    d_id = response.json()["id"]
    assert response.status_code == 200

    response = await client.post(f"/product/deal/{p2_id}&5", headers=headers_admin)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_basket_get(client: AsyncClient):
    response = await client.get(f"/product/deal/{d_id}", headers=headers_admin)
    assert response.status_code == 200

    response = await client.get(f"/product/deal/1000", headers=headers_admin)
    assert response.status_code == 200

    response_2 = await client.get(f"/product/deal/0", headers=headers_admin)
    assert response_2.status_code == 200


@pytest.mark.anyio
async def test_user_staff(client: AsyncClient):
    response = await client.post(f"/users/staff/{u2_id}", headers=headers_user)
    assert response.status_code == 403

    response = await client.post(f"/users/staff/{u2_id}", headers=headers_admin)
    assert response.status_code == 200
    # twice is for switch off is_staff flag
    response = await client.post(f"/users/staff/{u2_id}", headers=headers_admin)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_user_active(client: AsyncClient):
    response = await client.post(f"/users/active/{u2_id}", headers=headers_user)
    assert response.status_code == 403

    response = await client.post(f"/users/active/{u2_id}", headers=headers_admin)
    assert response.status_code == 200
    # switch on is_active
    response = await client.post(f"/users/active/{u2_id}", headers=headers_admin)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_basket_delete(client: AsyncClient):
    response = await client.delete(f"/product/deal/{p_id}", headers=headers_admin)
    assert response.status_code == 200

    response_2 = await client.delete(f"/product/deal/0", headers=headers_admin)
    assert response_2.status_code == 200

    response = await client.delete(f"/product/deal/{p_id}", headers=headers_user)
    print(response.json())
    assert response.status_code == 404


@pytest.mark.anyio
async def test_product_delete(client: AsyncClient):
    response = await client.delete(f"/product/{p2_id}", headers=headers_user)
    assert response.status_code == 403

    response = await client.delete(f"/product/{p2_id}", headers=headers_admin)
    assert response.status_code == 200

    response_2 = await client.delete(f"/product/{p_id}", headers=headers_admin)
    assert response_2.status_code == 200


@pytest.mark.anyio
async def test_user_delete(client: AsyncClient):
    response = await client.delete(f"/users/delete/{u_id}", headers=headers_user)
    assert response.status_code == 403

    response = await client.delete(f"/users/delete/{u2_id}", headers=headers_admin)
    assert response.status_code == 200

    response_2 = await client.delete(f"/users/delete/{u_id}", headers=headers_admin)
    assert response_2.status_code == 200
