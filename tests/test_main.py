import asyncio
import random

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from src.main import app
from src.sales.models import Product, Deal
from src.users.models import User
from src.users.utils import create_access_token, create_jwt_for_verify_email, get_hashed_password


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


@pytest.fixture(scope="session")
async def get_headers_admin():
    test_user = {"full_name": "test",
                 "email": "test_admin@test.com",
                 "phone": "+79998887766",
                 "hashed_password": get_hashed_password("Qwerty123!")}
    test_user_admin = await User.create(**test_user)
    test_user_admin.is_staff = True
    test_user_admin.is_superuser = True
    await test_user_admin.save()
    token = create_access_token(test_user["email"])
    headers = {'Authorization': f'Bearer {token}'}
    yield headers
    await test_user_admin.delete()


@pytest.fixture(scope="session")
async def get_headers_user():
    test_user_2 = {"full_name": "test2",
                   "email": "test_not_admin2@test.com",
                   "phone": "+79918687762",
                   "hashed_password": get_hashed_password("Qwerty123!")}
    test_user_ = await User.create(**test_user_2)
    token = create_access_token(test_user_2["email"])
    headers = {'Authorization': f'Bearer {token}'}
    yield headers
    await test_user_.delete()


@pytest.fixture
async def get_user() -> User:
    random_num = random.randint(100, 999)
    test_user_2 = {"full_name": f"test{random_num}",
                   "email": f"test{random_num}_not_admin2@test.com",
                   "phone": f"+7999{random_num}9999",
                   "hashed_password": get_hashed_password("Qwerty123!")}
    test_user = await User.create(**test_user_2)
    return test_user


@pytest.fixture
async def get_user_for_delete() -> User:
    random_num = random.randint(100, 999)
    test_user_2 = {"full_name": f"test{random_num}delete",
                   "email": f"test{random_num}_for_delete@test.com",
                   "phone": f"+7999{random_num}9899",
                   "hashed_password": get_hashed_password("Qwerty123!")}
    test_user = await User.create(**test_user_2)
    return test_user


@pytest.fixture
async def get_product() -> Product:
    random_num = random.randint(100, 999)
    data = {"name": f"test{random_num}", "price": 102, "photo": "test221"}
    prod = await Product.create(**data)
    return prod


@pytest.mark.anyio
async def test_create_user(client: AsyncClient):
    test_user_3 = {"full_name": "test3",
                   "email": "test3_not_admin2@test.com",
                   "phone": "+79918687362",
                   "password": "Qwerty123!",
                   "password_confirm": "Qwerty123!"}
    response = await client.post("/users/register", json=test_user_3)
    u_id = response.json()["id"]
    assert response.status_code == 200, "create user"

    response_1 = await client.post("/users/register", json=test_user_3)
    assert response_1.status_code == 400, "duplicate user"
    await User.filter(id=u_id).delete()

    test_user_3["password"] = "1"
    response_4 = await client.post("/users/register", json=test_user_3)
    assert response_4.status_code == 422, "invalid password"

    test_user_3["phone"] = "+72"
    response_2 = await client.post("/users/register", json=test_user_3)
    assert response_2.status_code == 422, "invalid phone"

    test_user_3["email"] = "1"
    response_3 = await client.post("/users/register", json=test_user_3)
    assert response_3.status_code == 422, "invalid email"


@pytest.mark.anyio
async def test_login_user(client: AsyncClient, get_user):
    user = await get_user

    user_email = {"email_or_phone": user.email,
                  "password": "Qwerty123!"}
    user_phone = {"email_or_phone": user.phone,
                  "password": "Qwerty123!"}
    user_invalid = {"email_or_phone": "phone",
                    "password": "password"}
    response = await client.post("/users/login", json=user_email)
    assert response.status_code == 200, "login by email"

    response_2 = await client.post("/users/login", json=user_phone)
    assert response_2.status_code == 200, "login by phone"

    response_3 = await client.post("/users/login", json=user_invalid)
    assert response_3.status_code == 400, "login wrong"

    await user.delete()


@pytest.mark.anyio
async def test_verify_send(client: AsyncClient, get_headers_user):
    response = await client.post("/users/verify_send", headers=get_headers_user)
    assert response.status_code == 200, "send token"


