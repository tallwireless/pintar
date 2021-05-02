from .tile import Tile
from PIL import Image, ImageFont
from typing import NoReturn
from .. import factory
from .. import config as global_config
from ..helpers import trim


def generateBoundText(text: str, font: ImageFont) -> Image:
    tmp_image, tmp_drawer = factory.imageFactory(10, 10)

    (text_x, text_y) = tmp_drawer.textsize(text, font)
    print(f"({text_x},{text_y})")
    # create a temporary image so we can crop it
    # this will eliminate any white space around the text
    tmp_image, tmp_drawer = factory.imageFactory(text_x, text_y)
    tmp_drawer.text((0, 0), text, 1, font)
    return trim(tmp_image)


class Text(Tile):
    """
    This is a simple text tile for putting text strings on the display.

    Required Configuration Attributes:
        text: the string of text to be displayed

    Optional Configuration Attributes:
        alignment:
            How to align the text within the box. Vaild options are left,
            center, right. Default: left
        vertical_alignment:
            Where to place the text vertically with in the space. Valid
            options are top, center, bottom. Default: center
        size:
            How big to make the text. Valid entries are greater that 0.
            default: 20
        font:
            font file to use for generating the text
    """

    # Set the type of tile
    tile_type = "text"

    def __init__(self, user_config) -> NoReturn:
        """
        Let's initialzed the class. Also setting some default parameters

        Args:
            config:
                This is dictionary containing the  configuration params

        """

        # Set the defaults for the configuration

        config = {
            "alignment": "left",
            "vertical_alignment": "center",
            "size": 20,
            "fontface": global_config.default_fontface,
        }

        # Overlay the user config on top of the default configuration
        config.update(user_config)

        # Let's call the parent __init__ to do some basic stuffs
        super(Text, self).__init__(config)
        self.config["font"] = factory.FontFactory(
            self.config["size"], self.config["fontface"]
        )

    def generateImage(self) -> Image:
        """
        Do the hard work of actually generating the image.

        Return:
            Image:
                A PIL.Image with the text inside
        """
        # how big is our text?
        tmp_image = generateBoundText(self.config["text"], self.config["font"])
        text_x = tmp_image.width
        text_y = tmp_image.height

        # Figure out where to put the text
        # for the x
        if self.config["alignment"] == "left":
            start_x = 0
        elif self.config["alignment"] == "center":
            start_x = (self.image.width - text_x) / 2
        elif self.config["alignment"] == "right":
            start_x = self.image.width - text_x
        else:
            raise ValueError("Invaild entry for 'alignment'")

        # for the y
        if self.config["vertical_alignment"] == "top":
            start_y = 0
        elif self.config["vertical_alignment"] == "center":
            start_y = (self.image.height - text_y) / 2
        elif self.config["vertical_alignment"] == "bottom":
            start_y = self.image.height - text_y
        else:
            raise ValueError("Invaild entry for 'vertical_alignment'")

        # and put the image in it's proper place
        self.image.paste(tmp_image, (int(start_x), int(start_y)))
        return self.image


def getClass() -> Tile:
    return Text
