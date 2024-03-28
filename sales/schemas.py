from pydantic import BaseModel, conint


class ProductIn(BaseModel):
    name: str
    price: conint(gt=0)
    photo: str


class ProductUpdate(BaseModel):
    name: str
    price: conint(gt=0)
    photo: str


class DealIn(BaseModel):
    product: conint(gt=0)
    count: conint(gt=0)

#
# from sales.models import Basket, Deal
#
# class BasketOut(BaseModel):
#
#     def total_price(self):
#         return getter_summ(self.user)





