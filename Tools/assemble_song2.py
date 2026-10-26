"""Song 2: Poppy's Counting Spots, cut to the Suno song with counting graphics.

Usage:
  python assemble2.py stills OUTDIR t1 t2 ...
  python assemble2.py video OUT.mp4
"""
import os, subprocess, sys
from PIL import Image, ImageDraw
import numpy as np
import imageio_ffmpeg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import W, H, FPS, Text, Emoji, Fade, PINK, GREEN, ORANGE, back_out, put, text_sprite
import assemble
from assemble import Timeline, Window

G = "/Users/ladywealthwarrior/Kids Channel/Giggle Garden/"
SONG2 = G + "Songs/Song 2-Poppys Counting Spots.mp3"
DUR = 107.5
YELLOW = "#FFE14D"
S2 = G + "Videos/Clips/Song 2/"
assemble.NAMES.update({
    101: S2 + "S2 Clip A Poppy Wave and Hop.mp4",
    102: S2 + "S2 Clip B Poppy Hops Lily Pads.mp4",
    103: S2 + "S2 Clip C Poppy Cheers.mp4",
    104: S2 + "S2 Clip D Poppy Spots.mp4",
    105: S2 + "S2 Clip E Bo Buzzes By.mp4",
})
A, B, C, D, E = 101, 102, 103, 104, 105

SEGMENTS = [
    # intro
    (0.0, 5.3, A, 0.0), (5.3, 8.5, 4, 0.0),
    # chorus 1
    (8.5, 12.8, 11, 0.0), (12.8, 16.8, B, 0.0), (16.8, 20.9, 10, 0.9),
    # verse 1: lily pads 1-5
    (20.9, 23.1, A, 2.4), (23.1, 25.2, B, 2.8), (25.2, 27.2, C, 0.0), (27.2, 29.1, B, 0.0), (29.1, 33.6, C, 1.0),
    # chorus 2
    (33.6, 37.6, 6, 0.0), (37.6, 41.6, B, 0.0), (41.6, 45.8, 10, 0.8),
    # verse 2: lily pads 6-10
    (45.8, 49.8, E, 0.0), (49.8, 53.9, 18, 0.0), (53.9, 57.6, 14, 0.0), (57.6, 62.4, A, 0.5),
    (62.4, 66.4, C, 0.0), (66.4, 69.0, 8, 0.0),
    # bridge: count to 10, then count the spots
    (69.0, 72.8, 4, 0.5), (72.8, 76.8, 5, 0.0), (76.8, 79.4, D, 0.0), (79.4, 84.6, D, 1.1, (1.1, 2.3)), (84.6, 89.5, 18, 0.3),
    # final chorus
    (89.5, 93.6, 11, 0.0), (93.6, 97.6, B, 0.0), (97.6, 102.2, 6, 0.5),
    # outro
    (102.2, DUR + 1, A, 0.0),
]


