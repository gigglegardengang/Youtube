# The Garden ABC Song: Shot List

**Song:** `Song 4-The Garden ABC Song.mp3` in Google Drive `Songs/`
**New clips to make:** 7 (S4 Clips A–G). Everything else reuses existing clips (see `Song 4 - The Garden ABC Song.md`).
**Rendar settings for every clip:** Seedance 1.5 Pro · 16:9 · 720p · 5 sec · Audio Off · Private (110 tokens each)
**Estimated cost:** about 770 tokens, or about 990 with retries

⭐ = **library clip**, reused in future songs

## How each shot is made
1. **ChatGPT scene picture:** upload the listed files, then paste the scene prompt followed by the style lock below. Save it as `Scenes/Song 4/S4 Shot X ....png`.
2. **Rendar clip:** upload the scene picture as the **Start frame**, then paste the motion prompt followed by the motion lock below. Save it as `Videos/Clips/Song 4/S4 Clip X ....mp4`.

**Style lock** (add to the end of every scene prompt):
> Keep every character exactly the same as their reference sheet: same design, colors, face, eyes and proportions. Light the characters with the same warm golden sunlight as the background, with soft contact shadows under them so they truly stand in the scene. Pixar-style 3D render, wide 16:9 landscape image, no text, no letters, no extra characters.

**Motion lock** (add to the end of every motion prompt):
> Keep every character's design exactly the same. Smooth, bouncy Pixar-style 3D animation, gentle natural motion, flowers swaying softly. No new characters, no text.

**Reference sheets:** Lulu = `Characters/Lulu/Lulu Character Sheet.png` · Bo = `Characters/Bo/Bo Character Sheet.png` · Poppy = `Characters/Poppy/Adorable Ladybug Character Turnaround Sheet.png` · Sunny = `Characters/Sunny/Sunny Reference Sheet.png` · Zoom = `Characters/Zoom/Zoom Character Sheet.png`

**Letters:** the stepping stones are left blank on purpose. The giant letters, words and emojis are added later as on-screen graphics, so they're always spelled correctly.

---

## Making order (riskiest first)
1. **S4 Clip G** (all five friends together). If it loses consistency, we'll use Clip 04 or Clip 08 for the finale instead.
2. Then Clips A–F in order.

---

### S4 Clip A ⭐ Lulu starts the letter path (intro and the start of each verse)
- **Upload:** Lulu sheet, BG Garden Wide
- **Scene:** The pebble path through the garden is now a path of big, round, smooth, flat stepping stones, blank with no markings, leading into the flowers. Lulu the caterpillar rests on the first stepping stone in the foreground, smiling, eyes bright and just awake, a small pink flower by one antenna.
- **Motion:** Lulu stretches and gives a little yawn, smiles at the camera, then inches forward onto the next stepping stone, her body scrunching up and stretching out like a real inchworm. Slow camera follow.

### S4 Clip B ⭐ Lulu inching along the path, side view (between letters)
- **Upload:** Lulu sheet, BG Garden Wide
- **Scene:** Side view of Lulu mid-inch on the path of big, round, blank stepping stones, her middle segments arched up, flowers and grass behind her, happy face.
- **Motion:** Lulu inches from left to right across the stepping stones, segments bunching and stretching in a bouncy rhythm, antennae bobbing, smiling. The camera tracks sideways with her.

### S4 Clip C Lulu smells the flowers (D daisy, F flower, T tulip)
- **Upload:** Lulu sheet, BG Garden Wide
- **Scene:** Lulu beside a big white daisy and a pink tulip that are both taller than she is, at the edge of the stepping-stone path. She leans in to sniff the daisy with her eyes closed and a dreamy smile.
- **Motion:** Lulu sniffs the daisy and smiles dreamily, then turns and sniffs the tulip, giggling as a petal tickles her nose.

### S4 Clip D ⭐ Rainbow over the garden (R)
- **Upload:** BG Garden Wide
- **Scene:** Use this exact background with no characters at all, just after a gentle rain: glistening dewdrops on the leaves and petals, and a soft, bright rainbow arching across the sky.
- **Motion:** The rainbow glows brighter and shimmers across the sky, dewdrops twinkle, flowers sway, and the camera slowly tilts up toward the rainbow.

### S4 Clip E ⭐ Lulu under a mushroom umbrella (U)
- **Upload:** Lulu sheet, BG Leaf Bed
- **Scene:** Lulu sheltering under a small red-and-white spotted mushroom like an umbrella, gentle light rain falling around her, a cozy happy smile.
- **Motion:** Gentle raindrops fall and bounce off the mushroom cap. Lulu peeks out, holds out a tiny hand to catch a raindrop, and giggles.

### S4 Clip F Bo flies a leaf kite (K)
- **Upload:** Bo sheet, BG Garden Wide
- **Scene:** Bo flying in the sunny sky above the garden, holding the string of a small kite made from a bright green leaf, smiling proudly.
- **Motion:** Bo flies in a happy, wobbly loop pulling his leaf kite, which flutters and dances in the breeze behind him. His little wings buzz fast.

### S4 Clip G Everyone cheers at the end of the path (Z and the big finish)
- **Upload:** Lulu, Poppy, Bo, Zoom and Sunny sheets, BG Garden Wide
- **Scene:** At the end of the stepping-stone path, Lulu is on the last stone in front. Behind her, left to right: Poppy cheering, Bo hovering with arms up, Zoom giving a thumbs up, and Sunny standing tall at the back. Everyone faces the camera with big happy smiles. Sunny is about four times taller than Poppy.
- **Motion:** Everyone cheers and bounces happily. Bo buzzes in a little circle, Sunny sways, Zoom pumps his tiny fist, and Lulu does a happy wiggle.

---

## Assembly (Claude)
The clips get cut to the song using measured lyric timing (`Tools/find_lyric_timing.py`), plus the title, a giant letter stone, the word and an emoji for every letter, the alphabet chant graphics in the bridge, and the fade ending. Then a thumbnail, Shorts and the upload card.
