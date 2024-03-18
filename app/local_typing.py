from pymongo.results import (
    BulkWriteResult as DBBulkWriteResult,
    DeleteResult as DBDeleteResult,
    InsertManyResult as DBInsertManyResult,
    InsertOneResult as DBInsertOneResult,
    UpdateResult as DBUpdateResult,
)
from motor.core import AgnosticCollection as AgnosticCollection, AgnosticCursor as AgnosticCursor, AgnosticDatabase as AgnosticDatabase, AgnosticClient as AgnosticClient, AgnosticClientSession as AgnosticClientSession, AgnosticChangeStream as AgnosticChangeStream, AgnosticCommandCursor as AgnosticCommandCursor

from motor.metaprogramming import create_class_with_framework
from typing import Type
from motor.frameworks import asyncio as asyncio_framework
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from 

# async def main():
#     client = await connect_to_mongo()

#     database: AsyncIOMotorDatabase = client["my_database"]
#     collection: AsyncIOMotorCollection = database["my_collection"]

#     # Insert a document
#     document = {"key": "value"}
#     await collection.insert_one(document)

#     # Find documents
#     async for doc in collection.find():
#         print(doc)

#     client.close()  # Close the connection


if __name__ == "__main__":
    print(type(AsyncIOMotorDatabase))
    print(Type[type(AsyncIOMotorCollection)])
    print(type(AsyncIOMotorClient))

ClientType = type[AgnosticClient[_DocumentType @ AgnosticClient]]
client: AgnosticClient = AsyncIOMotorClient(URI)

db = client["DB"]