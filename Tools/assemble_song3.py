"""Song 3: The Wiggle Wiggle Garden Dance, a freeze-dance cut to the Suno song.

Usage:
  python assemble3.py stills OUTDIR t1 t2 ...
  python assemble3.py video OUT.mp4
"""
import os, subprocess, sys
from PIL import Image
import imageio_ffmpeg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import W, H, FPS, Text, Emoji, Fade, PINK, GREEN, ORANGE, ease
import assemble
from assemble import Timeline, Window, Caption

G = "/Users/ladywealthwarrior/Kids Channel/Giggle Garden/"
SONG3 = G + "Songs/The Wiggle Wiggle Garden Song.mp3"
SONG_END = 121.92
DUR = 123.6
YELLOW, ICE = "#FFE14D", "#3A8FD8"
S3 = G + "Videos/Clips/Song 3/"
assemble.NAMES.update({
    201: S3 + "S3 Clip P1 Poppy One Foot.mp4",
    202: S3 + "S3 Clip B1 Bo Flaps.mp4",
    203: S3 + "S3 Clip Z1 Zoom Slow.mp4",
    204: S3 + "S3 Clip Z2 Zoom Fast.mp4",
    205: S3 + "S3 Clip L1 Lulu Wiggle.mp4",
    206: S3 + "S3 Clip G1 Group Dance Party.mp4",
})
P1, B1, Z1, Z2, L1, G1 = 201, 202, 203, 204, 205, 206
HOLD = "hold"

# (start, end, clip, offset) or (start, end, clip, HOLD, frozen time in clip)
SEGMENTS = [
    (0.0, 4.5, 3, 0.0), (4.5, 7.6, 4, 0.0),
    # chorus 1
    (7.6, 11.6, 5, 0.0), (11.6, 15.6, 6, 0.0), (15.6, 19.8, 7, 0.6),
    # Poppy: hop on one foot, FREEZE
    (19.8, 24.0, P1, 0.0), (24.0, 28.0, 18, 0.5), (28.0, 30.6, 18, HOLD, 4.5), (30.6, 32.2, 5, 2.0),
    # Bo: flap and buzz, FREEZE
    (32.2, 36.2, B1, 0.0), (36.2, 40.4, 19, 0.3), (40.4, 43.2, B1, HOLD, 2.6), (43.2, 44.7, 6, 2.5),
    # chorus 2
    (44.7, 48.7, 5, 0.8), (48.7, 52.8, 8, 0.0), (52.8, 57.0, 7, 0.4),
    # Zoom: slow, then fast, FREEZE
    (57.0, 61.0, Z1, 0.0), (61.0, 65.0, Z2, 0.0), (65.0, 67.9, Z2, HOLD, 4.0), (67.9, 69.4, 8, 2.5),
    # Lulu and Sunny
    (69.4, 73.6, L1, 0.0), (73.6, 77.8, 20, 0.5), (77.8, 81.8, 9, 0.8), (81.8, 86.0, 21, 0.5),
    # bridge: all together, quick cuts, FREEZE
    (86.0, 88.1, G1, 0.0), (88.1, 89.0, 18, 1.0), (89.0, 90.1, 19, 1.0), (90.1, 91.2, 20, 1.0),
    (91.2, 92.3, 21, 1.0), (92.3, 94.2, 22, 1.0), (94.2, 96.1, Z2, 1.5), (96.1, 99.4, G1, HOLD, 2.5),
    (99.4, 100.6, G1, 2.6),
    # final chorus
    (100.6, 104.6, G1, 0.0), (104.6, 108.6, 6, 0.5), (108.6, 112.9, 7, 0.0),
    # outro
    (112.9, 117.5, 4, 0.0), (117.5, DUR + 1, 3, 0.5),
]


def freeze(t0, go):
    return [
        Text("FREEZE!", 960, 900, 200, t0, go, fill="white", stroke=ICE),
        Text("Hold it...", 960, 1020, 80, t0 + 1.5, go, fill="white", stroke=ICE),
        Text("GO!", 960, 900, 200, go, go + 1.2, fill=YELLOW, stroke=GREEN, wobble=True),
    ]


def chorus(lines, hee):
    words = ["Wiggle, wiggle, shake it out!", "Spin around and jump and shout!",
             "Do the Giggle Garden Dance,", "Wiggle like you've got ants in your pants!"]
    return [Caption(w, a, b) for w, (a, b) in zip(words, lines)] + [
        Text("Hee hee hee!", 960, 150, 130, hee, hee + 1.8, fill=YELLOW, stroke=PINK, wobble=True)]


def word(txt, t0, t1, stroke=PINK, size=170):
    return Text(txt, 960, 160, size, t0, t1, fill=YELLOW, stroke=stroke, wobble=True)


