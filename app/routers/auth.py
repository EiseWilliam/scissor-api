from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

# from app.services.user import user_handler
from app.core.dependencies import user_handler
from app.core.exceptions import UnauthorizedException
from app.core.responses import DResponse, LoginTokenResponse
from app.schemas.user import CreateUser, CreateUserRequest

router = APIRouter(default_response_class=DResponse, tags=["auth"])


@router.post("/register")
async def register_user(data: CreateUserRequest, handler: user_handler):
    user = CreateUser(
        email=data.email,
        password=data.password,
    )
    new_user_id = await handler.register_user(user)
    return DResponse(content={"message": "user registered successfully", "user_id": new_user_id})


@router.post("/login", response_model=LoginTokenResponse)
async def login_user(data: Annotated[OAuth2PasswordRequestForm, Depends()], handler: user_handler):
    user = await handler.authenticate_user(data.username, data.password)
    if not user:
        raise UnauthorizedException("Wrong email or password.")
    tokens = await handler.generate_login_tokens(user)
    return LoginTokenResponse(**tokens, message="login successful, tokens generated")

@router.post("/refresh_login")
async def refresh_login_session(data: Annotated[OAuth2PasswordRequestForm, Depends()], handler: user_handler):
    pass
    


@router.get("/logout")
async def logout_user(handler: user_handler):
    pass


# @router.post("/login")
# async def login_for_access_token(
#     response: Response,

#     db: Annotated[AsyncSession, Depends(async_get_db)],
# ) -> dict[str, str]:
#     user = await authenticate_user(username_or_email=form_data.username, password=form_data.password, db=db)
#     if not user:
#         raise UnauthorizedException("Wrong username, email or password.")

#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = await create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

#     refresh_token = await create_refresh_token(data={"sub": user["username"]})
#     max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

#     response.set_cookie(
#         key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Lax", max_age=max_age
#     )

#     return {"access_token": access_token, "token_type": "bearer"}
