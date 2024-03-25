from typing import List, Any
from users.models import User, UserPydantic, UserPydanticFull, UserListPydantic
from starlette.exceptions import HTTPException
from users.schemas import UserAuth, UserAll, UserBase, UserInDB, TokenSchema, Status, UserToken
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from users.utils import get_user_by_email_or_phone, get_hashed_password, create_access_token, verify_password, \
    get_current_user

router = APIRouter(
    prefix="/users",
    tags=["User"]
)


@router.post("/", summary="Create new user", response_model=UserPydantic)
async def create_user(data: UserAuth):
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
        return await UserPydantic.from_tortoise_orm(user_obj)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=f"Some bad request {e}"
        )


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


@router.delete("/{user_id}", summary='Delete User for Admin or Owner', response_model=Status)
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_superuser or user_id == current_user.id:
        deleted_account = await User.filter(id=user_id).delete()
    else:
        raise HTTPException(status_code=403, detail=f"User {current_user.email} forbidden")
    if not deleted_account:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return Status(status_code="OK", detail=f" User {user_id} deleted")


@router.put("/{user_id}", summary='Update User for Admin or Owner', response_model=UserPydantic)
async def update_user(user_id: int, data: UserAuth, current_user: User = Depends(get_current_user)):
    if current_user.is_superuser or user_id == current_user.id:
        await User.filter(id=user_id).update(
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            hashed_password=get_hashed_password(data.password),
        )
    else:
        raise HTTPException(status_code=403, detail=f"User {current_user.email} forbidden")
    return await UserPydantic.from_queryset_single(User.get(id=user_id))


@router.get("/", summary='Get Users for Staff', response_model=List[UserListPydantic])
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        return await UserListPydantic.from_queryset(User.all())
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} forbidden")


@router.get("/{user_id}", summary='Get User for Staff or Owner', response_model=UserPydantic)
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff or user_id == current_user.id:
        return await UserPydantic.from_queryset_single(User.get(id=user_id))
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} forbidden")


@router.put("/active/{user_id}", summary='Set User.is_active for Staff', response_model=UserPydantic)
async def set_is_active(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        user = await User.filter(id=user_id).first()
        if user.is_active:
            user_ = await User.filter(id=user_id).update(is_active=False)
        else:
            user_ = await User.filter(id=user_id).update(is_active=True)

        return await UserPydantic.from_queryset_single(user_)
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} forbidden")


@router.put("/verify/{user_id}", summary='Set User.is_verify for Staff???', response_model=UserPydantic)
async def set_is_verify(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_staff:
        user = await User.filter(id=user_id).first()
        if user.is_verified:
            raise HTTPException(status_code=403, detail=f"{current_user.email} verified")
        else:
            user_ = await User.filter(id=user_id).update(is_verified=True)

        return await UserPydantic.from_queryset_single(user_)
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} forbidden")


@router.put("/super/{user_id}", summary='Set User.is_staff for Admin???', response_model=UserPydantic)
async def set_is_staff(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_superuser:
        user = await User.filter(id=user_id).first()
        if user.is_staff:
            user_ = await User.filter(id=user_id).update(is_staff=False)
        else:
            user_ = await User.filter(id=user_id).update(is_superuser=True)

        return await UserPydantic.from_queryset_single(user_)
    else:
        raise HTTPException(status_code=403, detail=f"{current_user.email} forbidden")
