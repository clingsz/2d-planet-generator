"""Display layer: planet data + display config -> PNG.

A planet's heightmap is treated as an equirectangular map. Two projections:
  - "flat":   direct rectangular map (optionally tiled-friendly), upscaled.
  - "sphere": orthographic projection onto a disk (a globe seen from space).
"""
import json
import numpy as np
from PIL import Image

import colormaps
from generate import planet_heightmap

DEFAULT_CONFIG = {
    "colormap": "terrain",
    "projection": "flat",   # "flat" | "sphere"
    "scale": 4,             # integer upscale factor for "flat"
    "radius": 256,          # disk radius in px for "sphere"
    "rotation": 0.0,        # longitude rotation (degrees) for "sphere"
    "shading": True,        # simple lambert-ish shading for "sphere"
    "background": [0, 0, 0, 0],  # RGBA, transparent by default for "sphere"
}


def _merge(base, override):
    out = dict(base)
    out.update(override or {})
    return out


def render_flat(height, cfg):
    rgb = colormaps.apply_colormap(height, cfg["colormap"])  # (w, h, 3)
    img = Image.fromarray(np.transpose(rgb, (1, 0, 2)), "RGB")  # (h, w)
    scale = max(1, int(cfg["scale"]))
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    return img


def render_sphere(height, cfg):
    w, h = height.shape
    R = int(cfg["radius"])
    D = 2 * R
    lon0 = np.radians(cfg["rotation"])

    # Output pixel grid in [-1, 1], y points up.
    ax = (np.arange(D) - R + 0.5) / R
    ay = (np.arange(D) - R + 0.5) / R
    nx, ny = np.meshgrid(ax, ay, indexing="xy")
    d2 = nx * nx + ny * ny
    inside = d2 <= 1.0
    nz = np.sqrt(np.clip(1.0 - d2, 0, None))

    lat = np.arcsin(np.clip(-ny, -1, 1))           # +pi/2 top .. -pi/2 bottom
    lon = np.arctan2(nx, nz) + lon0                 # rotate around vertical axis

    u = (lon / (2 * np.pi) + 0.5) % 1.0
    v = (0.5 - lat / np.pi)
    xi = np.clip((u * w).astype(int), 0, w - 1)
    yi = np.clip((v * h).astype(int), 0, h - 1)

    sampled = height[xi, yi]
    rgb = colormaps.apply_colormap(sampled, cfg["colormap"]).astype(np.float64)

    if cfg["shading"]:
        # light from upper-left-front; soft terminator
        light = np.array([-0.5, 0.5, 0.8])
        light = light / np.linalg.norm(light)
        normal = np.stack([nx, -ny, nz], axis=-1)
        shade = np.clip((normal * light).sum(-1), 0, 1)
        shade = 0.35 + 0.65 * shade            # ambient floor
        rgb *= shade[..., None]

    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    bg = cfg["background"]
    out = np.zeros((D, D, 4), dtype=np.uint8)
    out[..., :3] = bg[:3]
    out[..., 3] = bg[3] if len(bg) > 3 else 255
    out[inside, :3] = rgb[inside]
    out[inside, 3] = 255
    return Image.fromarray(out, "RGBA")


def render(planet, config):
    cfg = _merge(DEFAULT_CONFIG, config)
    height = planet_heightmap(planet)
    if cfg["projection"] == "sphere":
        return render_sphere(height, cfg)
    return render_flat(height, cfg)


def render_spin(planet, config, frames=36):
    """Render a list of RGB frames sweeping longitude 0..360 (a spinning globe).

    Forces the sphere projection. Transparent disk background is composited
    onto an opaque color so the frames work as a GIF.
    """
    cfg = _merge(DEFAULT_CONFIG, config)
    cfg["projection"] = "sphere"
    height = planet_heightmap(planet)
    bg = cfg["background"]
    bg_rgb = tuple(bg[:3]) if bg else (0, 0, 0)

    imgs = []
    for i in range(frames):
        cfg["rotation"] = 360.0 * i / frames
        rgba = render_sphere(height, cfg)
        flat = Image.new("RGB", rgba.size, bg_rgb)
        flat.paste(rgba, (0, 0), rgba)  # composite over opaque bg
        imgs.append(flat)
    return imgs


def save_gif(frames, path, fps=20):
    duration = max(1, int(1000 / fps))
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=duration, loop=0, optimize=True)


def load_config(path):
    if not path:
        return {}
    with open(path) as f:
        return json.load(f)
