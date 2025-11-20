__all__ = [
    "decode_token",
    "get_user",
    "get_user_async",
    "register_user",
    "authenticate_user",
    "create_access_token",
    "set_contextvars",
    "context_user",
    "context_request_id",
]

import contextvars
from datetime import timedelta
from functools import lru_cache
from uuid import uuid4

from auditlog.cid import correlation_id
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from fastapi import HTTPException, Request
from jose import JWTError, jwt

from fango.utils import run_async

context_user = contextvars.ContextVar("context_user")
context_request_id = contextvars.ContextVar("context_request_id")


def decode_token(auth: str) -> dict:
    try:
        _, token = auth.split()
        return jwt.decode(
            token,
            settings.PUBLIC_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
    except (ValueError, UnicodeDecodeError, JWTError) as e:
        raise HTTPException(status_code=403, detail=str(e))


def get_user(request: Request) -> User | None:
    """
    Function returns User instance by token.

    """
    UserModel: User = get_user_model()  # type: ignore
    if access_token := request.headers.get("Authorization"):
        payload = decode_token(access_token)
        if (
            user := UserModel.objects.only(*getattr(settings, "REQUEST_USER_FIELDS", ()))
            .filter(id=payload["user_id"])
            .first()
        ):
            return user


async def get_user_async(request: Request) -> User | None:
    """
    Function returns User instance by token async.

    """
    UserModel: User = get_user_model()  # type: ignore
    if access_token := request.headers.get("Authorization"):
        payload = decode_token(access_token)
        if (
            user := await UserModel.objects.only(*getattr(settings, "REQUEST_USER_FIELDS", ()))
            .filter(id=payload["user_id"])
            .afirst()
        ):
            return user


async def set_contextvars(request: Request) -> User | None:
    """
    Function is set context variables for request.

    """
    user = await get_user_async(request)
    request_id = str(uuid4())

    context_user.set(user)
    correlation_id.set(request_id)  # type: ignore
    context_request_id.set(request_id)

    return user


async def register_user(email: str, password: str) -> User:
    """
    Function is creating User instance by token async.

    """
    UserModel: User = get_user_model()  # type: ignore
    user = await UserModel.objects.acreate(
        email=email,
    )
    user.set_password(password)
    await user.asave(update_fields=["password"])
    return user


async def authenticate_user(request: Request, email: str, password: str) -> User:
    """
    Function is authenticate user with django backend.

    """
    return await run_async(authenticate, request=request, email=email, password=password)


def create_access_token(user: User) -> str:
    """
    Function is creating access token.

    """
    if expires_delta := timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
        expire = timezone.now() + expires_delta
    else:
        expire = timezone.now() + timedelta(minutes=15)

    to_encode = {
        "exp": expire,
        "jti": str(uuid4()),
        "user_id": user.pk,
        "token_type": "access",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@lru_cache
def get_user_from_token(access_token: str) -> User:
    """
    Function is get User by access token.

    """
    UserModel: User = get_user_model()  # type: ignore
    payload = decode_token(access_token)
    return UserModel.objects.get(pk=payload["user_id"])