class LilyPads:
    """A row of lily pads along the bottom that pops in one at a time as Poppy counts."""

    def __init__(self, times, t_end, size=92):
        self.times, self.t_end, self.size = times, t_end, size
        r = size // 2
        pad = Image.new("RGBA", (size + 8, size + 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(pad)
        d.ellipse((4, 4, size + 4, size + 4), fill=(70, 160, 70, 255), outline=(255, 255, 255, 255), width=5)
        d.pieslice((4, 4, size + 4, size + 4), 80, 100, fill=(0, 0, 0, 0))
        self.pad = pad

    def draw(self, base, t, t0):
        if t >= self.t_end:
            return
        n = len(self.times)
        gap = self.size + 34
        x0 = (W - gap * n) // 2 + 17
        for i, ti in enumerate(self.times):
            if t < ti:
                continue
            s = back_out((t - ti) / 0.3)
            spr = self.pad if s >= 0.99 else self.pad.resize((max(1, int(self.pad.width * s)),) * 2)
            cx = x0 + i * gap + self.size // 2
            put(base, spr, cx - spr.width / 2, 985 - spr.height / 2)
            num = text_sprite(str(i + 1), 50, "white", (40, 110, 40, 255))
            if s >= 0.99:
                put(base, num, cx - num.width / 2, 985 - num.height / 2)


def row_numbers(times, y, t_end, size=120, stroke=PINK):
    n = len(times)
    gap = min(170, (W - 200) // n)
    x0 = (W - gap * (n - 1)) // 2
    return [Window(Text(str(i + 1), x0 + i * gap, y, size, tt, fill=YELLOW, stroke=stroke), tt, t_end)
            for i, tt in enumerate(times)]


def big_number(n, t0, t1):
    return Window(Text(str(n), 1720, 190, 230, t0, fill=YELLOW, stroke=GREEN), t0, t1)


LAYERS = [
    Window(Text("Poppy's Counting Spots", 960, 140, 120, 0.3, fill=YELLOW, stroke=PINK), 0.3, 5.3),
    Text("Yay!", 960, 140, 150, 5.5, 8.5, fill=YELLOW, stroke=PINK, wobble=True),
    # chorus counts and "let's find out"
    *row_numbers([9.6, 10.0, 10.3], 150, 12.8),
    *row_numbers([17.0, 17.4, 18.1], 150, 18.3),
    Text("Let's find out!", 960, 150, 130, 18.3, 20.9, fill=YELLOW),
    *row_numbers([34.6, 35.0, 35.1], 150, 37.6),
    *row_numbers([41.9, 42.3, 42.8], 150, 43.2),
    Text("Let's find out!", 960, 150, 130, 43.2, 45.8, fill=YELLOW),
    *row_numbers([90.5, 90.8, 90.9], 150, 93.6),
    *row_numbers([97.8, 97.9, 98.9], 150, 99.3),
    Text("Let's find out!", 960, 150, 130, 99.3, 102.2, fill=YELLOW),
    # verses: big number top right plus a growing row of lily pads
    LilyPads([21.0, 23.2, 25.3, 27.3, 29.1], 33.6),
    *[big_number(i + 1, a, b) for i, (a, b) in enumerate([(21.0, 23.2), (23.2, 25.3), (25.3, 27.3), (27.3, 29.1), (29.1, 33.6)])],
    Text("Hop, hop, hop!", 760, 160, 110, 22.3, 23.2, fill="white", stroke=GREEN),
    Text("Splash!", 760, 160, 130, 26.4, 27.3, fill="white", stroke="#3A8FD8", wobble=True),
    Text("Hooray!", 760, 160, 140, 31.7, 33.6, fill=YELLOW, stroke=PINK, wobble=True),
    Window(LilyPads([45.8] * 5 + [45.8, 49.9, 54.0, 57.8, 62.6], 69.0, size=78), 45.8, 69.0),
    *[big_number(i + 6, a, b) for i, (a, b) in enumerate([(45.8, 49.9), (49.9, 54.0), (54.0, 57.8), (57.8, 62.6), (62.6, 69.0)])],
    Text("Bzzz!", 760, 160, 130, 48.0, 49.8, fill=YELLOW, stroke=ORANGE, wobble=True),
    Text("Way up high!", 760, 160, 110, 52.1, 53.9, fill="white", stroke=PINK),
    Text("Wait!", 760, 160, 150, 56.2, 57.6, fill=YELLOW, stroke=ORANGE, wobble=True),
    Text("Hip, hip, hooray!", 760, 160, 110, 63.7, 66.4, fill=YELLOW, stroke=PINK, wobble=True),
    # bridge: count to ten together, then count Poppy's 7 spots
    Text("Nice and loud!", 960, 150, 130, 70.6, 72.8, fill=YELLOW, stroke=ORANGE, wobble=True),
    *row_numbers([73.0, 73.3, 73.9, 74.3, 74.7, 75.0, 75.7, 76.2, 76.4, 76.7], 980, 76.8, size=110, stroke=ORANGE),
    Text("How many spots?", 960, 150, 120, 77.5, 81.0, fill=YELLOW, stroke=PINK),
    *row_numbers([81.1, 81.9, 82.4, 82.7, 83.2, 83.7, 84.2], 150, 84.6, size=130),
    Text("7 spots!", 960, 160, 170, 84.7, 89.5, fill=YELLOW, stroke=PINK, wobble=True),
    # outro
    Text("You're a super counter!", 960, 150, 115, 102.5, fill=YELLOW, stroke=PINK),
    Window(Emoji("⭐", 1590, 150, 120, 102.8), 102.8, DUR + 1),
    Fade(105.6, DUR),
]


def frame(tl, t):
    seg = next(s for s in SEGMENTS if s[0] <= t < s[1])
    t0, t1, n, off = seg[:4]
    fr = tl.frames(n)
    if len(seg) > 4:  # ping-pong between two points of the clip (holds a moment longer)
        a, b = seg[4]
        span = b - a
        k = ((t - t0) * 0.8) % (2 * span)
        src = a + (k if k < span else 2 * span - k)
        idx = int(src * assemble.CLIP_FPS)
    else:
        avail = len(fr) / assemble.CLIP_FPS - off
        rate = min(1.0, avail / (t1 - t0))
        idx = int((off + (t - t0) * rate) * assemble.CLIP_FPS)
    img = Image.fromarray(fr[min(idx, len(fr) - 1)]).resize((W, H), Image.BICUBIC).convert("RGBA")
    for layer in LAYERS:
        layer.draw(img, t, t0)
    return img.convert("RGB")


def main():
    tl = Timeline()
    if sys.argv[1] == "stills":
        for ts in sorted(float(x) for x in sys.argv[3:]):
            frame(tl, ts).save(f"{sys.argv[2]}/f_{ts:06.2f}.jpg", quality=85)
        return
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    p = subprocess.Popen([ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", SONG2, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                          "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                          "-af", "afade=t=out:st=103.6:d=1.2,apad", "-t", str(DUR), "-movflags", "+faststart", sys.argv[2]], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(tl, i / FPS).tobytes())
        if i % (FPS * 10) == 0:
            print(f"{i / FPS:5.0f}s / {DUR:.0f}s", flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()
