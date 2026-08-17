# 2D Planet Generator

**English** · [简体中文](README.zh-CN.md)

A small, headless, JSON-driven procedural planet generator. The `planetgen` CLI
creates reusable heightmap data, then renders that data as a flat map, a shaded
globe, or a seamlessly looping spin animation.

<p align="center">
  <img src="gallery/gallery_spin.gif" alt="Eight procedurally generated planets rotating" width="750">
</p>

<p align="center">
  <img src="gallery/spin_earth.gif" alt="A procedurally generated Earth-like planet rotating" width="300">
</p>

## Why planetgen?

- **Data and presentation are separate.** Generate a heightmap once, then try
  different palettes, projections, lighting, and rotations without regenerating
  the terrain.
- **Deterministic output.** The same JSON schema and seed produce the same world.
- **No graphics runtime.** It runs headlessly with only NumPy and Pillow.
- **Seamless longitude.** Wrapped noise removes the visible seam when a map is
  projected onto a rotating sphere.
- **17 named palettes.** Create Earth-like, ocean, lava, moon, icy, toxic, and
  other worlds from the same terrain data.

```text
generation schema (JSON) ── generate ──▶ planet.json (heightmap)
                                               │
planet.json + render config (JSON) ── render ──┴──▶ PNG / GIF
```

## Quick start

Requires Python 3.10 or newer.

```bash
git clone https://github.com/clingsz/2d-planet-generator.git
cd 2d-planet-generator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python main.py all \
  --schema schemas/default.gen.json \
  --config schemas/default.render.json \
  --out-data planet.json \
  --out-png planet.png
```

This writes the reusable terrain data to `planet.json` and the rendered globe to
`planet.png`.

## Commands

Generate terrain data:

```bash
python main.py generate \
  --schema schemas/default.gen.json \
  --out planet.json
```

Render the same terrain as a PNG:

```bash
python main.py render \
  --data planet.json \
  --config schemas/default.render.json \
  --out planet.png
```

Generate and render in one step:

```bash
python main.py all \
  --schema schemas/default.gen.json \
  --config schemas/default.render.json \
  --out-data planet.json \
  --out-png planet.png
```

Create a seamlessly looping spin animation:

```bash
python main.py gif \
  --data planet.json \
  --config schemas/default.render.json \
  --out planet.gif \
  --frames 72 \
  --fps 12
```

Both `--schema` and `--config` are optional; omitted values use built-in
defaults.

## Generation schema

The generation schema controls terrain. Every field is optional.

```jsonc
{
  "name": "default",
  "size": [200, 100],          // [width, height]; 2:1 works best on a sphere
  "seed": 1,                   // change the seed to create a different world
  "noise": {
    "scale": 30.0,             // larger = smoother, broader features
    "octaves": 4,              // number of detail layers
    "persistence": 0.5,        // amplitude retained by each detail layer
    "lacunarity": 2.0,         // frequency growth per detail layer
    "offset": [0, 0],
    "wrap_x": true             // join the left and right edges seamlessly
  },
  "shaping": {
    "normalize_mode": "global", // "global", "local", or "none"
    "flood": 0.0,              // negative = more ocean; positive = more land
    "falloff": false,          // sink the outer edges to create an island
    "elevate_horizontal": null,
    "elevate_vertical": null
  }
}
```

### Normalization modes

| Mode | Behavior | Best for |
| --- | --- | --- |
| `global` | Preserves absolute elevation relative to the theoretical noise amplitude. Palette sea levels remain meaningful. | Distinct ocean, desert, and dry worlds; recommended default |
| `local` | Stretches each generated map from its own minimum to maximum. | Using the entire palette on every terrain |
| `none` | Leaves the shaped noise unnormalized. | Debugging and custom pipelines |

### Tuning guide

| Goal | Adjustment |
| --- | --- |
| More fine detail | Increase `octaves`; decrease `scale` |
| Smoother, larger landforms | Decrease `octaves`; increase `scale` |
| Stronger elevation contrast | Increase `persistence`, for example to `0.6`–`0.7` |
| More ocean / more land | Decrease / increase `flood` |
| Island-shaped terrain | Set `falloff` to `true` |
| A completely different world | Change `seed` |

## Render config

Rendering is independent of generation, so one `planet.json` can produce many
visual styles.

```jsonc
{
  "colormap": "terrain",
  "projection": "sphere",     // "sphere" or "flat"
  "scale": 4,                  // nearest-neighbor scale for flat maps
  "radius": 256,               // globe radius in pixels
  "rotation": 0.0,             // longitude in degrees
  "shading": true,
  "background": [0, 0, 0, 0]  // RGBA
}
```

Available palettes:

```text
earth (terrain), moon, mars, ashy, lava, volcano, gobi, venus,
toxic, redstone, ocean, pandora, icy, dessert, tempest, hive, grayscale
```

Add a palette by defining another gradient in `colormaps.py`.

## Output data

`planet.json` is deliberately display-agnostic:

```jsonc
{
  "meta": {
    "name": "...",
    "size": [200, 100],
    "seed": 1,
    "schema": {}
  },
  "heightmap": [[0.0, 0.1], [0.2, 0.3]] // stored as [x][y]
}
```

## Project layout

| Path | Purpose |
| --- | --- |
| `noise.py` | Vectorized fractal Perlin noise |
| `shaping.py` | Normalization, flood, falloff, and directional shaping |
| `colormaps.py` | Named planet gradients and height-to-color mapping |
| `generate.py` | Generation schema → heightmap data |
| `render.py` | Heightmap data → flat map, globe, or animation frames |
| `main.py` | Command-line interface |
| `schemas/` | Example generation and render configs |
| `gallery/` | Example output generated by planetgen |

## Known limitations

- Longitude wraps seamlessly, but the poles can still show pinching because the
  source noise is sampled as an equirectangular map rather than directly on a
  sphere.
- The terrain uses fractal noise only; there is no dedicated crater generator
  yet.

## License

Released under the [MIT License](LICENSE).
