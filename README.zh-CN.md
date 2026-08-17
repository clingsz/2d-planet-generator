# planetgen

[English](README.md) · **简体中文**

一个轻量、无界面、由 JSON 驱动的程序化星球生成器。它先生成可复用的高度图数据，
再把同一份数据渲染成平面地图、带光照的球体，或无缝循环的自转 GIF。

<p align="center">
  <img src="gallery/gallery_spin.gif" alt="八种程序化生成的自转星球" width="750">
</p>

<p align="center">
  <img src="gallery/spin_earth.gif" alt="程序化生成的类地星球自转动画" width="300">
</p>

## 为什么用 planetgen？

- **数据层与显示层分离。** 地形只需生成一次，之后可以反复更换配色、投影、光照和
  旋转角度，无需重新生成高度图。
- **结果可复现。** 相同的 JSON schema 与 seed 会生成相同的世界。
- **不依赖图形运行时。** 仅依赖 NumPy 和 Pillow，可在服务器或 CI 中运行。
- **经度方向无缝。** 横向循环噪声消除了地图贴到自转球体上时的接缝。
- **17 种命名配色。** 同一份地形可以渲染成类地、海洋、熔岩、月球、冰冻、剧毒等
  不同世界。

```text
生成 schema (JSON) ── generate ──▶ planet.json（高度图）
                                          │
planet.json + 显示配置 (JSON) ── render ─┴──▶ PNG / GIF
```

## 快速开始

需要 Python 3.10 或更高版本。

```bash
git clone https://github.com/clingsz/planetgen.git
cd planetgen
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python main.py all \
  --schema schemas/default.gen.json \
  --config schemas/default.render.json \
  --out-data planet.json \
  --out-png planet.png
```

命令会把可复用的地形数据写入 `planet.json`，并把渲染结果写入 `planet.png`。

## 命令

生成地形数据：

```bash
python main.py generate \
  --schema schemas/default.gen.json \
  --out planet.json
```

将同一份地形渲染成 PNG：

```bash
python main.py render \
  --data planet.json \
  --config schemas/default.render.json \
  --out planet.png
```

一步生成并渲染：

```bash
python main.py all \
  --schema schemas/default.gen.json \
  --config schemas/default.render.json \
  --out-data planet.json \
  --out-png planet.png
```

生成无缝循环的自转 GIF：

```bash
python main.py gif \
  --data planet.json \
  --config schemas/default.render.json \
  --out planet.gif \
  --frames 72 \
  --fps 12
```

`--schema` 和 `--config` 都可以省略；省略后使用程序内置默认值。

## 生成 schema

生成 schema 控制地形本身，所有字段均可省略。

```jsonc
{
  "name": "default",
  "size": [200, 100],          // [宽, 高]；2:1 最适合贴到球体
  "seed": 1,                   // 修改 seed 会得到不同世界
  "noise": {
    "scale": 30.0,             // 越大越平滑，地貌块越大
    "octaves": 4,              // 细节层数
    "persistence": 0.5,        // 每层细节保留的振幅
    "lacunarity": 2.0,         // 每层细节增加的频率
    "offset": [0, 0],
    "wrap_x": true             // 左右边缘无缝衔接
  },
  "shaping": {
    "normalize_mode": "global", // "global"、"local" 或 "none"
    "flood": 0.0,              // 负数增加海洋，正数增加陆地
    "falloff": false,          // 压低四周，形成海岛
    "elevate_horizontal": null,
    "elevate_vertical": null
  }
}
```

### 归一化模式

| 模式 | 行为 | 适合场景 |
| --- | --- | --- |
| `global` | 相对于噪声的理论最大振幅保留绝对海拔，使配色中定义的海平面保持意义。 | 区分海洋星、沙漠星与干旱星；推荐默认值 |
| `local` | 把每张地图自身的最小值和最大值拉伸到完整范围。 | 让任意地形都用满整条配色 |
| `none` | 不对塑形后的噪声做归一化。 | 调试与自定义数据管线 |

### 调参速查

| 想要的效果 | 调整方式 |
| --- | --- |
| 更多细节 | 增加 `octaves`，减小 `scale` |
| 更平滑、更大块的地貌 | 减少 `octaves`，增大 `scale` |
| 更强的海拔对比 | 增大 `persistence`，例如 `0.6`–`0.7` |
| 更多海洋 / 更多陆地 | 减小 / 增大 `flood` |
| 海岛形地形 | 把 `falloff` 设为 `true` |
| 完全不同的世界 | 修改 `seed` |

## 显示配置

显示与生成互相独立，因此同一个 `planet.json` 可以产生很多种视觉风格。

```jsonc
{
  "colormap": "terrain",
  "projection": "sphere",     // "sphere" 球体或 "flat" 平面
  "scale": 4,                  // 平面地图的最近邻放大倍数
  "radius": 256,               // 球体半径（像素）
  "rotation": 0.0,             // 经度旋转角度
  "shading": true,
  "background": [0, 0, 0, 0]  // RGBA
}
```

可用配色：

```text
earth (terrain), moon, mars, ashy, lava, volcano, gobi, venus,
toxic, redstone, ocean, pandora, icy, dessert, tempest, hive, grayscale
```

在 `colormaps.py` 的渐变表中增加一项即可添加新配色。

## 输出数据

`planet.json` 与任何显示方式无关：

```jsonc
{
  "meta": {
    "name": "...",
    "size": [200, 100],
    "seed": 1,
    "schema": {}
  },
  "heightmap": [[0.0, 0.1], [0.2, 0.3]] // 按 [x][y] 存储
}
```

## 项目结构

| 路径 | 作用 |
| --- | --- |
| `noise.py` | 向量化分形 Perlin 噪声 |
| `shaping.py` | 归一化、海平面、falloff 与方向性塑形 |
| `colormaps.py` | 命名星球渐变与高度到颜色的映射 |
| `generate.py` | 生成 schema → 高度图数据 |
| `render.py` | 高度图数据 → 平面图、球体或动画帧 |
| `main.py` | 命令行入口 |
| `schemas/` | 生成与显示配置示例 |
| `gallery/` | 由 planetgen 生成的示例输出 |

## 已知限制

- 经度方向已经无缝，但两极仍可能出现挤压；原因是源噪声采样自等距柱状地图，而不是
  直接在球面采样。
- 当前地形只使用分形噪声，还没有专门的陨石坑生成器。
