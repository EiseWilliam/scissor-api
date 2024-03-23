import io
from typing import Literal

from bson import ObjectId
from fastapi import Request
import segno
from fastapi.responses import FileResponse
from PIL import Image

from app.schemas.qr import ListQR
from app.services.url import UrlHandler







class QRhandler(UrlHandler):
    async def get_user_qrs(self, user_id: str | ObjectId):
        return ListQR(urls=await (
            self._db_conn.get_collection(self._collection)
            .find({"user_id": user_id, "has_qr": True})
            .to_list(None)
        ))
        
    async def make_qr_for_short_url(self, short_url: str, request: Request):
        pass

    async def download_qr(self, short_url: str, format: Literal["jpg","svg", "png"], request: Request):
        host_url = request.base_url
        full_url = f"{host_url}{short_url}?ref=qr"
        out = io.BytesIO()
        segno.make(full_url, error="h").save(out, scale=5, kind=format)
        out.seek(0)  # Important to let Pillow load the PNG
        headers = {"Content-Disposition": 'attachment; filename="filename.xlsx"'}
        return FileResponse(out, headers=headers)


def build_qr_code(url: str, name: str, color: str = "blue", scale: int = 5):
    out = io.BytesIO()
    segno.make(url, error="h").save(out, scale=5, kind="png", dark=color)
    out.seek(0)  # Important to let Pillow load the PNG
    img = Image.open(out)

    img = img.convert("RGBA")  # Ensure colors for the output
    logo = Image.open("logo.png").convert("RGBA").resize((50, 13))
    qr_width, qr_height = img.size
    logo_width, logo_height = logo.size
    logo_max_size = qr_height // 3  # May use a fixed value as
    left = qr_width - logo_width
    top = qr_height - logo_height
    # Create a white border around the logo
    border_width = 5
    logo_with_border = Image.new(
        "RGBA",
        (logo_width * border_width, logo_height + 2 * border_width),
        (255, 255, 255, 255),
    )
    logo_with_border.paste(logo, (border_width, border_width))
    # Overlay the logo onto the QR code
    img.paste(logo_with_border, (left - 25, top - 25))
    img.save(f"app/static/qr/{name}.png", scale=scale, dark=color)
    return FileResponse(f"app/static/qr/{name}.png")

def build_without_logo_qr_code(url: str, name: str, color: str = "blue", scale: int = 5):
    out = io.BytesIO()
    segno.make(url, error="h").save(out, scale=5, kind="svg", dark=color)
    out.seek(0)
    return out
    



        
