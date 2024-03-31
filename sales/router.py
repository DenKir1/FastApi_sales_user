
from fastapi import APIRouter, Depends
from sales.models import Product_Pydantic, Product, Deal
from sales.schemas import ProductIn
from starlette.exceptions import HTTPException
from fastapi_pagination import Page, paginate

from users.models import User
from users.utils import get_current_user
from sales.utils import total_func

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


@router.post("/deal/{product_id}&{count_product}", summary="Create deal for User")
async def add_product_to_deal(product_id: int, count_product: int, current_user: User = Depends(get_current_user)):
    if count_product < 1:
        raise HTTPException(status_code=403, detail=f"{count_product} must be greater than 0")
    if current_user:
        prod = await Product.filter(id=product_id).first()
        if prod:
            deal_ = {
                "user": current_user,
                "product": prod,
                "count": count_product,
                "price": prod.price * count_product}
            obj = await Deal.create(**deal_)
            # Id is lost if use Pydantic schemas
            return obj
        else:
            raise HTTPException(status_code=403, detail=f"Product {product_id} not found")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.get("/deal/{d_id}", summary="Get basket for User (d_id=0) or deal_id")
async def get_basket(d_id: int, current_user: User = Depends(get_current_user)):
    if current_user:
        if d_id == 0:
            basket = await Deal.filter(user=current_user)
        else:
            basket = await Deal.filter(user=current_user, id=d_id).first()
        if basket:
            total = total_func(basket)
            return {"basket": basket, "total": total}
        else:
            return HTTPException(status_code=404, detail=f"{d_id} don't exist or {current_user.email} basket is empty")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")


@router.delete("/deal/{d_id}", summary="Delete basket for User (d_id=0) or deal_id")
async def delete_basket(d_id: int, current_user: User = Depends(get_current_user)):
    if current_user:
        if d_id == 0:
            deleted_item = await Deal.filter(user=current_user).delete()
        else:
            deleted_item = await Deal.filter(user=current_user, id=d_id).delete()
        if deleted_item:
            return HTTPException(status_code=200, detail=f"{current_user.email} deal {d_id or 'all'} was deleted")
        else:
            return HTTPException(status_code=404, detail=f"{current_user.email} deal {d_id or 'all'} is empty")
    else:
        raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")

#
# @router.put("/deal/{d_id}", summary="Delete Deal_id from basket for User")
# async def delete_basket_deal(d_id: int, current_user: User = Depends(get_current_user)):
#     if current_user:
#         obj = await Deal.filter(user=current_user, id=d_id).delete()
#         if not obj:
#             raise HTTPException(status_code=404, detail=f"Deal {d_id} not found")
#         else:
#             return HTTPException(status_code=200, detail=f"deal {d_id} is deleted from basket")
#     else:
#         raise HTTPException(status_code=401, detail=f"{current_user.email} is unauthorized user")
