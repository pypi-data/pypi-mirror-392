"""Tests for ``spyrite.__main__.main`` entry point."""

from __future__ import annotations

import json

# add root dir to sys.path for imports
from pathlib import Path
from typing import Iterable, Sequence

import pytest
from PIL import Image

from spyrite.__main__ import main as spyrite_main


def _make_icon(
    directory: Path,
    name: str,
    size: tuple[int, int],
    color: Sequence[int],
    fmt: str = "PNG",
) -> Path:
    mode = "RGBA" if fmt.lower() in {"png", "gif"} else "RGB"
    fill_color: Iterable[int] = color if mode == "RGBA" else color[:3]
    img = Image.new(mode, size, fill_color)
    path = directory / f"{name}.{fmt.lower()}"
    fmt_upper = fmt.upper()
    if fmt_upper == "JPG":
        fmt_upper = "JPEG"
    img.save(path, format=fmt_upper)
    return path


def test_main_errors_when_icon_directory_is_missing(tmp_path: Path, capsys) -> None:
    missing_dir = tmp_path / "no-icons"

    with pytest.raises(SystemExit) as excinfo:
        spyrite_main([str(missing_dir)])

    assert excinfo.value.code == 2
    stderr = capsys.readouterr().err
    assert "Icon directory" in stderr
    assert str(missing_dir) in stderr


def test_main_errors_when_icon_directory_is_empty(tmp_path: Path, capsys) -> None:
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()

    with pytest.raises(SystemExit) as excinfo:
        spyrite_main([str(icons_dir)])

    assert excinfo.value.code == 2
    stderr = capsys.readouterr().err
    assert "No files found" in stderr
    assert str(icons_dir) in stderr


def test_main_generates_sprite_with_custom_options(tmp_path: Path, capsys) -> None:
    icons_dir = tmp_path / "assets"
    icons_dir.mkdir()

    icon_specs = [
        ("alpha", "png", (4, 5), (255, 0, 0, 255)),
        ("beta", "jpg", (6, 5), (0, 255, 0)),
        ("gamma", "png", (8, 5), (0, 0, 255, 255)),
    ]
    for name, fmt, size, color in icon_specs:
        _make_icon(icons_dir, name, size, color, fmt)

    output_dir = tmp_path / "output"

    icon_height = 10
    padding = 3
    max_width = 25

    exit_code = spyrite_main(
        [
            str(icons_dir),
            "--output-dir",
            str(output_dir),
            "--icon-height",
            str(icon_height),
            "--padding",
            str(padding),
            "--max-width",
            str(max_width),
        ]
    )
    assert exit_code == 0

    sprite_path = output_dir / "sprite.png"
    metadata_path = output_dir / "sprite.json"

    with Image.open(sprite_path) as sprite:
        assert sprite.size == (19, 39)

    with metadata_path.open(encoding="utf-8") as fh:
        metadata = json.load(fh)

    expected_metadata = {
        "alpha": {"x": 0, "y": 0, "width": 8, "height": icon_height, "pixelRatio": 1},
        "beta": {"x": 0, "y": 13, "width": 12, "height": icon_height, "pixelRatio": 1},
        "gamma": {"x": 0, "y": 26, "width": 16, "height": icon_height, "pixelRatio": 1},
    }

    assert metadata == expected_metadata

    stdout = capsys.readouterr().out
    assert "sprite.png|json" in stdout
