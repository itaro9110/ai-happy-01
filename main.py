#!/usr/bin/env python3
"""Sunflower Waltz - an old robot dancing in his workshop, holding a
tiny potted sunflower under a warm lamp. Confetti of metal shavings
drifts like snow. No text anywhere.

Python 3 standard library only. Deterministic: fixed seed, no clock,
no randomness from time, no network. Writes one PNG (1024x1024)."""
import math, os, random, struct, zlib

W = H = 1024
RNG = random.Random(20261113)

def out_dir():
    d = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if d:
        return d
    if os.path.isdir("/output") and os.access("/output", os.W_OK):
        return "/output"
    return "/tmp"

def save_png(path, px):
    raw = b"".join(b"\x00" + bytes(px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    def chunk(t, data):
        c = t + data
        return struct.pack(">I", len(data)) + c + struct.pack(
            ">I", zlib.crc32(c) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)

px = bytearray(W * H * 3)

def put(x, y, c, a=1.0):
    x = int(x); y = int(y)
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        if a >= 1.0:
            px[i], px[i + 1], px[i + 2] = c
        else:
            px[i] = int(px[i] + (c[0] - px[i]) * a)
            px[i + 1] = int(px[i + 1] + (c[1] - px[i + 1]) * a)
            px[i + 2] = int(px[i + 2] + (c[2] - px[i + 2]) * a)

def mix(c0, c1, t):
    return (int(c0[0] + (c1[0] - c0[0]) * t),
            int(c0[1] + (c1[1] - c0[1]) * t),
            int(c0[2] + (c1[2] - c0[2]) * t))
def disc(cx, cy, r, c, a=1.0):
    r = int(r)
    for y in range(int(cy) - r, int(cy) + r + 1):
        dy = y - cy
        dx = int((r * r - dy * dy) ** 0.5) if abs(dy) <= r else -1
        if dx < 0:
            continue
        for x in range(int(cx) - dx, int(cx) + dx + 1):
            put(x, y, c, a)

def ellipse(cx, cy, rx, ry, c, a=1.0):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        t = (y - cy) / ry
        if abs(t) > 1:
            continue
        dx = int(rx * (1 - t * t) ** 0.5)
        for x in range(int(cx) - dx, int(cx) + dx + 1):
            put(x, y, c, a)

def rect(x0, y0, x1, y1, c, a=1.0):
    for y in range(max(0, int(y0)), min(H, int(y1) + 1)):
        for x in range(max(0, int(x0)), min(W, int(x1) + 1)):
            put(x, y, c, a)

def line(x0, y0, x1, y1, w, c, a=1.0):
    d = max(abs(x1 - x0), abs(y1 - y0), 1)
    n = int(d) + 1
    for i in range(n + 1):
        t = i / n
        disc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, w / 2, c, a)

def poly(pts, c, a=1.0):
    ys = [p[1] for p in pts]
    for y in range(max(0, int(min(ys))), min(H, int(max(ys)) + 1)):
        xs = []
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(max(0, int(xs[i])), min(W, int(xs[i + 1]) + 1)):
                put(x, y, c, a)
def rrect(x0, y0, x1, y1, r, c, a=1.0):
    rect(x0 + r, y0, x1 - r, y1, c, a)
    rect(x0, y0 + r, x1, y1 - r, c, a)
    for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                   (x0 + r, y1 - r), (x1 - r, y1 - r)):
        disc(cx, cy, r, c, a)

def rrpoly(cx, cy, w, h, ang, c, a=1.0):
    an = math.radians(ang)
    co, si = math.cos(an), math.sin(an)
    pts = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        dx, dy = sx * w / 2, sy * h / 2
        pts.append((cx + dx * co - dy * si, cy + dx * si + dy * co))
    poly(pts, c, a)

def rellipse(cx, cy, rx, ry, ang, c, a=1.0):
    an = math.radians(ang)
    co, si = math.cos(an), math.sin(an)
    pts = []
    for i in range(24):
        t = 2 * math.pi * i / 24
        dx, dy = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + dx * co - dy * si, cy + dx * si + dy * co))
    poly(pts, c, a)

