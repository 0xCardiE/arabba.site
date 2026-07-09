#!/usr/bin/env python3
"""Generate the 1200×630 Open Graph share image from the site logo.

Run after updating the logo or share copy:

    python3 scripts/generate-og-share.py
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "og-share.png"
LOGO = ROOT / "images" / "logo.png"

WIDTH = 1200
HEIGHT = 630

BRAND_ORANGE = (253, 105, 49)
BRAND_BLUE = (0, 98, 160)
TEXT_DARK = (51, 51, 51)
TEXT_MUTED = (119, 119, 119)
BG_TOP = (255, 255, 255)
BG_BOTTOM = (245, 245, 245)

TITLE = "Servis računala i laptopa"
SUBTITLE = "Rijeka · PC i Mac · od 1995."
DOMAIN = "arabba.hr"


def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_gradient_bg(draw):
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        color = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * ratio) for i in range(3))
        draw.line([(0, y), (WIDTH, y)], fill=color)


def main():
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), BG_TOP)
    draw = ImageDraw.Draw(canvas)
    draw_gradient_bg(draw)

    draw.rectangle([(0, 0), (WIDTH, 8)], fill=BRAND_ORANGE)
    draw.rectangle([(0, HEIGHT - 8), (WIDTH, HEIGHT)], fill=BRAND_ORANGE)

    logo = Image.open(LOGO).convert("RGBA")
    logo_target_w = 520
    scale = logo_target_w / logo.width
    logo = logo.resize((logo_target_w, int(logo.height * scale)), Image.Resampling.LANCZOS)

    logo_x = (WIDTH - logo.width) // 2
    logo_y = 150
    canvas.paste(logo, (logo_x, logo_y), logo)

    title_font = load_font(54, bold=True)
    subtitle_font = load_font(34)
    domain_font = load_font(30, bold=True)

    text_y = logo_y + logo.height + 48
    for text, font, color in (
        (TITLE, title_font, TEXT_DARK),
        (SUBTITLE, subtitle_font, TEXT_MUTED),
        (DOMAIN, domain_font, BRAND_ORANGE),
    ):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(((WIDTH - text_w) // 2, text_y), text, font=font, fill=color)
        text_y += (bbox[3] - bbox[1]) + 18

    accent_y = logo_y + logo.height + 24
    draw.line([(420, accent_y), (780, accent_y)], fill=BRAND_BLUE, width=3)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({WIDTH}×{HEIGHT})")


if __name__ == "__main__":
    main()
