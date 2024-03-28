from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from users.models import User


class Product(models.Model):
    """
    The Product model
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    price = fields.IntField()
    photo = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    class PydanticMeta:
        pass


class Basket(models.Model):
    """
    The Basket model
    """
    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation[User] = fields.OneToOneField("models.User", on_delete=fields.CASCADE)

    def total(self) -> int:
        deals_in_basket = Deal.filter(basket=self)
        total = 0
        for deal in deals_in_basket:
            total += deal.product.price * deal.count
        return total

    class Meta:
        ordering = ["id"]

    class PydanticMeta:
        computed = ("total", )
        max_recursion = 4
        allow_cycles = True


class Deal(models.Model):
    """
    The Deal model
    """
    id = fields.IntField(pk=True)
    basket = fields.ForeignKeyField("models.Basket", on_delete=fields.CASCADE)
    product = fields.ForeignKeyField("models.Product", related_name="products_in_deal")
    count = fields.IntField()

    class Meta:
        ordering = ["id"]

    class PydanticMeta:
        pass


Product_Pydantic = pydantic_model_creator(Product, name="Product")
ProductIn_Pydantic = pydantic_model_creator(Product, name="ProductIn", exclude_readonly=True)
Product_List_Pydantic = pydantic_queryset_creator(Product, name="Product_List")
Deal_Pydantic = pydantic_model_creator(Deal, name="Deal")
DealIn_Pydantic = pydantic_model_creator(Deal, name="DealIn", exclude_readonly=True)
Basket_Pydantic = pydantic_model_creator(Basket, name="Basket")

