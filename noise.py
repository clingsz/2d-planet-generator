"""Self-contained, vectorized Perlin fractal noise (numpy only).

No external noise libraries. Returns a (width, height) float array.
"""
import numpy as np


def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a, b, t):
    return a + t * (b - a)


def _grad(h, x, y):
    # 4 gradient directions, classic Perlin 2D
    h = h & 3
    u = np.where(h < 2, x, y)
    v = np.where(h < 2, y, x)
    return np.where((h & 1) == 0, u, -u) + np.where((h & 2) == 0, v, -v)


def _make_perm(seed):
    rng = np.random.default_rng(seed)
    p = np.arange(256, dtype=np.int32)
    rng.shuffle(p)
    return np.concatenate([p, p])  # length 512, avoids index overflow


def _perlin(x, y, perm):
    xi = np.floor(x).astype(np.int32) & 255
    yi = np.floor(y).astype(np.int32) & 255
    xf = x - np.floor(x)
    yf = y - np.floor(y)
    u = _fade(xf)
    v = _fade(yf)
    aa = perm[perm[xi] + yi]
    ab = perm[perm[xi] + yi + 1]
    ba = perm[perm[xi + 1] + yi]
    bb = perm[perm[xi + 1] + yi + 1]
    x1 = _lerp(_grad(aa, xf, yf), _grad(ba, xf - 1, yf), u)
    x2 = _lerp(_grad(ab, xf, yf - 1), _grad(bb, xf - 1, yf - 1), u)
    return _lerp(x1, x2, v)  # roughly [-1, 1]


def _fbm(gx, gy, perm, octave_offsets, scale, persistence, lacunarity):
    total = np.zeros_like(gx, dtype=np.float64)
    amp = 1.0
    freq = 1.0
    max_amp = 0.0
    for off in octave_offsets:
        sx = (gx + off[0]) / scale * freq
        sy = (gy + off[1]) / scale * freq
        total += _perlin(sx, sy, perm) * amp
        max_amp += amp
        amp *= persistence
        freq *= lacunarity
    return total, max_amp


def fractal_noise(size, scale=30.0, octaves=4, persistence=0.5,
                  lacunarity=2.0, offset=(0, 0), seed=1, wrap_x=True):
    """Fractal (fBm) Perlin noise.

    size: (width, height). Returns (raw, max_amp):
      - raw: array (width, height) of summed octave noise, roughly in
        [-max_amp, +max_amp] but realistically clustered near 0.
      - max_amp: sum of octave amplitudes (for global normalization).

    Each octave is sampled at an independent random offset (seeded), so the
    detail layers don't visibly align — same principle as the Unity Noise.cs.

    wrap_x: make the map horizontally periodic (left edge == right edge) by
    cross-fading the tile with its x-wrapped copy. This removes the seam when
    the map is wrapped onto a sphere (longitude wraps at +-180 deg).
    """
    w, h = size
    if scale <= 0:
        scale = 1e-4
    perm = _make_perm(seed)

    rng = np.random.default_rng(seed)
    octave_offsets = rng.integers(-100000, 100000, size=(octaves, 2))

    xs = np.arange(w) - w / 2 + offset[0]
    ys = np.arange(h) - h / 2 - offset[1]
    gx, gy = np.meshgrid(xs, ys, indexing="ij")  # (w, h)

    total, max_amp = _fbm(gx, gy, perm, octave_offsets, scale,
                          persistence, lacunarity)

    if wrap_x:
        # noise sampled one full width to the left; blend so x=0 and x=W match.
        wrapped, _ = _fbm(gx - w, gy, perm, octave_offsets, scale,
                          persistence, lacunarity)
        t = (np.arange(w) / w)[:, None]      # 0 at left .. 1 at right
        total = (1.0 - t) * total + t * wrapped

    return total, max_amp
