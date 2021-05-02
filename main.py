import sys
from pyaml import yaml

from pintar import config as global_config
from pintar import factory

# TODO: Formalize the arguments to the code
if len(sys.argv) < 2:
    print("Need a config file")
    exit(1)


# Load the configuration file
with open(sys.argv[1], "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# check to make sure that we have some required options in the configuration
# file
required_config = ["output", "tiles"]
for item in required_config:
    if item not in config:
        print("ERROR: Missing the required options")
        exit(1)

global_config.__dict__.update(config["output"])

output_image, drawer = factory.imageFactory()

# Let's run through the tiles and generate the content an put in on the output
# image
for tile, tile_config in config["tiles"].items():
    # Use the tile factory to create the tile
    tile_img = factory.generateTile(tile, tile_config)
    # Add the tile to the output image
    output_image.paste(tile_img, (tile_config["x"], tile_config["y"]))

# Write the image file out some where
output_image.save("test.bmp", format="BMP")
