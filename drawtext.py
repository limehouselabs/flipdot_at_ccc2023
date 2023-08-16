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

class Text:
    def __init__(self, string, invert=False):
        self.string = string
        self.invert = invert

    def render(self, sign):
        if self.string == "^^STRIPES^^":
            return Stripes().render(sign)
        elif self.string == "^^CHECKERBOARD^^":
            return Checkerboard().render(sign)
        elif self.string == "^^BLANK^^":
            return Blank(0).render(sign)
        elif self.string == "^^NOISE^^":
            return Noise().render(sign)

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


class Checkerboard:
    def render(self, sign):
        img = sign.create_image()
        img[::2, ::2] = True
        img[1::2, 1::2] = True
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

transition = (Random([Checkerboard(), Blank(0), Blank(1), Noise()]), 2)

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
            parsed.append((msg, time))
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

    sign = HanoverSign(address=1, width=84, height=7)

    if not fake:
        ser = Serial(port)
        controller = HanoverController(ser)
        controller.add_sign("dev", sign)

    while True:
        with open("messages.txt") as f:
            queue = [(Text(item[0]), item[1]) for item in parse_messages(f.read())]
            queue.append(transition)

        for item, wait in queue:
            image = item.render(sign)
            if not fake:
                controller.draw_image(image)
            draw_console(image)
            time.sleep(wait)

if __name__ == "__main__":
    main()
