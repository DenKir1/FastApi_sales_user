
from fastapi import APIRouter, Depends
from sales.models import Product_Pydantic, Product, Deal
from sales.schemas import ProductIn, DealIn, DealOut
from starlette.exceptions import HTTPException
from fastapi_pagination import Page, paginate

from users.models import User
from users.utils import get_current_user
from sales.utils import total_sum


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
async def update_product(p_id: int, product: ProductIn, current_user: User = Depends(get_current_user)):
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


@router.delete("/{p_id}", summary="Delete Product for Staff User")
async def delete_product(p_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        deleted_count = await Product.filter(id=p_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=404, detail=f"Product {p_id} not found")
        return HTTPException(status_code=200, detail=f"Product {p_id} was deleted ")
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} isn't staff user")


@router.post("/basket", summary="Add product in basket for User",)
async def add_deal(deal_cur: DealIn, current_user: User = Depends(get_current_user)):
    if current_user:
        prod = await Product.filter(id=deal_cur.product).first()
        if prod:
            deal_ = {"user": current_user, "product": prod, "count": deal_cur.count}
            obj = await Deal.create(**deal_)
            return await DealOut.from_tortoise_orm(obj)
        else:
            raise HTTPException(status_code=403, detail=f"Product {deal_cur.product} not found")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.get("/basket", summary="Get basket for User")
async def get_basket(current_user: User = Depends(get_current_user)):
    if current_user:
        basket = await Deal.filter(user=current_user)
        if basket:
            basket_list = await DealOut.from_queryset(basket)
            tot_sum = total_sum(current_user)
            return {"basket": basket_list, "total": tot_sum}
        else:
            return HTTPException(status_code=404, detail=f"{current_user.email} basket empty")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.delete("/basket", summary="Delete basket for User")
async def delete_basket(current_user: User = Depends(get_current_user)):
    if current_user:
        deleted_item = await Deal.filter(user=current_user).delete()
        if deleted_item:
            return HTTPException(status_code=200, detail=f"Basket {current_user.email} was deleted")
        else:
            return HTTPException(status_code=404, detail=f"{current_user.email} basket is empty")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.put("/basket/{d_id}", summary="Delete Deal_id from basket for User")
async def delete_basket_deal(d_id: int, current_user: User = Depends(get_current_user)):
    if current_user:
        obj = await Deal.filter(user=current_user, id=d_id).delete()
        if not obj:
            raise HTTPException(status_code=404, detail=f"Deal {d_id} not found")
        else:
            return HTTPException(status_code=200, detail=f"deal {d_id} is deleted from basket")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")
