
from pydantic import BaseModel, Field, HttpUrl

from app.schemas.base import Base
from app.schemas.url import Url

class QR(Base):
    original_url: HttpUrl = Field(
        ..., title="Original URL", description="The original URL"
    )
    short_url: str = Field(..., title="Short URL", description="The short URL")
    has_qr: bool = False
    title: str | None = Field(None, title="Title", description="The title of the URL")
    description: str | None = Field(
        None, title="Description", description="The description of the URL"
    )


class QROptions(BaseModel):
    color: str = "blue"
    mid_logo: str | None = None
    
class QRDetails(QR):
    qr_preview: str | None = None
    

class ListQR(BaseModel):
    urls: list[QR]
