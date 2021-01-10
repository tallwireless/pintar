from PIL import Image, ImageDraw, ImageFont
import arrow


def drawText(xy, bbox, text, font, drawer, offset=0):
    (text_x, text_y) = drawer.textsize(text, font=font)
    text_x = (bbox[0] - text_x) / 2 + xy[0]
    drawer.text((text_x, xy[1] + offset), text, font=font)
    return (xy[0], xy[1] + text_y + offset)


def makeClock(city, timezone, height=250, width=355):
    fonts = {
        "time": ImageFont.truetype(
            "/home/charlesr/.local/share/fonts/NerdFonts/Noto Sans Mono Condensed Nerd Font Complete.ttf",
            130,
        ),
        "city": ImageFont.truetype(
            "/usr/share/fonts/truetype/tlwg/Laksaman-Bold.ttf", 40
        ),
        "date": ImageFont.truetype(
            "/usr/share/fonts/truetype/tlwg/Laksaman-Bold.ttf", 40
        ),
    }
    img = Image.new("1", (width, height), (1))
    time = arrow.utcnow().to(timezone)
    drawer = ImageDraw.Draw(img)
    start = (0, 0)
    bbox = (width, height)
    current = start

    current = drawText(current, bbox, city, fonts["city"], drawer)
    current = drawText(current, bbox, time.format("HH:mm"), fonts["time"], drawer, -35)
    current = drawText(current, bbox, time.format("YYYY/MM/DD"), fonts["date"], drawer)
    return img


primary = Image.new("1", (800, 600), (1))
drawer = ImageDraw.Draw(primary)

cities = {"Philadelphia": "US/Eastern", "Chicago": "US/Central"}
current = (0, 0)
for city in cities:
    img = makeClock(city, cities[city], width=int(primary.getbbox()[2] / 2))
    primary.paste(img, current)
    current = (current[0] + img.getbbox()[2], current[1])

drawer.line(
    (primary.getbbox()[2] / 2, 0 + 40, primary.getbbox()[2] / 2, img.getbbox()[3] - 40),
    width=2,
)
line_factor = 10
drawer.line(
    (
        int(primary.getbbox()[2] / line_factor),
        img.getbbox()[3],
        int(primary.getbbox()[2] / line_factor) * (line_factor - 1),
        img.getbbox()[3],
    ),
    width=2,
)


primary.save("test.bmp", "BMP")
