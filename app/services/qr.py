import io
from fastapi.responses import FileResponse
import segno
from PIL import Image
import segno



def build_qr_code(url: str, name: str, color: str = "blue", scale: int = 5):
    out = io.BytesIO()
    segno.make(url, error='h').save(out, scale=5, kind='png', dark=color)
    out.seek(0)  # Important to let Pillow load the PNG
    img = Image.open(out)
    
    img = img.convert('RGBA')  # Ensure colors for the output
    logo = Image.open('logo.png').convert('RGBA').resize((50, 13))
    qr_width, qr_height = img.size
    logo_width, logo_height = logo.size
    logo_max_size = qr_height // 3  # May use a fixed value as 
    left = qr_width - logo_width
    top = qr_height - logo_height
    # Create a white border around the logo
    border_width = 5
    logo_with_border = Image.new('RGBA', (logo_width * border_width, logo_height + 2 * border_width), (255, 255, 255, 255))
    logo_with_border.paste(logo, (border_width, border_width))
    # Overlay the logo onto the QR code
    img.paste(logo_with_border, (left - 25, top - 25))
    img.save(f"app/static/qr/{name}.png", scale=scale, dark=color)
    return FileResponse(f"app/static/qr/{name}.png")
