from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

# from app.services.user import user_handler
from app.core.dependencies import current_user_dep, user_handler, get_current_user
from app.core.responses import BaseResponse, ProfileResponse, direct_response
from app.schemas.user import UpdateUser

router = APIRouter(default_response_class=ORJSONResponse, tags=["user"], )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user: current_user_dep):
    res = ProfileResponse(user=user)
    return direct_response(res)

@router.patch("/profile")
async def update_profile(data: UpdateUser,user: current_user_dep, handler: user_handler):
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
