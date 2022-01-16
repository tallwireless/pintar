from .tile import Tile
from .text import generateBoundText
from PIL import Image
from .. import factory
from io import BytesIO


class Bandwidth(Tile):
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

    tile_type = "bandwidth"
    additional_required = []

    def __init__(self, user_config: dict):

        # setup the default configuratio/an
        config = user_config
        super(Bandwidth, self).__init__(config, self.additional_required)

    def generateImage(self) -> Image:
        """
        generate all of the clocks and pass back the image!

        """

        import pandas as pd
        import plotly.express as px
        from influxdb import InfluxDBClient

        client = InfluxDBClient(
            host="collector.metrics.tallwireless.com",
            username="admin",
            password="frebre4w",
            ssl=True,
            port=443,
            database="systems",
        )
        data = client.query(
            """ SELECT non_negative_difference(first("bytes_recv"))*8/60 AS "input", non_negative_difference(first("bytes_sent"))*8/60 as "output" FROM "net" WHERE ("interface" = 'VERIZON') AND time >= now() - 15m GROUP BY time(1m) fill(null) """
        )
        # making the data reusable
        title = generateBoundText("Home Bandwidth", factory.FontFactory(60))
        self.image.paste(title, (int((self.config["size_x"] - title.width) / 2), 0))
        y = title.height + 15
        data = [i for i in data["net"]]
        df = pd.DataFrame(data, columns=["input", "output"])
        recv = [i["input"] for i in data]
        sent = [i["output"] for i in data]
        m = max([max(recv), max(sent)])
        dates = [i["time"] for i in data]
        images = []
        text = generateBoundText(self.__getLabel(recv[-1]), factory.FontFactory(40))
        for i in ["input", "output"]:
            df = pd.DataFrame(data, index=dates, columns=[i])

            fig = px.area(df, height=200, width=self.config["size_x"] / 2)
            fig.update_xaxes(visible=False, fixedrange=True)
            fig.update_yaxes(visible=False, fixedrange=True, range=[0, m])
            fig.update_layout(
                showlegend=False,
                plot_bgcolor="white",
                margin=dict(t=10, l=10, b=10, r=10),
            )
            images.append(Image.open(BytesIO(fig.to_image(format="png"))))

        middle = int(self.config["size_x"] / 2)
        self.image.paste(images[0], (0, y))
        self.image.paste(images[1], (middle, y))
        y += images[0].height
        text = generateBoundText(self.__getLabel(recv[-1]), factory.FontFactory(50))
        self.image.paste(text, (int((middle - text.width) / 2), y))
        text = generateBoundText(self.__getLabel(sent[-1]), factory.FontFactory(50))
        self.image.paste(text, (middle + int((middle - text.width) / 2), y))
        y += text.height + 5
        text = generateBoundText("Input", factory.FontFactory(35))
        self.image.paste(text, (int((middle - text.width) / 2), y))
        text = generateBoundText("Output", factory.FontFactory(35))
        self.image.paste(text, (middle + int((middle - text.width) / 2), y))

        return self.image

    def __getLabel(self, num: int) -> str:
        d = 0
        while num / pow(1000, d) > 1:
            d += 1

        d -= 1
        num = num / pow(1000, d)
        labels = {0: "bps", 1: "kbps", 2: "mbps", 3: "gbps"}
        rv = f"{num:.1f} {labels[d]}"
        return rv


def getClass():
    return Bandwidth
