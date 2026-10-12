#!/usr/bin/env python3
"""
Generative candidate — Direction A "La frontera de la incertidumbre"
Think Anywhere artistic production test v1 (project-to-art v2.1).

Not scientific visualization: 2D flow field with smooth transition
laminar-like stripes -> interference-like crossing structure.
Output: 1920x1080 PNG for comparative evaluation (not README hero yet).
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

try:
    from PIL import Image
except ImportError:
    raise SystemExit("pip install pillow numpy") from None

W, H = 1920, 1080
OUT = Path(__file__).resolve().parent / "think-anywhere-hero-v2-frontera-candidate-a.png"


def smoothstep(edge0: float, edge1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def main() -> None:
    xs = np.linspace(0, 1, W, dtype=np.float32)
    ys = np.linspace(0, 1, H, dtype=np.float32)
    xg, yg = np.meshgrid(xs, ys)

    # Transition mask: calm left -> complex right (~40% boundary aesthetic, not tau)
    t = smoothstep(0.38, 0.62, xg)

    # Base angle field: mostly horizontal laminar on left
    angle_l = np.zeros_like(xg)
    # Right: add crossing components (interference metaphor)
    angle_r = 0.9 * np.sin(2 * math.pi * (xg * 8 + yg * 3)) + 0.5 * np.sin(
        2 * math.pi * (xg * 5 - yg * 7)
    )
    angle = (1 - t) * angle_l + t * angle_r

    # Integrate streamlines implicitly via phase field
    freq = 28 + 40 * t
    phase = freq * (np.cos(angle) * xg + np.sin(angle) * yg)
    ripple = np.sin(2 * math.pi * phase)

    # Moiré layer on right
    moire = np.sin(2 * math.pi * (xg * 60 + yg * 20)) * np.sin(
        2 * math.pi * (xg * 55 - yg * 25)
    )
    field = (1 - t) * ripple + t * (0.55 * ripple + 0.45 * moire)

    # Color: deep blue-black base, silver lines, subtle ochre in high-interference zones
    base = np.array([12, 18, 32], dtype=np.float32)
    line = np.array([180, 190, 210], dtype=np.float32)
    accent = np.array([180, 120, 70], dtype=np.float32)

    intensity = 0.5 + 0.5 * field
    rgb = base + (line - base) * intensity[..., None]

    collision = t * np.clip(np.abs(moire) * np.abs(ripple), 0, 1)
    rgb = rgb + (accent - base) * (0.35 * collision[..., None])

    # Vignette for depth
    cx, cy = 0.45, 0.5
    vignette = 1.0 - 0.25 * ((xg - cx) ** 2 + (yg - cy) ** 2)
    rgb *= vignette[..., None]

    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    Image.fromarray(rgb, mode="RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
