"""Terrain shaping: falloff (island), directional elevate, normalization.

Ported and vectorized from the original Probe noise.py.
"""
import numpy as np


def _evaluate(value, a=3.0, b=2.2):
    v2a = value ** a
    return v2a / (v2a + (b - b * value) ** a)


def falloff_map(size):
    """Higher toward the edges -> subtracting it makes an island."""
    w, h = size
    xs = np.linspace(-1, 1, w)
    ys = np.linspace(-1, 1, h)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    value = np.maximum(np.abs(gx), np.abs(gy))
    return _evaluate(value)


def elevate_map(size, direction="horizontal", t=0.7):
    """Ramps up past threshold t along one axis; 0 before it."""
    w, h = size
    xs = np.linspace(-1, 1, w)
    ys = np.linspace(-1, 1, h)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    target = np.abs(gx) if direction == "horizontal" else np.abs(gy)
    ramp = np.clip((target - t) / (1 - t), 0, None)
    return np.where(target < t, 0.0, ramp)


def normalize(raw, mode="global", max_amp=1.0):
    """Map raw octave-sum noise into [0, 1].

    - "local":  per-map min-max stretch. Every planet fills the full range, so
      the colormap is always used end to end (planets look equally "full").
    - "global": absolute scaling (raw + 1) / max_amp, clamped to [0, 1].
      Heights keep an absolute meaning across seeds/planets, so a colormap
      whose stops encode a sea level (the ported game gradients do) yields
      genuinely different water coverage per planet. Ported from Unity Noise.cs.
    - "none":   no normalization (assumes input already in range).
    """
    if mode == "local":
        lo, hi = float(np.min(raw)), float(np.max(raw))
        if hi - lo < 1e-12:
            return np.zeros_like(raw)
        return (raw - lo) / (hi - lo)
    if mode == "global":
        return np.clip((raw + 1.0) / max_amp, 0.0, 1.0)
    return raw


def shape(raw, max_amp=1.0, normalize_mode="global", falloff=False,
          elevate_horizontal=None, elevate_vertical=None, flood=0.0):
    """Normalize then apply shaping passes; returns a new array in [0, 1].

    flood: sea-level bias added after normalization (then clipped to [0, 1]).
      Decouples shoreline from the colormap — negative floods the planet
      (more ocean), positive drains it (more land). 0 = no change.
    """
    m = normalize(raw, normalize_mode, max_amp)
    size = m.shape
    if falloff:
        m = np.clip(m - falloff_map(size), 0, None)
    if elevate_horizontal is not None:
        m = np.clip(m - elevate_map(size, "horizontal", elevate_horizontal), 0, None)
    if elevate_vertical is not None:
        m = np.clip(m - elevate_map(size, "vertical", elevate_vertical), 0, None)
    if flood:
        m = np.clip(m + flood, 0.0, 1.0)
    return m
