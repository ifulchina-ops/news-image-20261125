#!/usr/bin/env python3
"""The World Today - 25 November 2026.

A program/v1 entry for make.fun's news-image-20261125: it draws one
1024x1024 front-page image summing up the world's news of Wednesday
25 November 2026 and writes it to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png). Pure Python standard library: the PNG
bytes are encoded by hand (struct + zlib), the lettering is a small
5x7 bitmap font defined below, and every picture is drawn from
rectangles, circles, lines and polygons. No network, no files read,
no randomness: two runs write byte-identical output.

The stories are the day's real headlines as reported on 25 Nov 2026:
Ukraine's strikes on Russian ships (Gulf of Finland and off Libya),
NATO early-warning aircraft for Poland, naval mines hitting three
tankers in the Strait of Hormuz, the Houthi strike on Riyadh's
tallest tower, Nvidia's $1 trillion day as Huang returns as CEO,
and Trump's Thanksgiving turkey pardon - plus a ticker of the other
stories of the day.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# Palette: newsprint cream, ink navy, gold rules, red kickers.
CREAM = (246, 241, 229)
WHITE = (255, 255, 255)
INK = (24, 32, 44)
NAVY = (16, 35, 63)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
GREY = (74, 80, 90)
SKY = (173, 216, 230)
SEA = (30, 90, 140)
DEEP = (18, 64, 110)
HULL = (40, 50, 66)
ORANGE = (255, 140, 0)
YELLOW = (255, 200, 0)
GREEN = (34, 139, 34)
BROWN = (122, 74, 30)
TAN = (176, 120, 60)
STEEL = (120, 130, 145)

# 5x7 bitmap font: one line per glyph, seven 5-bit rows separated by
# spaces. Only capitals, digits and the punctuation the headlines use.
FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00110 01000 10000 11111",
    "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000",
    ".": "00000 00000 00000 00000 00000 01100 01100",
    ",": "00000 00000 00000 00000 01100 00100 01000",
    ":": "00000 01100 01100 00000 01100 01100 00000",
    ";": "00000 01100 01100 00000 01100 00100 01000",
    "'": "00100 00100 01000 00000 00000 00000 00000",
    "-": "00000 00000 00000 01110 00000 00000 00000",
    "\u2014": "00000 00000 00000 11111 00000 00000 00000",
    "!": "00100 00100 00100 00100 00100 00000 00100",
    "?": "01110 10001 00001 00110 00100 00000 00100",
    "/": "00001 00010 00010 00100 01000 01000 10000",
    "(": "00010 00100 01000 01000 01000 00100 00010",
    ")": "01000 00100 00010 00010 00010 00100 01000",
    "%": "11001 11010 00010 00100 01000 01011 10011",
    "$": "00100 01111 10100 01110 00101 11110 00100",
    "\u00b7": "00000 00000 00000 01100 01100 00000 00000",
    "+": "00000 00100 00100 11111 00100 00100 00000",
    "&": "01100 10010 10100 01000 10101 10010 01101",
}


class Canvas:
    """An RGB raster with small drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.rows = []
        for _ in range(h):
            row = bytearray(w * 3)
            for x in range(w):
                row[x * 3] = bg[0]
                row[x * 3 + 1] = bg[1]
                row[x * 3 + 2] = bg[2]
            self.rows.append(row)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            row = self.rows[y]
            row[x * 3] = c[0]
            row[x * 3 + 1] = c[1]
            row[x * 3 + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            row = self.rows[yy]
            for xx in range(x0, x1):
                row[xx * 3] = c[0]
                row[xx * 3 + 1] = c[1]
                row[xx * 3 + 2] = c[2]

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.px(x, y, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c):
        steps = max(24, int(2 * math.pi * r))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            self.px(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            f = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, f)))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def burst(self, cx, cy, r_out, r_in, n, c1, c2):
        """A starburst: n spikes alternating two colours."""
        for i in range(n * 2):
            a0 = math.pi * i / n
            a1 = math.pi * (i + 1) / n
            r = r_out if i % 2 == 0 else r_in
            tip = (int(cx + r * math.cos((a0 + a1) / 2)),
                   int(cy + r * math.sin((a0 + a1) / 2)))
            base1 = (int(cx + r_in * 0.45 * math.cos(a0)),
                     int(cy + r_in * 0.45 * math.sin(a0)))
            base2 = (int(cx + r_in * 0.45 * math.cos(a1)),
                     int(cy + r_in * 0.45 * math.sin(a1)))
            self.poly([base1, base2, tip], c1 if i % 2 == 0 else c2)
        self.disc(cx, cy, max(3, r_in // 3), YELLOW)

    # -- text ---------------------------------------------------------

    def glyph(self, ch, x, y, s, c):
        rows = FONT[ch].split(" ")
        for r, bits in enumerate(rows):
            for col, bit in enumerate(bits):
                if bit == "1":
                    self.rect(x + col * s, y + r * s, s, s, c)

    def text(self, s, x, y, sc, c):
        cx = x
        for ch in s:
            self.glyph(ch, cx, y, sc, c)
            cx += 6 * sc
        return cx

    def text_w(self, s, sc):
        return len(s) * 6 * sc - sc if s else 0

    def text_c(self, s, cx, y, sc, c):
        self.text(s, cx - self.text_w(s, sc) // 2, y, sc, c)

    def wrap(self, s, sc, maxw):
        lines = []
        cur = ""
        for word in s.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, sc) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, lines, x, y, sc, c, lh):
        for ln in lines:
            self.text(ln, x, y, sc, c)
            y += lh
        return y


def panel(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.frame(x, y, w, h, INK, 2)


def story(cv, x, y, w, h, kicker, headline, standfirst, art_top, art_fn):
    """A news panel: kicker, headline, standfirst, then a picture strip."""
    pad = 14
    ix = x + pad
    iw = w - 2 * pad
    cy = y + 14
    cv.text(kicker, ix, cy, 2, RED)
    cy += 24
    head_lines = cv.wrap(headline, 3, iw)
    cy = cv.para(head_lines, ix, cy, 3, INK, 27)
    cy += 4
    body_lines = cv.wrap(standfirst, 2, iw)
    cv.para(body_lines, ix, cy, 2, GREY, 20)
    art_fn(cv, x + pad, art_top, w - 2 * pad)
    cv.frame(x, y, w, h, INK, 2)


def art_lead(cv, x, y, w):
    """Gulf of Finland: a cargo ship under a drone strike at sea."""
    h = 240
    cv.rect(x, y, w, 118, SKY)
    cv.disc(x + 52, y + 34, 22, YELLOW)
    cv.rect(x, y + 118, w, h - 118, SEA)
    cv.rect(x, y + 118, w, 6, DEEP)
    # explosion over the ship
    cv.burst(x + w - 78, y + 52, 46, 20, 8, ORANGE, YELLOW)
    # drone
    cv.rect(x + 108, y + 58, 26, 8, HULL)
    cv.line(x + 100, y + 54, x + 142, y + 54, HULL)
    cv.line(x + 112, y + 66, x + 112, y + 78, HULL)
    cv.line(x + 130, y + 66, x + 130, y + 78, HULL)
    # ship: hull, cabins, funnel, mast
    cv.poly([(x + 18, y + 178), (x + w - 18, y + 178),
             (x + w - 44, y + 214), (x + 44, y + 214)], HULL)
    cv.rect(x + 96, y + 150, 74, 28, WHITE)
    cv.rect(x + 182, y + 142, 26, 36, RED)
    cv.line(x + 230, y + 178, x + 230, y + 128, HULL)
    cv.poly([(x + 230, y + 128), (x + 258, y + 138), (x + 230, y + 148)], RED)
    # waves
    for wx, wy in ((x + 30, y + 222), (x + 150, y + 230),
                   (x + 250, y + 222), (x + 60, y + 200)):
        cv.line(wx, wy, wx + 34, wy, WHITE)
    cv.line(x + 200, y + 226, x + 244, y + 226, WHITE)


def art_radar(cv, x, y, w):
    """NATO early-warning radar sweeping, with a jet above it."""
    cx, cy = x + 90, y + 36
    for r in (14, 28, 40):
        cv.ring(cx, cy, r, GREEN)
    cv.line(cx, cy, cx + 28, cy - 28, GREEN)
    cv.disc(cx, cy, 4, GREEN)
    # jet, side view: fuselage, nose, wings, tail fin
    jx, jy = x + w - 150, y + 6
    cv.rect(jx, jy + 14, 58, 5, HULL)
    cv.poly([(jx + 58, jy + 14), (jx + 74, jy + 16), (jx + 58, jy + 19)],
            HULL)
    cv.poly([(jx + 20, jy + 14), (jx + 32, jy), (jx + 40, jy + 14)], HULL)
    cv.poly([(jx + 20, jy + 19), (jx + 32, jy + 32), (jx + 40, jy + 19)],
            HULL)
    cv.poly([(jx + 4, jy + 14), (jx + 12, jy + 4), (jx + 16, jy + 14)],
            HULL)
    cv.text("AWACS", jx + 6, jy + 38, 1, GREY)


def art_tanker(cv, x, y, w):
    """An oil tanker on the strait, and a spiked naval mine."""
    cv.rect(x, y, w, 46, SEA)
    cv.poly([(x + 8, y + 8), (x + w - 96, y + 8),
             (x + w - 116, y + 34), (x + 28, y + 34)], HULL)
    cv.rect(x + 30, y + 12, 30, 10, WHITE)
    cv.rect(x + 66, y + 12, 18, 10, RED)
    # mine: black spiked ball
    mx, my = x + w - 52, y + 8
    for a in range(0, 360, 30):
        r = math.radians(a)
        cv.line(int(mx + 10 * math.cos(r)), int(my + 10 * math.sin(r)),
                int(mx + 20 * math.cos(r)), int(my + 20 * math.sin(r)), INK)
    cv.disc(mx, my, 12, INK)
    cv.disc(mx - 4, my - 4, 3, STEEL)


def art_tower(cv, x, y, w):
    """Riyadh's tallest tower, struck at the top."""
    tx = x + w // 2 - 26
    cv.rect(tx, y + 22, 52, 52, STEEL)
    cv.rect(tx + 8, y + 8, 36, 16, STEEL)
    cv.line(tx + 26, y + 8, tx + 26, y - 8, INK)
    for wy in range(y + 28, y + 70, 10):
        for wx in (tx + 6, tx + 20, tx + 34):
            cv.rect(wx, wy, 8, 5, NAVY)
    cv.burst(tx + 26, y - 2, 22, 10, 6, ORANGE, YELLOW)


def art_chip(cv, x, y, w):
    """A chip with a rising market arrow."""
    cx = x + 52
    cv.rect(cx - 34, y + 6, 68, 56, NAVY)
    cv.rect(cx - 20, y + 20, 40, 28, GOLD)
    for i in range(5):
        cv.rect(cx - 34 + i * 14, y - 2, 6, 8, INK)
        cv.rect(cx - 34 + i * 14, y + 62, 6, 8, INK)
    cv.line(x + 118, y + 62, x + 158, y + 34, GREEN)
    cv.line(x + 158, y + 34, x + 196, y + 40, GREEN)
    cv.line(x + 196, y + 40, x + 232, y + 8, GREEN)
    cv.poly([(x + 232, y + 8), (x + 214, y + 8), (x + 232, y + 26)], GREEN)
    cv.text("+31.5%", x + 128, y + 60, 2, GREEN)


def art_turkey(cv, x, y, w):
    """A pardoned turkey: fanned tail, brown body, small head."""
    cx = x + w // 2
    for i, a in enumerate((-52, -26, 0, 26, 52)):
        r = math.radians(a)
        tx = int(cx + 34 * math.sin(r))
        ty = int(y + 46 - 34 * math.cos(r))
        cv.ellipse(tx, ty, 12, 20, TAN if i % 2 else BROWN)
    cv.ellipse(cx, y + 52, 30, 24, BROWN)
    cv.disc(cx + 22, y + 22, 12, BROWN)
    cv.poly([(cx + 32, y + 20), (cx + 44, y + 24), (cx + 32, y + 28)], ORANGE)
    cv.disc(cx + 26, y + 18, 2, WHITE)
    cv.line(cx - 8, y + 74, cx - 8, y + 80, ORANGE)
    cv.line(cx + 8, y + 74, cx + 8, y + 80, ORANGE)


def build():
    cv = Canvas(W, H, CREAM)

    # Masthead.
    cv.rect(28, 28, 968, 100, NAVY)
    cv.text_c("THE WORLD TODAY", 512, 40, 7, WHITE)
    cv.text_c("WEDNESDAY \u00b7 25 NOVEMBER 2026", 512, 100, 2, GOLD)
    cv.rect(28, 132, 968, 4, GOLD)

    # Lead story: Ukraine strikes Russian ships at sea.
    panel(cv, 28, 144, 968, 272)
    cv.text("UKRAINE STRIKES AT SEA", 48, 160, 2, RED)
    cv.para(["UKRAINE HITS RUSSIAN", "SHIPS AT SEA"], 48, 188, 4, INK, 36)
    cv.para(cv.wrap(
        "ZELENSKYY CONFIRMS THE GULF OF FINLAND DRONE STRIKE \u2014 AND A "
        "WARSHIP SUNK OFF BENGHAZI, LIBYA. NORWAY URGES CAUTION.",
        2, 580), 48, 268, 2, GREY, 20)
    art_lead(cv, 648, 160, 328)

    # Second row: NATO / Hormuz.
    panel(cv, 28, 428, 474, 220)
    story(cv, 28, 428, 474, 220, "NATO WATCHES POLAND", "EARLY-WARNING AIRCRAFT FOR POLAND", "NATO TO SEND THE JETS AFTER MISSILES FELL ON POLAND.", 566, art_radar)
    panel(cv, 522, 428, 474, 220)
    story(cv, 522, 428, 474, 220, "MINES IN THE STRAIT", "THREE TANKERS HIT IN THE STRAIT OF HORMUZ", "IRAN'S GUARD NAVY SAYS MINES STRUCK THREE SHIPS.", 566, art_tanker)

    # Third row: Riyadh / Nvidia / turkeys.
    panel(cv, 28, 660, 312, 220)
    story(cv, 28, 660, 312, 220, "HOUTHIS HIT RIYADH", "TOWER STRIKE WOUNDS 11", "MISSILE HITS RIYADH TOWER. REBELS NEAR ADEN.", 800, art_tower)
    panel(cv, 356, 660, 312, 220)
    story(cv, 356, 660, 312, 220, "NVIDIA'S $1 TRILLION DAY", "HUANG IS BACK \u2014 SHARES UP 31.5%", "NVIDIA REGAINS NEARLY $1 TRILLION IN A DAY.", 800, art_chip)
    panel(cv, 684, 660, 312, 220)
    story(cv, 684, 660, 312, 220, "TURKEYS SPARED", "TRUMP PARDONS TWO TURKEYS", "FREEDOM AND FEATHERS LIVE. GIULIANI HONORED.", 800, art_turkey)

    # Ticker: the rest of the day.
    cv.rect(28, 892, 968, 60, NAVY)
    cv.text_c("ALSO TODAY \u2014 NEPAL QUAKE 5.6 \u00b7 SARKOZY CASE TO TRIAL",
              512, 900, 2, GOLD)
    cv.text_c("700,000 RUSSIAN SOLDIERS KILLED, STUDY FINDS \u00b7 "
              "ENGLAND BEAT AUSTRALIA IN T20", 512, 922, 2, WHITE)

    # Footer: where it came from.
    cv.text_c("HEADLINES AS REPORTED ON 25 NOVEMBER 2026 \u00b7 "
              "REUTERS / RFE-RL / AP", 512, 968, 2, GREY)
    return cv


def png_bytes(cv):
    raw = b"".join(b"\x00" + bytes(row) for row in cv.rows)

    def chunk(tag, data):
        body = tag + data
        return (struct.pack(">I", len(data)) + body +
                struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    data = png_bytes(build())
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, sha256 %s)"
          % (path, len(data), zlib.crc32(data) & 0xFFFFFFFF))
    import hashlib
    print("sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