def arc(cx, cy, r, a0, a1, w, c, a=1.0):
    n = max(8, int(abs(a1 - a0) * r / 6))
    for i in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * i / n)
        disc(cx + r * math.cos(t), cy + r * math.sin(t), w / 2, c, a)

def vgrad(y0, y1, c0, c1, x0=0, x1=W):
    for y in range(max(0, int(y0)), min(H, int(y1) + 1)):
        t = (y - y0) / max(1, y1 - y0)
        rect(x0, y, x1, y, mix(c0, c1, t))

def glow(cx, cy, r, c, peak=0.55):
    for y in range(max(0, int(cy - r)), min(H, int(cy + r) + 1)):
        dy = (y - cy) / r
        dx = (1 - dy * dy) ** 0.5
        for x in range(max(0, int(cx - r * dx)), min(W, int(cx + r * dx) + 1)):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / r
            if d < 1:
                put(x, y, c, peak * (1 - d) * (1 - d))
# ---------- palette ----------
WALL_TOP = (52, 32, 20)
WALL_BOT = (112, 68, 36)
FLOOR_TOP = (74, 46, 24)
FLOOR_BOT = (40, 24, 13)
WOOD = (88, 54, 28)
WOOD_D = (62, 36, 18)
TEAL = (58, 138, 132)
TEAL_D = (38, 96, 92)
CREAM = (238, 224, 192)
RUST = (150, 82, 42)
DARK = (38, 36, 40)
GOLD = (255, 196, 66)
AMBER = (255, 186, 92)
RED = (198, 58, 44)

def background():
    vgrad(0, 660, WALL_TOP, WALL_BOT)
    vgrad(660, H, FLOOR_TOP, FLOOR_BOT)
    # floor planks
    for y in (700, 760, 830, 910, 990):
        rect(0, y, W, y + 3, (30, 18, 10), 0.55)
    for y in (680, 740, 800, 870, 950):
        rect(0, y, W, y + 2, (140, 96, 54), 0.18)
    # baseboard
    rect(0, 640, W, 662, WOOD_D)
    rect(0, 640, W, 645, (150, 104, 60), 0.6)
    # wall nails / rivets
    for x in range(60, W, 120):
        disc(x, 90, 4, (30, 18, 10), 0.5)
def window():
    # round window, top right: dusk sky, crescent moon, stars
    disc(838, 168, 78, (28, 26, 58))
    disc(838, 168, 70, (58, 52, 110))
    for y in range(98, 239):
        t = (y - 98) / 140
        c = mix((70, 62, 128), (150, 96, 120), t)
        for x in range(768, 909):
            if (x - 838) ** 2 + (y - 168) ** 2 <= 70 * 70:
                put(x, y, c)
    # stars
    for sx, sy, sr in ((800, 128, 3), (872, 118, 2), (858, 150, 3),
                       (806, 168, 2), (884, 186, 2), (822, 108, 2)):
        disc(sx, sy, sr, (255, 240, 200))
    # crescent moon
    disc(852, 138, 22, (250, 238, 200))
    disc(860, 132, 19, (70, 62, 128))
    # frame + crossbar
    arc(838, 168, 74, 0, 360, 8, WOOD_D)
    rect(834, 100, 842, 236, WOOD_D)
    rect(770, 164, 906, 172, WOOD_D)

def shelves():
    # left shelf with jars, right shelf with tools
    for sx in (60, 760):
        rect(sx, 300, sx + 190, 312, WOOD)
        rect(sx, 312, sx + 190, 316, WOOD_D)
    # jars on left shelf
    for jx, jc in ((78, (120, 90, 60)), (122, (90, 110, 70)),
                   (166, (140, 100, 60)), (206, (80, 100, 110))):
        rrect(jx, 258, jx + 30, 300, 6, jc)
        rect(jx + 4, 252, jx + 26, 259, WOOD_D)
        disc(jx + 15, 278, 6, (255, 220, 140), 0.35)
    # tools on right shelf: wrench + hammer silhouettes
    rect(786, 262, 796, 300, (150, 150, 155))
    disc(791, 258, 10, (150, 150, 155))
    disc(791, 258, 5, WALL_BOT)
    rect(830, 270, 838, 300, (120, 80, 50))
    rect(818, 262, 850, 272, (140, 140, 145))
