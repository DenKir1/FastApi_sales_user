from typing import List, Any

from fastapi_mail import MessageSchema, MessageType, FastMail

from users.models import User, UserPydantic, UserPydanticFull, UserListPydantic
from starlette.exceptions import HTTPException
from users.schemas import UserAuth, UserAll, UserBase, UserInDB, TokenSchema, Status, UserToken, Verification, \
    UserIsActive, UserIsVerified, UserIsStaff
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from users.utils import get_user_by_email_or_phone, get_hashed_password, create_access_token, verify_password, \
    get_current_user, VERIFY_SECRET_KEY, get_user_verify, conf, create_jwt_for_verify_email, create_su_first

router = APIRouter(
    prefix="/users",
    tags=["User"]
)


@router.post("/register", summary="Create new user", response_model=UserPydantic)
async def create_user(data: UserAuth):
    if data.password != data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and Password_confirm don't same"
        )
    user = await User.filter(email=data.email).first()
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    try:
        user_obj = await User.create(
             full_name=data.full_name,
             email=data.email,
             phone=data.phone,
             hashed_password=get_hashed_password(data.password),
         )
        await create_su_first(user_obj)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=f"Some bad request {e}"
        )
    return await UserPydantic.from_tortoise_orm(user_obj)


@router.post("/login", summary="Create access token for user", response_model=TokenSchema)
async def login_token(form_data: UserToken = Depends(UserToken)):
    user = await get_user_by_email_or_phone(form_data.email_or_phone)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or phone"
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    return TokenSchema(access_token=create_access_token(user.email), token_type="Bearer")


@router.post("/verify_send", summary="Send key for verification User",)
async def simple_send(current_user: User = Depends(get_current_user)):
    token = create_jwt_for_verify_email(current_user.email)
    html = f"""<p>{token}</p>"""

    message = MessageSchema(
        subject="Your Token will be expired in an hour",
        recipients=[current_user.email, ],
        body=html,
        subtype=MessageType.html)

    try:
        # fm = FastMail(conf)
        # await fm.send_message(message)
        return Status(status_code="OK", detail=f"Letter for {current_user.email} sent with Token- {token}")
    except Exception as ex:
        Status(status_code="Bad", detail=f" Something wrong {ex}")


@router.delete("/delete/{user_id}", summary='Delete User for Admin or Owner', response_model=Status)
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_superuser or user_id == current_user.id:
        deleted_account = await User.filter(id=user_id).delete()
    else:
        raise HTTPException(status_code=403, detail=f"User {current_user.email} forbidden")
    if not deleted_account:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return Status(status_code="OK", detail=f" User {user_id} deleted")


@router.put("/update/{user_id}", summary='Update User for Admin or Owner', response_model=UserPydantic)
async def update_user(user_id: int, data: UserBase, current_user: User = Depends(get_current_user)):
    if current_user.is_superuser or user_id == current_user.id:
        user = await User.filter(id=user_id).first()
        if user:
            await User.filter(id=user_id).update(**data.model_dump(exclude_unset=True))
            return await UserPydantic.from_queryset_single(User.get(id=user_id))
        else:
            raise HTTPException(status_code=404, detail=f"User {user_id} don't found")
    else:
        raise HTTPException(status_code=403, detail=f"User {current_user.email} forbidden")


@router.get("/user_list", summary='Get Users for Staff', response_model=UserListPydantic)
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        return await UserListPydantic.from_queryset(User.all())
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} forbidden")


@router.get("/user/{user_id}", summary='Get User for Staff or Owner', response_model=UserPydantic)
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff or user_id == current_user.id:
        user = await User.filter(id=user_id).first()
        if user:
            return await UserPydantic.from_tortoise_orm(user)
        else:
            raise HTTPException(status_code=404, detail=f"User {user_id} don't found")
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} forbidden")


@router.post("/active/{user_id}", summary='Set User.is_active for Staff', response_model=UserPydantic)
async def set_is_active(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        user = await User.filter(id=user_id).first()
        if user:
            if user.is_active:
                user.is_active = False
            else:
                user.is_active = True
            await user.save()
            return await UserPydantic.from_tortoise_orm(user)
        else:
            raise HTTPException(status_code=403, detail=f"User {user_id} isn't found")
    else:
        raise HTTPException(status_code=403, detail=f"User {current_user.email} forbidden")


@router.post("/verify_post", summary='Paste your token for verification email', response_model=Status)
async def set_is_verify(token: TokenSchema):
    token_user = await get_user_verify(token.access_token)
    if isinstance(token_user, User):
        if token_user.is_verified:
            return Status(status_code="OK", detail=f" User {token_user.email} has already verified")
        else:
            token_user.is_verified = True
            await token_user.save()
            return Status(status_code="OK", detail=f" User {token_user.email} is verified")
    else:
        raise HTTPException(status_code=404, detail=f"Invalid token")


@router.post("/staff/{user_id}", summary='Set User.is_staff for Admin???', response_model=UserPydantic)
async def set_is_staff(user_id: int,  current_user: User = Depends(get_current_user)):
    if current_user.is_superuser:
        user = await User.filter(id=user_id).first()
        if user:
            if user.is_staff:
                user.is_staff = False
            else:
                user.is_staff = True
            await user.save()
            return await UserPydantic.from_tortoise_orm(user)
        else:
            raise HTTPException(status_code=403, detail=f"User {user_id} isn't found")
    else:
        raise HTTPException(status_code=403, detail=f"User {current_user.email} forbidden")


