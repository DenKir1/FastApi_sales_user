from pydantic import BaseModel, EmailStr, constr, model_validator


class UserToken(BaseModel):

    email_or_phone: str
    password: str


class UserBase(BaseModel):

    full_name: str
    email: EmailStr
    phone: constr(pattern=r'^\+7\d{10}$')


class UserUpdate(BaseModel):

    full_name: str
    phone: constr(pattern=r'^\+7\d{10}$')


class UserAuth(UserBase):
    password: constr(min_length=8)
    password_confirm: constr(min_length=8)

    @model_validator(mode='before')
    def hashed_password_validation(self):
        if not any(char.isupper() for char in self["password"]):
            raise ValueError('Пароль должен содержать заглавную букву!')
        if not any(char in '$%&!:.' for char in self["password"]):
            raise ValueError('Пароль должен содержать специальный символ: $%&!:.')
        return self


class UserAll(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    access_token: str = None


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
