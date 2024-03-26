from pydantic import BaseModel

from sales.models import Basket, Deal


def getter_summ(user=None) -> int:
    if user is None:
        return 0
    else:
        basket = await Basket.get(user=user)
        deals = await Deal.filter(basket=basket)
        total = 0
        for deal in deals:
            total += deal.product.price * deal.count
        return total


def total_price(self):
    return getter_summ(self.user)


class BasketOut(BaseModel):
    pass