@pytest.mark.anyio
async def test_verify_post(client: AsyncClient, get_user):
    user_curr = await get_user
    token = create_access_token(user_curr.email)
    headers = {'Authorization': f'Bearer {token}'}
    email_token = create_jwt_for_verify_email(user_curr.email)
    data = {"access_token": "email_token", "token_type": "Bearer"}
    response = await client.post("/users/verify_post", json=data, headers=headers)
    assert response.status_code == 404, "invalid email token"

    data["access_token"] = email_token
    response = await client.post("/users/verify_post", json=data, headers=headers)
    assert response.status_code == 200, "email is verified"
    await user_curr.delete()


@pytest.mark.anyio
async def test_users_list(client: AsyncClient, get_headers_user, get_headers_admin):
    response_2 = await client.get("/users/user_list", headers=get_headers_user)
    assert response_2.status_code == 403, "not admin"

    response = await client.get("/users/user_list", headers=get_headers_admin)
    assert response.status_code == 200, "admin user"


@pytest.mark.anyio
async def test_user_num(client: AsyncClient, get_user, get_headers_user, get_headers_admin):
    user_curr = await get_user
    token = create_access_token(user_curr.email)
    headers = {'Authorization': f'Bearer {token}'}
    response = await client.get(f"/users/user/{user_curr.id}", headers=headers)
    assert response.status_code == 200, "owner user"

    response_1 = await client.get(f"/users/user/{user_curr.id}", headers=get_headers_user)
    assert response_1.status_code == 403, "not owner or admin"

    response_2 = await client.get(f"/users/user/{user_curr.id}", headers=get_headers_admin)
    assert response_2.status_code == 200, "admin user"
    await user_curr.delete()


@pytest.mark.anyio
async def test_user_update(client: AsyncClient, get_user, get_headers_user, get_headers_admin):
    user_curr = await get_user
    token = create_access_token(user_curr.email)
    headers = {'Authorization': f'Bearer {token}'}

    data = {"full_name": "for_delete", "phone": "+71992998877"}
    response = await client.put(f"/users/update/{user_curr.id}", json=data, headers=headers)
    assert response.status_code == 200, "owner"

    response_2 = await client.put(f"/users/update/{user_curr.id}", json=data, headers=get_headers_user)
    assert response_2.status_code == 403, "no permission"

    response_3 = await client.put(f"/users/update/{user_curr.id}", json=data, headers=get_headers_admin)
    assert response_3.status_code == 200, "admin user"
    await user_curr.delete()


@pytest.mark.anyio
async def test_user_active(client: AsyncClient, get_user, get_headers_admin):
    user_curr = await get_user
    token = create_access_token(user_curr.email)
    headers = {'Authorization': f'Bearer {token}'}
    response = await client.post(f"/users/active/{user_curr.id}", headers=headers)
    assert response.status_code == 403, "not admin"

    response = await client.post(f"/users/active/{user_curr.id}", headers=get_headers_admin)
    assert response.status_code == 200, "admin"
    await user_curr.delete()


@pytest.mark.anyio
async def test_user_staff(client: AsyncClient, get_headers_admin, get_user):
    user_curr = await get_user
    token = create_access_token(user_curr.email)
    headers = {'Authorization': f'Bearer {token}'}
    response = await client.post(f"/users/staff/{user_curr.id}", headers=headers)
    assert response.status_code == 403, "not admin"

    response = await client.post(f"/users/staff/{user_curr.id}", headers=get_headers_admin)
    assert response.status_code == 200, "admin"
    await user_curr.delete()


@pytest.mark.anyio
async def test_user_delete(client: AsyncClient, get_user, get_user_for_delete, get_headers_user, get_headers_admin):
    user_ = await get_user
    response = await client.delete(f"/users/delete/{user_.id}", headers=get_headers_user)
    assert response.status_code == 403, "not admin"

    token = create_access_token(user_.email)
    headers = {'Authorization': f'Bearer {token}'}
    response_2 = await client.delete(f"/users/delete/{user_.id}", headers=headers)
    assert response_2.status_code == 200, "owner"

    user_2 = await get_user_for_delete
    response_3 = await client.delete(f"/users/delete/{user_2.id}", headers=get_headers_admin)
    assert response_3.status_code == 200, "admin"
    await user_.delete()
    await user_2.delete()


