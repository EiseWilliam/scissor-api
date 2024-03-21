from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from app.schemas.base import Base


class CreateUserRequest(BaseModel):
    email: Annotated[EmailStr, Field(examples=["user.userberg@example.com"], default=None)]
    password: Annotated[
        str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])
    ]
    confirm_password: Annotated[
        str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])
    ]
    model_config = ConfigDict(extra="forbid")

    @field_validator("confirm_password")
    def passwords_match(cls, v: str, info: FieldValidationInfo) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("passwords do not match")
        return v

    @field_validator("password")
    def password_complexity(cls, v):
        min_length = 8
        requirements = {
            "lowercase": any(char.islower() for char in v),
            "uppercase": any(char.isupper() for char in v),
            "digit": any(char.isdigit() for char in v),
            "special": any(not char.isalnum() and not char.isspace() for char in v),
        }
        if not all(requirements.values()):
            raise ValueError(
                "Password must meet complexity requirements: at least {} characters"
                "including lowercase, uppercase, digit, and special character".format(min_length)
            )
        return v
class RefreshSession(BaseModel):
    refresh_token: Annotated[str, Form()]
class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    @field_validator("confirm_password")
    def passwords_match(cls, v: str, info: FieldValidationInfo) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("passwords do not match")
        return v


class CreateUser(BaseModel):
    email: Annotated[EmailStr, Field(examples=["user.userberg@example.com"], default=None)]
    password: Annotated[
        str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])
    ]


class ReadUser(Base):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    profile_image_url: str | None = None
    is_verified: bool = False


class _ReadUser(Base):
    password: str
    model_config = ConfigDict(extra="allow")


class UpdateUser(BaseModel):
    model_config = ConfigDict(extra="forbid")
    first_name: Annotated[
        str | None, Field(min_length=2, max_length=30, examples=["User Userberg"], default=None)
    ]
    last_name: Annotated[
        str | None, Field(min_length=2, max_length=30, examples=["User Userberg"], default=None)
    ]
    email: Annotated[EmailStr | None, Field(examples=["user.userberg@example.com"], default=None)]
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            examples=["https://www.profileimageurl.com"],
            default=None,
        ),
    ]
