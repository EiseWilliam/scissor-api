from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer, validator


class Timestamp(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)

    @field_serializer("created_at")
    def serialize_dt(self, created_at: datetime | None, _info: Any) -> str | None:
        return created_at.isoformat() if created_at is not None else None

    @field_serializer("updated_at")
    def serialize_updated_at(self, updated_at: datetime | None, _info: Any) -> str | None:
        return updated_at.isoformat() if updated_at is not None else None


class FromMongo(BaseModel):
    id: str | ObjectId = Field(
        validation_alias="_id",
        description="The ID of the item",
        examples=["60f0c9b0e6f9a9a7e8f1b0a0"],
        title="ID",
        alias_priority=0,
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    @validator("id", pre=True)
    def validate_id(cls, id: str | ObjectId) -> str:
        return str(id) if isinstance(id, ObjectId) else id

    # @field_serializer('id')
    # def serialize_id(self, id: str | ObjectId) -> str:
    #     if isinstance(id, ObjectId):
    #         return str(id)
    #     return id


class Base(FromMongo, Timestamp):
    pass
    # class Config:
    #     allow_population_by_field_name = True
    #     # json_encoders = {ObjectId: str}
    #     # schema_extra = {
    #     #     "example": {
    #     #         "id": "60f0c9b0e6f9a9a7e8f1b0a0",
    #     #         "created_at": "2021-07-16T00:00:00+00:00",
    #     #         "updated_at": "2021-07-16T00:00:00+00:00",
    #     #     }
    #     # }