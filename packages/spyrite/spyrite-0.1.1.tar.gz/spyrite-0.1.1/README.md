# spyrite

Python library to create MapLibre/Mapbox compatible sprite file.

## Features

- Few dependencies (only Pillow)
- Input: Image files of icons (no SVG support)
  - Parameters:
    - max_width: Maximum width of the sprite image, default is 1024
    - icon_height: Height of each icon, default is 32
    - padding: Gap between icons, default is 2
- Output: MapLibre/Mapbox compatible sprite files (sprite.png and sprite.json)

## Sprite Specification

- Height of each icon is uniform (icon_height)
- Width of each icon is proportional to the original aspect ratio
- Total width of the sprite image does not exceed max_width in almost all cases
  - If an icon is too wide to fit in the remaining space of the current row, it is moved to the next row
  - If an icon with fixed height of icon_height is wider than max_width, the icon won't be resized and set to a row as is. Then, width of the sprite image may exceed max_width.

## CLI Usage

```bash
uv sync
uv run python -m spyrite --help
```

```planetext
usage: __main__.py [-h] [--output-dir OUTPUT_DIR] [--padding PADDING] [--icon-height ICON_HEIGHT]
                   [--max-width MAX_WIDTH]
                   icons_dir

Generate a MapLibre/Mapbox compatible sprite sheet from PNG icons.

positional arguments:
  icons_dir             Directory that contains source icons

options:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR
                        Directory to write output files to (default: current directory)
  --padding PADDING     XY gap (in px) inserted between icons (default: 2)
  --icon-height ICON_HEIGHT
                        Height (in px) each icon is resized to (default: 32)
  --max-width MAX_WIDTH
                        Maximum width (in px) of the generated sprite sheet (default: 1024)
```

```bash
uv run python -m spyrite icons_dir
# This will generate sprite.png and sprite.json in the current directory

uv run python -m spyrite icons_dir --output-dir output_dir --max-width 2048 --icon-height 128
# This will generate sprite.png and sprite.json in output_dir with specified parameters
```

### Example

```bash
# convert maki-icons https://github.com/mapbox/maki
uv run python -m spyrite sample/maki-icons --output-dir sample
```

![](sample/sprite.png)*sample/sprite.png*
[sample/sprite.json](sample/sprite.json)
