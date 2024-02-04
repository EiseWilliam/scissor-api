# direct orjson responder, bypassing jsonable_encoder
from os import access
from typing import Any
import orjson
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from app.schemas.user import ReadUser

def direct_response(model: BaseModel, *args, **kwargs):
    """
    Generate a direct response using the provided model.

    Args:
        model (BaseModel): The model to generate the response from.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        DResponse: The direct response object.
    """
    return DResponse(content=model.model_dump(), *args, **kwargs)


class DResponse(ORJSONResponse):
    """
    Custom Default JSON response class that extends ORJSONResponse.
    """
    def render(self, content: Any) -> bytes:
        return orjson.dumps(
            content,
            default=str,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )
        
        
class BaseResponse(BaseModel):
    status: str = "success"
    message: str
    
# auth responses
class LoginTokenResponse(BaseResponse):
    token_type: str = "bearer"
    access_token: str | None = None
    refresh_token: str | None = None
    
    
# user responses
class ProfileResponse(BaseResponse):
    message: str = "user profile retrieved successfully"
    user: ReadUser
