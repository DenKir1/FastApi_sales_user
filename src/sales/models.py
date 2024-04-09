from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator


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
        exclude = ["products_in_deal", ]


class Deal(models.Model):
    """
    The Deal model
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("users.User", on_delete=fields.CASCADE)
    product = fields.ForeignKeyField("sales.Product", related_name="products_in_deal")
    count = fields.IntField()
    price = fields.IntField()

    class Meta:
        ordering = ["id"]

    class PydanticMeta:
        pass


Product_Pydantic = pydantic_model_creator(Product)
ProductIn_Pydantic = pydantic_model_creator(Product, exclude_readonly=False)
Product_List_Pydantic = pydantic_queryset_creator(Product)
Deal_Pydantic = pydantic_model_creator(Deal)
DealIn_Pydantic = pydantic_model_creator(Deal, exclude_readonly=True)
DealListPydantic = pydantic_queryset_creator(Deal)
