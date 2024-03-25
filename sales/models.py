from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


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

    class PydanticMeta:
        pass


class Basket(models.Model):
    """
    The Basket model
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    products: fields.ForeignKeyRelation[Product] = fields.ForeignKeyField("models.Product", related_name="products")

    class PydanticMeta:
        pass


Product_Pydantic = pydantic_model_creator(Product, name="Product")
ProductIn_Pydantic = pydantic_model_creator(Product, name="ProductIn", exclude_readonly=True)
Basket_Pydantic = pydantic_model_creator(Basket, name="Basket")
BasketIn_Pydantic = pydantic_model_creator(Basket, name="BasketIn", exclude_readonly=True)
