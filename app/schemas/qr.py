
from pydantic import BaseModel


class QROptions(BaseModel):
    color: str = "blue"
    mid_logo: str | None = None
    