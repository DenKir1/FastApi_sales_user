
from typing import List

from fastapi import APIRouter, FastAPI, Depends

from sales.models import Product_Pydantic, ProductIn_Pydantic, Product, Product_List_Pydantic, Deal, Deal_Pydantic, \
    Basket, DealIn_Pydantic, Basket_Pydantic
from sales.schemas import BasketOut
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from fastapi_pagination import Page, add_pagination, paginate

from users.models import User
from users.utils import get_current_user

app = FastAPI()
add_pagination(app)
router = APIRouter(
    prefix="/Product",
    tags=["Product"]
)


class Status(BaseModel):
    message: str


@router.get("/product_list", summary="List of Products for Authorized User", response_model=Product_List_Pydantic)
async def get_products(current_user: User = Depends(get_current_user)) -> Page[Product_List_Pydantic]:
    if current_user:
        products = await Product_List_Pydantic.from_queryset(Product.filter(is_active=True))
        return paginate(products)
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.post("/product", summary="Post Product for Staff User", response_model=Product_Pydantic)
async def create_product(product: ProductIn_Pydantic, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        obj = await Product.create(**product.model_dump(exclude_unset=True))
        return await Product_Pydantic.from_tortoise_orm(obj)
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} isn't staff user")


@router.get("/product/{id}", summary="Get Product for Authorized User", response_model=Product_Pydantic)
async def get_product(p_id: int, current_user: User = Depends(get_current_user)):
    if current_user:
        return await Product_Pydantic.from_queryset_single(Product.get(id=p_id))
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.put("/product/{p_id}", summary="Update Product for Staff User", response_model=Product_Pydantic)
async def update_product(p_id: int, product: ProductIn_Pydantic, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        await Product.filter(id=p_id).update(**product.model_dump(exclude_unset=True))
        return await Product_Pydantic.from_queryset_single(Product.get(id=p_id))
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} isn't staff user")


@router.delete("/product/{p_id}", summary="Delete Product for Staff User", response_model=Status)
async def delete_product(p_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        deleted_count = await Product.filter(id=p_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=404, detail=f"Product {p_id} not found")
        return Status(message=f"Product {p_id} was deleted ")
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} isn't staff user")


@router.post("/basket", summary="Add product in basket for User", response_model=Deal_Pydantic)
async def add_product(deal: DealIn_Pydantic, current_user: User = Depends(get_current_user)):
    if current_user:
        basket = await Basket.get(user=current_user)
        product = await Product.get(id=deal.product)
        if not product:
            raise HTTPException(status_code=403, detail=f"Product {deal.product} not found")

        deal = {"basket": basket,
                "product": product,
                "count": deal.count,
                }
        obj = await Deal.create(**deal)
        return await BasketOut.from_tortoise_orm(basket)
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.get("/basket", summary="Get basket for User", response_model=Deal_Pydantic)
async def get_basket(current_user: User = Depends(get_current_user)):
    if current_user:
        basket = await Basket.get(user=current_user)
        return await BasketOut.from_tortoise_orm(basket)
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.delete("/basket", summary="Delete basket for User", response_model=Deal_Pydantic)
async def delete_basket(current_user: User = Depends(get_current_user)):
    if current_user:
        basket = await Basket.get(user=current_user)
        await Deal.filter(basket=basket).delete()
        return Status(message=f"Basket {current_user.email} was deleted ")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.put("/basket/{d_id}", summary="Delete Deal_id from basket for User", response_model=Deal_Pydantic)
async def delete_basket_deal(d_id: int, current_user: User = Depends(get_current_user)):
    if current_user:
        basket = await Basket.get(user=current_user)
        obj = await Deal.filter(basket=basket, id=d_id).delete()
        if not obj:
            raise HTTPException(status_code=404, detail=f"Deal {d_id} not found")
        return await BasketOut.from_tortoise_orm(basket)
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


