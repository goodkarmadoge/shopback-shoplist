#!/usr/bin/env python3
"""Build the ShopList tutorial video from frames/, narration.mp3 and its timestamps.

Shots are cut to the narration's actual timing and subtitles follow each spoken
phrase. Needs ffmpeg on the PATH (with libass, as standard builds have).
Run:  python build_video.py      ->  ShopList_tutorial.mp4 and ShopList_tutorial.srt
"""
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
FPS, XFADE, LEAD, TAIL, END_CARD = 30, 0.4, 0.3, 1.2, 2.6

# The five beats of the script and the frames shown during each one.
BEATS = [
    ("Planning", ["01"]),
    ("Type", ["02", "03"]),
    ("ShopList sorts", ["04", "05"]),
    ("Then", ["06", "07", "08"]),
    ("Your Cashback", ["09", "10"]),  # the end card (11) follows
]

ts = json.loads((HERE / "narration_timestamps.json").read_text(encoding="utf-8"))
al = ts["alignment"]
chars, starts, ends = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]

# Words with their spoken start and end times.
words, cur = [], None
for c, s, e in zip(chars, starts, ends):
    if c.isspace():
        if cur:
            words.append(cur)
            cur = None
        continue
    if cur is None:
        cur = {"w": c, "s": s, "e": e}
    else:
        cur["w"] += c
        cur["e"] = e
if cur:
    words.append(cur)
speech_end = words[-1]["e"]

# Where each beat starts in the audio.
beat_starts, wi = [], 0
for phrase, _ in BEATS:
    parts = phrase.split()
    while not all(re.sub(r"\W", "", words[wi + k]["w"]).lower() == p.lower() for k, p in enumerate(parts)):
        wi += 1
    beat_starts.append(0.0 if not beat_starts else words[wi]["s"] + LEAD)

total = speech_end + LEAD + TAIL
cut_points = beat_starts + [total - END_CARD]
shots = []  # (frame, duration)
for i, (_, frames) in enumerate(BEATS):
    span = cut_points[i + 1] - cut_points[i]
    for f in frames:
        shots.append((f, span / len(frames)))
shots.append(("11", END_CARD))

# Subtitle cues: break at sentence ends, at commas once a line has some length, and at ~34 characters.
cues, line = [], []
def flush():
    if line:
        cues.append([line[0]["s"] + LEAD, line[-1]["e"] + LEAD + 0.15, " ".join(w["w"] for w in line)])
        line.clear()
SMALL = {"a", "an", "the", "to", "for", "and", "or", "with", "of", "your", "it"}
def bare(w):
    return re.sub(r"\W", "", w["w"]).lower()
for w in words:
    if line and len(" ".join(x["w"] for x in line + [w])) > 36:
        carry = []
        while len(line) > 1 and bare(line[-1]) in SMALL:
            carry.insert(0, line.pop())
        flush()
        line.extend(carry)
    line.append(w)
    text = " ".join(x["w"] for x in line)
    if w["w"][-1] in ".?!:" or (w["w"][-1] == "," and len(text) >= 18):
        flush()
flush()
for a, b in zip(cues, cues[1:]):
    a[1] = min(a[1], b[0] - 0.02)

def ass_t(s):
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"
def srt_t(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"

ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter,54,&H00FFFFFF,&H00FFFFFF,&H00111111,&H22111111,1,0,0,0,100,100,0,0,3,18,0,2,90,90,110,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ass += "".join(f"Dialogue: 0,{ass_t(a)},{ass_t(b)},Sub,,0,0,0,,{t}\n" for a, b, t in cues)
(HERE / "subs.ass").write_text(ass, encoding="utf-8")
(HERE / "ShopList_tutorial.srt").write_text(
    "".join(f"{i}\n{srt_t(a)} --> {srt_t(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(cues, 1)), encoding="utf-8")

# Render: slow push-in on each frame, cross-fades, burned-in subtitles, narration mixed in.
args = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
for f, _ in shots:
    args += ["-i", f"frames/{f}.png"]
args += ["-i", "narration.mp3"]
fc = []
for i, (_, d) in enumerate(shots):
    n = int(round((d + (XFADE if i < len(shots) - 1 else 0)) * FPS))
    fc.append(f"[{i}:v]scale=2160:3840,zoompan=z='1+0.035*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={n}:s=1080x1920:fps={FPS},format=yuv420p,setsar=1[v{i}]")
prev, acc = "v0", 0.0
for i in range(1, len(shots)):
    acc += shots[i - 1][1]
    fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={XFADE}:offset={acc:.3f}[x{i}]")
    prev = f"x{i}"
fc.append(f"[{prev}]subtitles=subs.ass:fontsdir=fonts[outv]")
fc.append(f"[{len(shots)}:a]adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},apad[outa]")
args += ["-filter_complex", ";".join(fc), "-map", "[outv]", "-map", "[outa]", "-t", f"{total:.3f}",
         "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "ShopList_tutorial.mp4"]
subprocess.run(args, check=True, cwd=HERE)
print(f"Saved ShopList_tutorial.mp4 ({total:.1f} s) and ShopList_tutorial.srt")