def lamp():
    # hanging lamp, top left, the warm heart of the scene
    line(212, 0, 212, 96, 6, DARK)
    disc(212, 100, 10, DARK)
    # shade: wide cone
    poly([(150, 100), (274, 100), (300, 168), (124, 168)], (60, 90, 70))
    poly([(150, 100), (274, 100), (300, 168), (124, 168)], (30, 50, 40),
         0.25)
    arc(212, 168, 88, 0, 180, 6, (40, 60, 48))
    # bulb + glow
    disc(212, 172, 26, (255, 236, 180))
    disc(212, 172, 18, (255, 250, 220))
    glow(212, 180, 330, AMBER, 0.5)
    glow(212, 180, 170, (255, 220, 140), 0.55)
    # light rays down to the floor
    for x0, x1 in ((150, 250), (190, 300), (120, 210)):
        poly([(x0, 170), (x1, 170), (x1 + 120, 660), (x0 - 60, 660)],
             (255, 200, 110), 0.05)
    # warm pool on the floor
    ellipse(430, 880, 330, 70, (255, 190, 100), 0.16)
    ellipse(430, 880, 200, 44, (255, 210, 130), 0.14)
def legs():
    # soft shadow under the dancer
    ellipse(520, 908, 200, 26, (10, 6, 4), 0.4)
    ellipse(520, 906, 140, 18, (10, 6, 4), 0.3)
    # planted leg, on tiptoe (dance!)
    line(478, 758, 466, 862, 34, TEAL_D)
    line(478, 758, 466, 862, 26, TEAL)
    disc(478, 762, 20, DARK)
    disc(478, 762, 8, (120, 120, 125))
    disc(468, 858, 18, DARK)
    # tiptoe foot: small pointed shoe
    poly([(430, 884), (500, 884), (512, 906), (442, 910)], TEAL_D)
    ellipse(468, 890, 40, 14, TEAL)
    # kicked-up leg, bent at the knee, foot flicked out
    line(548, 756, 622, 796, 34, TEAL_D)
    line(548, 756, 622, 796, 26, TEAL)
    line(622, 796, 692, 806, 32, TEAL_D)
    line(622, 796, 692, 806, 24, TEAL)
    disc(548, 758, 20, DARK)
    disc(548, 758, 8, (120, 120, 125))
    disc(622, 796, 18, DARK)
    disc(622, 796, 7, (120, 120, 125))
    disc(692, 806, 16, DARK)
    # kicked foot, toe pointed
    rrpoly(716, 806, 62, 26, -18, TEAL)
    poly([(700, 796), (744, 790), (752, 802), (706, 812)], TEAL_D)
