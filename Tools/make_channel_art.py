"""YouTube channel banner (2560x1440) and profile icon (800x800) for Giggle Garden."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import text_sprite, emoji_sprite, pose, PINK, GREEN

G = "/Users/ladywealthwarrior/Kids Channel/Giggle Garden/"
OUT = G + "Channel Art/"
YELLOW = "#FFE14D"


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def glow(spr, radius=26, color=(255, 255, 240)):
    a = spr.getchannel("A").filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(radius))
    g = Image.new("RGBA", spr.size, color + (0,))
    g.putalpha(a.point(lambda v: min(255, int(v * 1.6))))
    return g


def banner():
    W, H = 2560, 1440
    bg = cover(Image.open(G + "Backgrounds/BG Garden Wide.png").convert("RGB"), W, H).convert("RGBA")
    # soft light band behind the safe area (1546x423 centered) so the title pops
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(band).rounded_rectangle((420, 520, 2140, 920), radius=200, fill=(255, 250, 230, 120))
    bg.alpha_composite(band.filter(ImageFilter.GaussianBlur(40)))

    title = text_sprite("Giggle Garden", 118, YELLOW, PINK)
    title2 = text_sprite("Gang", 112, YELLOW, PINK)
    sub = text_sprite("Sing  \u2022  Dance  \u2022  Learn!", 46, "white", GREEN)
    ty = 515
    for spr, y in [(title, ty), (title2, ty + title.height - 38)]:
        x = (W - spr.width) // 2
        bg.alpha_composite(glow(spr), (x, y))
        bg.alpha_composite(spr, (x, y))
    sy = ty + title.height - 38 + title2.height - 26
    bg.alpha_composite(sub, ((W - sub.width) // 2, sy))
    print("title spans", (W - title.width) // 2, (W + title.width) // 2, "bottom", sy + sub.height)

    def place(name, size, cx, bottom):
        spr = pose(name, size)
        bg.alpha_composite(spr, (int(cx - spr.width / 2), int(bottom - spr.height)))
        print(name, int(cx - spr.width / 2), int(cx + spr.width / 2))

    # everyone stays inside the mobile safe area (x 507-2053, y 508-931) except Sunny
    place("Bo/Bo Flying and Waving", 250, 760, 740)
    place("Poppy/Poppy Wave", 300, 640, 930)
    place("Lulu/Lulu Waving", 300, 1915, 930)
    place("Zoom/Zoom Thumbs Up", 250, 1780, 935)
    # Sunny stands tall at the far right (shows on desktop and TV)
    place("Sunny/Sunny Waving", 820, 2330, 1130)
    os.makedirs(OUT, exist_ok=True)
    bg.convert("RGB").save(OUT + "Giggle Garden Banner 2560x1440.png")
    # preview with the mobile safe area marked
    prev = bg.convert("RGB").resize((1280, 720))
    d = ImageDraw.Draw(prev)
    d.rectangle(((2560 - 1546) // 4, (1440 - 423) // 4, (2560 + 1546) // 4, (1440 + 423) // 4), outline="red", width=3)
    d.rectangle((0, (1440 - 423) // 4, 1279, (1440 + 423) // 4), outline="cyan", width=2)
    prev.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner_preview.jpg"), quality=85)


def icon():
    S = 800
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bg = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(bg)
    for r in range(S // 2, 0, -4):  # warm sky-to-sun radial gradient
        k = r / (S / 2)
        col = (int(255 - 40 * k), int(236 - 30 * k), int(150 + 80 * k), 255)
        d.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), fill=col)
    im.alpha_composite(bg)
    sunny = pose("Sunny/Sunny Waving", 1150)
    # crop to Sunny's face and petals
    fw = sunny.width
    face = sunny.crop((int(fw * 0.12), 0, int(fw * 0.88), int(fw * 0.76)))
    s = S * 0.98 / face.width
    face = face.resize((int(face.width * s), int(face.height * s)), Image.LANCZOS)
    im.alpha_composite(face, ((S - face.width) // 2, int(S * 0.04)))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, S, S), fill=255)
    out = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    out.paste(im, (0, 0), mask)
    out.save(OUT + "Giggle Garden Profile Icon 800x800.png")
    im.convert("RGB").save(OUT + "Giggle Garden Profile Icon 800x800 (square).png")


if __name__ == "__main__":
    banner()
    icon()
    print("done")
