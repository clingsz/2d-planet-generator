"""planetgen CLI.

Examples:
  python main.py generate --schema schemas/default.gen.json --out planet.json
  python main.py render   --data planet.json --config schemas/default.render.json --out planet.png
  python main.py all      --schema schemas/default.gen.json --config schemas/default.render.json \
                          --out-data planet.json --out-png planet.png
"""
import argparse

import generate as gen
import render as ren


def cmd_generate(args):
    schema = gen.load_schema(args.schema) if args.schema else {}
    planet = gen.generate(schema)
    gen.save_planet(planet, args.out)
    print(f"wrote {args.out}  size={planet['meta']['size']} seed={planet['meta']['seed']}")


def cmd_render(args):
    planet = gen.load_schema(args.data)  # planet.json is plain JSON too
    cfg = ren.load_config(args.config)
    img = ren.render(planet, cfg)
    img.save(args.out)
    print(f"wrote {args.out}  {img.size[0]}x{img.size[1]} mode={img.mode}")


def cmd_gif(args):
    planet = gen.load_schema(args.data)
    cfg = ren.load_config(args.config)
    frames = ren.render_spin(planet, cfg, frames=args.frames)
    ren.save_gif(frames, args.out, fps=args.fps)
    print(f"wrote {args.out}  {frames[0].size[0]}x{frames[0].size[1]} "
          f"{len(frames)} frames @ {args.fps}fps")


def cmd_all(args):
    schema = gen.load_schema(args.schema) if args.schema else {}
    planet = gen.generate(schema)
    gen.save_planet(planet, args.out_data)
    cfg = ren.load_config(args.config)
    img = ren.render(planet, cfg)
    img.save(args.out_png)
    print(f"wrote {args.out_data} and {args.out_png}")


def main():
    p = argparse.ArgumentParser(prog="planetgen")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="schema -> planet.json (data layer)")
    g.add_argument("--schema", help="generation schema JSON (optional; defaults used)")
    g.add_argument("--out", default="planet.json")
    g.set_defaults(func=cmd_generate)

    r = sub.add_parser("render", help="planet.json + config -> PNG (display layer)")
    r.add_argument("--data", default="planet.json")
    r.add_argument("--config", help="display config JSON (optional; defaults used)")
    r.add_argument("--out", default="planet.png")
    r.set_defaults(func=cmd_render)

    gf = sub.add_parser("gif", help="planet.json + config -> spinning GIF")
    gf.add_argument("--data", default="planet.json")
    gf.add_argument("--config", help="display config JSON (optional)")
    gf.add_argument("--out", default="planet.gif")
    gf.add_argument("--frames", type=int, default=72)
    gf.add_argument("--fps", type=int, default=12)
    gf.set_defaults(func=cmd_gif)

    a = sub.add_parser("all", help="generate + render in one shot")
    a.add_argument("--schema")
    a.add_argument("--config")
    a.add_argument("--out-data", default="planet.json")
    a.add_argument("--out-png", default="planet.png")
    a.set_defaults(func=cmd_all)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
