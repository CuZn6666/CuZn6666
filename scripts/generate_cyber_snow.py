#!/usr/bin/env python3
"""Render Cyber Snow locally. Python 3.10+ and Pillow; no network access.

All animation functions are periodic in normalized time. Particles have a
smooth birth/death envelope so slow snowfall can loop in six seconds without
having to cross the whole canvas. No frame at t=1 is duplicated in the GIF.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1000, 320
SCALE = 2
COLORS = {
    "background": "#05080D",
    "terminal": "#0B111B",
    "secondary": "#111827",
    "cyan": "#00D4FF",
    "ice": "#7DD3FC",
    "white": "#E5F3FF",
    "muted": "#94A3B8",
}
# Layer: relative population, radius, opacity, travel per 6-second cycle.
LAYERS = ((0.52, 0.65, 65, 48), (0.36, 1.0, 105, 78), (0.12, 1.65, 155, 116))


def rgb(value):
    return tuple(bytes.fromhex(value.lstrip("#")))


def mix(a, b, weight):
    return tuple(round(x + (y - x) * weight) for x, y in zip(a, b))


def font_path(explicit, mono=False):
    candidates = ([explicit] if explicit else []) + (
        ["/System/Library/Fonts/SFNSMono.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
         "C:/Windows/Fonts/consola.ttf"] if mono else
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "C:/Windows/Fonts/arialbd.ttf"]
    )
    if explicit and not Path(explicit).is_file():
        raise ValueError(f"Font not found: {explicit}")
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    raise ValueError("No supported font found; supply --font and --mono-font paths.")


class Canvas:
    def __init__(self, image, sans, mono):
        self.image = image
        self.draw = ImageDraw.Draw(image)
        self.sans, self.mono = sans, mono

    def text(self, xy, text, size, color, mono=True):
        font = ImageFont.truetype(self.mono if mono else self.sans, round(size * SCALE))
        self.draw.text(tuple(round(v * SCALE) for v in xy), text, font=font,
                       fill=color, anchor="lt")

    def line(self, points, color, width=1):
        self.draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
                       fill=color, width=max(1, round(width * SCALE)))

    def rect(self, box, fill, outline=None, radius=0, width=1):
        self.draw.rounded_rectangle(tuple(round(x * SCALE) for x in box),
                                    radius=round(radius * SCALE), fill=fill,
                                    outline=outline, width=round(width * SCALE))

    def dot(self, x, y, radius, fill):
        self.draw.ellipse(tuple(round(v * SCALE) for v in
                               (x-radius, y-radius, x+radius, y+radius)), fill=fill)


@dataclass(frozen=True)
class Particle:
    x: float
    y: float
    phase: float
    drift: float
    radius: float
    opacity: float
    travel: float
    crystal: bool


class Scene:
    def __init__(self, count=64, seed=27, speed=1.0, sans=None, mono=None):
        self.sans, self.mono = font_path(sans), font_path(mono, True)
        self.speed = speed
        rng = random.Random(seed)
        self.particles = []
        for index in range(count):
            fraction = index / max(count, 1)
            layer = LAYERS[0] if fraction < .52 else LAYERS[1] if fraction < .88 else LAYERS[2]
            _, radius, opacity, travel = layer
            self.particles.append(Particle(
                rng.uniform(20, 980), rng.uniform(35, 320), rng.random(),
                rng.uniform(-13, 13), radius * rng.uniform(.75, 1.25),
                opacity * rng.uniform(.65, 1), travel * rng.uniform(.8, 1.2),
                fraction >= .88))
        self.base = self.make_base()

    def canvas(self, image):
        return Canvas(image, self.sans, self.mono)

    def make_base(self):
        # A low-resolution analytic glow avoids noisy gradients and GIF bloat.
        small = Image.new("RGB", (250, 80))
        pixels = small.load()
        for y in range(80):
            for x in range(250):
                cyan = math.exp(-(((x-214)/53)**2 + ((y-49)/42)**2))
                violet = math.exp(-(((x-157)/48)**2 + ((y-5)/20)**2))
                pixels[x, y] = (round(5+3*cyan+3*violet), round(8+10*cyan), round(13+16*cyan+5*violet))
        base = small.resize((WIDTH*SCALE, HEIGHT*SCALE), Image.Resampling.BICUBIC)
        c = self.canvas(base)
        c.rect((18, 14, 982, 306), COLORS["terminal"], "#243444", 12)
        # Restrained diffuse light, clipped inside the terminal.
        light = Image.new("RGBA", base.size)
        lc = self.canvas(light)
        lc.dot(859, 190, 88, (0, 145, 210, 16))
        lc.dot(726, 66, 45, (91, 72, 157, 10))
        light = light.filter(ImageFilter.GaussianBlur(39*SCALE))
        base = Image.alpha_composite(base.convert("RGBA"), light).convert("RGB")
        c = self.canvas(base)
        c.line([(19, 49), (981, 49)], "#22303E")
        for x, color in [(39, "#487084"), (55, "#426178"), (71, "#34495F")]:
            c.dot(x, 32, 3, color)
        c.text((97, 27), "tongxin@heidelberg: ~", 10, COLORS["muted"])
        c.text((749, 27), "CYBER SNOW / MIDNIGHT", 10, "#6C8B9F")
        c.text((59, 73), "$", 19, COLORS["cyan"])
        c.text((83, 73), "whoami", 19, COLORS["ice"])
        c.text((57, 108), "Tongxin Zhang", 51, COLORS["white"], mono=False)
        c.text((60, 173), "Computer Science @ Heidelberg University", 16, COLORS["muted"])
        c.text((60, 211), "CAREER DIRECTION", 9, "#648698")
        c.text((60, 229), "C++ Software Engineer  /  Machine Learning Engineer", 14, COLORS["ice"])
        c.text((60, 251), "Quantitative Developer | HFT", 14, COLORS["ice"])
        c.line([(60, 282), (940, 282)], "#1C3040")
        c.text((60, 291), "C++  /  ALGORITHMS  /  NUMERICAL COMPUTING", 8, "#668497")
        c.text((788, 291), "HEIDELBERG, DE", 8, "#668497")
        # Quiet source-code texture and an abstract ice lattice, not a dashboard.
        for y, s in [(77, "template <class Real>"), (95, "auto estimate = mean(paths);"),
                     (113, "// precision in every step")]:
            c.text((721, y), s, 10, "#244050")
        cx, cy = 829, 204
        for radius in (40, 65):
            points = [(cx+radius*math.cos(a*math.pi/3), cy+radius*math.sin(a*math.pi/3)) for a in range(7)]
            c.line(points, "#173544", .6)
        for arm in range(6):
            angle = arm * math.pi / 3 + math.pi / 6
            end = (cx+70*math.cos(angle), cy+70*math.sin(angle))
            c.line([(cx, cy), end], "#31566A", .8)
            for distance in (30, 48):
                node = (cx+distance*math.cos(angle), cy+distance*math.sin(angle))
                for sign in (-1, 1):
                    branch = angle+sign*math.pi/3
                    c.line([node, (node[0]+13*math.cos(branch), node[1]+13*math.sin(branch))], "#294C5E", .7)
            c.dot(*end, 1.6, "#628B9E")
        c.dot(cx, cy, 3, "#80BDD2")
        return base

    def render(self, time):
        time %= 1.0
        frame = self.base.copy().convert("RGBA")
        particles = Image.new("RGBA", frame.size)
        glow = Image.new("RGBA", frame.size)
        c, g = self.canvas(particles), self.canvas(glow)
        for p in self.particles:
            age = (time+p.phase) % 1.0
            y = 40 + ((p.y-40+p.travel*self.speed*age) % 275)
            x = p.x + p.drift * math.sin(math.tau*age)
            envelope = math.sin(math.pi*age)**2
            edge = max(0, min(1, (y-51)/15, (281-y)/15))
            # Preserve text contrast; most visible motion lives on the right.
            protect = .24 if 45 < x < 680 and 66 < y < 274 else 1.0
            alpha = round(p.opacity*envelope*edge*protect)
            if alpha < 2:
                continue
            color = (*rgb(COLORS["ice"]), alpha)
            c.dot(x, y, p.radius, color)
            if p.crystal:
                for angle in (0, math.pi/3, 2*math.pi/3):
                    dx, dy = p.radius*1.8*math.cos(angle), p.radius*1.8*math.sin(angle)
                    c.line([(x-dx, y-dy), (x+dx, y+dy)], color, .45)
                g.dot(x, y, p.radius*3, (*rgb(COLORS["cyan"]), alpha//5))
        for i, (x, y) in enumerate(((700, 158), (934, 222), (908, 77), (766, 265))):
            pulse = (.5+.5*math.sin(math.tau*(time+i/4)))**3
            alpha = round(25+90*pulse)
            c.line([(x-3, y), (x+3, y)], (125, 211, 252, alpha), .5)
            c.line([(x, y-3), (x, y+3)], (125, 211, 252, alpha), .5)
            g.dot(x, y, 4, (0, 212, 255, round(18*pulse)))
        frame = Image.alpha_composite(frame, glow.filter(ImageFilter.GaussianBlur(3*SCALE)))
        frame = Image.alpha_composite(frame, particles)
        c = self.canvas(frame)
        pulse = .25+.75*(.5+.5*math.cos(math.tau*2*time))**2
        c.rect((164, 73, 174, 92), mix(rgb(COLORS["terminal"]), rgb(COLORS["cyan"]), pulse), radius=1)
        # The faint status word breathes; no large moving text.
        c.text((722, 135), "[ precision / performance ]", 9,
               mix((26, 48, 61), (56, 90, 108), .5+.5*math.sin(math.tau*time)))
        return frame.convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def generate(args):
    if not 1 <= args.fps <= 50 or not 1 <= args.seconds <= 30:
        raise ValueError("Use 1–50 FPS and a duration of 1–30 seconds.")
    if not 0 <= args.particles <= 500 or not 0 < args.speed <= 5:
        raise ValueError("Use 0–500 particles and speed in (0, 5].")
    if args.cyan:
        rgb(args.cyan)
        COLORS["cyan"] = args.cyan
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    scene = Scene(args.particles, args.seed, args.speed, args.font, args.mono_font)
    count = round(args.seconds*args.fps)
    frames = [scene.render(i/count) for i in range(count)]
    # One palette for every frame prevents temporal color flicker.
    contact = Image.new("RGB", (WIDTH, HEIGHT*6))
    for i in range(6):
        contact.paste(frames[i*count//6], (0, HEIGHT*i))
    palette = contact.quantize(colors=240, method=Image.Quantize.MEDIANCUT)
    # Reserve accents that occupy too few pixels for adaptive quantization.
    # This preserves the true cyan cursor and smooth dark-to-cyan breathing.
    reserved = [mix(rgb(COLORS["terminal"]), rgb(COLORS["cyan"]), i/15)
                for i in range(16)]
    palette.putpalette(palette.getpalette()[:720] + [v for color in reserved for v in color])
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    # GIF delays are centiseconds. Distribute rounding, preserving total time.
    ticks = round(args.seconds*100)
    durations = [(round((i+1)*ticks/count)-round(i*ticks/count))*10 for i in range(count)]
    indexed[0].save(output/"cyber-snow.gif", save_all=True,
                    append_images=indexed[1:], loop=0, duration=durations,
                    optimize=True, disposal=1)
    frames[0].save(output/"cyber-snow-preview.png", optimize=True)
    size = (output/"cyber-snow.gif").stat().st_size
    print(f"Rendered {count} frames, {sum(durations)} ms, {size/1024/1024:.2f} MiB")
    if size > 5_000_000:
        print("Hint: reduce --particles or --fps to stay below 5 MB.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(ROOT/"assets"))
    parser.add_argument("--seconds", type=float, default=6)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--particles", type=int, default=64)
    parser.add_argument("--speed", type=float, default=1, help="Travel multiplier; retains a seamless loop")
    parser.add_argument("--seed", type=int, default=27)
    parser.add_argument("--cyan", help="Primary accent as #RRGGBB")
    parser.add_argument("--font", help="Path to a bold TrueType/OpenType name font")
    parser.add_argument("--mono-font", help="Path to a monospace TrueType/OpenType font")
    generate(parser.parse_args())
