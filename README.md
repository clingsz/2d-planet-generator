<p align="center">
  <img src="gallery/hero.png" alt="A family of procedurally generated 2D planets" width="100%">
</p>

<h1 align="center">2D Planet Generator</h1>

<p align="center">
  <strong>One seed → heightmap, world map, shaded globe, and looping GIF.</strong><br>
  A tiny, headless planet factory for games, prototypes, art pipelines, and procedural-world experiments.
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-7c3aed" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/runtime-headless-0891b2" alt="Headless runtime">
</p>

## Turn a JSON recipe into a world

Use 2D Planet Generator when you need **repeatable planet assets without an
editor, game engine, or graphics runtime**. Describe terrain in JSON, choose a
seed, and render the result as reusable data or finished art.

```bash
python main.py all \
  --schema schemas/default.gen.json \
  --config schemas/default.render.json \
  --out-data planet.json \
  --out-png planet.png
```

The same `planet.json` can be rendered again with another palette, projection,
size, light, or rotation. Generation and presentation stay separate.

## Who is this for?

| You are… | You need… | planetgen gives you… |
| --- | --- | --- |
| An indie game developer | Planets for a world map, level select, card, or background | Deterministic PNG globes and looping GIFs |
| A procedural-generation tinkerer | Fast terrain experiments without engine setup | Seeded Perlin heightmaps controlled by JSON |
| A 2D or pixel artist | A strong base to paint over or recolor | Flat maps, shaded spheres, and 17 palettes |
| A tools or pipeline developer | Batch-friendly assets for scripts, servers, or CI | A headless CLI with only NumPy and Pillow |
| A teacher or learner | A compact example of noise → data → projection | Small, readable Python modules with no noise library |

Use something else if you need physically accurate spherical simulation,
interactive editing, cloud or atmosphere rendering, biomes, or real crater
placement. This project is intentionally a small terrain-and-rendering tool.

## What can it make?

<p align="center">
  <img src="gallery/gallery_spin.gif" alt="Eight generated planet styles rotating" width="750">
</p>

- A display-agnostic JSON heightmap for your own renderer or game.
- A longitude-seamless 2:1 flat world map.
- A transparent or solid-background shaded globe.
- A seamless, endlessly looping rotation GIF.
- Earth, ocean, lava, moon, icy, toxic, alien, and other looks from the same
  terrain.

<p align="center">
  <img src="gallery/spin_earth.gif" alt="Generated Earth-like planet rotating" width="300">
</p>

## Start in 30 seconds

Requires Python 3.10 or newer.

```bash
git clone https://github.com/clingsz/2d-planet-generator.git
cd 2d-planet-generator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate terrain data and a shaded globe.
python main.py all \
  --schema schemas/default.gen.json \
  --config schemas/default.render.json \
  --out-data planet.json \
  --out-png planet.png

# Turn the same terrain into a six-second looping animation.
python main.py gif \
  --data planet.json \
  --config schemas/default.render.json \
  --out planet.gif \
  --frames 72 \
  --fps 12
```

Both `--schema` and `--config` are optional. Omit them to use the built-in
defaults.

## Pick your outcome

| Goal | What to do | Output |
| --- | --- | --- |
| Create a new world's terrain | Change `seed`, then run `generate` | `planet.json` |
| Get a ready-to-use planet image | Run `all` with the sphere config | `planet.json` + `planet.png` |
| Make a looping animation | Run `gif` on an existing planet | `planet.gif` |
| Make a flat map or texture | Set `projection` to `flat`, then run `render` | Rectangular PNG |
| Re-theme the same world | Change only `colormap`, then run `render` again | New art, identical terrain |
| Make many reproducible variants | Run the CLI with different schemas or seeds | Batch-friendly deterministic assets |

## Mental model

```text
generation schema (JSON)
        │
        ▼
     generate ─────────────▶ planet.json
                              heightmap data
                                   │
                    render config  │
                           ┌───────┴────────┐
                           ▼                ▼
                      flat / sphere     spinning GIF
                           │                │
                           ▼                ▼
                          PNG              GIF
```

The key idea is simple: **terrain is data; appearance is a view of that data.**

## Task recipes

### 1. Generate a different planet

Edit `seed` in `schemas/default.gen.json`, then run:

