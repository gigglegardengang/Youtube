"""Cut the Pixar-style Rendar clips to the Giggle Garden theme song, with sing-along text.

Usage:
  python assemble.py stills OUTDIR t1 t2 ...
  python assemble.py video OUT.mp4
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imageio_ffmpeg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import (W, H, FPS, DUR, SONG, FONT, PINK, GREEN, ORANGE, Text, Emoji, Petals, Fade,
                    numbers_arc, put, ease)

CLIPS = "/Users/ladywealthwarrior/Kids Channel/Giggle Garden/Videos/Clips/"
NAMES = {int(f[5:7]): CLIPS + f for f in os.listdir(CLIPS) if f.startswith("Clip ") and f.endswith(".mp4")}
CLIP_FPS = 24
YELLOW = "#FFE14D"


class Window:
    """Show a layer only between a and b."""

    def __init__(self, layer, a, b):
        self.layer, self.a, self.b = layer, a, b

    def draw(self, base, t, t0):
        if self.a <= t < self.b:
            self.layer.draw(base, t, t0)


class Caption:
    """Sing-along lyric line along the bottom of the screen."""

    def __init__(self, txt, t0, t1, size=66):
        self.txt, self.t0, self.t1, self.size = txt, t0, t1, size
        f = ImageFont.truetype(FONT, size)
        sw = 7
        bb = ImageDraw.Draw(Image.new("RGBA", (8, 8))).textbbox((0, 0), txt, font=f, stroke_width=sw)
        im = Image.new("RGBA", (bb[2] - bb[0] + 40, bb[3] - bb[1] + 30), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20 - bb[0], 15 - bb[1]), txt, font=f, fill="white", stroke_width=sw,
                                stroke_fill=(90, 40, 80, 255))
        self.spr = im

    def draw(self, base, t, t0):
        if not (self.t0 <= t < self.t1):
            return
        a = min(ease((t - self.t0) / 0.2), ease((self.t1 - t) / 0.2))
        spr = self.spr
        if a < 1:
            spr = spr.copy()
            spr.putalpha(spr.getchannel("A").point(lambda v: int(v * a)))
        put(base, spr, (W - spr.width) / 2, H - spr.height - 40)


def chorus(t0, t_giggle, t_kids, t_ha, t1, lines, petals=False):
    mid = (t0 + t_giggle) / 2
    segs = [(t0, mid, 5, 0.0), (mid, t_giggle, 6, 0.0), (t_giggle, t_kids, 7, 0.0), (t_kids, t1, 8, 0.0)]
    words = ["Come on down to Giggle Garden,", "where the flowers sway and the sunbeams shine!",
             "Wiggle your toes and giggle a little,", "everybody's welcome, every time!"]
    layers = [Caption(w, a, b) for w, (a, b) in zip(words, lines)]
    layers += [
        Text("Giggle, giggle!", 960, 140, 120, t_giggle, t_kids, fill=YELLOW, wobble=True),
        Text("Ha ha ha!", 470, 140, 110, t_ha, t1, fill="white", stroke=ORANGE, wobble=True),
        Text("Hee hee hee!", 1430, 140, 110, t_ha + 0.85, t1, fill="white", stroke=GREEN, wobble=True),
    ]
    if petals:
        layers = [Window(Petals(t0), t0, t1), Window(Petals(t0 + 3, n=24, seed=11), t0 + 3, t1)] + layers
    return segs, layers


# (start, end, clip number, start offset within clip in seconds)
SEGMENTS = [
    (0.0, 1.85, 2, 0.0),
    (1.85, 4.7, 3, 0.0),
    (4.7, 7.2, 4, 0.0),
]
LAYERS = [
    Text("Giggle Garden", 960, 470, 190, 0.3, 1.85, fill=YELLOW, stroke=PINK),
    Text("Good morning!", 960, 130, 120, 4.85, 7.2, fill=YELLOW),
]

for args in [
    (7.2, 16.0, 19.9, 21.5, 23.7, [(7.3, 9.3), (9.3, 11.8), (11.9, 13.8), (13.9, 15.9)], False),
    (44.5, 53.5, 57.6, 59.2, 60.5, [(44.6, 46.8), (46.8, 49.3), (49.4, 51.4), (51.5, 53.4)], False),
    (113.1, 122.0, 126.1, 128.2, 129.8, [(113.3, 115.3), (115.4, 117.9), (118.0, 119.9), (120.0, 121.9)], True),
]:
    s, l = chorus(*args)
    SEGMENTS += s
    LAYERS += l

SEGMENTS += [
    # Verse 1: Sunny
    (23.7, 28.3, 9, 0.0),
    (28.3, 32.6, 3, 0.4),
    (32.6, 34.5, 4, 0.5),
    # Verse 2: Poppy
    (34.5, 36.7, 1, 0.0),
    (36.7, 38.9, 10, 0.0),
    (38.9, 43.3, 11, 0.0),
    (43.3, 44.5, 10, 3.6),
    # Verse 3: Bo
    (60.5, 65.9, 12, 0.0),
    (65.9, 71.0, 13, 0.0),
    # Verse 4: Zoom
    (71.0, 76.3, 14, 0.0),
    (76.3, 80.7, 15, 0.0),
    (80.7, 82.5, 8, 1.5),
    # Verse 5: Lulu
    (82.5, 86.8, 16, 0.0),
    (86.8, 90.6, 17, 0.0),
    # Bridge
    (90.6, 94.6, 18, 0.0),
    (94.6, 98.8, 19, 0.0),
    (98.8, 103.1, 20, 0.0),
    (103.1, 106.9, 21, 0.0),
    (106.9, 113.1, 22, 0.0),
    # Outro
    (129.8, 132.6, 3, 1.0),
    (132.6, DUR + 1, 4, 0.0),
]
SEGMENTS.sort()

LAYERS += [
    Text("Hi, Sunny!", 960, 130, 130, 32.8, 34.5, fill=YELLOW),
    Text("?", 1250, 380, 260, 37.1, 38.9, fill=YELLOW, stroke=PINK, wobble=True),
    *[Window(Text(str(i + 1), 330 + i * 210, 930, 130, tt, fill=YELLOW, stroke=PINK), tt, 43.3)
      for i, tt in enumerate([40.0, 40.3, 40.6, 41.0, 41.3, 41.6, 41.9])],
    Text("Whee!", 1500, 260, 140, 42.7, 43.3, fill=YELLOW, wobble=True),
    Text("Let's find out!", 960, 140, 130, 43.4, 44.5, fill=YELLOW),
    Text("Breathe in...", 960, 120, 110, 67.9, 68.4, fill="white", stroke=GREEN),
    Text("Breathe out...", 960, 120, 110, 68.4, 69.8, fill="white", stroke=GREEN),
    Text("I can try!", 960, 130, 130, 70.2, 71.0, fill=YELLOW),
    Text("ZOOM!", 1420, 260, 190, 77.3, 80.7, fill=YELLOW, stroke=ORANGE, wobble=True),
    Text("Go, Zoom, go!", 960, 140, 130, 80.8, 82.5, fill=YELLOW, stroke=ORANGE),
    Text("Z", 1300, 330, 130, 84.9, 86.8, fill="white", stroke="#7B61C9", float_up=True),
    Text("z", 1400, 260, 105, 85.4, 86.8, fill="white", stroke="#7B61C9", float_up=True),
    Text("z", 1480, 200, 85, 85.9, 86.8, fill="white", stroke="#7B61C9", float_up=True),
    Window(Emoji("\U0001F34E", 560, 200, 150, 86.9), 86.9, 89.0),
    Window(Emoji("\U0001F353", 960, 150, 150, 87.3), 87.3, 89.0),
    Window(Emoji("\U0001FADB", 1360, 200, 150, 88.0), 88.0, 89.0),
    Text("Snack time!", 960, 140, 140, 89.0, 90.6, fill=YELLOW, stroke=PINK, wobble=True),
    Text("JUMP!", 960, 150, 190, 93.1, 94.6, fill=YELLOW, stroke=PINK, wobble=True),
    Text("BZZZ!", 960, 150, 190, 97.4, 98.8, fill=YELLOW, stroke=ORANGE, wobble=True),
    Text("WIGGLE!", 960, 150, 190, 101.4, 103.1, fill=YELLOW, stroke=GREEN, wobble=True),
    Text("SWAY!", 960, 150, 190, 104.4, 106.9, fill=YELLOW, stroke=PINK, wobble=True),
    Text("s l o o o w l y", 960, 160, 130, 110.4, 113.1, fill="white", stroke=GREEN),
    Caption("See you in the garden!", 130.0, 132.6),
    Text("Bye-bye!", 960, 140, 150, 133.1, fill=YELLOW, stroke=PINK, wobble=True),
    Emoji("\U0001F44B", 1330, 140, 130, 133.2),
    Fade(133.9, 135.0),
]
# Emoji layers have no end time; limit them to their scene.
_EMOJI_END = {86.9: 90.6, 87.3: 90.6, 88.0: 90.6, 133.2: DUR + 1}


class Timeline:
    def __init__(self):
        self.cache_clip, self.cache_frames = None, None

    def frames(self, n):
        if self.cache_clip != n:
            gen = imageio_ffmpeg.read_frames(NAMES[n])
            meta = next(gen)
            w, h = meta["size"]
            self.cache_frames = [np.frombuffer(b, np.uint8).reshape(h, w, 3) for b in gen]
            self.cache_clip = n
        return self.cache_frames

    def frame(self, t):
        seg = next(s for s in SEGMENTS if s[0] <= t < s[1])
        t0, t1, n, off = seg
        fr = self.frames(n)
        avail = len(fr) / CLIP_FPS - off
        rate = min(1.0, avail / (t1 - t0))
        idx = int((off + (t - t0) * rate) * CLIP_FPS)
        img = Image.fromarray(fr[min(idx, len(fr) - 1)]).resize((W, H), Image.BICUBIC).convert("RGBA")
        for layer in LAYERS:
            layer.draw(img, t, t0)
        return img.convert("RGB")


def main():
    tl = Timeline()
    if sys.argv[1] == "stills":
        for ts in sorted(float(x) for x in sys.argv[3:]):
            tl.frame(ts).save(f"{sys.argv[2]}/f_{ts:06.2f}.jpg", quality=85)
        return
    out = sys.argv[2]
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    p = subprocess.Popen([ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", SONG, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                          "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                          "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(tl.frame(i / FPS).tobytes())
        if i % (FPS * 10) == 0:
            print(f"{i / FPS:5.0f}s / {DUR:.0f}s", flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()
