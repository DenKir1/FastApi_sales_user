from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator


class User(models.Model):
    """
    The User model
    """
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    phone = fields.CharField(max_length=12, unique=True)
    full_name = fields.CharField(max_length=200)
    hashed_password = fields.CharField(max_length=128, null=True)
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    class PydanticMeta:
        exclude = ["hashed_password", ]


UserPydantic = pydantic_model_creator(User)
UserPydanticFull = pydantic_model_creator(User, exclude_readonly=True)
UserListPydantic = pydantic_queryset_creator(User, include=("id", ))
