from tortoise.functions import Sum

from sales.models import Deal
from users.models import User


async def total_sum(user: User):
    total_ = await Deal.annotate(sum=Sum("price")).filter(user=user)
    return total_
