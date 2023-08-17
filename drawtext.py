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
MIN_FRAME_TIME=0.2


class Screen:
    def save(self):
        return f"^^{ self.__class__.__name__.upper() }^^"

    def render(self, sign):
        return


class Text(Screen):
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

    def save(self):
        return self.string


class Stripes(Screen):
    def render(self, sign):
        img = sign.create_image()
        img[::3, ::3] = True
        img[1::3, 1::3] = True
        img[2::3, 2::3] = True
        return img


class Stars(Screen):
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


class Diamonds(Screen):
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


class Checkerboard(Screen):
    def render(self, sign):
        img = sign.create_image()
        img[::2, ::2] = True
        img[1::2, 1::2] = True
        return img


class ImageFromFile(Screen):
    def __init__(self, filename):
        self.name = filename
        self.filename = f"images/{ filename }.txt"

    def render(self, sign):
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

    def save(self):
        return f"^^{ self.name }^^"


class Empty(Screen):
    def render(self, sign):
        img = sign.create_image()
        img.fill(0)
        return img

class Full(Screen):
    def render(self, sign):
        img = sign.create_image()
        img.fill(1)
        return img


class Noise(Screen):
    def render(self, sign):
        img = sign.create_image()
        img[:] = np.random.choice(a=[False, True], size=img.shape)
        return img

inbuilt = {
    "STRIPES": Stripes(),
    "CHECKERBOARD": Checkerboard(),
    "EMPTY": Empty(),
    "FULL": Full(),
    "NOISE": Noise(),
    "STARS": Stars(),
    "DIAMONDS": Diamonds(),
}

class Random(Screen):
    def __init__(self):
        self.options = list(inbuilt.values())

    def render(self, sign):
        all_options = [ImageFromFile(i["name"]) for i in get_images()] + self.options
        return random.choice(all_options).render(sign)

inbuilt.update({"RANDOM": Random()})


def parse_image_file(name):
    image = {"name": name.split('.')[0]}
    with open("images/%s" % name) as f:
        image['content'] = f.read()
    return image


def get_images():
    images = []
    for name in os.listdir('images'):
        if os.path.isdir(f"images/{ name }"):
            for subname in os.listdir(f"images/{ name }"):
                images.append(parse_image_file(f"{ name }/{ subname }"))
        else:
            images.append(parse_image_file(name))
    return images

def get_specials():
    return (
        [f"^^{ i['name'] }^^" for i in get_images()] +
        [f"^^{ i }^^" for i in inbuilt.keys()]
    )


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

            if msg.startswith("^^") and msg.endswith("^^"):
                key = msg.replace("^", "")
                if key in inbuilt:
                    parsed.append((inbuilt[key], time))
                elif os.path.isdir(f"images/{ key }"):
                    raw_frames = os.listdir(f"images/{ key }")
                    time = max([time/len(raw_frames), MIN_FRAME_TIME])
                    for frame in sorted(raw_frames):
                        file_suffix = f"{ key }/{ frame.removesuffix('.txt') }"
                        parsed.append((ImageFromFile(file_suffix), time))
                else:
                    parsed.append((ImageFromFile(key), time))
            else:
                screen = Text(msg)
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
