"""Render the Giggle Garden theme song example video from the user's poses and backgrounds.

Usage:
  python render.py stills OUTDIR t1 t2 ...   # save preview frames
  python render.py video OUT.mp4             # render the full video with the song
"""
import functools, math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

ROOT = "/Users/ladywealthwarrior/Kids Channel"
CH = ROOT + "/Giggle Garden/Characters/"
BGD = ROOT + "/Giggle Garden/Backgrounds/"
SONG = ROOT + "/Welcome to the Giggle Garden.mp3"
W, H, FPS = 1920, 1080, 30
DUR = 135.0
BEAT = 60 / 115          # measured tempo: 115 BPM
PHASE = 0.325            # time of the first beat
FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
EMOJI = "/System/Library/Fonts/Apple Color Emoji.ttc"
PINK, GREEN, ORANGE = "#E0457B", "#2E8B57", "#F28C28"


def clamp(u):
    return min(max(u, 0.0), 1.0)


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def back_out(u):
    u = clamp(u)
    c = 1.70158
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2


def beat_count(t, beats=1.0):
    return math.floor((t - PHASE) / (BEAT * beats))


# ---------- assets ----------

@functools.lru_cache(None)
def pose(name, size):
    im = Image.open(CH + name + ".png").convert("RGBA")
    a = im.getchannel("A").filter(ImageFilter.MinFilter(5)).point(lambda v: 0 if v < 60 else v)
    im.putalpha(a)  # trims the soft glow halo around the cut-outs
    s = size / im.width
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    return im.crop(im.getbbox())


@functools.lru_cache(None)
def background(name):
    return Image.open(BGD + name + ".png").convert("RGB").resize((W, H), Image.LANCZOS)


def background_frame(name, z):
    im = background(name)
    if z <= 1.0001:
        return im.copy()
    w, h = W / z, H / z
    x0, y0 = (W - w) / 2, (H - h) / 2
    return im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))


