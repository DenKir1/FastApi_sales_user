from pydantic import BaseModel, conint


class ProductIn(BaseModel):
    name: str
    price: conint(gt=0)
    photo: str


class DealIn(BaseModel):
    product: conint(gt=0)
    count: conint(gt=0)


class DealOut(BaseModel):
    id: int
    product: ProductIn
    count: int
