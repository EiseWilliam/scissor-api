from sys import orig_argv
from fastapi import Form
from pydantic import BaseModel, Field
from app.schemas.base import Base

class ShortenUrl(BaseModel):
    url: str = Field(..., title="URL to shorten", description="The URL to shorten")
    custom_alias: str | None = Field(None, title="Custom alias", description="The custom alias for the shortened URL")
    
class UrlActivity(BaseModel):
    timestamp: str = Field(..., title="Timestamp", description="The timestamp to get analytics for", examples=["2021-08-01T12:00:00Z"])
    ip_address: str | None = Field(None, title="IP Address", description="The IP address of the click")
    browser: str | None = Field(None, title="Browser", description="The browser of the click")
    referer: str | None = Field(..., title="Referer", description="The referer to get analytics for", examples=["https://example.com/"])
    
    
class UrlAnalyticsResponse(BaseModel):
    total_clicks: int = Field(0, title="Total Clicks", description="The total number of clicks for the short URL")
    last_clicked: str | None = Field(None, title="Last Clicked", description="The last time the short URL was clicked", examples=["2021-08-01T12:00:00Z"])
    activities: list[UrlActivity] | None