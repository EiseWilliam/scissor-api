import asyncio
from typing import Coroutine
import uvloop
from app.celery import celery_app
from app.services.data.analytics import analytics_processor
from linkpreview import link_preview
from app.db.database import db



def run_async(awaitable: Coroutine):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)


async def update_url(short_url: str, **kwargs):
    return await db.urls.update_one({"short_url": short_url}, {"$set": kwargs})


@celery_app.task
def track_activity(short_url: str,ref:str|None,*args):
    if ref is None:
        run_async(analytics_processor.track_click(short_url, *args)) 
        return f"Processed analytics for {short_url}"
    if ref is "qr":
        run_async(analytics_processor.track_scan(short_url, *args)) 
        return f"Processed analytics for {short_url}"
    if ref is not "qr":
        run_async(analytics_processor.track_click(short_url, *args)) 
        return f"Processed analytics for {short_url}"



@celery_app.task
def populate_preview(short_url: str, original_url: str):
    data = link_preview(original_url)
    preview = {"title": data.title, "description": data.description, "thumbnail": data.image} 
    res = run_async(update_url(short_url, **preview)) 
    if res.acknowledged:
        return f"Preview data populated for {short_url}"
    return "Failed to populate preview data"
