
from pydantic import BaseModel, conint


class ProductIn(BaseModel):
    name: str
    price: conint(gt=0)
    photo: str


class DealOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    count: int
    price: int


class DealIn(BaseModel):
    product_id: int
    count: int
    price: int
