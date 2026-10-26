# Project status

A snapshot of where Giggle Garden Gang stands, so any new work session can pick up from here.

**Channel:** https://www.youtube.com/@GiggleGardenGang. Nursery rhyme and sing-along songs for preschoolers.
**Characters:** Sunny (sunflower), Poppy (ladybug), Bo (bee), Zoom (snail), Lulu (caterpillar).
**Workflow so far:** songs made in Suno → still scenes made in ChatGPT → animated clips made in Rendar →
the Python scripts in `Tools/` cut the clips to the song and add sing-along text, then make Shorts, thumbnails and channel art.

## The launch videos

| # | Song | Lyrics / plan | Song audio | Clips | Finished video |
| --- | --- | --- | --- | --- | --- |
| 1 | Welcome to the Giggle Garden (theme song) | lyrics in `published/video-1-...md` | missing | Clips 01–22, in Drive | in Drive |
| 2 | Poppy's Counting Spots | `Songs/Song 2 - Poppy's Counting Spots.md` | in `Songs/` | S2 Clips A–E, in Drive | in Drive |
| 3 | The Wiggle Wiggle Garden Dance | `Songs/Song 3 - The Wiggle Wiggle Garden Dance.md` | in `Songs/` | S3 Clips P1, B1, Z1, Z2, L1, G1, in Drive | in Drive |

Eight finished Shorts are in Drive: 1 Zoom vs Lulu Race, 2 Breathe with Bo, 3 Garden Dance Along, 4 Hop and Count with Poppy,
5 How Many Spots, 6 Freeze Dance with Poppy, 7 Freeze Dance with Bo, 8 Slow and Fast with Zoom.

## Google Drive
Video files live in Drive, not GitHub: `Giggle Garden Gang/Videos/`
- Finished videos 1–3, plus an old example version of video 1
- `Clips/` (Clips 01–22), `Clips/Song 2/`, `Clips/Song 3/`, `Clips/Old versions/`
- `Shorts/` (Shorts 1–8) and `Shorts/Old letterbox versions/`
- The `._` files are leftover Mac junk files (4 KB each) and can be deleted.

## In the repo
- Character poses: `Sunny/`, `Poppy/`, `Bo/`, `Zoom/`, `Lulu/`
- `Backgrounds/` (8), `Channel Art/` (banner, logos, profile icons)
- Song 2 and 3 audio and plans in `Songs/`
- Video-making scripts in `Tools/`

## Still missing
- [x] Bo's character images
- [ ] **Theme song** audio (`Welcome to the Giggle Garden.mp3`) and its Suno settings (lyrics are in `published/`)
- [ ] **Scenes** (the ChatGPT still images used for clips and FREEZE poses, `Scenes/`): not in Drive or the repo yet
- [x] Rendar clips, finished videos and Shorts (in Drive)
- [ ] **Thumbnails** (`Thumbnail 1/2/3 ... .png`)
- [x] YouTube links for videos 1–3, plus titles, descriptions, tags and settings (`published/`)
- [ ] Confirm whether videos 1–3 are public, scheduled or unlisted; Shorts 1–8 not posted yet

## Notes on the scripts
- They point at files on the old Mac (`/Users/ladywealthwarrior/Kids Channel/...`) and Mac fonts, so they need updating to run from this repo.
- Some were renamed during the move, but they still import each other by their old names:
  `render.py` (also copied as `render_theme_song.py`), `assemble.py` → `assemble_pixar_video.py`,
  `assemble2.py` → `assemble_song2.py`, `assemble3.py` → `assemble_song3.py`, `vshorts.py` → `make_shorts_fullscreen.py`.

## Trello board
https://trello.com/b/0Y2ObkVM is the working board. Its contents are copied here:
- `published/`: upload details and YouTube links for videos 1–3
- `plan/shorts.md`: Shorts 1–8, posting order, titles and descriptions
- `plan/content-calendar.md`: the 60-day plan (Mon learning song, Wed habits/feelings, Fri fun or compilation)
- `plan/characters.md`: ChatGPT prompts for each character
- `plan/channel-keywords.md`
Next up on the calendar: **W1 Mon: The Garden ABC Song (Lulu)**.
