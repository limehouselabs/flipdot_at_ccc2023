import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pyflipdot.sign import HanoverSign
from pyflipdot.pyflipdot import HanoverController
from serial import Serial
from pathlib import Path
import string
import time
import click
import itertools
import random
import os

HANOVER_WIDTH=84
HANOVER_HEIGHT=7

class Text:
    def __init__(self, string, invert=False):
        self.string = string
        self.invert = invert

    def render(self, sign):
        font = Path(__file__).resolve().parent / "fonts" / "5x5.ttf"

        pil_font = ImageFont.truetype(str(font), size=10, encoding="unic")
        left, top, right, bottom = pil_font.getbbox(self.string)
        text_width = right - left
        text_height = bottom - top

        if text_width > sign.width:
            raise ValueError("Text too wide: " + self.string)

        offset = ((sign.width - text_width) // 2, (sign.height - text_height) // 2)

        canvas = Image.new("1", [sign.width, sign.height], 1 if self.invert else 0)
        draw = ImageDraw.Draw(canvas)
        draw.text(offset, self.string, font=pil_font, fill=0 if self.invert else 1, anchor="lt")
        return np.asarray(canvas)

    def __repr__(self):
        return '[Text("' + self.string + '")]'


class Stripes:
    def render(self, sign):
        img = sign.create_image()
        img[::3, ::3] = True
        img[1::3, 1::3] = True
        img[2::3, 2::3] = True
        return img


class Stars:
    def render(self, sign):
        img = sign.create_image()
        img [0::90, ::8] = True
        img [0::90, 6::8] = True
        img [1::90, 1::8] = True
        img [1::90, 5::8] = True
        img [2::90, 2::8] = True
        img [2::90, 4::8] = True
        img [3::90, ::] = True
        img [3::90, 7::8] = False
        img [4::90, 4::8] = True
        img [4::90, 2::8] = True
        img [5::90, 5::8] = True
        img [5::90, 1::8] = True
        img [6::90, 6::8] = True
        img [6::90, ::8] = True
        return img


class Diamonds:
    def render(self, sign):
        img = sign.create_image()
        img [::90, 3::6] = True
        img [1::90, 2::6] = True
        img [1::90, 4::6] = True
        img [2::90, 1::6] = True
        img [2::90, 5::6] = True
        img [3::90, ::6] = True
        img [4::90, 1::6] = True
        img [4::90, 5::6] = True
        img [5::90, 2::6] = True
        img [5::90, 4::6] = True
        img [6::90, 3::6] = True
        return img


class Checkerboard:
    def render(self, sign):
        img = sign.create_image()
        img[::2, ::2] = True
        img[1::2, 1::2] = True
        return img

class ImageFromFile:
    def __init__(self, filename):
        filename = f"images/{ filename }.txt"

    def render(self, sign, name):
        if not os.path.exists(self.filename):
            raise ValueError(f"Image not found: '{ self.filename }'")
        img = sign.create_image()
        with open(self.filename) as f:
            data = [
                [c == "█" for c in list(r)] for r in f.read().splitlines()
            ]
            for y in range(HANOVER_HEIGHT):
                for x in range(HANOVER_WIDTH):
                   img[y][x] = data[y][x]
        return img


class Blank:
    def __init__(self, value):
        self.value = value

    def render(self, sign):
        img = sign.create_image()
        img.fill(self.value)
        return img


class Noise:
    def render(self, sign):
        img = sign.create_image()
        img[:] = np.random.choice(a=[False, True], size=img.shape)
        return img


class Random:
    def __init__(self, options):
        self.options = options

    def render(self, sign):
        rval = random.randint(0, len(self.options) - 1)
        return self.options[rval].render(sign)


def progressive(text, invert=False, dwell=1, final_dwell=5):
    trans = str.maketrans(string.ascii_letters, len(string.ascii_letters) * "_")
    for i in range(len(text)):
        this_dwell = dwell if i < len(text) - 1 else final_dwell
        this_text = text[: i + 1] + text[i+1:].translate(trans)
        yield (Text(this_text, invert), this_dwell)

#queue = [
#    (Text("CURRENT BEER"), 5),
#    (Text("MYSTERY PILS"), 5),
#    (Text("( A BIT FOAMY )"), 5),
#    transition,
#]

# Oh fuck it, it's hot
def parse_messages(text):
    parsed = []
    for line in text.splitlines():
        if line.strip() != "":
            msg = line
            split = line.rfind(";")
            time = 5
            if split != -1:
                msg = line[:split].strip()
                time = int(line[split+1:].strip())

            if msg == "^^STRIPES^^":
                screen = Stripes()
            elif msg == "^^CHECKERBOARD^^":
                screen = Checkerboard()
            elif msg == "^^BLANK^^":
                screen = Blank(0)
            elif msg == "^^NOISE^^":
                screen = Noise()
            elif msg == "^^STARS^^":
                screen = Stars()
            elif msg == "^^DIAMONDS^^":
                screen = Diamonds()
            elif msg == "^^TRANSITION^^":
                screen = Random([
                    Stripes(),
                    Stars(),
                    Diamonds(),
                    Checkerboard(),
                    Blank(0),
                    Blank(1),
                    Noise(),
                ])
            elif msg.startswith("^^") and msg.endswith("^^"):
                screen = ImageFromFile(msg)
            else:
                screen = Text(msg)

            parsed.append((screen, time))
    return parsed

def draw_console(image):
    for row in image:
        for col in row:
            print("█" if col else " ", end="")
        print()
    print()


@click.command()
@click.option("--port", default="/dev/ttyUSB0")
@click.option("--fake", is_flag=True)
def main(port, fake):

    sign = HanoverSign(address=1, width=HANOVER_WIDTH, height=HANOVER_HEIGHT)

    if not fake:
        ser = Serial(port)
        controller = HanoverController(ser)
        controller.add_sign("dev", sign)

    while True:
        with open("messages.txt") as f:
            queue = parse_messages(f.read())

        for item, wait in queue:
            image = item.render(sign)
            if not fake:
                controller.draw_image(image)
            draw_console(image)
            time.sleep(wait)

if __name__ == "__main__":
    main()
