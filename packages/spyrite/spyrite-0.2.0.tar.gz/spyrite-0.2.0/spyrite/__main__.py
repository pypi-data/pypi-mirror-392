from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from spyrite.make_sprite import MakeSpriteOptions, make_sprite

_DEFAULT_OPTIONS = MakeSpriteOptions()


def _non_negative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("Value must be zero or greater.")
    return number


def _positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Value must be a positive integer.")
    return number


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a MapLibre/Mapbox compatible sprite sheet from PNG icons.",
    )
    parser.add_argument(
        "icons_dir",
        type=Path,
        help="Directory that contains source icons",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=".",
        help="Directory to write output files to (default: current directory)",
    )
    parser.add_argument(
        "--padding",
        type=_non_negative_int,
        default=_DEFAULT_OPTIONS.padding,
        help="XY gap (in px) inserted between icons (default: %(default)s)",
    )
    parser.add_argument(
        "--icon-height",
        type=_positive_int,
        default=_DEFAULT_OPTIONS.icon_height,
        help="Height (in px) each icon is resized to (default: %(default)s)",
    )
    parser.add_argument(
        "--max-width",
        type=_positive_int,
        default=_DEFAULT_OPTIONS.sprite_max_width,
        help="Maximum width (in px) of the generated sprite sheet (default: %(default)s)",
    )
    parser.add_argument(
        "--retina",
        action="store_true",
        default=_DEFAULT_OPTIONS.retina,
        help="Flag indicating that the output should be treated as retina assets.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    icons_dir = args.icons_dir.expanduser()
    if not icons_dir.exists():
        parser.error(f"Icon directory '{icons_dir}' does not exist.")
    if not icons_dir.is_dir():
        parser.error(f"'{icons_dir}' is not a directory.")

    # glob all image files: png, jpg, jpeg, gif
    img_paths = (
        list(icons_dir.glob("*.png"))
        + list(icons_dir.glob("*.jpg"))
        + list(icons_dir.glob("*.jpeg"))
        + list(icons_dir.glob("*.gif"))
    )
    img_paths.sort()
    if not img_paths:
        parser.error(f"No files found in '{icons_dir}'.")

    options = MakeSpriteOptions(
        padding=args.padding,
        retina=args.retina,
        icon_height=args.icon_height,
        sprite_max_width=args.max_width,
    )

    try:
        sprite = make_sprite(img_paths, options)
    except ValueError as exc:  # Defensive: make_sprite also validates
        parser.exit(status=1, message=f"Error: {exc}\n")

    # write files
    output_dir_path = Path(args.output_dir.expanduser())
    output_dir_path.mkdir(parents=True, exist_ok=True)
    spritejson_filename = "sprite@2x.json" if args.retina else "sprite.json"
    spritepng_filename = "sprite@2x.png" if args.retina else "sprite.png"
    sprite.image.save(output_dir_path / spritepng_filename)
    metadata_path = output_dir_path / spritejson_filename
    with metadata_path.open("w", encoding="utf-8") as fh:
        json.dump(sprite.json, fh, ensure_ascii=False)
        fh.write("\n")

    print(f"{spritepng_filename}|{spritejson_filename} written to {output_dir_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
