"""Data layer: generation schema (JSON) -> planet data (heightmap matrix).

The output planet dict is display-agnostic. Rendering/projection happens
separately in render.py.
"""
import json
import numpy as np

import noise
import shaping

DEFAULT_SCHEMA = {
    "name": "default",
    "size": [200, 100],
    "seed": 1,
    "noise": {
        "scale": 30.0,
        "octaves": 4,
        "persistence": 0.5,
        "lacunarity": 2.0,
        "offset": [0, 0],
        "wrap_x": True,
    },
    "shaping": {
        "normalize_mode": "global",  # "global" | "local" | "none"
        "flood": 0.0,                # sea-level bias: <0 more ocean, >0 more land
        "falloff": False,            # island: edges sink
        "elevate_horizontal": None,  # threshold t, or null to disable
        "elevate_vertical": None,    # threshold t, or null to disable
    },
}


def _merge(base, override):
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def generate(schema):
    """schema: dict. Returns planet dict with 'meta' and 'heightmap'."""
    schema = _merge(DEFAULT_SCHEMA, schema)
    size = tuple(schema["size"])
    n = schema["noise"]
    s = schema["shaping"]

    raw, max_amp = noise.fractal_noise(
        size,
        scale=n["scale"],
        octaves=n["octaves"],
        persistence=n["persistence"],
        lacunarity=n["lacunarity"],
        offset=tuple(n["offset"]),
        seed=schema["seed"],
        wrap_x=n.get("wrap_x", True),
    )
    # backward compat: old schemas used {"normalize": true/false}
    mode = s.get("normalize_mode")
    if mode is None:
        mode = "local" if s.get("normalize", True) else "none"
    height = shaping.shape(
        raw,
        max_amp=max_amp,
        normalize_mode=mode,
        falloff=s.get("falloff", False),
        elevate_horizontal=s.get("elevate_horizontal"),
        elevate_vertical=s.get("elevate_vertical"),
        flood=s.get("flood", 0.0),
    )

    return {
        "meta": {
            "name": schema["name"],
            "size": list(size),
            "seed": schema["seed"],
            "schema": schema,
        },
        # stored as [x][y] to match the (width, height) generation convention
        "heightmap": np.round(height, 4).tolist(),
    }


def load_schema(path):
    with open(path) as f:
        return json.load(f)


def save_planet(planet, path):
    with open(path, "w") as f:
        json.dump(planet, f)


def planet_heightmap(planet):
    """Return the heightmap as a (width, height) float array."""
    return np.asarray(planet["heightmap"], dtype=np.float64)
