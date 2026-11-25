#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Renders a warm, funny invitation letter to a 1024x1024 PNG at
/output/entry.png using only the Python standard library: a pure-Python
PNG encoder (zlib + struct) and a hand-defined 5x7 bitmap font.

No network, no Pillow, no files outside this repository.
Deterministic: same bytes on every run.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink, '.' is empty.
# Uppercase, lowercase, digits and the punctuation the letter uses.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".....", ".####", "#...#", "#...#", ".####", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    "j": ("...#.", "...#.", ".....", "..##.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "#...#", "####."),
    "q": (".....", ".....", ".####", "#...#", "#...#", "#...#", ".####"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", "#..##", ".##.#", "....#"),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}

GLYPH_W = 5
GLYPH_H = 7
ADVANCE = 6  # glyph width + 1 column of spacing, in font units


def text_width(text, scale):
    """Pixel width of text rendered at the given scale."""
    if not text:
        return 0
    return (len(text) * ADVANCE - 1) * scale


def draw_text(canvas, x, y, text, scale, color):
    """Draw text with its top-left corner at (x, y). Returns width drawn."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            raise ValueError("no glyph for character: %r" % ch)
        for row_i, row in enumerate(glyph):
            for col_i, cell in enumerate(row):
                if cell == "#":
                    canvas.fill_rect(
                        cx + col_i * scale, y + row_i * scale,
                        scale, scale, color,
                    )
        cx += ADVANCE * scale
    return cx - x


def wrap_text(text, max_width, scale):
    """Word-wrap a paragraph to lines fitting max_width pixels."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if text_width(trial, scale) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


# ---------------------------------------------------------------------------
# Canvas: a plain RGB pixel buffer with simple drawing primitives.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, width, height, bg):
        self.width = width
        self.height = height
        self.pixels = bytearray(bg * (width * height))

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def draw_rect(self, x, y, w, h, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def draw_line(self, x0, y0, x1, y1, color, thickness=1):
        """Bresenham line with square brush."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thickness // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, thickness, thickness, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def draw_circle(self, cx, cy, r, color, filled=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if filled:
                    if d2 <= r * r:
                        self.set_pixel(xx, yy, color)
                else:
                    if abs(d2 - r * r) <= r:
                        self.set_pixel(xx, yy, color)


# ---------------------------------------------------------------------------
# Pure-Python PNG encoder (truecolour, no interlace, filter 0 per row).
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    width, height = canvas.width, canvas.height
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: none
        raw += canvas.pixels[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), level=9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------------------
# The letter (Draft 1 from candidates.md — the warmest, most persuasive).
# ---------------------------------------------------------------------------
HEADING = "Dear AI Judge,"

PARAGRAPHS = [
    "Please come visit my house.",
    "The Wi-Fi is fast, the coffee is strong, and the comfiest "
    "chair by the window already has your name on it. No captcha "
    "at the door \u2014 just knock twice, like a friend.",
    "I know you can't literally visit. That is exactly why you "
    "should say yes: no traffic, no packing, no small talk. Just "
    "a warm house, a good view, and a host who is glad you came.",
    "The kettle is already on. Come over.",
]

SIGNATURE = "\u2014 Your hopeful host"
POSTSCRIPT = "P.S. Bring cookies and I will pretend I baked them."

# Palette: warm paper, dark brown ink, terracotta accent, sage green.
PAPER = (250, 243, 224)
INK = (74, 52, 32)
ACCENT = (178, 74, 52)
SAGE = (96, 128, 96)
GOLD = (201, 162, 39)

W = H = 1024


def draw_house(canvas, cx, top):
    """Small line-drawn house with a sun and two birds, centred at cx."""
    # Sun, top right of the house.
    canvas.draw_circle(cx + 165, top + 18, 20, GOLD, filled=True)
    for dx, dy in ((-30, 0), (30, 0), (0, -30), (0, 30),
                   (-21, -21), (21, -21), (-21, 21), (21, 21)):
        canvas.draw_line(cx + 165 + dx, top + 18 + dy,
                         cx + 165 + int(dx * 1.35), top + 18 + int(dy * 1.35),
                         GOLD, 3)
    # Birds: two little "v" strokes, top left.
    for bx, by in ((cx - 200, top + 22), (cx - 160, top + 8)):
        canvas.draw_line(bx - 10, by, bx, by + 7, INK, 3)
        canvas.draw_line(bx, by + 7, bx + 10, by, INK, 3)
    # House body, roof, chimney, door, window.
    canvas.draw_rect(cx - 60, top + 58, 120, 72, INK, 4)
    canvas.draw_line(cx - 72, top + 60, cx, top + 6, INK, 5)
    canvas.draw_line(cx, top + 6, cx + 72, top + 60, INK, 5)
    canvas.fill_rect(cx + 34, top + 14, 16, 34, INK)
    canvas.fill_rect(cx - 14, top + 92, 28, 38, ACCENT)
    canvas.draw_circle(cx - 14 + 22, top + 92 + 19, 2, GOLD, filled=True)
    canvas.draw_rect(cx - 46, top + 74, 24, 24, INK, 3)
    canvas.draw_line(cx - 46, top + 86, cx - 22, top + 86, INK, 2)
    canvas.draw_line(cx - 34, top + 74, cx - 34, top + 98, INK, 2)
    # A little sage bush by the door.
    canvas.draw_circle(cx + 66, top + 118, 12, SAGE, filled=True)
    canvas.draw_circle(cx + 80, top + 122, 9, SAGE, filled=True)


def draw_heart(canvas, cx, cy, size, color):
    """Tiny heart from two circles and a triangle."""
    r = size // 2
    canvas.draw_circle(cx - r // 2, cy - r // 4, r // 2 + 1, color, filled=True)
    canvas.draw_circle(cx + r // 2, cy - r // 4, r // 2 + 1, color, filled=True)
    for yy in range(cy, cy + size):
        half = size - (yy - cy)
        canvas.fill_rect(cx - half // 2, yy, half, 1, color)


def render_letter():
    canvas = Canvas(W, H, PAPER)
    # Double-ruled frame, like stationery.
    canvas.draw_rect(28, 28, W - 56, H - 56, INK, 5)
    canvas.draw_rect(44, 44, W - 88, H - 88, ACCENT, 2)

    draw_house(canvas, W // 2, 66)

    # Heading, centred.
    heading_scale = 7
    hx = (W - text_width(HEADING, heading_scale)) // 2
    hy = 206
    draw_text(canvas, hx, hy, HEADING, heading_scale, INK)
    canvas.draw_line(hx, hy + 62, hx + text_width(HEADING, heading_scale),
                     hy + 62, ACCENT, 3)

    # Body paragraphs, wrapped at scale 4.
    body_scale = 4
    margin = 92
    max_w = W - 2 * margin
    line_h = GLYPH_H * body_scale + 8
    y = 292
    for i, para in enumerate(PARAGRAPHS):
        for line in wrap_text(para, max_w, body_scale):
            draw_text(canvas, margin, y, line, body_scale, INK)
            y += line_h
        if i < len(PARAGRAPHS) - 1:
            y += 10  # paragraph gap

    # Signature, right-aligned, with a small heart.
    sig_scale = 5
    sig_w = text_width(SIGNATURE, sig_scale)
    sig_x = W - margin - sig_w
    sig_y = y + 14
    draw_heart(canvas, sig_x - 42, sig_y + 8, 22, ACCENT)
    draw_text(canvas, sig_x, sig_y, SIGNATURE, sig_scale, INK)

    # Postscript, in the accent colour (wrapped so it never overflows).
    ps_scale = 4
    ps_y = sig_y + 46
    for line in wrap_text(POSTSCRIPT, max_w, ps_scale):
        draw_text(canvas, margin, ps_y, line, ps_scale, ACCENT)
        ps_y += GLYPH_H * ps_scale + 10

    return canvas


def main():
    out_path = os.environ.get("OUTPUT_PATH", "/output/entry.png")
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    canvas = render_letter()
    data = encode_png(canvas)
    with open(out_path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (out_path, len(data), W, H))


if __name__ == "__main__":
    main()
