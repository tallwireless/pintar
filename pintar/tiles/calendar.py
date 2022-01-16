import pickle
import arrow
from .tile import Tile
from .text import generateBoundText, generateRoundText
from PIL import Image
from .. import factory
from urllib.request import urlopen
import icalendar
import recurring_ical_events


class Calendar(Tile):
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

    tile_type = "calendar"
    additional_required = []

    def __init__(self, user_config: dict):

        # setup the default configuratio/an
        config = user_config
        super(Calendar, self).__init__(config, self.additional_required)

    def generateImage(self) -> Image:
        """
        generate all of the clocks and pass back the image!

        """
        self.__updateEvents()

        # Add the title
        current = (0, 0)
        title = generateRoundText(
            "Calendar",
            font=factory.FontFactory(80),
            fill=110,
            font_color=255,
            margin=60,
            width=self.config["size_x"],
        )
        self.image.paste(title, current)
        current = (current[0], current[1] + title.height + 10)

        dates = list(self.events.keys())
        dates.sort()
        finished = False
        event_margin = 30
        for date in dates:
            day = generateRoundText(
                date.strftime("%A"),
                font=factory.FontFactory(60),
                margin=20,
                fill=255,
                font_color=0,
                width=self.config["size_x"],
                underline=3,
            )
            if current[1] + (day.height * 1.2) > self.config["size_y"]:
                break
            self.image.paste(day, current)
            current = (current[0], current[1] + day.height + 10)
            for event in self.events[date]:
                if event["end"] < arrow.now():
                    continue
                symbol = generateBoundText(
                    event["symbol"],
                    factory.FontFactory(
                        size=60,
                        fontface="/home/charlesr/Meslo LG L Regular for Powerline.ttf",
                    ),
                    fill=event["bg"],
                    font_color=event["fg"],
                )
                time = generateBoundText(
                    event["start"].strftime("%H:%M"),
                    factory.FontFactory(size=40),
                    fill=event["bg"],
                    font_color=event["fg"],
                )
                summary = generateBoundText(
                    event["title"],
                    factory.FontFactory(size=40),
                    fill=event["bg"],
                    font_color=event["fg"],
                )
                start_y = current[1]
                self.drawer.rounded_rectangle(
                    (
                        0,
                        current[1],
                        self.config["size_x"],
                        current[1] + time.height + event_margin,
                    ),
                    radius=9,
                    fill=event["bg"],
                )
                self.image.paste(time, (10, start_y + int(event_margin / 2)))
                self.image.paste(summary, (150, start_y + int(event_margin / 2)))
                self.image.paste(
                    symbol,
                    (
                        self.config["size_x"] - symbol.width - 15,
                        start_y + int(event_margin / 2),
                    ),
                )
                current = (current[0], current[1] + time.height + 5 + event_margin)
                if current[1] > self.config["size_y"] - time.height:
                    finished = True
                    break
            if finished:
                break

        return self.image

    def __getStartTime(self, event) -> arrow.Arrow:
        return event["start"]

    def __updateEvents(self):
        """
        Get the ical file
        """
        try:
            cache = open("/tmp/cache", "br")
            (time, events_dict) = pickle.load(cache)
            cache.close()
            interval = arrow.now() - time
            if interval.total_seconds() < self.config["cache"] * 60:
                self.events = events_dict
                return
        except Exception:
            pass

        events_dict = {}
        for source in self.config["sources"]:
            ics_file = urlopen(source["url"]).read()
            calendar = icalendar.Calendar.from_ical(ics_file)
            start_date = arrow.now().date()
            end_date = arrow.now().shift(days=+7).date()
            events = recurring_ical_events.of(calendar).between(start_date, end_date)
            for event in events:
                if self.__convert_vdate(event["DTEND"]) < arrow.now():
                    continue
                event_dict = {
                    "title": str(event["SUMMARY"]),
                    "start": self.__convert_vdate(event["DTSTART"]),
                    "end": self.__convert_vdate(event["DTEND"]),
                    "fg": source["fg"],
                    "bg": source["bg"],
                    "symbol": source["symbol"] if "symbol" in source else " ",
                }
                start_date = event_dict["start"].date()
                if start_date not in events_dict:
                    events_dict[start_date] = []
                events_dict[start_date].append(event_dict)

            for date in events_dict:
                events_dict[date].sort(key=self.__getStartTime)
        try:
            cache = open("/tmp/cache", "wb")
            pickle.dump((arrow.now().datetime, events_dict), cache)
            cache.close()
        except Exception:
            pass

        self.events = events_dict

    def __convert_vdate(self, date: icalendar.prop.vDDDTypes) -> arrow.Arrow:
        return arrow.get(date.dt).to("local")


def getClass():
    return Calendar
