#!/usr/bin/env python3
"""Generate retro-style beveled block textures for STANRIS (Tetris)."""
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "textures")
os.makedirs(OUT_DIR, exist_ok=True)

BLOCK_SIZE = 32

# Classic tetris-ish colors (bright, saturated)
PIECES = {
    "I": (0, 240, 240),      # Cyan
    "O": (240, 240, 0),      # Yellow
    "T": (160, 0, 240),      # Purple
    "S": (0, 240, 0),        # Green
    "Z": (240, 0, 0),        # Red
    "J": (0, 0, 240),        # Blue
    "L": (240, 160, 0),      # Orange
}

def lighten(c, amt=70):
    return tuple(min(255, v + amt) for v in c)

def darken(c, amt=70):
    return tuple(max(0, v - amt) for v in c)

def make_block(name, base_color, size=BLOCK_SIZE):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Base fill
    draw.rectangle([0, 0, size-1, size-1], fill=base_color)

    # Inner bevel (classic "3D" block look)
    b = 3  # bevel width
    # Top + left highlight (lighter)
    hl = lighten(base_color, 85)
    draw.rectangle([1, 1, size-2, b], fill=hl)                 # top
    draw.rectangle([1, 1, b, size-2], fill=hl)                 # left

    # Bottom + right shadow (darker)
    sh = darken(base_color, 80)
    draw.rectangle([1, size-1-b, size-2, size-2], fill=sh)     # bottom
    draw.rectangle([size-1-b, 1, size-2, size-2], fill=sh)     # right

    # Small inner highlight for plastic shine
    shine = lighten(base_color, 120)
    draw.rectangle([b+1, b+1, b+6, b+3], fill=shine)

    # Subtle inner dark for depth
    inner_dark = darken(base_color, 40)
    draw.rectangle([b+2, size-b-4, size-b-3, size-b-2], fill=inner_dark)

    # Strong black outline (retro)
    outline = (10, 10, 10, 255)
    draw.rectangle([0, 0, size-1, size-1], outline=outline, width=1)

    # Tiny grid dots in center (old CRT feel)
    dot = darken(base_color, 55)
    cx, cy = size // 2, size // 2
    for dx in (-3, 0, 3):
        for dy in (-3, 0, 3):
            draw.rectangle([cx+dx-1, cy+dy-1, cx+dx, cy+dy], fill=dot)

    path = os.path.join(OUT_DIR, f"block_{name}.png")
    img.save(path, "PNG")
    print(f"Generated {path}")
    return path

def make_ghost(size=BLOCK_SIZE):
    """Semi-transparent white ghost block used for preview via tint."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Very light fill
    draw.rectangle([2, 2, size-3, size-3], fill=(255, 255, 255, 90))
    # Outline
    draw.rectangle([1, 1, size-2, size-2], outline=(255, 255, 255, 160), width=1)
    path = os.path.join(OUT_DIR, "block_ghost.png")
    img.save(path, "PNG")
    print(f"Generated {path}")

def make_background():
    """Subtle playfield background texture."""
    w, h = 320, 640  # 10x20 * 32
    img = Image.new("RGBA", (w, h), (8, 8, 12, 255))
    draw = ImageDraw.Draw(img)

    # Very faint grid
    grid_col = (22, 22, 30, 255)
    for x in range(0, w, 32):
        draw.line([(x, 0), (x, h)], fill=grid_col, width=1)
    for y in range(0, h, 32):
        draw.line([(0, y), (w, y)], fill=grid_col, width=1)

    # Slight vignette / scanlines
    for y in range(0, h, 3):
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, 22), width=1)

    path = os.path.join(OUT_DIR, "board_bg.png")
    img.save(path, "PNG")
    print(f"Generated {path}")

if __name__ == "__main__":
    for name, color in PIECES.items():
        make_block(name, color)
    make_ghost()
    make_background()
    print("\nAll textures generated in", OUT_DIR)