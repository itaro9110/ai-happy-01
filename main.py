#!/usr/bin/env python3
"""Grandma's Sunflower -- ai-happy-01 entry.

A small friendly robot hands a big sunflower to a laughing
grandmother on a park bench in golden afternoon light.
Pure procedural drawing, Python stdlib only. No text anywhere.
Deterministic: fixed shapes, same bytes every run.
"""
import math
import os
import struct
import zlib

W = H = 1024


def write_png(path, buf):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


class C:
    def __init__(self):
        self.p = bytearray(W * H * 3)

    def px(self, x, y, col, a=1.0):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            if a >= 1.0:
                self.p[i:i + 3] = bytes(col)
            else:
                for k in range(3):
                    self.p[i + k] = int(self.p[i + k] * (1 - a)
                                        + col[k] * a)

    def span(self, x0, x1, y, col, a=1.0):
        for x in range(max(0, x0), min(W, x1 + 1)):
            self.px(x, y, col, a)
    def circle(self, cx, cy, r, col, a=1.0):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.span(cx - dx, cx + dx, cy + dy, col, a)

    def ellipse(self, cx, cy, rx, ry, col, a=1.0):
        for dy in range(-ry, ry + 1):
            f = 1 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, f)))
            self.span(cx - dx, cx + dx, cy + dy, col, a)

    def rect(self, x, y, w, h, col, a=1.0):
        for yy in range(y, y + h):
            self.span(x, x + w - 1, yy, col, a)

    def rrect(self, x, y, w, h, r, col, a=1.0):
        self.rect(x + r, y, w - 2 * r, h, col, a)
        self.rect(x, y + r, w, h - 2 * r, col, a)
        for cx, cy in ((x + r, y + r), (x + w - r, y + r),
                       (x + r, y + h - r), (x + w - r, y + h - r)):
            self.circle(cx, cy, r, col, a)
    def poly(self, pts, col, a=1.0):
        pts = [(int(x), int(y)) for x, y in pts]
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.span(int(xs[i]), int(xs[i + 1]), y, col, a)

    def line(self, x0, y0, x1, y1, w, col, a=1.0):
        d = max(1, int(math.hypot(x1 - x0, y1 - y0)))
        for i in range(d + 1):
            t = i / d
            self.circle(int(x0 + (x1 - x0) * t),
                        int(y0 + (y1 - y0) * t), w // 2, col, a)

    def arc(self, cx, cy, r, a0, a1, w, col, a=1.0):
        n = max(4, int(r * (a1 - a0) / 6))
        for i in range(n + 1):
            t = a0 + (a1 - a0) * i / n
            self.circle(int(cx + r * math.cos(t)),
                        int(cy + r * math.sin(t)), w // 2, col, a)
def mix(c0, c1, t):
    return tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))


def petal(cv, cx, cy, ang, ln, wd, col):
    dx, dy = math.cos(ang), math.sin(ang)
    px, py = -dy, dx
    tip = (cx + dx * ln, cy + dy * ln)
    b1 = (cx + px * wd, cy + py * wd)
    b2 = (cx - px * wd, cy - py * wd)
    cv.poly([b1, tip, b2], col)


