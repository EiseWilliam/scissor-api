from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.backend import auth as security
from app.core.backend.auth import cookie_scheme, oauth2_scheme
from app.db.database import db as simple_db
from app.schemas.user import ReadUser
from app.services.url import UrlHandler
from app.services.user import UserHandler


def get_db() -> AsyncIOMotorDatabase:
    return simple_db


db = Annotated[AsyncIOMotorDatabase, Depends(get_db)]


def get_user_handler(db: db) -> UserHandler:
    return UserHandler(db)


user_handler = Annotated[UserHandler, Depends(get_user_handler)]


# schemes
def get_url_handler(db: db) -> UrlHandler:
    return UrlHandler(db)


url_handler = Annotated[UrlHandler, Depends(get_url_handler)]


async def get_jwt(token: str = Depends(oauth2_scheme), token2: str = Depends(cookie_scheme)) -> Any:
    if token:
        return token
    else:
        return token2


jwt_scheme = Annotated[str, Depends(get_jwt)]

# async def get_current_user(
#     token: str = Depends(get_jwt),
#     db: AsyncIOMotorDatabase = Depends(get_db),
# ) -> Any:
#     payload = await security.decode_token(token)
#     if not payload:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_TOKEN")
#     user = await user_handler.get_by_email(payload["email"], db)
#     if not user:
#         raise HTTPException(status_code=401, detail="UNAUTHORIZED")
#     return user


async def get_current_user(token: jwt_scheme, handler: user_handler) -> ReadUser:
    if token:
        payload = await security.verify_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_TOKEN")
        user = await handler.get_by_email(payload["email"])
        if not user:
            raise HTTPException(status_code=401, detail="UNAUTHORIZED")
        return user
    else:
        raise HTTPException(status_code=401, detail="UNAUTHENTICATED")


current_user_dep = Annotated[ReadUser, Depends(get_current_user)]


async def get_active_user(
    current_user: dict = Depends(get_current_user),
) -> Any:
    if not current_user["is_active"]:
        raise HTTPException(status_code=403, detail="INACTIVE_USER")
    return current_user


async def get_superuser(
    current_user: dict = Depends(get_current_user),
) -> Any:
    if not current_user["is_superuser"]:
        raise HTTPException(status_code=403, detail="NOT_SUPERUSER")
    return current_user