@pytest.mark.anyio
async def test_create_product(client: AsyncClient, get_headers_admin, get_headers_user):
    data = {"name": "test221", "price": 102, "photo": "test221"}
    response = await client.post("/product/create_product", json=data, headers=get_headers_admin)
    p_id = response.json()["id"]
    assert response.status_code == 200, "create product"

    response_3 = await client.post("/product/create_product", json=data, headers=get_headers_admin)
    assert response_3.status_code == 404, "product duplicate"

    response_2 = await client.post("/product/create_product", json=data, headers=get_headers_user)
    assert response_2.status_code == 403, "not admin"
    await Product.filter(id=p_id).delete()


@pytest.mark.anyio
async def test_product_list(client: AsyncClient, get_headers_user, get_product):
    prod = await get_product
    response = await client.get("/product/product_list", headers=get_headers_user)
    assert response.status_code == 200, "authenticated"

    response_2 = await client.get("/product/product_list")
    assert response_2.status_code == 403, "not authenticated"
    await prod.delete()


@pytest.mark.anyio
async def test_product_get(client: AsyncClient, get_headers_user, get_product):
    prod = await get_product
    response = await client.get(f"/product/{prod.id}", headers=get_headers_user)
    assert response.status_code == 200, "authenticated"

    response_2 = await client.get(f"/product/{prod.id}")
    assert response_2.status_code == 403, "not authenticated"
    await prod.delete()


@pytest.mark.anyio
async def test_product_update(client: AsyncClient, get_headers_user, get_headers_admin, get_product):
    prod = await get_product
    data = {"name": "test_for_delete", "price": 103, "photo": "test32"}
    response = await client.put(f"/product/{prod.id}", json=data, headers=get_headers_user)
    assert response.status_code == 403, "not admin"

    response = await client.put(f"/product/{prod.id}", json=data, headers=get_headers_admin)
    assert response.status_code == 200, "admin"
    await prod.delete()


@pytest.mark.anyio
async def test_product_delete(client: AsyncClient, get_product, get_headers_user, get_headers_admin):
    prod = await get_product
    response = await client.delete(f"/product/{prod.id}", headers=get_headers_user)
    assert response.status_code == 403, "not admin"

    response = await client.delete(f"/product/{prod.id}", headers=get_headers_admin)
    assert response.status_code == 200, "admin"
    await prod.delete()


@pytest.mark.anyio
async def test_product_active(client: AsyncClient, get_headers_user, get_headers_admin, get_product):
    prod = await get_product
    response = await client.post(f"/product/{prod.id}", headers=get_headers_admin)
    assert response.status_code == 200, "admin"

    response = await client.post(f"/product/{prod.id}", headers=get_headers_user)
    assert response.status_code == 403, "not admin"
    await prod.delete()


@pytest.mark.anyio
async def test_basket_add(client: AsyncClient, get_headers_user, get_product):
    prod = await get_product
    response = await client.post(f"/product/deal/{prod.id}&5", headers=get_headers_user)
    assert response.status_code == 200, "add user basket"

    response_2 = await client.post(f"/product/deal/{prod.id}&5")
    assert response_2.status_code == 403, "no user"
    await prod.delete()


@pytest.mark.anyio
async def test_basket_get(client: AsyncClient, get_headers_user, get_product):
    prod = await get_product
    user_curr = await User.get(email="test_not_admin2@test.com")
    data_deal = {"user": user_curr, "product": prod, "count": 1, "price": 102}
    deal = await Deal.create(**data_deal)
    response = await client.get(f"/product/deal/{deal.id}", headers=get_headers_user)
    assert response.status_code == 200

    response_2 = await client.get(f"/product/deal/0", headers=get_headers_user)
    assert response_2.status_code == 200
    await prod.delete()


@pytest.mark.anyio
async def test_basket_delete(client: AsyncClient, get_product, get_user):
    prod = await get_product
    user_curr = await get_user
    data_deal = {"user": user_curr, "product": prod, "count": 1, "price": 102}
    deal = await Deal.create(**data_deal)
    token = create_access_token(user_curr.email)
    headers = {'Authorization': f'Bearer {token}'}
    response = await client.delete(f"/product/deal/{deal.id}", headers=headers)
    assert response.status_code == 200

    await Deal.create(**data_deal)
    response_2 = await client.delete(f"/product/deal/0", headers=headers)
    assert response_2.status_code == 200

    response_3 = await client.delete(f"/product/deal/0", headers=headers)
    assert response_3.status_code == 404
    await prod.delete()
    await user_curr.delete()
