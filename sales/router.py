
from typing import List

from fastapi import APIRouter

from sales.models import Product_Pydantic, ProductIn_Pydantic, Product
from pydantic import BaseModel
from starlette.exceptions import HTTPException

router = APIRouter(
    prefix="/Product",
    tags=["Product"]
)


class Status(BaseModel):
    message: str


@router.get("/Product", response_model=List[Product_Pydantic])
async def get_products():
    return await Product_Pydantic.from_queryset(Product.all())


@router.post("/Product", response_model=Product_Pydantic)
async def create_product(product: ProductIn_Pydantic):
    obj = await Product.create(**product.model_dump(exclude_unset=True))
    return await Product_Pydantic.from_tortoise_orm(obj)


@router.get("/product/{id}", response_model=Product_Pydantic)
async def get_product(p_id: int):
    return await Product_Pydantic.from_queryset_single(Product.get(id=p_id))


@router.put("/product/{p_id}", response_model=Product_Pydantic)
async def update_product(p_id: int, product: ProductIn_Pydantic):
    await Product.filter(id=p_id).update(**product.model_dump(exclude_unset=True))
    return await Product_Pydantic.from_queryset_single(Product.get(id=p_id))


@router.delete("/product/{p_id}", response_model=Status)
async def delete_product(p_id: int):
    deleted_count = await Product.filter(id=p_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Product {p_id} not found")
    return Status(message=f"Deleted Product {p_id}")
