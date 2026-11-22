#!/usr/bin/env python3
"""Refresh local statistics from public GitHub data, without tokens or image services."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import urllib.request

from PIL import Image
from generate_cyber_snow import Canvas, COLORS, SCALE, font_path

ROOT = Path(__file__).resolve().parents[1]
USER = "CuZn6666"


def fetch(url):
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "cyber-snow-profile"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    repos, page = [], 1
    while True:
        batch = fetch(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    owned = [r for r in repos if r["owner"]["login"].lower() == USER.lower() and not r["private"]]
    projects = sum(not r["fork"] and r["name"].lower() != USER.lower() for r in owned)
    stars = sum(r["stargazers_count"] for r in owned)
    now = datetime.now(timezone.utc)
    data = {"username": USER, "retrieved_at": now.isoformat(),
            "source": f"https://api.github.com/users/{USER}/repos",
            "public_repositories": len(owned), "project_repositories": projects,
            "stars_on_owned_public_repositories": stars,
            "project_definition": "Owned public non-fork repositories, excluding the profile repository",
            "repositories": [{"name": r["name"], "stars": r["stargazers_count"],
                              "fork": r["fork"]} for r in owned]}
    image = Image.new("RGB", (1000*SCALE, 160*SCALE), COLORS["background"])
    c = Canvas(image, font_path(None), font_path(None, True))
    c.rect((1, 1, 999, 159), COLORS["terminal"], "#243444", 12)
    c.text((30, 21), "$ github / public snapshot", 12, COLORS["ice"])
    c.text((810, 21), now.strftime("%Y-%m-%d"), 12, COLORS["muted"])
    for i, (value, label) in enumerate(((len(owned), "PUBLIC REPOSITORIES"),
                                       (projects, "PROJECT REPOSITORIES"),
                                       (stars, "REPOSITORY STARS"))):
        x = 31+i*330
        if i:
            c.line([(x-25, 66), (x-25, 133)], "#223344")
        c.text((x, 66), f"{value:02d}", 36, COLORS["white"], mono=False)
        c.text((x, 119), label, 10, COLORS["muted"])
        c.rect((x, 145, x+34, 146), COLORS["cyan"])
    assets = ROOT/"assets"
    assets.mkdir(exist_ok=True)
    image.resize((1000, 160), Image.Resampling.LANCZOS).save(assets/"github-stats.png", optimize=True)
    (assets/"github-stats.json").write_text(json.dumps(data, indent=2)+"\n")
    readme = ROOT/"README.md"
    content = readme.read_text()
    alt = (f"GitHub public snapshot: {len(owned)} public repositories, {projects} project repositories "
           f"excluding this profile, and {stars} stars across owned public repositories. "
           f"Snapshot dated {now:%Y-%m-%d}.")
    content = re.sub(r"GitHub public snapshot:[^\]]+", alt, content)
    content = re.sub(r"Public repository snapshot · .*? · Stored locally;",
                     f"Public repository snapshot · {now:%d %B %Y} · Stored locally;", content)
    readme.write_text(content)
    print(f"Snapshot {now:%Y-%m-%d}: {len(owned)} public repos, {projects} project repos, {stars} stars")


if __name__ == "__main__":
    main()
