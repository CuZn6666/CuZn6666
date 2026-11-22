# Cyber Snow — profile maintenance

This profile is designed for `CuZn6666/CuZn6666`. The README uses GitHub Markdown, supported HTML, and local raster assets. No JavaScript, custom CSS, iframe, animated SVG, or external image service is required to display it.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | Public English profile |
| `assets/cyber-snow.gif` | 1000 × 320 animated terminal; 72 frames, 6 seconds, 12 FPS, infinite loop |
| `assets/cyber-snow-preview.png` | Static, full-color alternative |
| `assets/github-stats.png` | Matching local statistics card |
| `assets/github-stats.json` | Public statistics source, retrieval time, and metric definitions |
| `scripts/generate_cyber_snow.py` | Deterministic, offline Pillow renderer |
| `scripts/update_github_stats.py` | Explicit refresh from the public GitHub API; also updates README date and alt text |
| `scripts/validate_profile.py` | Asset, animation, syntax, and optional link checks |
| `scripts/requirements.txt` | Pinned Pillow dependency |
| `.gitignore` | Excludes the virtual environment, caches, and temporary previews |
| `docs/PROFILE_GUIDE.md` | This guide |

## Generate the animation

Run these commands from the profile repository. Python 3.10+ is required.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python scripts/generate_cyber_snow.py
.venv/bin/python scripts/validate_profile.py
```

Only dependency installation requires internet access. The animation renderer is entirely offline. On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`.

The renderer discovers installed macOS, Linux, or Windows fonts. This version was generated with Arial Bold and SF Mono on macOS. Font files are not redistributed. For Linux, install DejaVu Sans and DejaVu Sans Mono or supply your own licensed fonts:

```sh
.venv/bin/python scripts/generate_cyber_snow.py \
  --font /path/to/Bold.ttf \
  --mono-font /path/to/Mono.ttf
```

The same seed, settings, Pillow version, and fonts produce the same frames. Changing fonts can change text width; inspect the static preview after a font change.

## Adjust the design

```sh
# Fewer particles, slower travel, the same seamless six-second loop:
.venv/bin/python scripts/generate_cyber_snow.py \
  --particles 48 --speed 0.8 --seconds 6 --fps 12

# Alternate accent, with outputs kept separate for comparison:
.venv/bin/python scripts/generate_cyber_snow.py \
  --cyan '#38BDF8' --seed 42 --output .preview/variant
```

Edit `COLORS` for the full palette and `LAYERS` for depth-dependent sizes, opacity, and travel. Text and layout live in `Scene.make_base()`. `--speed` changes travel distance per cycle; increasing `--seconds` with the same speed makes the movement slower in real time.

Particles use deterministic random positions, individual drift, three depth layers, and a sine-squared birth/death envelope. Their wrap points are invisible. The cursor, stars, and code-text intensity are periodic. The final frame is followed by the first frame without duplicating an endpoint. Two-times supersampling keeps small details smooth; a shared 256-color palette with reserved cyan accents avoids color flicker, and GIF delta frames keep the file small. Frame delays alternate between 80 and 90 ms because GIF timing is quantized to centiseconds.

The shipped GIF is **251,464 bytes (about 0.24 MiB)**. All four image/data assets together are approximately 0.33 MiB. Recheck sizes after customization.

## Refresh statistics

```sh
.venv/bin/python scripts/update_github_stats.py
.venv/bin/python scripts/validate_profile.py --online
```

This command needs internet access and reads only public repository metadata. It uses no credentials. The public README loads the saved PNG; it does not contact the API or a third-party statistics server. No automated workflow or background refresh is configured.

Definitions: public repositories include this profile; project repositories exclude this profile and forks; repository stars are summed across owned public repositories. Counts are explicitly dated, not represented as live data or as measures of engineering skill.

## Content verification and editorial decisions

Reviewed on 22 November 2026:

