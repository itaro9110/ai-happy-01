#!/usr/bin/env python3
"""The Reunion -- ai-happy-01 entry.

A golden dog leaps joyfully into its owner's arms at the front
door at golden hour. Pure procedural drawing, Python stdlib only.
No text anywhere. Deterministic: fixed seed, same bytes every run.
"""
import math
import os
import random
import struct
import zlib

W = H = 1024


def out_dir():
    d = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if d:
        return d
    if os.path.isdir("/output") and os.access("/output", os.W_OK):
        return "/output"
    return "/tmp"


def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def png_bytes(rows, w, h):
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b""))


def hx(s):
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rows = [bytearray(w * 3) for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = x * 3
            self.rows[y][i:i + 3] = bytes(c)

    def blend(self, x, y, c, a):
        if a <= 0 or not (0 <= x < self.w and 0 <= y < self.h):
            return
        if a >= 1:
            self.set(x, y, c)
            return
        i = x * 3
        r = self.rows[y]
        r[i] = int(r[i] + (c[0] - r[i]) * a)
        r[i + 1] = int(r[i + 1] + (c[1] - r[i + 1]) * a)
        r[i + 2] = int(r[i + 2] + (c[2] - r[i + 2]) * a)

    def rect(self, x0, y0, x1, y1, c, a=1.0):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        if x1 <= x0 or y1 <= y0:
            return
        if a >= 1.0:
            row = bytes(c) * (x1 - x0)
            for y in range(y0, y1):
                self.rows[y][x0 * 3:x1 * 3] = row
        else:
            for y in range(y0, y1):
                for x in range(x0, x1):
                    self.blend(x, y, c, a)

    def vgrad(self, x0, x1, y0, y1, top, bot):
        for y in range(max(0, y0), min(self.h, y1)):
            t = (y - y0) / max(1, y1 - y0 - 1)
            c = tuple(int(top[i] + (bot[i] - top[i]) * t)
                      for i in range(3))
            self.rect(x0, y, x1, y + 1, c)

    def disc(self, cx, cy, r, c, a=1.0):
        r2 = r * r
        for y in range(int(cy - r), int(cy + r) + 1):
            dy = y - cy
            dx = int(math.sqrt(max(0, r2 - dy * dy)))
            self.rect(int(cx - dx), y, int(cx + dx) + 1, y + 1, c, a)

    def ellipse(self, cx, cy, rx, ry, rot, c, a=1.0):
        co, si = math.cos(rot), math.sin(rot)
        ext = int(rx + ry)
        for y in range(max(0, int(cy - ext)), min(self.h, int(cy + ext))):
            for x in range(max(0, int(cx - ext)),
                           min(self.w, int(cx + ext))):
                dx, dy = x - cx, y - cy
                u = (dx * co + dy * si) / rx
                v = (-dx * si + dy * co) / ry
                if u * u + v * v <= 1:
                    self.blend(x, y, c, a)

    def poly(self, pts, c, a=1.0):
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))),
                       min(self.h, int(max(ys)) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, int(xs[i + 1]) + 1, y + 1, c, a)

    def capsule(self, x1, y1, x2, y2, r, c, a=1.0):
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L * r, dx / L * r
        self.poly([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny),
                   (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)], c, a)
        self.disc(x1, y1, r, c, a)
        self.disc(x2, y2, r, c, a)


def arc(c, cx, cy, r, a0, a1, w, col, a=1.0):
    n = 24
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        c.disc(cx + r * math.cos(t), cy + r * math.sin(t), w, col, a)


def draw_room(c):
    # warm wall, golden hour
    c.vgrad(0, W, 0, 820, hx("F8D391"), hx("EFA964"))
    # glow spilling from the doorway
    for r, a in ((420, 0.20), (320, 0.25), (220, 0.30)):
        c.disc(830, 430, r, hx("FFE9A8"), a)
    # wooden floor
    c.rect(0, 820, W, H, hx("B07A45"))
    for y in range(820, H, 46):
        c.rect(0, y, W, y + 4, hx("8F5C30"))
    for x in (180, 520, 860):
        c.rect(x, 820, x + 4, H, hx("8F5C30"))
    # light pool on the floor from the doorway
    c.poly([(720, 820), (980, 820), (1000, H), (480, H)],
           hx("FFE9A8"), 0.28)
    # welcome mat
    c.rect(700, 850, 950, 925, hx("7C322C"))
    c.rect(715, 862, 935, 913, hx("A4443C"))
    c.rect(730, 882, 920, 892, hx("C96A5E"), 0.7)
    # a pair of shoes beside the mat
    c.ellipse(620, 885, 30, 14, -0.15, hx("6B4423"))
    c.ellipse(660, 892, 30, 14, -0.05, hx("5A3A1E"))
    # small potted plant, left corner
    c.poly([(55, 740), (125, 740), (115, 800), (65, 800)], hx("B65C3A"))
    c.ellipse(72, 700, 14, 48, -0.3, hx("4E8A4A"))
    c.ellipse(95, 692, 14, 54, 0.1, hx("3E7040"))
    c.ellipse(118, 706, 12, 42, 0.4, hx("4E8A4A"))


