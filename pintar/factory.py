from PIL import Image, ImageDraw
from . import config
from .tiles.tile import Tile
import importlib


def imageFactory(x: int = config.size_x, y: int = config.size_y) -> (Image, ImageDraw):
    """
    Generated a new image to spec

    Args:
        x (int): Number of pixels wide
        y (int): Number of pixel high

    Return:
        (PIL.Image, PIL.ImageDrawer)

    """
    if x is None:
        x = config.size_x
    if y is None:
        y = config.size_y

    i = Image.new(config.image_type, (x, y), config.background)
    d = ImageDraw.Draw(i)
    return (i, d)


def get_tile(tile: str) -> Tile:
    try:
        mod = importlib.import_module("pintar.tiles." + tile)
        tile_class = getattr(mod, "getClass")
    except Exception as e:
        raise ValueError(f"Invalid tile {tile} ({e})")
    return tile_class


def generateTile(tile: str, tile_config: dict) -> Image:
    # Get the tile class
    tile_class = get_tile(tile)()(tile_config)
    return tile_class.generateImage()
