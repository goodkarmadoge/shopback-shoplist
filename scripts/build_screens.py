#!/usr/bin/env python3
"""Turn the design/*.dc.html screens into screens.js for the web prototype.

Each screen keeps its markup (the <x-dc> body, minus <helmet>) and its logic
script. Image URLs from the design canvas are mapped to local illustrations.
Run from the repo root:  python3 scripts/build_screens.py
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DESIGN = ROOT / "design"

IMAGES = {
    "/_blob/562337d77cd1e2c0b7e58fed67bc2a8e": "img/soundbar.svg",
    "/_blob/7199813906b95561fcfa8d0beed0ae10": "img/lamp.svg",
    "/_blob/ffeba48b103ae978b1782d7c30b28d51": "img/dogfood.svg",
    "/_blob/7afbdf3afe27ab0c2f3bdb965cc3a40b": "img/bathmat.svg",
}

canvas = json.loads((DESIGN / "canvas.json").read_text())
boards = canvas["boards"]

screens = {}
for path in sorted(DESIGN.glob("*.dc.html")):
    src = path.read_text()
    for blob, local in IMAGES.items():
        src = src.replace(blob, local)
    body = re.search(r"<x-dc>(.*)</x-dc>", src, re.S).group(1)
    body = re.sub(r"<helmet>.*?</helmet>", "", body, flags=re.S).strip()
    script = re.search(r"data-dc-script[^>]*>(.*?)</script>", src, re.S).group(1)
    title = re.search(r"<title>(.*?)</title>", src, re.S).group(1)
    name = path.name.replace(".dc.html", "")
    b = boards.get(path.name, {})
    screens[name] = {
        "title": b.get("title", title),
        "w": b.get("w", 390),
        "h": b.get("h", 844),
        "html": body,
        "script": script,
    }

out = ROOT / "screens.js"
out.write_text("window.SCREENS = " + json.dumps(screens, ensure_ascii=False) + ";\n")
print(f"wrote {out.name}: {len(screens)} screens")
