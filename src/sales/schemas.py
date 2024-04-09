
from pydantic import BaseModel, conint, ConfigDict

from src.users.schemas import UserAll


class ProductIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    price: conint(gt=0)
    photo: str


class ProductAll(ProductIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class DealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    #user_id: int
    #product_id: int
    user: UserAll
    product: ProductAll
    count: int
    price: int


class DealIn(BaseModel):
    product_id: int
    count: int
    price: int
