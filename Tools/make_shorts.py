"""Cut vertical YouTube Shorts (1080x1920) from the finished theme song video."""
import os, subprocess, sys
from PIL import Image, ImageFilter
import imageio_ffmpeg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import text_sprite, emoji_sprite, PINK, GREEN, ORANGE

SRC = "/Users/ladywealthwarrior/Kids Channel/Giggle Garden/Videos/Welcome to the Giggle Garden - Pixar.mp4"
OUT = "/Users/ladywealthwarrior/Kids Channel/Giggle Garden/Videos/Shorts/"
SW, SH = 1080, 1920
YELLOW = "#FFE14D"

SHORTS = [
    # file name, start, end, title lines, title stroke, emoji
    ("Short 1 - Zoom vs Lulu Race", 71.0, 82.5, ["Who's faster?", "Zoom or Lulu?"], ORANGE, "\U0001F40C"),
    ("Short 2 - Breathe with Bo", 60.5, 71.0, ["Feeling nervous?", "Breathe with Bo!"], GREEN, "\U0001F41D"),
    ("Short 3 - Garden Dance Along", 90.6, 113.1, ["Dance along!", "Jump, buzz, wiggle!"], PINK, "\U0001F3B6"),
]


def overlay_png(title, stroke, emoji, path):
    im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    y = 150
    for i, line in enumerate(title):
        spr = text_sprite(line, 104 if i == 0 else 92, YELLOW if i == 0 else "white", stroke)
        if spr.width > SW - 40:
            s = (SW - 40) / spr.width
            spr = spr.resize((int(spr.width * s), int(spr.height * s)), Image.LANCZOS)
        im.alpha_composite(spr, ((SW - spr.width) // 2, y))
        y += spr.height - 10
    e = emoji_sprite(emoji, 150)
    im.alpha_composite(e, ((SW - e.width) // 2, y + 10))
    logo = text_sprite("Giggle Garden", 110, YELLOW, PINK)
    sun = emoji_sprite("\U0001F33B", 110)
    total = logo.width + sun.width + 10
    x0 = (SW - total) // 2
    im.alpha_composite(logo, (x0, SH - 330))
    im.alpha_composite(sun, (x0 + logo.width + 10, SH - 330 + (logo.height - sun.height) // 2))
    sub = text_sprite("New songs every week!", 64, "white", PINK)
    im.alpha_composite(sub, ((SW - sub.width) // 2, SH - 200))
    im.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    tmp = os.path.dirname(os.path.abspath(__file__))
    for name, a, b, title, stroke, emoji in SHORTS:
        png = f"{tmp}/{name}.png"
        overlay_png(title, stroke, emoji, png)
        d = b - a
        fc = ("[0:v]split[a][b];"
              f"[a]scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH},boxblur=24:2,"
              "eq=brightness=-0.12:saturation=1.1[bg];"
              f"[b]scale={SW}:-2[fg];"
              "[bg][fg]overlay=0:(H-h)/2-40[v1];"
              "[v1][1:v]overlay=0:0,"
              f"fade=t=in:st=0:d=0.3,fade=t=out:st={d - 0.5:.2f}:d=0.5[v];"
              f"[0:a]afade=t=in:st=0:d=0.3,afade=t=out:st={d - 0.6:.2f}:d=0.6[aout]")
        cmd = [ff, "-v", "error", "-y", "-ss", f"{a}", "-t", f"{d}", "-i", SRC, "-i", png,
               "-filter_complex", fc, "-map", "[v]", "-map", "[aout]", "-c:v", "libx264", "-crf", "19",
               "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k",
               "-movflags", "+faststart", f"{OUT}{name}.mp4"]
        subprocess.run(cmd, check=True)
        print("made", name, f"{d:.1f}s")


if __name__ == "__main__":
    main()
