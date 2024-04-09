from fastapi import Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
import jwt
from starlette import status
from src.users.models import User
from src.users.schemas import TokenPayload
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_mail import ConnectionConfig
from src import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.EMAIL_HOST_USER,
    MAIL_PASSWORD=config.EMAIL_HOST_PASSWORD,
    MAIL_FROM=config.EMAIL_HOST_USER,
    MAIL_PORT=config.EMAIL_PORT,
    MAIL_SERVER=config.EMAIL_HOST,
    MAIL_FROM_NAME="Onion Store FastApi",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


JWT_SECRET_KEY = config.JWT_SECRET_KEY
VERIFY_SECRET_KEY = config.VERIFY_SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = HTTPBearer()


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


async def get_user_by_email_or_phone(email_or_phone: str):
    if email_or_phone.startswith("+7"):
        user = await User.filter(phone=email_or_phone).first()
    else:
        user = await User.filter(email=email_or_phone).first()

    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.filter(email=token_data.sub).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inactive user",
        )
    return user


def create_jwt_for_verify_email(email) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "sub": str(email)}
    secret = jwt.encode(to_encode, VERIFY_SECRET_KEY, ALGORITHM)
    return secret


async def get_user_verify(token: str) -> User:
    try:
        payload = jwt.decode(token, VERIFY_SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) > datetime.now():
            user = await User.filter(email=token_data.sub).first()
            return user
    except Exception:
        raise HTTPException(status_code=404, detail=f"Invalid token")


# async def create_su_first(user: User) -> None:
#     """Three first users will become admins (need for test)"""
#     if user.id < 4:
#         user.is_active = True
#         user.is_verified = True
#         user.is_staff = True
#         user.is_superuser = True
#         await user.save()
