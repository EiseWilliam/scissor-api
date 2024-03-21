from datetime import datetime, timezone
from typing import Any, Generic, List, TypeVar

from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.local_typing import (
    AgnosticCursor,
    DBDeleteResult,
    DBInsertManyResult,
    DBInsertOneResult,
    DBUpdateResult,
)

CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
ReadSchema = TypeVar("ReadSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class BaseCRUD(Generic[CreateSchema, ReadSchema, UpdateSchema]):
    def __init__(
        self,
        db_conn: AsyncIOMotorDatabase,
        collection: str,
    ):
        self._collection = collection
        self._db_conn = db_conn

    async def on_create(self) -> None:
        pass

    async def on_update(self) -> None:
        pass

    async def on_delete(self) -> None:
        pass

    async def get(self, **filters) -> ReadSchema:
        item = await self._db_conn.get_collection(self._collection).find_one(filters)
        return item
    
    async def id_exists(self, id: str) -> bool:
        item = await self._db_conn.get_collection(self._collection).find_one({"_id": ObjectId(id)})
        return item is not None

    async def count(self) -> int:
        return await self._db_conn.get_collection(self._collection).count_documents({})

    async def get_multiple(self, sort_by: str | None = None, n=100, **filters) -> List:
        items_cursor: AgnosticCursor = self._db_conn.get_collection(self._collection).find(filters)
        if sort_by:
            items_cursor = items_cursor.sort(sort_by)
        items_cursor = items_cursor.limit(n)
        items: list = await items_cursor.to_list(n)
        return items

    async def get_by_id(self, id: str) -> ReadSchema:
        item = await self._db_conn.get_collection(self._collection).find_one({"_id": ObjectId(id)})
        if item is None:
            raise HTTPException(status_code=404, detail="Item with {id} not found")
        return item

    async def create(self, item: CreateSchema | dict, **defaults_fields: Any) -> str:
        if isinstance(item, BaseModel):
            item_updated = item.model_dump()
        else:
            item_updated = item
        if defaults_fields:
            item_updated.update(**defaults_fields)
        result = await self._create(item_updated)
        await self.on_create()
        return str(result.inserted_id)  # type: ignore

    async def create_many(self, items: list[CreateSchema], **defaults_fields: Any) -> list[str]:
        items_updated = [item.model_dump() for item in items]
        if defaults_fields:
            items_updated = [{**item, **defaults_fields} for item in items_updated]
        result = await self._create_many(items_updated)
        await self.on_create()
        return [str(id) for id in result.inserted_ids]

    async def update(self, id: str, item: UpdateSchema) -> bool:
        if await self.id_exists(
            id,
        ):
            result = await self._update(
                id, item.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
            )
            await self.on_update()
            return result.acknowledged
        else:
            return False

    async def delete(self, id: str) -> bool:
        if await self.id_exists(id):
            result = await self._delete(id)
            await self.on_delete()
            return result.acknowledged
        else:
            return False

    # Would invoke time stamps if enabled
    async def _create(self, item_dict: dict[str, Any]) -> DBInsertOneResult:
        item_dict["created_at"] = item_dict["updated_at"] = datetime.now(timezone.utc)
        return await self.__create(item_dict)

    async def _create_many(self, items_dict: list[dict[str, Any]]) -> DBInsertManyResult:
        items_updated = list(
            map(
                lambda item: (
                    item.update(
                        {"created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}
                    )
                ),
                items_dict,
            )
        )
        return await self._db_conn.get_collection(self._collection).insert_many(items_updated)

    async def _update(self, id: str, item_dict: dict[str, Any]) -> DBUpdateResult:
        item_dict["updated_at"] = datetime.now(timezone.utc)
        return await self.__update(id, item_dict)

    async def _delete(self, id: str) -> DBDeleteResult | DBUpdateResult:
        return await self._db_conn.get_collection(self._collection).delete_one({"_id": ObjectId(id)})

    # Won't invoke time stamps no matter what
    #  This is for internal use only, only use to avoid functions triggered by events a
    async def __create(self, item_dict: dict[str, Any]) -> DBInsertOneResult:
        return await self._db_conn.get_collection(self._collection).insert_one(item_dict)

    async def __update(self, id: str, item_dict: dict[str, Any]) -> DBUpdateResult:
        return await self._db_conn.get_collection(self._collection).update_one(
            {"_id": ObjectId(id)}, {"$set": item_dict}
        )
