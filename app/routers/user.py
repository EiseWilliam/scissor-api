from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

# from app.services.user import user_handler
from app.core.dependencies import CurrentUser, user_handler
from app.core.responses import BaseResponse, ProfileResponse, direct_response
from app.schemas.user import UpdateUser
from app.routers.limiter import limiter


router = APIRouter(
    default_response_class=ORJSONResponse,
    tags=["user"],
)


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user: CurrentUser):
    res = ProfileResponse(user=user)
    return direct_response(res)


@router.patch("/profile")
async def update_profile(data: UpdateUser, user: CurrentUser, handler: user_handler):
    status = await handler.update_user(user.id, data)
    if status:
        return BaseResponse(message="profile updated successfully")


@router.put("/settings/password")
async def change_password():
    pass


@router.delete("/settings")
async def delete_account():
    pass


@router.put("/settings/email")
async def change_email():
    pass
