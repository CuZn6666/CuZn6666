#!/usr/bin/env python3
"""Check the shipped profile assets; optionally check public links with --online."""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
import re
import statistics
import urllib.request

from PIL import Image, ImageChops, ImageStat
from generate_cyber_snow import Scene

ROOT = Path(__file__).resolve().parents[1]


class ImagePaths(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img":
            assert attrs.get("alt"), "Images need meaningful alt text"
            self.paths.append(attrs["src"])
        if tag == "a" and attrs.get("href", "").startswith("assets/"):
            self.paths.append(attrs["href"])


def check_url(url):
    request = urllib.request.Request(url, headers={"User-Agent": "cyber-snow-validation"})
    with urllib.request.urlopen(request, timeout=25) as response:
        assert response.status == 200, (url, response.status)
        return f"HTTP {response.status}: {url}"


def main(online=False):
    readme = (ROOT/"README.md").read_text()
    parser = ImagePaths()
    parser.feed(readme)
    paths = parser.paths + re.findall(r"\]\((assets/[^)]+)\)", readme)
    for path in paths:
        assert (ROOT/path).is_file(), f"Missing asset: {path}"
    assert not re.search(r"<(script|iframe|style)\b", readme, re.I)
    for path in (ROOT/"scripts").glob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    gif_path = ROOT/"assets/cyber-snow.gif"
    gif = Image.open(gif_path)
    assert gif.info.get("loop") == 0, "GIF must loop forever"
    assert gif.size == (1000, 320)
    assert gif_path.stat().st_size < 5_000_000
    frames, delays = [], []
    for i in range(gif.n_frames):
        gif.seek(i)
        frames.append(gif.convert("RGB"))
        delays.append(gif.info["duration"])
    assert len(frames) > 1 and all(delay > 0 for delay in delays)
    changes = [sum(ImageStat.Stat(ImageChops.difference(frame, frames[(i+1) % len(frames)])).mean)/3
               for i, frame in enumerate(frames)]
    assert statistics.median(changes) > 0, "Animation must actually move"
    assert changes[-1] <= max(changes[:-1])*1.5, "Large discontinuity at the loop boundary"
    scene = Scene()
    assert ImageChops.difference(scene.render(0), scene.render(1)).getbbox() is None
    assert Image.open(ROOT/"assets/cyber-snow-preview.png").size == gif.size
    assert Image.open(ROOT/"assets/github-stats.png").size == (1000, 160)
    print(f"PASS: {len(frames)} frames, {sum(delays)} ms, infinite loop, {gif_path.stat().st_size:,} bytes")
    print(f"Frame differences: median={statistics.median(changes):.5f}; seam={changes[-1]:.5f}")
    print("PASS: local paths, Python syntax, static previews, periodic scene, no executable embeds")
    if online:
        urls = sorted(set(re.findall(r'https://[^\s)"<>]+', readme)))
        with ThreadPoolExecutor(max_workers=4) as pool:
            for result in pool.map(check_url, urls):
                print(result)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--online", action="store_true", help="Also check README HTTPS links")
    main(cli.parse_args().online)
