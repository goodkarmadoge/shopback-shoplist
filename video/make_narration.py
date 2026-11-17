#!/usr/bin/env python3
"""Generate the ShopList tutorial narration with ElevenLabs.

Reads the API key from the ELEVENLABS_API_KEY environment variable and writes
narration.mp3 and narration_timestamps.json next to this script.
Run:  python make_narration.py
"""
import base64
import json
import os
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
VOICE_ID = os.environ.get("SHOPLIST_VOICE_ID", "TkWPqputI7tf9YDFpxF3")  # "Derek - Test"
MODEL_ID = "eleven_multilingual_v2"

key = os.environ.get("ELEVENLABS_API_KEY")
if not key:
    sys.exit("Set ELEVENLABS_API_KEY first.")

text = " ".join((HERE / "narration.txt").read_text(encoding="utf-8").split())
body = json.dumps({
    "text": text,
    "model_id": MODEL_ID,
    "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True},
}).encode("utf-8")
req = urllib.request.Request(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps?output_format=mp3_44100_128",
    data=body,
    headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    data = json.loads(r.read().decode("utf-8"))

(HERE / "narration.mp3").write_bytes(base64.b64decode(data["audio_base64"]))
(HERE / "narration_timestamps.json").write_text(json.dumps({"text": text, "alignment": data["alignment"]}, indent=1), encoding="utf-8")
print("Saved narration.mp3 and narration_timestamps.json")
print(f"Spoken length: {data['alignment']['character_end_times_seconds'][-1]:.1f} s")
