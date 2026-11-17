# ShopList tutorial video kit

Everything needed to render the 45-second ShopList tutorial with Derek's ElevenLabs narration and burned-in subtitles.

| File | What it is |
| --- | --- |
| `frames/01.png`–`11.png` | The 9:16 shots, captured from the prototype (11 is the end card) |
| `narration.txt` | The voiceover script |
| `make_narration.py` | Calls ElevenLabs (voice "Derek - Test") and saves `narration.mp3` + `narration_timestamps.json` |
| `build_video.py` | Cuts the shots to the narration's real timing, writes subtitles, and renders `ShopList_tutorial.mp4` |
| `compose_frames.py` | How the frames were made, for reference (paths point at the original workspace) |
| `fonts/` | Inter Bold for the subtitles (SIL Open Font License) |

## Run it

Needs Python 3 and ffmpeg on the PATH.

```sh
cd video
# set your key in the shell first, never in a file you commit
#   macOS/Linux:   export ELEVENLABS_API_KEY=...
#   Windows (PowerShell):   $env:ELEVENLABS_API_KEY="..."
python make_narration.py
python build_video.py
```

Output: `ShopList_tutorial.mp4` (about 46 seconds, 1080×1920, narration + subtitles) and `ShopList_tutorial.srt`.

To try a different voice, set `SHOPLIST_VOICE_ID` before running `make_narration.py`.
