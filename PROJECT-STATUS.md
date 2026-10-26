# Project status

A snapshot of where Giggle Garden Gang stands, so any new work session can pick up from here.

**Channel:** https://www.youtube.com/@GiggleGardenGang. Nursery rhyme and sing-along songs for preschoolers.
**Characters:** Sunny (sunflower), Poppy (ladybug), Bo (bee), Zoom (snail), Lulu (caterpillar).
**Workflow so far:** songs made in Suno → still scenes made in ChatGPT → animated clips made in Rendar →
the Python scripts in `Tools/` cut the clips to the song and add sing-along text, then make Shorts, thumbnails and channel art.

## The launch videos

| # | Song | Lyrics / plan | Song audio | Clips | Finished video |
| --- | --- | --- | --- | --- | --- |
| 1 | Welcome to the Giggle Garden (theme song) | missing | missing | Clips 01–22, not in the repo | not in the repo |
| 2 | Poppy's Counting Spots | `Songs/Song 2 - Poppy's Counting Spots.md` | in `Songs/` | S2 Clips A–E, not in the repo | not in the repo |
| 3 | The Wiggle Wiggle Garden Dance | `Songs/Song 3 - The Wiggle Wiggle Garden Dance.md` | in `Songs/` | S3 Clips P1, B1, Z1, Z2, L1, G1, not in the repo | not in the repo |

The scripts also make three Shorts from video 1 (Zoom vs Lulu Race, Breathe with Bo, Garden Dance Along) and Shorts from videos 2 and 3.

## In the repo
- Character poses: `Sunny/`, `Poppy/`, `Zoom/`, `Lulu/`
- `Backgrounds/` (8), `Channel Art/` (banner, logos, profile icons)
- Song 2 and 3 audio and plans in `Songs/`
- Video-making scripts in `Tools/`

## Still missing
- [ ] **Bo's character images** (`Bo/` folder: e.g. "Bo Flying and Waving", "Bo Dancing V2", "Bo Huggable V2")
- [ ] **Theme song** audio (`Welcome to the Giggle Garden.mp3`) and its lyrics/plan
- [ ] **Scenes** (the ChatGPT still images used for clips and FREEZE poses, `Scenes/`), going to Google Drive
- [ ] **Rendar clips** (`Videos/Clips/`) and **finished videos and Shorts**, going to Google Drive
- [ ] **Thumbnails** (`Thumbnail 1/2/3 ... .png`)
- [ ] Which videos are already live on YouTube, and their titles, descriptions and links

## Notes on the scripts
- They point at files on the old Mac (`/Users/ladywealthwarrior/Kids Channel/...`) and Mac fonts, so they need updating to run from this repo.
- Some were renamed during the move, but they still import each other by their old names:
  `render.py` (also copied as `render_theme_song.py`), `assemble.py` → `assemble_pixar_video.py`,
  `assemble2.py` → `assemble_song2.py`, `assemble3.py` → `assemble_song3.py`, `vshorts.py` → `make_shorts_fullscreen.py`.