def draw_door(c):
    # frame
    c.rect(700, 60, 990, 820, hx("7C4A21"))
    # bright open doorway, golden light
    c.vgrad(735, 955, 95, 820, hx("FFF3C4"), hx("FFD97A"))
    # warm halo just inside the doorway
    c.disc(845, 430, 150, hx("FFF6D8"), 0.25)


def draw_owner_body(c):
    SKIN = hx("E8B98A")
    SWE = hx("2E7D7B")
    SWD = hx("256362")
    PANTS = hx("3A3A44")
    HAIR = hx("4A3226")
    # legs
    c.capsule(722, 610, 712, 792, 21, PANTS)
    c.capsule(770, 610, 782, 792, 21, PANTS)
    c.ellipse(708, 800, 26, 12, 0, hx("2E2A26"))
    c.ellipse(786, 800, 26, 12, 0, hx("2E2A26"))
    # torso, seen from behind
    c.capsule(746, 400, 746, 620, 56, SWE)
    # neck and head: back of the head, hair covers the face
    c.capsule(746, 350, 746, 395, 16, SKIN)
    c.disc(746, 330, 48, HAIR)


def draw_dog(c):
    FUR = hx("E9A94E")
    DARK = hx("C9852F")
    CREAM = hx("F6D493")
    EAR = hx("B97A2E")
    NOSE = hx("3A2A1E")
    TONG = hx("E87A8A")
    MOUTH = hx("4A2E1E")
    EYE = hx("2E2018")
    # tail: smooth tapered plume curving up behind
    for k in range(20):
        t = k / 19
        x = 255 - 130 * t
        y = 530 - 130 * t + 30 * t * t
        c.disc(x, y, 26 - 13 * t, FUR)
    # back legs stretched out behind
    c.capsule(320, 570, 245, 675, 20, FUR)
    c.capsule(345, 595, 280, 690, 20, FUR)
    c.disc(242, 677, 20, CREAM)
    c.disc(277, 692, 20, CREAM)
    # body, angled up toward the owner
    c.ellipse(400, 545, 165, 78, -0.45, FUR)
    c.ellipse(405, 572, 95, 34, -0.45, CREAM)
    c.ellipse(425, 595, 120, 28, -0.45, DARK, 0.25)

    # front legs reaching up toward the owner's hands
    c.capsule(505, 485, 600, 420, 19, FUR)
    c.capsule(525, 515, 620, 450, 19, FUR)
    c.disc(602, 418, 18, CREAM)
    c.disc(622, 448, 18, CREAM)
    # floppy ear flying back
    c.poly([(530, 385), (475, 360), (432, 400), (460, 440),
            (515, 435)], EAR)
    c.poly([(515, 393), (478, 377), (453, 405), (475, 427),
            (507, 421)], DARK)
    # head
    c.disc(555, 435, 62, FUR)
    # snout and muzzle
    c.ellipse(600, 428, 42, 28, -0.4, CREAM)
    c.disc(638, 412, 15, NOSE)
    c.ellipse(600, 458, 20, 13, 0, MOUTH)
    # tongue hanging out, happy
    c.capsule(598, 462, 605, 515, 10, TONG)
    # happy closed eye: an upward arch
    arc(c, 540, 412, 16, 3.3, 6.1, 6, EYE)


def draw_owner_arms(c):
    SWE = hx("2E7D7B")
    SKIN = hx("E8B98A")
    # arms wrapping around the leaping dog
    c.capsule(708, 420, 646, 492, 17, SWE)
    c.capsule(784, 425, 676, 516, 17, SWE)
    c.disc(640, 498, 17, SKIN)
    c.disc(672, 522, 17, SKIN)


def draw_motes(c, rng):
    for _ in range(26):
        x = rng.randint(640, 980)
        y = rng.randint(110, 780)
        c.disc(x, y, rng.randint(2, 5), hx("FFF6D8"),
               rng.uniform(0.25, 0.7))


def main():
    rng = random.Random(20261114)
    c = Canvas(W, H)
    draw_room(c)
    draw_door(c)
    draw_owner_body(c)
    # soft glow behind the dog, and its shadow on the floor
    c.disc(400, 510, 260, hx("FFE9A8"), 0.14)
    c.ellipse(400, 905, 190, 22, 0, hx("5A3A1A"), 0.18)
    # motion lines behind the leap
    for x0, y0, x1, y1 in ((170, 450, 230, 438), (155, 525, 220, 516),
                           (175, 600, 235, 592)):
        c.capsule(x0, y0, x1, y1, 5, hx("FFF3C4"), 0.5)
    draw_dog(c)
    draw_owner_arms(c)
    draw_motes(c, rng)
    out = os.path.join(out_dir(), "entry.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(png_bytes(c.rows, W, H))
    print(out)


if __name__ == "__main__":
    main()