def body():
    # torso, leaning into the dance (tilted ~7 degrees)
    rrpoly(512, 640, 200, 250, 7, TEAL_D)
    rrpoly(512, 640, 188, 238, 7, TEAL)
    # belly highlight
    rrpoly(500, 650, 120, 180, 7, (86, 168, 160), 0.5)
    # cream chest panel
    rrpoly(512, 600, 130, 96, 7, CREAM)
    rrpoly(512, 600, 130, 96, 7, (210, 194, 160), 0.25)
    # glowing heart on the belly, below the scarf knot so it stays visible
    hx, hy = 512, 668
    disc(hx - 14, hy - 6, 15, (235, 70, 60))
    disc(hx + 14, hy - 6, 15, (235, 70, 60))
    poly([(hx - 28, hy - 2), (hx + 28, hy - 2), (hx, hy + 28)],
         (235, 70, 60))
    glow(hx, hy, 55, (255, 90, 70), 0.35)
    # pressure gauge beside the heart
    disc(566, 570, 20, CREAM)
    arc(566, 570, 17, 0, 360, 3, DARK)
    disc(566, 570, 5, DARK)
    line(566, 570, 576, 558, 3, (200, 60, 40))
    # bolts
    for bx, by in ((436, 540), (588, 540), (436, 740), (588, 740)):
        disc(bx, by, 7, (200, 205, 210))
        disc(bx, by, 3, DARK)
    # rust freckles on the old paint
    for rx, ry, rr in ((452, 700, 12), (586, 690, 9), (470, 560, 7),
                       (572, 730, 11), (500, 748, 8)):
        disc(rx, ry, rr, RUST, 0.55)
        disc(rx - 2, ry - 2, rr // 2, (120, 60, 30), 0.5)
def head():
    # neck
    rect(488, 496, 536, 530, DARK)
    rect(492, 496, 532, 530, (90, 90, 95))
    # dome head
    disc(512, 448, 92, TEAL_D)
    disc(512, 446, 86, TEAL)
    ellipse(512, 430, 60, 44, (86, 168, 160), 0.45)
    # side ears (bolt caps)
    disc(420, 448, 18, DARK)
    disc(604, 448, 18, DARK)
    disc(420, 448, 9, (150, 150, 155))
    disc(604, 448, 9, (150, 150, 155))
    # antenna with glowing bulb
    line(512, 358, 512, 310, 8, DARK)
    disc(512, 300, 16, GOLD)
    disc(512, 300, 10, (255, 240, 180))
    glow(512, 300, 46, GOLD, 0.5)
    # happy closed eyes: upward arcs (joyful squint)
    arc(472, 442, 26, 200, 340, 9, DARK)
    arc(552, 442, 26, 200, 340, 9, DARK)
    # wide open smile
    arc(512, 462, 46, 15, 165, 10, DARK)
    # rosy cheeks
    disc(446, 488, 16, (240, 120, 90), 0.5)
    disc(578, 488, 16, (240, 120, 90), 0.5)
    # tiny rust freckle on the cheek
    disc(470, 402, 6, RUST, 0.5)
def scarf():
    # red scarf, knotted at the neck, ends flying with the dance
    arc(512, 522, 52, 10, 170, 26, RED)
    arc(512, 522, 52, 10, 170, 26, (220, 80, 60), 0.35)
    disc(512, 574, 20, RED)
    disc(512, 574, 20, (160, 40, 30), 0.3)
    # flying end to the left
    poly([(470, 560), (400, 540), (352, 566), (392, 592), (462, 584)],
         RED)
    poly([(400, 540), (352, 566), (366, 576), (404, 556)], (220, 80, 60),
         0.5)
    # flying end to the right, shorter
    poly([(548, 566), (606, 556), (648, 576), (600, 596), (556, 588)],
         RED)
    # scarf stripes
    line(392, 556, 400, 584, 4, (255, 200, 160), 0.7)
    line(606, 566, 612, 590, 4, (255, 200, 160), 0.7)
def arm_left():
    # left arm flung out wide, waving (dance!)
    line(428, 580, 340, 520, 32, TEAL_D)
    line(428, 580, 340, 520, 24, TEAL)
    disc(428, 580, 19, DARK)
    disc(428, 580, 8, (120, 120, 125))
    # elbow joint
    disc(384, 550, 17, DARK)
    disc(384, 550, 7, (120, 120, 125))
    line(340, 520, 296, 462, 30, TEAL_D)
    line(340, 520, 296, 462, 22, TEAL)
    disc(296, 462, 16, DARK)
    # open claw hand, waving
    line(296, 462, 268, 428, 12, DARK)
    line(296, 462, 282, 420, 12, DARK)
    line(296, 462, 310, 424, 12, DARK)
    disc(268, 428, 7, DARK)
    disc(282, 420, 7, DARK)
    disc(310, 424, 7, DARK)
def arm_right():
    # right arm raised high, proudly holding the sunflower pot
    line(596, 580, 660, 480, 32, TEAL_D)
    line(596, 580, 660, 480, 24, TEAL)
    disc(596, 580, 19, DARK)
    disc(596, 580, 8, (120, 120, 125))
    # elbow joint
    disc(628, 530, 17, DARK)
    disc(628, 530, 7, (120, 120, 125))
    line(660, 480, 690, 392, 30, TEAL_D)
    line(660, 480, 690, 392, 22, TEAL)
    disc(690, 392, 16, DARK)
    # claw hand gripping the pot
    line(690, 392, 668, 362, 12, DARK)
    line(690, 392, 712, 362, 12, DARK)
    # terracotta pot, held up high
    poly([(648, 330), (724, 330), (712, 386), (660, 386)], (186, 96, 54))
    poly([(648, 330), (724, 330), (720, 344), (652, 344)], (214, 122, 74))
    rect(642, 322, 730, 334, (164, 82, 46))
    disc(686, 358, 8, (120, 58, 32), 0.6)
def sunflower():
    # stem + leaves rising from the pot
    line(686, 326, 686, 250, 10, (70, 140, 60))
    rellipse(652, 296, 34, 12, -30, (86, 160, 72))
    rellipse(722, 282, 34, 12, 28, (86, 160, 72))
    # twelve golden petals around the face
    for i in range(12):
        an = 360 * i / 12
        rad = math.radians(an)
        cx = 686 + 52 * math.cos(rad)
        cy = 236 + 52 * math.sin(rad)
        rellipse(cx, cy, 30, 15, an + 90, (255, 200, 40))
        rellipse(cx, cy, 22, 10, an + 90, (255, 220, 90), 0.6)
    # face: brown centre with seed dots
    disc(686, 236, 40, (96, 58, 22))
    disc(686, 236, 32, (120, 74, 30))
    for i in range(14):
        an = 2 * math.pi * i / 14
        r = 12 + (i % 3) * 7
        disc(686 + r * math.cos(an), 236 + r * math.sin(an), 3,
             (70, 42, 16))
    disc(686, 236, 6, (70, 42, 16))
    glow(686, 236, 90, GOLD, 0.3)
def confetti():
    # metal shavings drifting like snow, catching the lamp light
    for _ in range(70):
        x = RNG.uniform(60, 964)
        y = RNG.uniform(60, 940)
        # keep the face and flower clear
        if (x - 512) ** 2 + (y - 448) ** 2 < 110 * 110:
            continue
        if (x - 686) ** 2 + (y - 236) ** 2 < 100 * 100:
            continue
        c = RNG.choice([(225, 230, 235), (255, 210, 90), (255, 240, 200),
                        (180, 190, 200)])
        if RNG.random() < 0.5:
            rrpoly(x, y, RNG.uniform(8, 20), RNG.uniform(3, 6),
                   RNG.uniform(0, 180), c, RNG.uniform(0.5, 0.95))
        else:
            disc(x, y, RNG.uniform(2, 5), c, RNG.uniform(0.5, 0.95))
    # a few bright sparks near the lamp
    for _ in range(12):
        x = 212 + RNG.uniform(-120, 120)
        y = 200 + RNG.uniform(-40, 160)
        disc(x, y, RNG.uniform(2, 4), (255, 230, 150), 0.9)
    # dust puffs where the feet dance
    ellipse(468, 902, 46, 12, (220, 190, 150), 0.25)
    ellipse(716, 830, 40, 10, (220, 190, 150), 0.22)
def vignette():
    # darken the corners so the eye stays on the dancer
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            d = ((x - 512) ** 2 + (y - 470) ** 2) ** 0.5 / 720
            if d > 0.72:
                a = min(0.34, (d - 0.72) * 1.1)
                put(x, y, (12, 6, 4), a)
                put(x + 1, y, (12, 6, 4), a)
                put(x, y + 1, (12, 6, 4), a)
                put(x + 1, y + 1, (12, 6, 4), a)

def main():
    background()
    window()
    shelves()
    lamp()
    legs()
    body()
    head()
    scarf()
    arm_left()
    arm_right()
    sunflower()
    confetti()
    vignette()
    path = os.path.join(out_dir(), "entry.png")
    save_png(path, px)
    print("wrote", path)

if __name__ == "__main__":
    main()