@functools.lru_cache(None)
def text_sprite(txt, size, fill, stroke):
    f = ImageFont.truetype(FONT, size)
    sw = max(6, size // 11)
    bb = ImageDraw.Draw(Image.new("RGBA", (8, 8))).textbbox((0, 0), txt, font=f, stroke_width=sw)
    pad = 24
    im = Image.new("RGBA", (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((pad - bb[0] + 6, pad - bb[1] + 8), txt, font=f, fill=(60, 30, 40, 110),
           stroke_width=sw, stroke_fill=(60, 30, 40, 110))
    d.text((pad - bb[0], pad - bb[1]), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return im


@functools.lru_cache(None)
def emoji_sprite(ch, size):
    f = ImageFont.truetype(EMOJI, 160)
    im = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    s = size / im.height
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


@functools.lru_cache(None)
def grass_strip():
    im = Image.open(BGD + "BG Grass Strip.png").convert("RGBA")
    a = im.getchannel("A").filter(ImageFilter.MinFilter(3))
    im.putalpha(a)
    s = 0.5
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)


def put(base, spr, x, y):
    """Composite spr onto base with its top-left at (x, y), clipping to the frame."""
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(spr.width, W - x), min(spr.height, H - y)
    if sx1 > sx0 and sy1 > sy0:
        base.alpha_composite(spr, dest=(x + sx0, y + sy0), source=(sx0, sy0, sx1, sy1))


def scaled(spr, sc):
    if abs(sc - 1) < 0.01:
        return spr
    return spr.resize((max(1, round(spr.width * sc)), max(1, round(spr.height * sc))), Image.BILINEAR)


# ---------- layers ----------

class Char:
    """A character cut-out anchored at its feet (bottom-center)."""

    def __init__(self, seq, x, y, size, path=None, enter=None, enter_t=None, bob=0, bob_beats=1.0,
                 tilt=0, tilt_period=2.0, pulse=None, hops=(), hop_h=130, flip=False, swap_offset=0):
        self.seq = seq if isinstance(seq, list) else [(-1, seq)]
        self.path = path or [(0, x, y)]
        self.size, self.enter, self.enter_t = size, enter, enter_t
        self.bob, self.bob_beats = bob, bob_beats
        self.tilt, self.tilt_period = tilt, tilt_period
        self.pulse, self.hops, self.hop_h = pulse or [], hops, hop_h
        self.flip, self.swap_offset = flip, swap_offset

    def pose_name(self, t):
        cur = self.seq[0]
        for e in self.seq:
            if e[0] <= t:
                cur = e
        names = cur[1]
        if isinstance(names, tuple):
            beats = cur[2] if len(cur) > 2 else 1.0
            return names[(beat_count(t, beats) + self.swap_offset) % len(names)]
        return names

    def position(self, t):
        p = self.path
        if t <= p[0][0]:
            return p[0][1], p[0][2]
        for (ta, xa, ya), (tb, xb, yb) in zip(p, p[1:]):
            if ta <= t < tb:
                u = ease((t - ta) / (tb - ta))
                return xa + (xb - xa) * u, ya + (yb - ya) * u
        return p[-1][1], p[-1][2]

    def draw(self, base, t, scene_t0):
        et = self.enter_t if self.enter_t is not None else scene_t0
        if self.enter and t < et:
            return
        x, y = self.position(t)
        sc = 1.0
        if self.enter == "pop":
            sc *= back_out((t - et) / 0.35)
        elif self.enter == "rise":
            y += (1 - ease((t - et) / 0.4)) * 600
        for ta, tb, sa, sb in self.pulse:
            if t >= ta:
                sc_p = sa + (sb - sa) * ease((t - ta) / (tb - ta)) if t < tb else sb
        if self.pulse and t >= self.pulse[0][0]:
            sc *= sc_p
        if self.bob:
            y -= abs(math.sin(math.pi * (t - PHASE) / (BEAT * self.bob_beats))) * self.bob
        for ht in self.hops:
            if ht <= t < ht + 0.42:
                y -= math.sin(math.pi * (t - ht) / 0.42) * self.hop_h
        spr = pose(self.pose_name(t), self.size)
        if self.flip:
            spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
        spr = scaled(spr, sc) if sc > 0.02 else None
        if spr is None:
            return
        if self.tilt:
            ang = self.tilt * math.sin(2 * math.pi * t / self.tilt_period)
            spr = spr.rotate(ang, resample=Image.BICUBIC, expand=True)
        put(base, spr, x - spr.width / 2, y - spr.height)


class Text:
    def __init__(self, txt, x, y, size, t0, t1=None, fill="white", stroke=PINK, wobble=False, float_up=False):
        self.txt, self.x, self.y, self.size, self.t0, self.t1 = txt, x, y, size, t0, t1
        self.fill, self.stroke, self.wobble, self.float_up = fill, stroke, wobble, float_up

    def draw(self, base, t, scene_t0):
        if t < self.t0 or (self.t1 is not None and t >= self.t1):
            return
        spr = scaled(text_sprite(self.txt, self.size, self.fill, self.stroke), back_out((t - self.t0) / 0.3))
        y = self.y
        if self.wobble:
            spr = spr.rotate(5 * math.sin(2 * math.pi * (t - PHASE) / (2 * BEAT)), resample=Image.BICUBIC, expand=True)
        if self.float_up:
            y -= (t - self.t0) * 70
            a = spr.getchannel("A").point(lambda v: int(v * clamp(1.6 - (t - self.t0) / 1.5)))
            spr = spr.copy()
            spr.putalpha(a)
        put(base, spr, self.x - spr.width / 2, y - spr.height / 2)


class Emoji:
    def __init__(self, ch, x, y, size, t0):
        self.ch, self.x, self.y, self.size, self.t0 = ch, x, y, size, t0

    def draw(self, base, t, scene_t0):
        if t < self.t0:
            return
        spr = scaled(emoji_sprite(self.ch, self.size), back_out((t - self.t0) / 0.3))
        y = self.y - 12 * abs(math.sin(math.pi * (t - PHASE) / BEAT))
        put(base, spr, self.x - spr.width / 2, y - spr.height / 2)


class Grass:
    def __init__(self, drop=0):
        self.drop = drop

    def draw(self, base, t, scene_t0):
        g = grass_strip()
        y = H - g.height + 40 + self.drop
        x = -30
        while x < W:
            put(base, g, x, y)
            x += g.width - 60


class Sparkles:
    def __init__(self, pts, t0=None, color=(255, 250, 210, 255)):
        self.pts, self.t0, self.color = pts, t0, color

    def draw(self, base, t, scene_t0):
        if self.t0 is not None and t < self.t0:
            return
        d = ImageDraw.Draw(base)
        for i, (x, y, r) in enumerate(self.pts):
            k = 0.5 + 0.5 * math.sin(2 * math.pi * (t * 1.3 + i * 0.37))
            rr, w = r * (0.4 + 0.6 * k), r * 0.22 * (0.4 + 0.6 * k)
            d.polygon([(x, y - rr), (x + w, y - w), (x + rr, y), (x + w, y + w), (x, y + rr),
                       (x - w, y + w), (x - rr, y), (x - w, y - w)], fill=self.color)


class Petals:
    def __init__(self, t0, n=46, seed=7):
        rnd = random.Random(seed)
        self.t0 = t0
        self.p = [(rnd.uniform(0, W), rnd.uniform(-H, 0), rnd.uniform(90, 170), rnd.uniform(20, 60),
                   rnd.uniform(0, 6.3), rnd.uniform(14, 26),
                   rnd.choice([(255, 150, 190), (255, 196, 214), (255, 225, 120), (210, 170, 255)]))
                  for _ in range(n)]

    def draw(self, base, t, scene_t0):
        d = ImageDraw.Draw(base)
        dt = t - self.t0
        for x0, y0, v, sway, ph, r, col in self.p:
            y = (y0 + v * dt) % (H + 120) - 60
            x = x0 + sway * math.sin(dt * 1.6 + ph)
            d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=col + (235,))


class Fade:
    def __init__(self, ta, tb):
        self.ta, self.tb = ta, tb

    def draw(self, base, t, scene_t0):
        if t >= self.ta:
            a = int(255 * ease((t - self.ta) / (self.tb - self.ta)))
            base.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, a)))


