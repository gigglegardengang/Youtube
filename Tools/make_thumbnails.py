"""YouTube thumbnails (1280x720) for the three launch videos."""
import os, sys
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import text_sprite, emoji_sprite, PINK, GREEN, ORANGE

G = "/Users/ladywealthwarrior/Kids Channel/Giggle Garden/"
OUT = G + "Thumbnails/"
W, H = 1280, 720
YELLOW = "#FFE14D"


def base(path, crop=None):
    im = Image.open(path).convert("RGB")
    if crop:  # (x0, y0, x1, y1) fractions of the source
        x0, y0, x1, y1 = crop
        im = im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H))
    im = ImageEnhance.Color(im).enhance(1.18)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return im.convert("RGBA")


def shade(im, side):
    """Soft dark gradient behind the title so it reads on any background."""
    g = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(g)
    if side == "left":
        for x in range(W // 2):
            d.line((x, 0, x, H), fill=int(120 * (1 - x / (W / 2))))
    else:
        for x in range(W // 2):
            d.line((W - 1 - x, 0, W - 1 - x, H), fill=int(120 * (1 - x / (W / 2))))
    layer = Image.new("RGBA", (W, H), (60, 20, 60, 255))
    layer.putalpha(g)
    im.alpha_composite(layer)


def lines(im, items, x_center, y):
    for txt, size, fill, stroke in items:
        spr = text_sprite(txt, size, fill, stroke)
        if spr.width > 640:
            s = 640 / spr.width
            spr = spr.resize((int(spr.width * s), int(spr.height * s)), Image.LANCZOS)
        im.alpha_composite(spr, (int(x_center - spr.width / 2), y))
        y += spr.height - 18
    return y


def badge(im, txt, color, x, y, size=46):
    spr = text_sprite(txt, size, "white", color)
    im.alpha_composite(spr, (x, y))


def main():
    os.makedirs(OUT, exist_ok=True)

    # 1. Theme song: the whole gang waving
    im = base(G + "Scenes/Shot 03 Sunny Good Morning.png", (0.02, 0.0, 0.78, 0.86))
    shade(im, "left")
    lines(im, [("Welcome to", 70, "white", PINK), ("Giggle", 132, YELLOW, PINK), ("Garden!", 132, YELLOW, PINK)], 330, 70)
    badge(im, "Sing & Dance!", GREEN, 70, 560, 58)
    e = emoji_sprite("\U0001F33B", 110)
    im.alpha_composite(e, (520, 545))
    im.convert("RGB").save(OUT + "Thumbnail 1 - Welcome to the Giggle Garden.png")

    # 2. Counting: Poppy cheering on the lily pads, big number
    im = base(G + "Scenes/Song 2/S2 Shot C Poppy Cheer.png", (0.08, 0.0, 0.92, 0.95))
    shade(im, "right")
    big = text_sprite("1-10", 210, YELLOW, PINK)
    im.alpha_composite(big, (W - big.width - 40, 60))
    lines(im, [("Count", 108, "white", GREEN), ("with Poppy!", 92, "white", GREEN)], W - 300, 320)
    for i, n in enumerate(["1", "2", "3"]):
        dot = text_sprite(n, 60, "white", (40, 110, 40, 255))
        im.alpha_composite(dot, (W - 470 + i * 120, 560))
    im.convert("RGB").save(OUT + "Thumbnail 2 - Poppy's Counting Spots.png")

    # 3. Freeze dance: dance party with an icy FREEZE
    im = base(G + "Scenes/Song 3/S3 Shot Z2 Zoom Fast v2.png", (0.05, 0.0, 0.8, 0.85))
    shade(im, "left")
    lines(im, [("Wiggle", 128, YELLOW, PINK), ("Dance!", 128, YELLOW, PINK)], 320, 70)
    fr = text_sprite("FREEZE!", 116, "white", "#3A8FD8")
    fr = fr.rotate(-6, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(fr, (40, 430))
    im.convert("RGB").save(OUT + "Thumbnail 3 - The Wiggle Wiggle Garden Dance.png")

    # contact sheet for checking, plus a tiny version to test phone size
    sheet = Image.new("RGB", (3 * 640, 360 + 120), (30, 30, 30))
    for i, n in enumerate(sorted(os.listdir(OUT))):
        t = Image.open(OUT + n)
        sheet.paste(t.resize((640, 360)), (i * 640, 0))
        sheet.paste(t.resize((210, 118)), (i * 640 + 215, 361))
    sheet.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "thumbs_sheet.jpg"), quality=85)
    print("done")


if __name__ == "__main__":
    main()
