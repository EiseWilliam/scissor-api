
from pydantic import BaseModel

from app.schemas.url import Url


class QROptions(BaseModel):
    color: str = "blue"
    mid_logo: str | None = None
    
class QRDetails(Url):
    qr_preview: str | None = None
    
    