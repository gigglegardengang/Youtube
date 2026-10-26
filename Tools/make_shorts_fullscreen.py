"""Full-screen 9:16 YouTube Shorts: crop each Rendar clip vertically and pan to follow the characters.

Usage:
  python vshorts.py stills OUTDIR
  python vshorts.py video
"""
import os, subprocess, sys
from PIL import Image
import imageio_ffmpeg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
from render import Text, text_sprite, emoji_sprite, ease, PINK, GREEN, ORANGE, SONG
import assemble
from assemble import SEGMENTS, Timeline

VW, VH = 1080, 1920
render.W, render.H = VW, VH  # overlays draw on the vertical canvas
OUT = "/Users/ladywealthwarrior/Kids Channel/Giggle Garden/Videos/Shorts/"
YELLOW = "#FFE14D"

# Where to centre the 9:16 window in each clip: (time within clip, x as a fraction of width)
PAN = {
    8: [(0, 0.42)],
    12: [(0.2, 0.30), (1.5, 0.45), (3.0, 0.34), (4.8, 0.55)],
    13: [(0, 0.44)],
    14: [(0.2, 0.38), (1.5, 0.42), (3.0, 0.45)],
    15: [(0, 0.50)],
    18: [(0.2, 0.45), (1.5, 0.50), (4.8, 0.55)],
    19: [(0.2, 0.45), (1.5, 0.42), (3.0, 0.48), (4.8, 0.55)],
    20: [(0, 0.46)],
    21: [(0.2, 0.60), (1.5, 0.55), (3.0, 0.50)],
    22: [(0.2, 0.37), (1.5, 0.42), (3.0, 0.50), (4.8, 0.58)],
}

SHORTS = [
    ("Short 1 - Zoom vs Lulu Race", 71.0, 82.5, ["Who's faster?", "Zoom or Lulu?"], ORANGE, [
        Text("ZOOM!", 540, 1380, 190, 77.3, 80.7, fill=YELLOW, stroke=ORANGE, wobble=True),
        Text("Go, Zoom, go!", 540, 1380, 120, 80.8, 82.5, fill=YELLOW, stroke=ORANGE),
    ]),
    ("Short 2 - Breathe with Bo", 60.5, 71.0, ["Feeling nervous?", "Breathe with Bo!"], GREEN, [
        Text("Breathe in...", 540, 1380, 110, 67.9, 68.4, fill="white", stroke=GREEN),
        Text("Breathe out...", 540, 1380, 110, 68.4, 69.8, fill="white", stroke=GREEN),
        Text("I can try!", 540, 1380, 130, 70.2, 71.0, fill=YELLOW),
    ]),
    ("Short 3 - Garden Dance Along", 90.6, 113.1, ["Dance along!", "Jump, buzz, wiggle!"], PINK, [
        Text("JUMP!", 540, 1380, 190, 93.1, 94.6, fill=YELLOW, stroke=PINK, wobble=True),
        Text("BZZZ!", 540, 1380, 190, 97.4, 98.8, fill=YELLOW, stroke=ORANGE, wobble=True),
        Text("WIGGLE!", 540, 1380, 170, 101.4, 103.1, fill=YELLOW, stroke=GREEN, wobble=True),
        Text("SWAY!", 540, 1380, 190, 104.4, 106.9, fill=YELLOW, stroke=PINK, wobble=True),
        Text("s l o o o w l y", 540, 1380, 110, 110.4, 113.1, fill="white", stroke=GREEN),
    ]),
]


def pan_x(n, ct):
    keys = PAN[n]
    if ct <= keys[0][0]:
        return keys[0][1]
    for (ta, xa), (tb, xb) in zip(keys, keys[1:]):
        if ta <= ct < tb:
            return xa + (xb - xa) * ease((ct - ta) / (tb - ta))
    return keys[-1][1]


def header(title, stroke):
    im = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    y = 130
    for i, line in enumerate(title):
        spr = text_sprite(line, 104 if i == 0 else 88, YELLOW if i == 0 else "white", stroke)
        if spr.width > VW - 40:
            s = (VW - 40) / spr.width
            spr = spr.resize((int(spr.width * s), int(spr.height * s)), Image.LANCZOS)
        im.alpha_composite(spr, ((VW - spr.width) // 2, y))
        y += spr.height - 12
    logo = text_sprite("Giggle Garden", 64, YELLOW, PINK)
    sun = emoji_sprite("\U0001F33B", 64)
    x0 = (VW - logo.width - sun.width - 6) // 2
    im.alpha_composite(logo, (x0, y + 6))
    im.alpha_composite(sun, (x0 + logo.width + 6, y + 6 + (logo.height - sun.height) // 2))
    return im


class Vertical:
    def __init__(self):
        self.tl = Timeline()

    def frame(self, t, head, layers):
        t0, t1, n, off = next(s for s in SEGMENTS if s[0] <= t < s[1])
        fr = self.tl.frames(n)
        avail = len(fr) / assemble.CLIP_FPS - off
        rate = min(1.0, avail / (t1 - t0))
        ct = off + (t - t0) * rate
        src = Image.fromarray(fr[min(int(ct * assemble.CLIP_FPS), len(fr) - 1)])
        cw = src.height * VW / VH
        x0 = min(max(pan_x(n, ct) * src.width - cw / 2, 0), src.width - cw)
        img = src.resize((VW, VH), Image.BICUBIC, box=(x0, 0, x0 + cw, src.height)).convert("RGBA")
        img.alpha_composite(head)
        for layer in layers:
            layer.draw(img, t, t0)
        return img.convert("RGB")


def main():
    v = Vertical()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    if sys.argv[1] == "stills":
        out = sys.argv[2]
        for name, a, b, title, stroke, layers in SHORTS:
            head = header(title, stroke)
            for k in range(5):
                t = a + (b - a) * (k + 0.5) / 5
                v.frame(t, head, layers).resize((270, 480)).save(f"{out}/{name[:7]}_{k}.jpg", quality=85)
        return
    os.makedirs(OUT, exist_ok=True)
    for name, a, b, title, stroke, layers in SHORTS:
        head = header(title, stroke)
        d = b - a
        p = subprocess.Popen([ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
                              "-r", "30", "-i", "-", "-ss", f"{a}", "-t", f"{d}", "-i", SONG,
                              "-filter_complex",
                              f"[0:v]fade=t=in:st=0:d=0.3,fade=t=out:st={d - 0.5:.2f}:d=0.5[v];"
                              f"[1:a]afade=t=in:st=0:d=0.3,afade=t=out:st={d - 0.6:.2f}:d=0.6[aa]",
                              "-map", "[v]", "-map", "[aa]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                              "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                              "-movflags", "+faststart", f"{OUT}{name}.mp4"], stdin=subprocess.PIPE)
        for i in range(int(d * 30)):
            p.stdin.write(v.frame(a + i / 30, head, layers).tobytes())
        p.stdin.close()
        p.wait()
        print("made", name, f"{d:.1f}s", flush=True)


if __name__ == "__main__":
    main()
