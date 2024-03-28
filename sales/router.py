
from typing import List

from fastapi import APIRouter, FastAPI, Depends
from fastapi_pagination.bases import AbstractParams


from sales.models import Product_Pydantic, ProductIn_Pydantic, Product, Product_List_Pydantic, Deal, Deal_Pydantic, \
    Basket, DealIn_Pydantic, Basket_Pydantic
from sales.schemas import ProductIn, ProductUpdate, DealIn
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from fastapi_pagination import Page, add_pagination, paginate, Params

from users.models import User
from users.schemas import Status
from users.utils import get_current_user


router = APIRouter(
    prefix="/product",
    tags=["Product"]
)


@router.get("/product_list", summary="List of Products for Authorized User")
async def get_products(current_user: User = Depends(get_current_user)) -> Page[Product_Pydantic]:
    if current_user:
        prod = await Product_Pydantic.from_queryset(Product.filter(is_active=True))
        return paginate(prod, safe=True)
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.post("/create_product", summary="Create Product for Staff User", response_model=Product_Pydantic)
async def create_product(product: ProductIn, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        prod = await Product.filter(name=product.name).first()
        if prod:
            raise HTTPException(status_code=404, detail=f"{product.name} has already exist")
        else:
            obj = await Product.create(**product.model_dump(exclude_unset=True))
            return await Product_Pydantic.from_tortoise_orm(obj)
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} isn't staff user")


@router.get("/{id}", summary="Get Product for Authorized User", response_model=Product_Pydantic)
async def get_product(p_id: int, current_user: User = Depends(get_current_user)):
    if current_user:
        prod = await Product.filter(id=p_id).first()
        if prod:
            return await Product_Pydantic.from_tortoise_orm(prod)
        else:
            raise HTTPException(status_code=404, detail=f"Product {p_id} don't found")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.put("/{p_id}", summary="Update Product for Staff User", response_model=Product_Pydantic)
async def update_product(p_id: int, product: ProductUpdate, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        prod = await Product.filter(id=p_id).first()
        if prod:
            await Product.filter(id=p_id).update(**product.model_dump(exclude_unset=True))
            return await Product_Pydantic.from_queryset_single(Product.get(id=p_id))
        else:
            raise HTTPException(status_code=404, detail=f"Product {p_id} don't found")
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} isn't staff user")


@router.post("/{p_id}", summary='Set Product.is_active for Staff', response_model=Product_Pydantic)
async def product_is_active(p_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        prod = await Product.filter(id=p_id).first()
        if prod:
            if prod.is_active:
                prod.is_active = False
            else:
                prod.is_active = True
            await prod.save()
            return await Product_Pydantic.from_queryset_single(Product.get(id=p_id))
        else:
            raise HTTPException(status_code=403, detail=f"Product {p_id} isn't found")
    else:
        raise HTTPException(status_code=403, detail=f"User {current_user.email} forbidden")


@router.delete("/{p_id}", summary="Delete Product for Staff User", response_model=Status)
async def delete_product(p_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        deleted_count = await Product.filter(id=p_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=404, detail=f"Product {p_id} not found")
        return Status(status_code="OK", detail=f"Product {p_id} was deleted ")
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} isn't staff user")


@router.post("/basket", summary="Add product in basket for User", response_model=Basket_Pydantic)
async def add_product(deal: DealIn, current_user: User = Depends(get_current_user)):
    if current_user:
        product = await Product.filter(id=deal.product).first()
        if not product:
            raise HTTPException(status_code=403, detail=f"Product {deal.product} not found")
        basket = await Basket.update_or_create(user=current_user)
        deal = {"basket": basket[0],
                "product": product,
                "count": deal.count,
                }
        await Deal.create(**deal)
        return await Basket_Pydantic.from_queryset_single(Basket.get(user=current_user))
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.get("/basket", summary="Get basket for User", response_model=Basket_Pydantic)
async def get_basket(current_user: User = Depends(get_current_user)):
    if current_user:
        basket = await Basket.filter(user=current_user).first()
        if basket:
            return await Basket_Pydantic.from_tortoise_orm(basket)
        else:
            return HTTPException(status_code=404, detail=f"{current_user.email} basket empty")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.delete("/basket", summary="Delete basket for User", response_model=Status)
async def delete_basket(current_user: User = Depends(get_current_user)):
    if current_user:
        basket = await Basket.filter(user=current_user).first()
        if basket:
            await Deal.filter(basket=basket).delete()
            return Status(message=f"Basket {current_user.email} was deleted ")
        else:
            return HTTPException(status_code=404, detail=f"{current_user.email} basket empty")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.put("/basket/{d_id}", summary="Delete Deal_id from basket for User", response_model=Basket_Pydantic)
async def delete_basket_deal(d_id: int, current_user: User = Depends(get_current_user)):
    if current_user:
        basket = await Basket.filter(user=current_user).first()
        if basket:
            obj = await Deal.filter(basket=basket, id=d_id).delete()
            if not obj:
                raise HTTPException(status_code=404, detail=f"Deal {d_id} not found")
            return await Basket_Pydantic.from_queryset_single(Basket.get(user=current_user))
        else:
            return HTTPException(status_code=404, detail=f"{current_user.email} basket empty")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")
