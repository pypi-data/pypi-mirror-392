"""Unit tests for functions in ``spyrite.sprite``."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from spyrite.make_sprite import MakeSpriteOptions, _fix_icon_size, make_sprite


def _write_icon(
    directory: Path,
    name: str,
    size: tuple[int, int],
    color: tuple[int, int, int, int] = (255, 0, 0, 255),
) -> Path:
    path = directory / f"{name}.png"
    Image.new("RGBA", size, color).save(path)
    return path


def test_make_sprite_requires_at_least_one_icon() -> None:
    with pytest.raises(ValueError, match="No icons found"):
        make_sprite([], MakeSpriteOptions())


def test_make_sprite_wraps_rows_and_builds_metadata(tmp_path: Path) -> None:
    paths = [
        _write_icon(tmp_path, "alpha", (4, 5), (255, 0, 0, 255)),
        _write_icon(tmp_path, "beta", (6, 5), (0, 255, 0, 255)),
        _write_icon(tmp_path, "gamma", (2, 5), (0, 0, 255, 255)),
    ]

    options = MakeSpriteOptions(padding=2, icon_height=10, sprite_max_width=15)

    sprite = make_sprite(paths, options)

    assert sprite.image.size == (14, 36)
    assert sprite.json == {
        "alpha": {"x": 0, "y": 0, "width": 8, "height": 10, "pixelRatio": 1},
        "beta": {"x": 0, "y": 12, "width": 12, "height": 10, "pixelRatio": 1},
        "gamma": {"x": 0, "y": 24, "width": 4, "height": 10, "pixelRatio": 1},
    }


def test_fix_icon_size_returns_same_image_when_height_matches() -> None:
    original = Image.new("RGBA", (8, 10), (1, 2, 3, 4))

    resized = _fix_icon_size(original, 10)

    assert resized is original
    assert resized.size == (8, 10)


def test_fix_icon_size_scales_width_proportionally() -> None:
    original = Image.new("RGBA", (6, 3), (5, 6, 7, 255))

    resized = _fix_icon_size(original, 12)

    assert resized.size == (24, 12)
