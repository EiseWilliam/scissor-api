from pydantic import BaseModel, Field, HttpUrl

from app.schemas.base import Base
from app.core.config.settings import settings

BASE_URL = settings.HOST_URL

class ShortenUrl(BaseModel):
    url: HttpUrl = Field(..., title="URL to shorten", description="The URL to shorten")
    custom_alias: str | None = Field(
        None, title="Custom alias", description="The custom alias for the shortened URL"
    )


class UpdateUrl(BaseModel):
    original_url: HttpUrl | None = Field("", title="Original URL", description="The original URL")
    short_url: str | None = Field("", title="Short URL", description="The short URL")
    title: str | None = Field("", title="Title", description="The title of the URL")


class Url(Base):
    original_url: HttpUrl = Field(..., title="Original URL", description="The original URL")
    short_url: str = Field(..., title="Short URL", description="The short URL")
    has_qr: bool = False
    title: str | None = Field(None, title="Title", description="The title of the URL")
    description: str | None = Field(None, title="Description", description="The description of the URL")
    thumbnail: str | None = Field(None, title="Thumbnail", description="The thumbnail of the URL")
    
    @root_validator(pre=True)
    def add_prefix_to_short_url(cls, values):
        v = values.get('short_url')
        if v:
            values[v] = f"{BASE_URL}/{v}"
        return values
    # user_id: str | None = Field(None, title="User ID", description="The user ID")
    # created_at: str | datetime = Fielnpd(None, title="Created At", description="The time the URL was created", examples=["2021-08-01T12:00:00Z"])
    # updated_at: str | datetime = Field(None, title="Updated At", description="The time the URL was last updated", examples=["2021-08-01T12:00:00Z"])


class UrlClicks(BaseModel):
    short_urls: list[str]


class ListUrl(BaseModel):
    urls: list[Url]


class UrlActivity(BaseModel):
    timestamp: str = Field(
        ...,
        title="Timestamp",
        description="The timestamp to get analytics for",
        examples=["2021-08-01T12:00:00Z"],
    )
    ip_address: str | None = Field(None, title="IP Address", description="The IP address of the click")
    browser: str | None = Field(None, title="Browser", description="The browser of the click")
    referer: str | None = Field(
        ...,
        title="Referer",
        description="The referer to get analytics for",
        examples=["https://example.com/"],
    )


class UrlAnalyticsResponse(BaseModel):
    total_clicks: int = Field(
        0, title="Total Clicks", description="The total number of clicks for the short URL"
    )
    last_clicked: str | None = Field(
        None,
        title="Last Clicked",
        description="The last time the short URL was clicked",
        examples=["2021-08-01T12:00:00Z"],
    )
    activities: list[UrlActivity] | None