# ---------- scenes ----------

class Scene:
    def __init__(self, t0, t1, bg, layers, zoom=(1.0, 1.05)):
        self.t0, self.t1, self.bg, self.layers, self.zoom = t0, t1, bg, layers, zoom


def sunny_talk(t_start, t_stop, t0):
    return [(t0, "Sunny/Sunny Waving v2"),
            (t_start, ("Sunny/Sunny Waving", "Sunny/Sunny Waving v2"), 0.5),
            (t_stop, "Sunny/Sunny Waving")]


def bug_row(t_in, stagger=0.15):
    return [
        Char("Poppy/Poppy Wave", 290, 1050, 340, enter="rise", enter_t=t_in, tilt=4, tilt_period=1.0),
        Char("Bo/Bo Flying and Waving", 600, 850, 370, enter="rise", enter_t=t_in + stagger, bob=14, bob_beats=2),
        Char("Zoom/Zoom Thumbs Up", 1340, 1060, 360, enter="rise", enter_t=t_in + 2 * stagger),
        Char("Lulu/Lulu Waving", 1650, 1065, 420, enter="rise", enter_t=t_in + 3 * stagger, tilt=3, tilt_period=1.2),
    ]


def chorus(t0, t_giggle, t_kids, t_ha, t1, petals=False):
    dance = {
        "Poppy": ("Poppy/Poppy Dancing", "Poppy/Poppy Jump"),
        "Bo": ("Bo/Bo Dancing V2", "Bo/Bo Huggable V2"),
        "Zoom": ("Zoom/Zoom Dancing", "Zoom/Zoom Flexing"),
        "Lulu": ("Lulu/Lulu Dancing", "Lulu/Lulu Giggly"),
        "Sunny": ("Sunny/Sunny Dancing", "Sunny/Sunny Cheerful"),
    }
    laugh = {
        "Poppy": ("Poppy/Poppy Jump", "Poppy/Poppy Dancing"),
        "Bo": ("Bo/Bo Huggable V2", "Bo/Bo Dancing V2"),
        "Zoom": ("Zoom/Zoom Laughing", "Zoom/Zoom Dancing"),
        "Lulu": ("Lulu/Lulu Giggly", "Lulu/Lulu Dancing"),
        "Sunny": ("Sunny/Sunny Laughing", "Sunny/Sunny Dancing"),
    }

    def seq(k):
        return [(t0, dance[k], 2), (t_giggle, laugh[k], 1)]

    layers = [
        Char(seq("Sunny"), 1720, 1090, 820, tilt=3, tilt_period=4 * BEAT),
        Grass(),
        Char(seq("Poppy"), 560, 660, 250, bob=16),
        Char(seq("Bo"), 815, 600, 300, bob=22, swap_offset=1),
        Char(seq("Zoom"), 1065, 665, 280, bob=12),
        Char(seq("Lulu"), 1330, 668, 320, bob=14, swap_offset=1),
        Text("Giggle, giggle!", 960, 150, 120, t_giggle, t_kids, fill="#FFE14D", wobble=True),
        Text("Ha ha ha!", 470, 150, 110, t_ha, fill="white", stroke=ORANGE, wobble=True),
        Text("Hee hee hee!", 1420, 150, 110, t_ha + 0.85, fill="white", stroke=GREEN, wobble=True),
    ]
    if petals:
        layers.insert(0, Petals(t0))
        layers.append(Petals(t0 + 3, n=24, seed=11))
    return Scene(t0, t1, "BG Mushroom Stage", layers, zoom=(1.0, 1.04))


