"""Full-screen 9:16 Shorts from Video 2 (Poppy's Counting Spots) and Video 3 (Wiggle Wiggle Garden Dance).

Usage:
  python vshorts2.py stills OUTDIR
  python vshorts2.py video
"""
import os, subprocess, sys
from PIL import Image
import imageio_ffmpeg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vshorts  # sets render.W/H to the vertical canvas
from vshorts import VW, VH, OUT, header, pan_x, PAN
from render import Text, PINK, GREEN, ORANGE
import assemble
import assemble2
import assemble3

YELLOW, ICE = "#FFE14D", "#3A8FD8"
PAN.update({
    5: [(0, 0.42)], 6: [(0, 0.50)],
    101: [(0.2, 0.36), (1.5, 0.43), (3.0, 0.48)],
    102: [(0.2, 0.40), (1.5, 0.52), (3.0, 0.47), (4.8, 0.57)],
    103: [(0, 0.44)], 104: [(0, 0.44)],
    201: [(0.2, 0.45), (3.0, 0.48)], 202: [(0.2, 0.48), (1.5, 0.43), (4.8, 0.50)],
    203: [(0.2, 0.45), (3.0, 0.45), (4.8, 0.50)], 204: [(0.2, 0.45), (1.5, 0.43), (4.8, 0.50)],
})
_ICE = Image.new("RGB", (100, 100), (205, 230, 255))


def big(txt, t0, t1, stroke=PINK, size=170, fill=YELLOW):
    return Text(txt, 540, 1450, size, t0, t1, fill=fill, stroke=stroke, wobble=True)


def freeze(t0, go):
    return [Text("FREEZE!", 540, 1450, 190, t0, go, fill="white", stroke=ICE),
            Text("Hold it...", 540, 1600, 80, t0 + 1.5, go, fill="white", stroke=ICE),
            Text("GO!", 540, 1450, 200, go, go + 1.2, fill=YELLOW, stroke=GREEN, wobble=True)]


def count_row(times, y, t_end, size=120, stroke=PINK, per_row=5):
    out = []
    for i, tt in enumerate(times):
        row, col = divmod(i, per_row)
        n = min(per_row, len(times) - row * per_row)
        x = 540 + (col - (n - 1) / 2) * 190
        out.append(assemble.Window(Text(str(i + 1), x, y + row * 170, size, tt, fill=YELLOW, stroke=stroke), tt, t_end))
    return out


SHORTS = [
    ("Short 4 - Hop and Count with Poppy", assemble2, assemble2.SONG2, 20.9, 33.6,
     ["Hop & count!", "1, 2, 3, 4, 5!"], GREEN, [
         *[assemble.Window(Text(str(i + 1), 540, 1420, 300, a, fill=YELLOW, stroke=GREEN), a, b)
           for i, (a, b) in enumerate([(21.0, 23.2), (23.2, 25.3), (25.3, 27.3), (27.3, 29.1), (29.1, 31.6)])],
         big("Hooray!", 31.7, 33.6),
     ]),
    ("Short 5 - How Many Spots", assemble2, assemble2.SONG2, 76.8, 89.5,
     ["How many spots", "does Poppy have?"], PINK, [
         *count_row([81.1, 81.9, 82.4, 82.7, 83.2, 83.7, 84.2], 1380, 84.6, size=140, per_row=4),
         big("7 spots!", 84.7, 89.5, size=180),
     ]),
    ("Short 6 - Freeze Dance with Poppy", assemble3, assemble3.SONG3, 19.8, 31.4,
     ["Freeze dance!", "Hop with Poppy!"], ICE, [
         big("HOP!", 22.1, 23.6), big("Other foot!", 23.7, 26.2, GREEN, 120), big("HOP!", 26.3, 27.9),
         *freeze(28.0, 30.6),
     ]),
    ("Short 7 - Freeze Dance with Bo", assemble3, assemble3.SONG3, 32.2, 44.0,
     ["Freeze dance!", "Buzz with Bo!"], ICE, [
         big("BUZZ!", 34.5, 36.1, ORANGE), big("Flap fast!", 36.2, 38.5, GREEN, 130), big("BUZZ!", 38.6, 40.3, ORANGE),
         *freeze(40.4, 43.2),
     ]),
    ("Short 8 - Slow and Fast with Zoom", assemble3, assemble3.SONG3, 57.0, 68.8,
     ["Slow... or FAST?", "Dance with Zoom!"], ORANGE, [
         Text("s l o o o w . . .", 540, 1450, 110, 59.0, 60.9, fill="white", stroke=GREEN),
         big("FAST!", 63.4, 65.0, ORANGE, 200),
         *freeze(65.0, 67.9),
     ]),
]


class Vertical:
    def __init__(self):
        self.tl = assemble.Timeline()

    def frame(self, mod, t, head, layers):
        seg = next(s for s in mod.SEGMENTS if s[0] <= t < s[1])
        t0, t1, n = seg[:3]
        fr = self.tl.frames(n)
        held = False
        if seg[3] == "hold":
            ct, held = seg[4], True
        elif len(seg) > 4:  # ping-pong hold (Video 2 spot counting)
            a, b = seg[4]
            span = b - a
            k = ((t - t0) * 0.8) % (2 * span)
            ct = a + (k if k < span else 2 * span - k)
        else:
            off = seg[3]
            avail = len(fr) / assemble.CLIP_FPS - off
            ct = off + (t - t0) * min(1.0, avail / (t1 - t0))
        src = Image.fromarray(fr[min(int(ct * assemble.CLIP_FPS), len(fr) - 1)])
        cw = src.height * VW / VH
        x0 = min(max(pan_x(n, ct) * src.width - cw / 2, 0), src.width - cw)
        img = src.resize((VW, VH), Image.BICUBIC, box=(x0, 0, x0 + cw, src.height))
        if held:
            img = Image.blend(img, _ICE.resize((VW, VH)), 0.18)
        img = img.convert("RGBA")
        img.alpha_composite(head)
        for layer in layers:
            layer.draw(img, t, t0)
        return img.convert("RGB")


def main():
    v = Vertical()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    if sys.argv[1] == "stills":
        for name, mod, song, a, b, title, stroke, layers in SHORTS:
            head = header(title, stroke)
            for k in range(5):
                t = a + (b - a) * (k + 0.5) / 5
                v.frame(mod, t, head, layers).resize((270, 480)).save(f"{sys.argv[2]}/{name[:7]}_{k}.jpg", quality=85)
        return
    for name, mod, song, a, b, title, stroke, layers in SHORTS:
        head = header(title, stroke)
        d = b - a
        p = subprocess.Popen([ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
                              "-r", "30", "-i", "-", "-ss", f"{a}", "-t", f"{d}", "-i", song,
                              "-filter_complex",
                              f"[0:v]fade=t=in:st=0:d=0.3,fade=t=out:st={d - 0.5:.2f}:d=0.5[v];"
                              f"[1:a]afade=t=in:st=0:d=0.3,afade=t=out:st={d - 0.7:.2f}:d=0.7[aa]",
                              "-map", "[v]", "-map", "[aa]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                              "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                              "-movflags", "+faststart", f"{OUT}{name}.mp4"], stdin=subprocess.PIPE)
        for i in range(int(d * 30)):
            p.stdin.write(v.frame(mod, a + i / 30, head, layers).tobytes())
        p.stdin.close()
        p.wait()
        print("made", name, f"{d:.1f}s", flush=True)


if __name__ == "__main__":
    main()
