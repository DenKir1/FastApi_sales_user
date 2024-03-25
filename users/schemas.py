from typing import Optional

from pydantic import BaseModel, EmailStr, constr, model_validator
from starlette import status


class UserToken(BaseModel):

    email_or_phone: str
    password: str


class UserBase(BaseModel):

    full_name: str
    email: EmailStr
    phone: constr(pattern=r'^\+7\d{10}$')


class UserAuth(UserBase):
    password: constr(min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Name LastName",
                "email": "sample@sample.com",
                "phone": "+79998887766",
                "password": "My2verystrongpa$$word",
            }
        }

    #@model_validator(mode='before')
    #@classmethod
    #def hashed_password_validation(cls, v):
    #    if not any(char.isupper() for char in v['hashed_password']):
    #        raise ValueError('Пароль должен содержать заглавную букву!')
    #    if not any(char in '$%&!:.' for char in v['hashed_password']):
    #        raise ValueError('Пароль должен содержать один из специальных символов: $%&!:.')
    #    return v


class UserAll(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    access_token: str = None


class UserInDB(UserAll):
    hashed_password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenData(TokenSchema):
    user: UserBase


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class Status(BaseModel):
    status_code: str
    detail: str
