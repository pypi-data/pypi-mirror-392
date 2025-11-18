from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass
class Sprite:
    image: Image.Image
    json: dict[str, dict[str, int]]


@dataclass
class MakeSpriteOptions:
    padding: int = 2
    retina: bool = False
    icon_height: int = 32
    sprite_max_width: int = 1024


def make_sprite(
    img_paths: list[Path],
    options: MakeSpriteOptions = MakeSpriteOptions(),
) -> Sprite:
    if len(img_paths) == 0:
        raise ValueError("No icons found in the specified directory.")

    x_offset = 0
    spritejson: dict[str, dict[str, int]] = {}

    # Retina対応の場合は高さを2倍にする(幅は自動的にに調整される)
    icon_height = options.icon_height * (2 if options.retina else 1)

    # 高さが揃ったImageオブジェクトの配列
    images: list[_Icon] = []
    for path in img_paths:
        img = Image.open(path).convert("RGBA")
        img = _fix_icon_size(img, icon_height)
        images.append(_Icon(name=path.stem, image=img))

    # スプライトの配置を保存する二次元配列
    rows: list[list[_Icon]] = []

    # 1行にアイコンを詰め込んでいく
    current_row: list[_Icon] = []
    current_row_width = 0
    for img in images:
        w, h = img.image.size
        if current_row_width + w + options.padding > options.sprite_max_width:
            # max_widthを超えてしまうので次の行へ
            rows.append(current_row)
            current_row = [img]
            current_row_width = w + options.padding
            spritejson[img.name] = {
                "x": 0,
                "y": len(rows) * (icon_height + options.padding),
                "width": w,
                "height": h,
                "pixelRatio": 2 if options.retina else 1,
            }
            x_offset = w + options.padding
        else:
            current_row.append(img)
            current_row_width += w + options.padding
            spritejson[img.name] = {
                "x": x_offset,
                "y": len(rows) * (icon_height + options.padding),
                "width": w,
                "height": h,
                "pixelRatio": 2 if options.retina else 1,
            }
            x_offset += w + options.padding
    if current_row:
        # 最終行
        rows.append(current_row)

    # 行ごとにならべたアイコンを一つの画像にまとめる
    sprite_height = len(rows) * (icon_height + options.padding)
    sprite_width = 0  # 最長の行の幅
    for row in rows:
        row_width = sum(icon.image.size[0] + options.padding for icon in row)
        sprite_width = max(sprite_width, row_width)
    sprite_img = Image.new("RGBA", (sprite_width, sprite_height), (0, 0, 0, 0))
    y_offset = 0
    for row in rows:
        x_offset = 0
        for icon in row:
            sprite_img.paste(icon.image, (x_offset, y_offset))
            w, h = icon.image.size
            x_offset += w + options.padding
        y_offset += icon_height + options.padding

    sprite = Sprite(image=sprite_img, json=spritejson)
    return sprite


@dataclass
class _Icon:
    name: str
    image: Image.Image


def _fix_icon_size(icon_img: Image.Image, fixed_height: int) -> Image.Image:
    """Resize icon image to fixed height while maintaining aspect ratio."""
    w, h = icon_img.size
    if h == fixed_height:
        return icon_img

    new_w = int(w * (fixed_height / h))
    resized_img = icon_img.resize((new_w, fixed_height), Image.Resampling.LANCZOS)
    return resized_img