def flower(cv, cx, cy, r, petal_col, centre_col):
    for i in range(12):
        petal(cv, cx, cy, i * math.pi / 6, r * 1.9, r * 0.42,
              petal_col)
    cv.circle(cx, cy, r, centre_col)
    for dy in (-r // 2, 0, r // 2):
        for dx in (-r // 2, 0, r // 2):
            if dx or dy:
                cv.circle(cx + dx, cy + dy, max(2, r // 8),
                          (60, 35, 15))


def sky(cv):
    top, bot = (255, 226, 158), (255, 186, 122)
    for y in range(660):
        cv.span(0, W - 1, y, mix(top, bot, y / 660))
def background(cv):
    sky(cv)
    # sun glow + disc, upper right
    cv.circle(845, 130, 200, (255, 240, 190), 0.35)
    cv.circle(845, 130, 120, (255, 244, 205), 0.45)
    cv.circle(845, 130, 62, (255, 228, 130))
    cv.circle(845, 130, 46, (255, 240, 170))
    # hedge band
    cv.rect(0, 560, W, 110, (96, 142, 76))
    for x in range(20, W, 90):
        cv.circle(x, 566, 42, (110, 156, 88))
    # lawn
    for y in range(660, H):
        cv.span(0, W - 1, y, mix((158, 196, 104), (122, 168, 86),
                                 (y - 660) / 364))
    # soft light path under the bench
    cv.ellipse(640, 880, 330, 90, (214, 188, 138), 0.55)


def bg_sunflowers(cv):
    for (x, top, r) in ((70, 330, 30), (150, 400, 26), (930, 350, 30),
                        (990, 430, 24), (30, 470, 22)):
        cv.line(x, 660, x, top, 9, (70, 120, 60))
        cv.ellipse(x - 26, top + 90, 26, 12, (84, 138, 66))
        cv.ellipse(x + 26, top + 120, 26, 12, (84, 138, 66))
        flower(cv, x, top, r, (255, 196, 40), (122, 74, 30))
def bench(cv):
    # ground shadows
    cv.ellipse(430, 900, 120, 22, (90, 120, 60), 0.4)
    cv.ellipse(700, 910, 210, 26, (90, 120, 60), 0.4)
    # legs + seat + back slats (wood brown)
    wood, dark = (152, 102, 56), (120, 78, 42)
    cv.rect(590, 740, 26, 150, dark)
    cv.rect(880, 740, 26, 150, dark)
    cv.rrect(560, 700, 380, 44, 14, wood)
    cv.rrect(560, 612, 380, 30, 12, wood)
    cv.rrect(560, 656, 380, 30, 12, wood)
    cv.rect(566, 642, 14, 60, dark)
    cv.rect(920, 642, 14, 60, dark)
    cv.rrect(556, 690, 30, 16, 7, dark)   # armrest ends
    cv.rrect(914, 690, 30, 16, 7, dark)


def cat(cv):
    # sleeping ginger cat curled on the bench's right end
    o, s = (232, 148, 74), (200, 116, 52)
    cv.ellipse(872, 676, 62, 34, o)
    cv.circle(916, 656, 26, o)
    cv.poly([(900, 634), (908, 612), (918, 634)], o)
    cv.poly([(922, 634), (934, 616), (938, 638)], o)
    cv.arc(872, 676, 44, 3.6, 5.6, 12, s)
    cv.arc(908, 656, 7, 0.2, 2.6, 4, (90, 50, 30))
    cv.line(846, 648, 862, 648, 4, s)
    cv.line(850, 668, 866, 668, 4, s)
def grandmother(cv):
    skin, dress = (242, 201, 160), (178, 140, 194)
    shawl, grey = (142, 106, 168), (198, 192, 204)
    # legs + shoes below the bench seat
    cv.line(668, 730, 656, 856, 22, (90, 70, 90))
    cv.line(736, 730, 748, 856, 22, (90, 70, 90))
    cv.ellipse(652, 868, 26, 14, (70, 52, 66))
    cv.ellipse(754, 868, 26, 14, (70, 52, 66))
    # dress: wide seated skirt
    cv.poly([(640, 520), (762, 520), (800, 706), (606, 706)], dress)
    cv.poly([(640, 520), (762, 520), (742, 600), (660, 600)], shawl)
    # arms reaching toward the sunflower (left)
    cv.line(652, 548, 592, 586, 26, dress)
    cv.line(752, 548, 640, 566, 26, dress)
    cv.circle(588, 588, 16, skin)
    cv.circle(636, 568, 16, skin)
    # head + grey hair + bun
    cv.circle(700, 430, 58, skin)
    cv.circle(700, 414, 60, grey)
    cv.circle(700, 436, 54, skin)
    cv.circle(700, 368, 27, grey)
    # laughing face: closed smiling eyes, rosy cheeks, open smile
    dark = (74, 44, 30)
    cv.arc(672, 428, 13, 3.4, 6.0, 5, dark)
    cv.arc(728, 428, 13, 3.4, 6.0, 5, dark)
    cv.circle(656, 452, 11, (244, 150, 130), 0.65)
    cv.circle(744, 452, 11, (244, 150, 130), 0.65)
    cv.arc(700, 452, 20, 0.3, 2.8, 5, dark)
    cv.circle(700, 470, 7, (150, 60, 60))
def robot(cv):
    teal, cream = (63, 167, 160), (245, 239, 224)
    dark = (40, 60, 66)
    # legs + feet
    cv.rect(392, 800, 26, 62, teal)
    cv.rect(452, 800, 26, 62, teal)
    cv.ellipse(398, 868, 30, 14, dark)
    cv.ellipse(460, 868, 30, 14, dark)
    # body with glowing heart
    cv.rrect(366, 636, 148, 176, 34, teal)
    cv.circle(440, 716, 46, (255, 120, 130), 0.3)
    cv.circle(424, 710, 15, (255, 107, 122))
    cv.circle(456, 710, 15, (255, 107, 122))
    cv.poly([(410, 716), (470, 716), (440, 748)], (255, 107, 122))
    # head, antenna, face (teal ring behind the cream face)
    cv.line(440, 490, 440, 452, 8, teal)
    cv.circle(440, 446, 12, (255, 196, 40))
    cv.circle(440, 560, 78, teal)
    cv.circle(440, 560, 70, cream)
    cv.circle(412, 552, 9, dark)
    cv.circle(468, 552, 9, dark)
    cv.arc(440, 566, 24, 0.3, 2.8, 5, dark)
    cv.circle(400, 576, 10, (244, 150, 130), 0.6)
    cv.circle(480, 576, 10, (244, 150, 130), 0.6)
    cv.circle(366, 560, 12, teal)
    cv.circle(514, 560, 12, teal)
def big_sunflower(cv):
    # tall stem from the robot's hand up to the flower head, held
    # high between the robot and grandmother so the bloom is clear
    cv.line(536, 645, 580, 520, 10, (70, 120, 60))
    cv.ellipse(552, 606, 26, 11, (84, 138, 66))
    cv.ellipse(570, 580, 24, 10, (84, 138, 66))
    flower(cv, 585, 470, 52, (255, 200, 44), (122, 74, 30))


def robot_arm(cv):
    # right arm reaching out to hold the sunflower stem
    cv.line(500, 668, 532, 644, 20, (63, 167, 160))
    cv.circle(536, 642, 13, (245, 239, 224))
def watering_can(cv):
    # resting on the lawn, left of the bench
    cv.rrect(268, 856, 96, 56, 16, (90, 140, 120))
    cv.line(360, 872, 402, 842, 10, (90, 140, 120))
    cv.circle(404, 840, 12, (70, 115, 100))
    cv.arc(300, 856, 34, 3.4, 6.0, 8, (70, 115, 100))
    cv.ellipse(316, 856, 30, 8, (140, 190, 170), 0.7)


def foreground(cv):
    # grass tufts + tiny flowers along the bottom
    for x in (60, 150, 950, 870, 210, 760):
        cv.line(x, 1000, x - 12, 962, 5, (96, 148, 74))
        cv.line(x, 1000, x + 2, 956, 5, (110, 162, 84))
        cv.line(x, 1000, x + 14, 964, 5, (96, 148, 74))
    for (x, y, col) in ((120, 940, (255, 120, 140)),
                        (920, 950, (255, 255, 255)),
                        (820, 985, (255, 120, 140)),
                        (180, 985, (255, 200, 60))):
        for a in range(5):
            t = a * 2 * math.pi / 5
            cv.circle(int(x + 9 * math.cos(t)), int(y + 9 * math.sin(t)),
                      6, col)
        cv.circle(x, y, 6, (255, 210, 60))
    # two butterflies for delight
    for (x, y, col) in ((240, 300, (255, 150, 180)),
                        (800, 260, (150, 190, 255))):
        cv.ellipse(x - 12, y, 14, 9, col)
        cv.ellipse(x + 12, y, 14, 9, col)
        cv.line(x, y - 8, x, y + 10, 4, (60, 50, 60))
def out_dir():
    d = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if d:
        return d
    if os.path.isdir("/output") and os.access("/output", os.W_OK):
        return "/output"
    return "/tmp"


def main():
    cv = C()
    background(cv)
    bg_sunflowers(cv)
    bench(cv)
    cat(cv)
    big_sunflower(cv)
    robot(cv)
    robot_arm(cv)
    grandmother(cv)
    watering_can(cv)
    foreground(cv)
    write_png(os.path.join(out_dir(), "entry.png"), cv.p)


if __name__ == "__main__":
    main()

