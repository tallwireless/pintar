from PIL import Image, ImageChops
import sys
from . import config


def debug(s):
    sys.stderr.write(f"DEBUG: {s}\n")


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    # Bounding box given as a 4-tuple defining the left, upper, right, and lower pixel coordinates.
    # If the image is completely empty, this method returns None.
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def getSymbol(symbol: str, width: int, height: int) -> Image:
    import freetype as ft
    from numpy import asarray, uint8

    face = ft.Face(
        "/home/charlesr/.local/share/fonts/Meslo LG L DZ Bold for Powerline.ttf"
    )
    face.set_pixel_sizes(width, height)
    face.load_char("")
    bitmap = face.glyph.bitmap.buffer

    return Image.fromarray(asarray(bitmap, dtype=uint8), mode=config.image_type)