- **Education, experience, awards, and contact:** the original November 2026 resume versions confirmed Heidelberg B.Sc. Computer Science, expected graduation in 2027, Cinemo dates, Python/Linux automation, 15,000+ integration tests, approximately 50% shorter test cycles, the competition results, and the published contact email. The resume itself is not copied into this repository.
- **Career direction:** C++ software engineering, ML engineering, and quantitative/HFT development are goals. The profile makes no claim of professional HFT employment, profitable strategies, or production trading infrastructure.
- **Monte Carlo:** the local `quant` checkout at commit `4460ef3` contains C++17/CMake, Asian and lookback payoffs, exact GBM discretization, standard errors, mergeable statistics, CTest registration, and a single-threaded benchmark. `src/gbm.cpp` explicitly implements exact discretization, not Euler–Maruyama. Parallel execution was not found, so the profile describes the current single-threaded implementation and marks the work in progress.
- **Monte Carlo link:** the supplied `CuZn6666/quant` URL returned 404 through the connector, public API, and authenticated CLI. This does not establish whether it is private, removed, or unavailable to the account. The profile therefore has no broken link and says the source is not publicly available. Restore a project link only after confirming a public URL; this task changes no repository visibility.
- **CNN:** the public README, local layer / PGD / Grad-CAM code, and the public [benchmark report](https://github.com/CuZn6666/cnn_adversarial_gradcam_cifar10/blob/main/deliverables/WP6/runtime_benchmark_after.md) support the selected features. The 207.72× number is kept in a disclosure with the actual input shape, convolution configuration, warm-up, iteration count, timer, and historical-baseline limitation. It is not described as overall model acceleration. GPU claims are unnecessary for this profile and are omitted.
- **Full stack:** the public [README](https://github.com/CuZn6666/Product-Integration-Studio), `ProductService.java`, and `App.tsx` confirm persistent product CRUD, REST validation, frontend search/filtering, and simulated integration visualization. The description preserves the simulation boundary.
- **Tools:** Docker and SQL appear in the original resume; GitHub Actions is present in the CNN repository. Other listed languages and tools are supported by the inspected projects or resume.

No other project was edited, built, committed, or pushed. Local source files were read only.

## Preview and validation

Open `README.md` in your editor's Markdown preview. Open `assets/cyber-snow.gif` in a browser to observe multiple loops, and compare it with `assets/cyber-snow-preview.png`.

For a GitHub-rendered preview without committing, use GitHub's Markdown API:

```sh
mkdir -p .preview
gh api markdown -F text=@README.md -f mode=gfm \
  -f context=CuZn6666/CuZn6666 > .preview/body.html
```

This renders Markdown to HTML but does not create a commit or modify a remote file. The fragment needs a preview page and local image paths for browser viewing. GitHub's final page styling is controlled by the visitor's theme. The dark background belongs to the banner and statistics card; Markdown cannot set the entire profile background. Main text stays native and readable in light and dark themes. Image width is constrained by GitHub's renderer, with normal text repeating essential banner information for small screens and assistive technology. Wide tables use GitHub's native horizontal scrolling.

Completed checks: all 72 GIF frames decode; the duration is 6000 ms; `loop=0`; the rendered scene is exactly periodic; the boundary difference is below the median adjacent-frame difference; the cursor varies; local image paths exist; Python files parse; GitHub's Markdown API renders the table, disclosure, headings, and images; every included HTTPS link returns 200; `git diff --check` passes. Static assets were visually inspected.

**Preview limitation:** browser automation was unavailable in this session. Full-page desktop/mobile and live browser animation observation were not completed. Temporary GitHub-rendered dark/light preview pages were prepared locally under ignored `.preview/`; they use approximate theme styling, not a claim of pixel-identical GitHub output. Inspect the final profile in both GitHub themes after publishing.

## Review, commit, and publish

These commands are provided for the owner to run after approving the files. No commit or push was performed during generation.

```sh
cd /Users/tongxinzhang/Desktop/CuZn6666
git rev-parse --show-toplevel
git remote -v
git status --short
git diff --check
.venv/bin/python scripts/validate_profile.py --online
git diff -- README.md
git add README.md .gitignore \
  assets/cyber-snow.gif assets/cyber-snow-preview.png \
  assets/github-stats.png assets/github-stats.json \
  scripts/generate_cyber_snow.py scripts/update_github_stats.py \
  scripts/validate_profile.py scripts/requirements.txt \
  docs/PROFILE_GUIDE.md
git diff --cached --stat
git commit -m "Redesign profile with Cyber Snow terminal and verified projects"
git push origin main
```

After pushing, visit [github.com/CuZn6666](https://github.com/CuZn6666). Check the dark and light themes, a narrow mobile viewport, both project links, the benchmark disclosure, and the snowfall over at least two loops.