LAYERS = [
    Window(Text("The Wiggle Wiggle Garden Dance", 960, 140, 105, 0.3, fill=YELLOW, stroke=PINK), 0.3, 4.5),
    Text("Yeah!", 960, 150, 160, 4.6, 6.5, fill=YELLOW, stroke=PINK, wobble=True),
    *chorus([(7.7, 9.6), (9.6, 11.6), (11.7, 13.6), (13.7, 15.9)], 18.0),
    *chorus([(44.8, 46.6), (46.7, 48.6), (48.8, 50.8), (50.9, 53.0)], 55.2),
    *chorus([(100.6, 102.4), (102.5, 104.4), (104.5, 106.4), (106.5, 108.7)], 110.9),
    # Poppy
    Caption("Poppy says: Hop on one foot!", 20.0, 22.0),
    word("HOP!", 22.1, 23.6), Caption("Now the other foot!", 23.7, 25.8), word("HOP!", 26.3, 27.9),
    *freeze(28.0, 30.6),
    # Bo
    Caption("Bo says: Flap your arms and buzz!", 32.3, 34.4),
    word("BUZZ!", 34.5, 36.1, ORANGE), Caption("Flap them fast!", 36.2, 38.5), word("BUZZ!", 38.6, 40.3, ORANGE),
    *freeze(40.4, 43.2),
    # Zoom
    Caption("Zoom says: Dance real slow!", 57.1, 58.9),
    Text("s l o o o w . . .", 960, 160, 130, 59.0, 60.9, fill="white", stroke=GREEN),
    Caption("Now dance super fast!", 60.9, 63.3), word("FAST!", 63.4, 65.0, ORANGE, 190),
    *freeze(65.0, 67.9),
    # Lulu
    Caption("Lulu says: Wiggle head to toe!", 69.5, 71.5),
    Caption("Wiggle your head!", 71.6, 72.6), Caption("Wiggle your nose!", 72.6, 73.6),
    Caption("Wiggle your tummy!", 73.6, 74.7), Caption("Wiggle your toes!", 74.7, 76.6),
    # Sunny
    Caption("Sunny says: Stretch up tall!", 77.9, 79.7),
    word("STRETCH!", 79.8, 81.8), Caption("Sway to the left...", 81.9, 82.9), Caption("...sway to the right!", 82.9, 84.0),
    # bridge
    Caption("Now let's do it all together!", 86.2, 88.1),
    word("HOP!", 88.2, 89.0), word("BUZZ!", 89.0, 90.1, ORANGE), word("WIGGLE!", 90.2, 91.2, GREEN),
    word("STRETCH!", 91.3, 92.3), Text("s l o o o w . . .", 960, 160, 130, 92.4, 94.2, fill="white", stroke=GREEN),
    word("FAST!", 94.3, 96.1, ORANGE, 190),
    *freeze(96.2, 99.4),
    # outro
    Text("Great dancing!", 960, 150, 140, 113.1, 116.6, fill=YELLOW, stroke=PINK, wobble=True),
    Caption("See you in the garden!", 115.4, 116.6),
    Text("Bye-bye!", 960, 150, 150, 116.7, fill=YELLOW, stroke=PINK, wobble=True),
    Window(Emoji("\U0001F44B", 1330, 150, 130, 116.8), 116.8, DUR + 1),
    Fade(122.0, DUR),
]

_ICE_TINT = Image.new("RGB", (W, H), (205, 230, 255))


def frame(tl, t):
    seg = next(s for s in SEGMENTS if s[0] <= t < s[1])
    t0, t1, n = seg[:3]
    fr = tl.frames(n)
    if seg[3] == HOLD:  # freeze-frame: hold one moment, slowly push in, cool icy tint
        idx = int(seg[4] * assemble.CLIP_FPS)
        img = Image.fromarray(fr[min(idx, len(fr) - 1)])
        z = 1.0 + 0.06 * ease((t - t0) / (t1 - t0))
        w, h = img.width / z, img.height / z
        x0, y0 = (img.width - w) / 2, (img.height - h) / 2
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
        img = Image.blend(img, _ICE_TINT, 0.18 * min(1.0, (t - t0) / 0.15))
    else:
        off = seg[3]
        avail = len(fr) / assemble.CLIP_FPS - off
        rate = min(1.0, avail / (t1 - t0))
        idx = int((off + (t - t0) * rate) * assemble.CLIP_FPS)
        img = Image.fromarray(fr[min(idx, len(fr) - 1)]).resize((W, H), Image.BICUBIC)
    img = img.convert("RGBA")
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
                          "-r", str(FPS), "-i", "-", "-i", SONG3, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                          "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                          "-af", f"afade=t=out:st={SONG_END - 1.0:.2f}:d=1.0,apad", "-t", str(DUR),
                          "-movflags", "+faststart", sys.argv[2]], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(tl, i / FPS).tobytes())
        if i % (FPS * 10) == 0:
            print(f"{i / FPS:5.0f}s / {DUR:.0f}s", flush=True)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()