def numbers_arc(times):
    out = []
    for i, tt in enumerate(times):
        ang = math.radians(200 - i * (220 / 6))
        out.append(Text(str(i + 1), 960 + 430 * math.cos(ang), 560 - 330 * math.sin(ang), 130, tt,
                        fill="#FFE14D", stroke=PINK))
    return out


def bo_zigzag(t0, t1, x0, x1, ya, yb, step=BEAT):
    pts, t, i = [], t0, 0
    while t <= t1 + 1e-6:
        u = (t - t0) / (t1 - t0)
        pts.append((t, x0 + (x1 - x0) * u, ya if i % 2 == 0 else yb))
        t += step
        i += 1
    return pts


SCENES = [
    # Intro
    Scene(0.0, 1.85, "BG Garden Wide", [
        Text("Giggle Garden", 960, 470, 190, 0.3, fill="#FFE14D", stroke=PINK),
        Sparkles([(560, 360, 40), (1360, 380, 46), (700, 600, 30), (1240, 620, 34)], t0=0.4),
    ], zoom=(1.0, 1.1)),
    Scene(1.85, 4.7, "BG Sunnys Patch", [
        Char(sunny_talk(1.9, 4.4, 1.85), 960, 1050, 900),
        Grass(),
    ], zoom=(1.0, 1.05)),
    Scene(4.7, 7.2, "BG Sunnys Patch", [
        Char("Sunny/Sunny Cheerful", 960, 1050, 900, tilt=2, tilt_period=2.1),
        Grass(),
        *bug_row(4.8),
        Text("Good morning!", 960, 130, 120, 4.85, fill="#FFE14D"),
    ]),
    # Chorus 1
    chorus(7.2, 16.0, 19.9, 21.5, 23.7),
    # Verse 1: Sunny
    Scene(23.7, 28.3, "BG Sunnys Patch", [
        Char([(0, "Sunny/Sunny Sleepy"), (27.25, "Sunny/Sunny Waving")], 960, 1060, 950,
             pulse=[(23.7, 28.3, 1.0, 1.06)]),
        Grass(),
    ], zoom=(1.0, 1.08)),
    Scene(28.3, 32.6, "BG Sunnys Patch", [
        Sparkles([(250, 180, 46), (420, 300, 34), (180, 420, 28), (560, 140, 38), (700, 330, 24)]),
        Char("Sunny/Sunny Cheerful", 960, 1060, 950, tilt=2.5, tilt_period=2.1),
        Grass(),
    ], zoom=(1.04, 1.0)),
    Scene(32.6, 34.5, "BG Sunnys Patch", [
        Char("Sunny/Sunny Laughing", 960, 1050, 900),
        Grass(),
        *bug_row(32.65, 0.1),
        Text("Hi, Sunny!", 960, 130, 130, 32.8, fill="#FFE14D"),
    ], zoom=(1.0, 1.0)),
    # Verse 2: Poppy
    Scene(34.5, 36.7, "BG Puddle Pond", [
        Char([(0, "Poppy/Poppy Mid Stride"), (35.9, "Poppy/Poppy Wave")], 0, 0, 400,
             path=[(34.5, -200, 1010), (35.9, 960, 1010)], bob=18, bob_beats=0.5),
    ]),
    Scene(36.7, 38.9, "BG Puddle Pond", [
        Char("Poppy/Poppy Curious", 960, 1010, 420),
        Text("?", 1230, 430, 260, 37.1, fill="#FFE14D", stroke=PINK, wobble=True),
    ]),
    Scene(38.9, 43.3, "BG Puddle Pond", [
        Char([(0, "Poppy/Poppy Counting"), (42.6, "Poppy/Poppy Jump")], 960, 1010, 420, hops=(42.7,), hop_h=160),
        *numbers_arc([40.0, 40.3, 40.6, 41.0, 41.3, 41.6, 41.9]),
        Text("Whee!", 1500, 260, 140, 42.7, fill="#FFE14D", wobble=True),
    ], zoom=(1.0, 1.03)),
    Scene(43.3, 44.5, "BG Puddle Pond", [
        Char("Poppy/Poppy Pointing up", 960, 1010, 420),
        Text("Let's find out!", 960, 140, 130, 43.4, fill="#FFE14D"),
    ]),
    # Chorus 2
    chorus(44.5, 53.5, 57.6, 59.2, 60.5),
    # Verse 3: Bo
    Scene(60.5, 63.9, "BG Garden Wide", [
        Char("Bo/Bo Joyful", 0, 0, 340, path=bo_zigzag(60.6, 63.8, -250, 2150, 300, 400)),
    ], zoom=(1.0, 1.04)),
    Scene(63.9, 65.9, "BG Sunnys Patch", [
        Char("Sunny/Sunny Hand on Heart", 1640, 1070, 720),
        Grass(),
        Char("Bo/Bo Shy V2", 820, 820, 470, bob=16, bob_beats=2),
    ]),
    Scene(65.9, 67.8, "BG Sunnys Patch", [
        Char("Sunny/Sunny Hand on Heart", 1640, 1070, 720),
        Grass(),
        Char("Bo/Bo Nervous", 820, 820, 470, bob=8, bob_beats=2),
    ]),
    Scene(67.8, 70.1, "BG Sunnys Patch", [
        Char("Sunny/Sunny Hand on Heart", 1640, 1070, 720),
        Grass(),
        Char([(0, "Bo/Bo Deep Breath"), (68.9, "Bo/Bo Mascot V2")], 820, 820, 470,
             pulse=[(67.9, 68.4, 1.0, 1.18), (68.4, 68.9, 1.18, 1.0)]),
        Text("Breathe in...", 820, 120, 110, 67.9, 68.4, fill="white", stroke=GREEN),
        Text("Breathe out...", 820, 120, 110, 68.4, 69.7, fill="white", stroke=GREEN),
    ], zoom=(1.0, 1.0)),
    Scene(70.1, 71.0, "BG Sunnys Patch", [
        Char("Sunny/Sunny Hand on Heart", 1640, 1070, 720),
        Grass(),
        Char("Bo/Bo Thumbs Up V2", 820, 820, 470),
        Text("I can try!", 820, 130, 130, 70.2, fill="#FFE14D"),
    ], zoom=(1.0, 1.0)),
    # Verse 4: Zoom
    Scene(71.0, 74.1, "BG Garden Wide", [
        Char("Zoom/Zoom Racing Crouch", 1040, 1050, 440),
    ], zoom=(1.0, 1.05)),
    Scene(74.1, 76.3, "BG Garden Wide", [
        Char("Zoom/Zoom Flexing", 1040, 1050, 440),
        Sparkles([(905, 830, 44), (960, 760, 26)]),
    ]),
    Scene(76.3, 78.1, "BG Garden Wide", [
        Char("Zoom/Zoom Races Forward", 0, 0, 440, path=[(76.3, 1000, 1050), (78.1, 1050, 1050)]),
        Text("ZOOM!", 1420, 300, 190, 77.3, fill="#FFE14D", stroke=ORANGE, wobble=True),
    ]),
    Scene(78.1, 80.7, "BG Garden Wide", [
        Char("Zoom/Zoom Tired", 1050, 1030, 440),
        Char("Lulu/Lulu Inching", 0, 0, 400, path=[(78.15, 2200, 1075), (80.7, -250, 1075)], bob=8, bob_beats=0.5),
    ]),
    Scene(80.7, 82.5, "BG Garden Wide", [
        Char("Zoom/Zoom Thumbs Up", 960, 1050, 440),
        Char("Poppy/Poppy Jump", 520, 1060, 320, enter="rise", enter_t=80.75, hops=(81.1, 81.6), hop_h=90),
        Char("Bo/Bo Dancing V2", 1420, 900, 360, enter="rise", enter_t=80.85, bob=18),
        Text("Go, Zoom, go!", 960, 140, 130, 80.8, fill="#FFE14D", stroke=ORANGE),
    ], zoom=(1.0, 1.0)),
    # Verse 5: Lulu
    Scene(82.5, 84.4, "BG Leaf Bed", [
        Char("Lulu/Lulu’ Apple Snack", 960, 810, 600, hops=(82.6, 83.3), hop_h=35),
    ]),
    Scene(84.4, 86.8, "BG Leaf Bed", [
        Char("Lulu/Lulu Sleepy", 960, 810, 600),
        Text("Z", 1240, 360, 130, 84.9, fill="white", stroke="#7B61C9", float_up=True),
        Text("z", 1340, 290, 105, 85.4, fill="white", stroke="#7B61C9", float_up=True),
        Text("z", 1420, 230, 85, 85.9, fill="white", stroke="#7B61C9", float_up=True),
    ]),
    Scene(86.8, 88.9, "BG Leaf Bed", [
        Char("Lulu/Lulu with Strawberry", 960, 810, 600),
        Emoji("\U0001F34E", 560, 220, 150, 86.9),
        Emoji("\U0001F353", 960, 170, 150, 87.3),
        Emoji("\U0001FADB", 1360, 220, 150, 88.0),
    ]),
    Scene(88.9, 90.6, "BG Leaf Bed", [
        Char("Lulu/Lulu Giggly", 960, 810, 600, bob=12),
        Text("Snack time!", 960, 140, 140, 89.0, fill="#FFE14D", stroke=PINK, wobble=True),
    ]),
    # Bridge: dance-along
    Scene(90.6, 94.6, "BG Mushroom Stage", [
        Char([(0, ("Poppy/Poppy Dancing", "Poppy/Poppy Jump"), 1), (93.0, "Poppy/Poppy Jump")], 960, 700, 460,
             hops=(93.1, 93.55), hop_h=150, bob=10),
        Text("JUMP!", 960, 150, 190, 93.1, fill="#FFE14D", stroke=PINK, wobble=True),
    ], zoom=(1.0, 1.04)),
    Scene(94.6, 98.8, "BG Mushroom Stage", [
        Char("Bo/Bo Joyful", 0, 0, 420, path=bo_zigzag(94.6, 98.7, 250, 1670, 420, 600)),
        Text("BZZZ!", 960, 150, 190, 97.4, fill="#FFE14D", stroke=ORANGE, wobble=True),
    ], zoom=(1.0, 1.04)),
    Scene(98.8, 103.1, "BG Mushroom Stage", [
        Char([(0, ("Lulu/Lulu Dancing", "Lulu/Lulu Giggly"), 0.5)], 960, 710, 540, tilt=5, tilt_period=2 * BEAT),
        Text("WIGGLE!", 960, 150, 190, 101.4, fill="#FFE14D", stroke=GREEN, wobble=True),
    ], zoom=(1.0, 1.04)),
    Scene(103.1, 106.9, "BG Mushroom Stage", [
        Char([(0, ("Sunny/Sunny Dancing", "Sunny/Sunny Cheerful"), 2)], 960, 1110, 920, tilt=8, tilt_period=4 * BEAT),
        Grass(),
        Text("SWAY!", 960, 150, 190, 104.4, fill="#FFE14D", stroke=PINK, wobble=True),
    ], zoom=(1.0, 1.04)),
    Scene(106.9, 113.1, "BG Mushroom Stage", [
        Char("Zoom/Zoom Sliding", 0, 0, 440, path=[(107.0, 480, 700), (112.9, 1240, 700)]),
        Text("s l o o o w l y", 960, 160, 130, 110.4, fill="white", stroke=GREEN),
    ], zoom=(1.0, 1.06)),
    # Final chorus
    chorus(113.1, 122.0, 126.1, 128.2, 129.8, petals=True),
    # Outro
    Scene(129.8, DUR + 1, "BG Sunnys Patch", [
        Char(sunny_talk(130.0, 131.8, 129.8), 960, 1050, 900),
        Grass(),
        *bug_row(129.85, 0.1),
        Text("Bye-bye!", 960, 140, 150, 133.1, fill="#FFE14D", stroke=PINK, wobble=True),
        Emoji("\U0001F44B", 1330, 140, 130, 133.2),
        Fade(133.9, 135.0),
    ], zoom=(1.0, 1.04)),
]


def render(t):
    sc = next(s for s in SCENES if s.t0 <= t < s.t1)
    u = (t - sc.t0) / max(0.001, min(sc.t1, DUR) - sc.t0)
    base = background_frame(sc.bg, sc.zoom[0] + (sc.zoom[1] - sc.zoom[0]) * u).convert("RGBA")
    for layer in sc.layers:
        layer.draw(base, t, sc.t0)
    return base.convert("RGB")


def main():
    mode = sys.argv[1]
    if mode == "stills":
        out = sys.argv[2]
        for ts in sys.argv[3:]:
            render(float(ts)).save(f"{out}/frame_{float(ts):06.2f}.jpg", quality=85)
        return
    out = sys.argv[2]
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", SONG, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
           "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for i in range(n):
        p.stdin.write(render(i / FPS).tobytes())
        if i % (FPS * 10) == 0:
            print(f"{i / FPS:5.0f}s / {DUR:.0f}s", flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()
