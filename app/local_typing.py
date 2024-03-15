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


