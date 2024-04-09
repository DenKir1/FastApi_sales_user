
from pydantic import BaseModel, conint, ConfigDict


class ProductIn(BaseModel):
    name: str
    price: conint(gt=0)
    photo: str


class ProductAll(ProductIn):
    id: int


class DealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    count: int
    price: int


class DealIn(BaseModel):
    product_id: int
    count: int
    price: int
