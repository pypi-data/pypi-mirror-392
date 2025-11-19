import importlib.resources as resources
from typing import Literal
from io import BytesIO
from PIL import Image
import requests
import shutil
from pathlib import Path


def copy_resource(filename: str, destination: Path):
    file_name = filename
    pkg = "yt_dlp_termux_gui.resources"
    if filename.find("/") != -1:
        segments = filename.split("/")
        pkg += "." + ".".join(segments[:-1])
        file_name = segments[-1]
    with resources.open_binary(pkg, file_name) as src, open(destination, "wb") as dst:
        shutil.copyfileobj(src, dst)

    
def get_image_bytes(image_url: str, size: Literal['thumbnail', 'default']):
    response = requests.get(image_url)
    response.raise_for_status()  # ensure it downloaded successfully
    
    buf_png = BytesIO()
    img = Image.open(BytesIO(response.content))

    if size == "default":
        img.save(buf_png, format="PNG", optimize=True)
        return buf_png.getvalue()
    
    target_ratio = 3 / 2
    width, height = img.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        right = left + new_width
        top = 0
        bottom = height
    else:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        left = 0
        right = width

    img_cropped = img.crop((left, top, right, bottom))
    img_cropped.save(buf_png, format="PNG", optimize=True)
    png_bytes = buf_png.getvalue()
    
    return png_bytes

