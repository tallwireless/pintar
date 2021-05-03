import arrow
from .tile import Tile
from .text import generateBoundText
from PIL import Image
from .. import factory


class Clock(Tile):
    """
    This tile will produce a digital style clock for each city and timezone
    given in the cities section of the configuration.

    Optional Configuration Parameters:
        alignment:
            How the clocks should be aligned in the space. Valid entries are
            horizonal and vertical. Default horizonal.
        cities:
            A dictionary of cities and their timezones. Key is the city, and
            the value is the timezone. Default is the configured timezone for
            the running device.
    """

    tile_type = "clock"

    def __init__(self, user_config: dict):
        # setup the default configuration
        config = {"alignment": "horizonal", "cities": {"Local": "local"}}

        config.update(user_config)
        super(Clock, self).__init__(config)

    def generateImage(self) -> Image:
        """
        generate all of the clocks and pass back the image!

        """
        num_cities = len(self.config["cities"])
        layout = {"city": 70, "time": 170, "date": 60}
        if self.config["alignment"] == "vertical":
            width = int(self.config["size_x"])
            height = int(self.config["size_y"] / num_cities)
            x_add = 0
            y_add = height
        elif self.config["alignment"] == "horizonal":
            width = int(self.config["size_x"] / num_cities)
            height = int(self.config["size_y"])
            x_add = width
            y_add = 0
        else:
            raise ValueError("Invaild configuration option for alignment")

        current = (0, 0)
        total_cities = len(self.config["cities"])
        for (count, (city, timezone)) in enumerate(self.config["cities"].items()):
            img = self.makeClock(city, timezone, width, height, layout)
            self.image.paste(img, current)
            current = (current[0] + x_add, current[1] + y_add)

            if count < (total_cities - 1):
                line_length = 8
                x_interval = int(width / line_length)
                start_x = x_interval
                end_x = x_interval * (line_length - 1)
                y = current[1]
                self.drawer.line((start_x, y, end_x, y), width=5)

        return self.image

    def makeClock(
        self, city: str, timezone: str, width: int, height: int, layout: dict
    ) -> Image:
        img, drawer = factory.imageFactory(width, height)
        time = arrow.utcnow().to(timezone)

        city_text = generateBoundText(
            city,
            factory.FontFactory(layout["city"]),
        )
        time_text = generateBoundText(
            time.format("HH:mm"),
            factory.FontFactory(layout["time"]),
        )
        date_text = generateBoundText(
            time.format("YYYY-MM-DD"),
            factory.FontFactory(layout["date"]),
        )
        margin = 40
        total_y = city_text.height + time_text.height + date_text.height + margin * 2
        start_y = int((height - total_y) / 2)
        start_x = int((width - city_text.width) / 2)
        img.paste(city_text, (start_x, start_y))
        start_x = int((width - time_text.width) / 2)
        img.paste(time_text, (start_x, start_y + city_text.height + margin))
        start_x = int((width - date_text.width) / 2)
        img.paste(
            date_text,
            (start_x, start_y + city_text.height + time_text.height + margin * 2),
        )
        return img


def getClass():
    return Clock
