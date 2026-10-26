import json, sys
from faster_whisper import WhisperModel

audio, out = sys.argv[1], sys.argv[2]
model = WhisperModel("small.en", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    audio, word_timestamps=True, vad_filter=False, beam_size=5,
    initial_prompt="Good morning, Giggle Garden! Sunny, Poppy, Bo, Zoom the snail, Lulu the caterpillar.",
)
data = []
for s in segments:
    words = [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])]
    data.append({"s": round(s.start, 2), "e": round(s.end, 2), "text": s.text.strip(), "words": words})
    print(f"{s.start:6.2f}-{s.end:6.2f}  {s.text.strip()}")
json.dump(data, open(out, "w"), indent=1)
