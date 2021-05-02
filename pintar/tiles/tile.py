from .. import factory
from PIL import Image


class Tile(object):
    """
    This is an abstract class for tiles, and contains the structure a tile
    should have.

    Attributes:
        config: the configuration for the tile

    """

    def __init__(self, config: dict, additional_required: list = []):
        """
        Sets up the class

        Args:
            config:
                A dictionary containing the configuration for the tile
        """
        self.config = config

        # Let's check for the basic configuration options and append anything
        # from the child class
        required_config = ["size_x", "size_y", "x", "y"]
        required_config.extend(additional_required)

        # Check for required configuration entries
        for item in required_config:
            if item not in config:
                raise ValueError(
                    f"Missing required attribute {item} in for {self.tile_type} tile configuration"
                )

        # Let's generated the image and drawer
        self.image, self.drawer = factory.imageFactory(
            self.config["size_x"], self.config["size_y"]
        )

    def generateImage(self) -> Image:
        # Generates internal content and then returns the Python Pillow Image
        # object to be meraged into the primary image
        print("not here")
        pass
