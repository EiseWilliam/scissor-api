from datetime import timedelta
from typing import Any
from bson import ObjectId

from fastapi import HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import EmailStr

from app.core.backend import auth as security
from app.schemas.user import CreateUser, ReadUser, UpdateUser, _ReadUser
from app.services.base_crud import BaseCRUD


class UserHandler(BaseCRUD[CreateUser, ReadUser, UpdateUser]):
    def __init__(self, db_conn: AsyncIOMotorDatabase):
        super().__init__(db_conn, "users")

    async def email_exists(self, email: EmailStr) -> bool:
        item = await self._db_conn.get_collection(self._collection).find_one({"email": email})
        return item is not None

    async def get_by_email(self, email: str) -> ReadUser | None:
        item = await self._db_conn.get_collection(self._collection).find_one({"email": email})
        if item:
            return ReadUser(**item)

    async def private_get_by_email(self, email: str) -> _ReadUser | None:
        item = await self._db_conn.get_collection(self._collection).find_one({"email": email})
        if item:
            return _ReadUser(**item)

    def handle_password(self, user: CreateUser) -> CreateUser:
        user.password = security.hash_password(user.password)
        return user

    async def register_user(self, user: CreateUser) -> Any:
        if await self.email_exists(user.email):
            raise HTTPException(status_code=409, detail="EMAIL_ALREADY_REGISTERED")
        user_to_db = self.handle_password(user)
        user_in_db = await self.create(
            user_to_db,
        )
        return user_in_db
    
    async def update_user(self, id: str | ObjectId, item: UpdateUser) -> bool:
        if isinstance(id, ObjectId):
            id = str(id)
        result = await self._update(
            id, item.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
        )
        await self.on_update()
        return result.acknowledged
     
    async def authenticate_user(self, email: str, password: str) -> Any:
        user = await self.private_get_by_email(email)
        if not user:
            return None
        if not await security.verify_password(password, user.password):
            return None

        return user

    async def generate_login_tokens(self, user: ReadUser) -> dict[str, str]:
        access_token_expires = timedelta(security.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await security.create_access_token(
            data={"sub": str(user.id), "email": user.email}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(security.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = await security.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}, expires_delta=refresh_token_expires
        )
        return {"access_token": access_token, "refresh_token": refresh_token}

    # verification
    # async def request_email_verification(self, user: ReadUser, request: Request) -> None:
    #     if not user:
    #         return None
    #     if user.is_verified:
    #         return None
    #     token_data = {
    #         "sub": str(user.id),
    #         "email": user.email,
    #         "aud": VERIFICATION_TOKEN_AUDIENCE,
    #     }
    #     verification_code = await security.create_verification_code(token_data)
    #     await self.after_request_verification(user, verification_code, request)

    # async def verify_email(
    #     self, verification_code: str, request: Request | None = None
    # ) -> bool | None:
    #     payload = await security.decode_verification_code(verification_code, VERIFICATION_TOKEN_AUDIENCE)
    #     user = await self.get_by_id(payload["sub"], self._db_conn)
    #     if not user:
    #         raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    #     if user["is_verified"]:
    #         raise HTTPException(status_code=400, detail="USER_ALREADY_VERIFIED")
    #     user_dict = {"is_verified": True}
    #     await self._update(payload["sub"], user_dict, self._db_conn)
    #     await self.after_verification(payload, request)
    #     return True

    # # <--------   Triggered by events ----------->
    # async def after_request_verification(
    #     self, user: ReadUser, verification_code: str, request: Request
    # ) -> None:
    #     sent = await send_verification_email(user.email, verification_code, request)
    #     if sent is True:
    #         pass
    #     else:
    #         raise HTTPException(status_code=500, detail="EMAIL_NOT_SENT")

    # async def after_verification(self, user: dict, request: Request | None = None) -> None:
    #     print(user["email"], " has been verified")
