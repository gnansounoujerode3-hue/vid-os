#!/usr/bin/env python3
"""Build the editable paper-style Our Work showcase frame and rounded masks.

Requires Pillow: python3 -m pip install Pillow
"""
from __future__ import annotations

import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
W, H = 720, 1280
MAIN = (228, 224, 468, 832)  # x, y, w, h; 9:16
SOURCE = (18, 650, 180, 320)

PAPER = (247, 246, 241, 255)
INK = (25, 27, 28, 255)
MUTED = (110, 110, 104, 255)
PURPLE = (123, 47, 238, 255)
GREEN = (34, 94, 72, 255)


def font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / filename), size)


def centered(draw: ImageDraw.ImageDraw, y: int, text: str, face: ImageFont.FreeTypeFont,
             color: tuple[int, int, int, int], tracking: int = 0) -> None:
    if tracking == 0:
        box = draw.textbbox((0, 0), text, font=face)
        draw.text(((W - (box[2] - box[0])) / 2, y), text, font=face, fill=color)
        return
    widths = [draw.textlength(char, font=face) for char in text]
    x = (W - sum(widths) - tracking * (len(text) - 1)) / 2
    for char, width in zip(text, widths):
        draw.text((round(x), y), char, font=face, fill=color)
        x += width + tracking


def card_shadow(image: Image.Image, rect: tuple[int, int, int, int], radius: int) -> None:
    x, y, w, h = rect
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x + 7, y + 13, x + w + 8, y + h + 14),
                         radius=radius + 4, fill=(23, 30, 28, 50))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(15)))


def build_layout() -> None:
    image = Image.new("RGBA", (W, H), PAPER)
    draw = ImageDraw.Draw(image, "RGBA")

    # Quiet paper grain and fine diagonal texture, kept low contrast behind the footage.
    for x in range(-H, W + H, 42):
        draw.line((x, 0, x + H, H), fill=(169, 166, 156, 9), width=1)
    rng = random.Random(26)
    for _ in range(1500):
        px, py = rng.randrange(W), rng.randrange(H)
        shade = rng.choice((165, 177, 189, 213))
        draw.point((px, py), fill=(shade, shade, shade - 3, rng.randrange(8, 24)))

    # Brand-like accents without copying the reference studio's logo or handle.
    draw.arc((592, 112, 792, 312), 72, 276, fill=(123, 47, 238, 165), width=10)
    draw.arc((-100, 992, 286, 1166), 192, 342, fill=(34, 94, 72, 238), width=13)
    draw.line((0, 1092, 720, 1092), fill=(34, 94, 72, 210), width=6)
    draw.line((0, 1100, 720, 1100), fill=(255, 255, 255, 140), width=2)

    # Minimal custom edit mark.
    draw.rounded_rectangle((333, 25, 387, 68), radius=12, outline=INK, width=3)
    draw.line((345, 54, 356, 39, 365, 49, 374, 36), fill=PURPLE, width=4, joint="curve")
    draw.ellipse((370, 51, 378, 59), fill=GREEN)
    centered(draw, 83, "OUR WORK", font("InstrumentSans-Bold.ttf", 50), INK)
    centered(draw, 143, "01  /  PRIORITIES  —  ENGLISH SOCIAL EDIT", font("GeistMono-Regular.ttf", 15), MUTED, 1)
    draw.line((282, 180, 438, 180), fill=PURPLE, width=4)

    # Floating video cards with soft shadows; transparent windows are filled by FFmpeg.
    for rect, radius in ((MAIN, 30), (SOURCE, 22)):
        x, y, w, h = rect
        card_shadow(image, rect, radius)
        draw = ImageDraw.Draw(image, "RGBA")
        draw.rounded_rectangle((x - 7, y - 7, x + w + 7, y + h + 7),
                               radius=radius + 7, fill=(255, 255, 255, 255),
                               outline=(230, 229, 221, 255), width=2)
        # Clear a rounded window so the synchronized footage can show through.
        draw.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=radius,
                               fill=(0, 0, 0, 0))
        draw.rounded_rectangle((x - 1, y - 1, x + w, y + h), radius=radius + 1,
                               outline=(255, 255, 255, 235), width=3)

    draw = ImageDraw.Draw(image, "RGBA")
    # Small labels, patterned after the reference's before/after edit markers.
    draw.rounded_rectangle((SOURCE[0], SOURCE[1] - 37, SOURCE[0] + 139, SOURCE[1] - 7),
                           radius=14, fill=INK)
    draw.text((SOURCE[0] + 12, SOURCE[1] - 33), "SOURCE CUT", font=font("GeistMono-Regular.ttf", 13), fill=(255, 255, 255, 255))
    draw.rounded_rectangle((MAIN[0], MAIN[1] - 37, MAIN[0] + 144, MAIN[1] - 7),
                           radius=14, fill=PURPLE)
    draw.text((MAIN[0] + 12, MAIN[1] - 33), "MOTION EDIT", font=font("GeistMono-Regular.ttf", 13), fill=(255, 255, 255, 255))

    # A restrained directional cue links the source preview to the final treatment.
    draw.line((198, 814, 216, 814), fill=PURPLE, width=3)
    draw.polygon(((216, 807), (226, 814), (216, 821)), fill=PURPLE)

    # Footer block and thin separator.
    draw.line((28, 1150, 692, 1150), fill=(189, 187, 176, 255), width=2)
    draw.text((30, 1172), "CUT  ·  CAPTIONS  ·  MOTION", font=font("GeistMono-Regular.ttf", 16), fill=INK)
    draw.text((30, 1201), "ORIGINAL VOICE  /  ENGLISH TEXT", font=font("GeistMono-Regular.ttf", 12), fill=MUTED)
    badge = "9:16  /  01"
    face = font("GeistMono-Regular.ttf", 13)
    bx = 692 - draw.textlength(badge, font=face)
    draw.rounded_rectangle((bx - 13, 1170, 692, 1200), radius=14, fill=(238, 234, 249, 255))
    draw.text((bx, 1177), badge, font=face, fill=PURPLE)

    image.save(ASSETS / "our-work-layout.png", optimize=True)


def build_mask(path: Path, width: int, height: int, radius: int) -> None:
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    mask.save(path, optimize=True)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    build_layout()
    build_mask(ASSETS / "our-work-main-mask.png", MAIN[2], MAIN[3], 30)
    build_mask(ASSETS / "our-work-source-mask.png", SOURCE[2], SOURCE[3], 22)
    print("Built Our Work layout and rounded masks in", ASSETS)


if __name__ == "__main__":
    main()
