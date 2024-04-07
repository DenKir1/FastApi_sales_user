from typing import List

from fastapi_mail import MessageSchema, MessageType
from src.users.models import User, UserPydantic
from starlette.exceptions import HTTPException
from src.users.schemas import UserAuth, TokenSchema, UserToken, UserUpdate
from fastapi import Depends, HTTPException, status, APIRouter
from src.users.utils import get_user_by_email_or_phone, get_hashed_password, create_access_token, verify_password, \
    get_current_user, get_user_verify, create_jwt_for_verify_email

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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=f"Some bad request {e}"
        )
    return await UserPydantic.from_tortoise_orm(user_obj)


@router.post("/login", summary="Create access token for user", response_model=TokenSchema)
async def login_token(form_data: UserToken):
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
    if current_user.is_verified:
        return HTTPException(status_code=200, detail=f"{current_user.email} has already verified")

    token = create_jwt_for_verify_email(current_user.email)
    html = f"""<p>{token}</p>"""

    message = MessageSchema(
        subject="Your Token will be expired in an hour",
        recipients=[current_user.email, ],
        body=html,
        subtype=MessageType.html)

    try:
        # # Send email for verify user
        # fm = FastMail(conf)
        # await fm.send_message(message)
        print(token)
        return HTTPException(status_code=200, detail=f"Letter for {current_user.email} was sent with Token")
    except Exception as ex:
        raise HTTPException(status_code=404, detail=f" Something is wrong {ex}")


@router.delete("/delete/{user_id}", summary='Delete User for Admin or Owner')
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_superuser or user_id == current_user.id:
        deleted_account = await User.filter(id=user_id).delete()
    else:
        raise HTTPException(status_code=403, detail=f"User {current_user.email} forbidden")
    if not deleted_account:
        raise HTTPException(status_code=404, detail=f"User {user_id} isn't found")
    return HTTPException(status_code=200, detail=f"User {user_id} deleted")


@router.put("/update/{user_id}", summary='Update User for Admin or Owner', response_model=UserPydantic)
async def update_user(user_id: int, data: UserUpdate, current_user: User = Depends(get_current_user)):
    if current_user.is_superuser or user_id == current_user.id:
        user = await User.filter(id=user_id).first()
        if user:
            await User.filter(id=user_id).update(**data.model_dump(exclude_unset=True))
            return await UserPydantic.from_queryset_single(User.get(id=user_id))
        else:
            raise HTTPException(status_code=404, detail=f"User {user_id} isn't found")
    else:
        raise HTTPException(status_code=403, detail=f"User {current_user.email} forbidden")


@router.get("/user_list", summary='Get Users for Staff', response_model=List[UserPydantic])
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        return await UserPydantic.from_queryset(User.all())
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} forbidden")


@router.get("/user/{user_id}", summary='Get User for Staff or Owner', response_model=UserPydantic)
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff or user_id == current_user.id:
        user = await User.filter(id=user_id).first()
        if user:
            return await UserPydantic.from_tortoise_orm(user)
        else:
            raise HTTPException(status_code=404, detail=f"User {user_id} isn't found")
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


@router.post("/verify_post", summary='Paste your token for verification email')
async def set_is_verify(token: TokenSchema):
    token_user = await get_user_verify(token.access_token)
    if isinstance(token_user, User):
        if token_user.is_verified:
            raise HTTPException(status_code=200, detail=f"User {token_user.email} has already verified")
        else:
            token_user.is_verified = True
            await token_user.save()
            raise HTTPException(status_code=200, detail=f"User {token_user.email} is verified")
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