```bash
python main.py generate \
  --schema schemas/default.gen.json \
  --out planet.json
```

The same schema plus the same seed always produces the same terrain.

### 2. Render one planet in several styles

Keep `planet.json`, change only `colormap` in the render config, and render
again:

```bash
python main.py render \
  --data planet.json \
  --config schemas/default.render.json \
  --out planet-earth.png
```

Try `earth`, `ocean`, `moon`, `lava`, `icy`, or `pandora`. No terrain
regeneration is needed.

### 3. Make a game-ready flat map

Use a render config like this:

```json
{
  "colormap": "earth",
  "projection": "flat",
  "scale": 4
}
```

Then render:

```bash
python main.py render \
  --data planet.json \
  --config flat.render.json \
  --out planet-map.png
```

### 4. Export a seamless spin

```bash
python main.py gif \
  --data planet.json \
  --config schemas/default.render.json \
  --out planet.gif \
  --frames 72 \
  --fps 12
```

More frames make the motion smoother and the file larger. Rotation speed is
`360 / frames × fps` degrees per second. Wrapped longitude is enabled by
default, so the loop has no map seam.

## Generation input

Every generation field is optional:

```jsonc
{
  "name": "default",
  "size": [200, 100],          // [width, height]; 2:1 fits a sphere best
  "seed": 1,                   // change this to create another world
  "noise": {
    "scale": 30.0,             // larger = smoother, broader features
    "octaves": 4,              // number of detail layers
    "persistence": 0.5,        // amplitude retained by each layer
    "lacunarity": 2.0,         // frequency growth per layer
    "offset": [0, 0],
    "wrap_x": true             // seamless left and right edges
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

### Terrain tuning cheat sheet

| Desired result | Change |
| --- | --- |
| Finer, busier detail | Increase `octaves`; decrease `scale` |
| Smoother, larger landforms | Decrease `octaves`; increase `scale` |
| Stronger height contrast | Increase `persistence`, for example to `0.6`–`0.7` |
| More ocean / more land | Decrease / increase `flood` |
| Island-shaped terrain | Set `falloff` to `true` |
| A completely different world | Change `seed` |

### Normalization modes

| Mode | Behavior | Use it for |
| --- | --- | --- |
| `global` | Preserves elevation relative to the theoretical noise amplitude, so palette sea levels remain meaningful | Distinct ocean, desert, and dry worlds; recommended default |
| `local` | Stretches each map from its own minimum to maximum | Forcing every terrain to use the full palette |
| `none` | Leaves shaped noise unnormalized | Debugging and custom pipelines |

## Render input

```jsonc
{
  "colormap": "terrain",
  "projection": "sphere",     // "sphere" or "flat"
  "scale": 4,                  // nearest-neighbor scale for flat maps
  "radius": 256,               // globe radius in pixels
  "rotation": 0.0,             // longitude in degrees
  "shading": true,
  "background": [0, 0, 0, 0]  // RGBA; transparent by default
}
```

Available palettes:

```text
earth (terrain), moon, mars, ashy, lava, volcano, gobi, venus,
toxic, redstone, ocean, pandora, icy, dessert, tempest, hive, grayscale
```

Add a new palette by defining another gradient in `colormaps.py`.

## Output contract

`planet.json` is deliberately display-agnostic and easy to consume elsewhere:

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

## Project map

| Path | Responsibility |
| --- | --- |
| `noise.py` | Vectorized fractal Perlin noise |
| `shaping.py` | Normalization, flood, falloff, and directional shaping |
| `colormaps.py` | Named planet gradients and height-to-color mapping |
| `generate.py` | Generation schema → reusable heightmap data |
| `render.py` | Heightmap data → flat map, globe, or animation frames |
| `main.py` | Command-line interface |
| `schemas/` | Ready-to-edit generation and render recipes |
| `gallery/` | Images and GIFs generated by the project |

## Current boundaries

- Longitude wraps seamlessly, but poles can still pinch because noise is sampled
  as an equirectangular map rather than directly on a sphere.
- Terrain currently uses fractal noise only; there is no dedicated crater,
  biome, cloud, or atmosphere generator yet.

## License

Released under the [MIT License](LICENSE). Build a world with it.
