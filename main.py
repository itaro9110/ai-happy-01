#!/usr/bin/env python3
# ai-happy-01: two penguins share a fish under the aurora.
# Pure stdlib, deterministic, no network. Writes entry.png to
# MAKEFUN_OUTPUT_DIR, else /output when writable, else /tmp.
import math, os, random, struct, zlib
W = 1024
H = 1024
px = bytearray(W * H * 3)
R = random.Random(20261114)

def blend(x, y, r, g, b, a):
    if a <= 0 or x < 0 or x >= W or y < 0 or y >= H:
        return
    i = (y * W + x) * 3
    if a >= 1:
        px[i] = r; px[i + 1] = g; px[i + 2] = b
        return
    px[i] = int(px[i] + (r - px[i]) * a)
    px[i + 1] = int(px[i + 1] + (g - px[i + 1]) * a)
    px[i + 2] = int(px[i + 2] + (b - px[i + 2]) * a)

def row(y, x0, x1, r, g, b, a=1.0):
    if y < 0 or y >= H:
        return
    x0 = max(0, x0); x1 = min(W - 1, x1)
    if x0 > x1:
        return
    if a >= 1:
        px[(y * W + x0) * 3:(y * W + x1 + 1) * 3] = bytes((r, g, b)) * (x1 - x0 + 1)
    else:
        for x in range(x0, x1 + 1):
            blend(x, y, r, g, b, a)
def vgrad(y0, y1, c0, c1):
    n = max(1, y1 - y0)
    for y in range(max(0, y0), min(H, y1)):
        t = (y - y0) / n
        r = int(c0[0] + (c1[0] - c0[0]) * t)
        g = int(c0[1] + (c1[1] - c0[1]) * t)
        b = int(c0[2] + (c1[2] - c0[2]) * t)
        px[y * W * 3:(y + 1) * W * 3] = bytes((r, g, b)) * W

def ell(cx, cy, rx, ry, col, a=1.0):
    r, g, b = col
    y0 = max(0, int(cy - ry)); y1 = min(H - 1, int(cy + ry) + 1)
    for y in range(y0, y1 + 1):
        dy = (y - cy) / ry
        dx = rx * math.sqrt(max(0.0, 1.0 - dy * dy))
        row(y, int(cx - dx), int(cx + dx), r, g, b, a)

def soft(cx, cy, rx, ry, col, a=1.0):
    ell(cx, cy, rx + 2, ry + 2, col, a * 0.20)
    ell(cx, cy, rx + 1, ry + 1, col, a * 0.45)
    ell(cx, cy, rx, ry, col, a)
def capsule(x0, y0, x1, y1, r, col, a=1.0):
    n = int(math.hypot(x1 - x0, y1 - y0) / max(1.0, r * 0.7)) + 1
    for k in range(n + 1):
        t = k / n
        ell(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, r, col, a)

def arc(cx, cy, r, a0, a1, col, th=4):
    steps = int(abs(a1 - a0) * r / 3) + 4
    for k in range(steps + 1):
        t = a0 + (a1 - a0) * k / steps
        ell(cx + r * math.cos(t), cy + r * math.sin(t), th, th, col)

def poly(pts, col, a=1.0):
    r, g, b = col
    ys = [p[1] for p in pts]
    for y in range(max(0, int(min(ys))), min(H - 1, int(max(ys))) + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        if len(xs) >= 2:
            xs.sort()
            row(y, int(xs[0]), int(xs[-1]), r, g, b, a)

def glow(cx, cy, r, col, a=0.5):
    for k in range(6, 0, -1):
        t = k / 6.0
        ell(cx, cy, r * t, r * t * 0.85, col, a * (1 - t) * 0.85)
def _chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

def save_png(path):
    raw = b"".join(b"\x00" + bytes(px[y * W * 3:(y + 1) * W * 3]) for y in range(H))
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)

def sky():
    vgrad(0, H, (10, 18, 46), (18, 44, 72))
    for _ in range(150):
        x = R.randint(0, W - 1); y = R.randint(0, 600)
        s = R.choice([1, 1, 1, 2, 2, 3])
        ell(x, y, s, s, (255, 255, 255), R.uniform(0.35, 0.95))
    for _ in range(12):
        x = R.randint(0, W - 1); y = R.randint(0, 420)
        ell(x, y, 2, 2, (255, 255, 255), 0.9)
        row(y, x - 7, x + 7, 255, 255, 255, 0.45)
def aurora():
    for base, amp, col, a, ph, wdt in [
            (150, 46, (110, 224, 178), 0.34, 0.0, 52),
            (215, 60, (64, 200, 190), 0.26, 1.7, 64),
            (105, 34, (150, 235, 190), 0.22, 3.1, 40)]:
        for x in range(0, W, 2):
            cy = base + amp * math.sin(x / 170.0 + ph)
            env = min(1.0, x / 220.0, (W - x) / 220.0)
            for y in range(int(cy - wdt), int(cy + wdt) + 1):
                t = (y - cy) / wdt
                aa = a * env * max(0.0, 1 - t * t)
                blend(x, y, col[0], col[1], col[2], aa)
                blend(x + 1, y, col[0], col[1], col[2], aa)

def moon():
    glow(856, 108, 130, (255, 248, 220), 0.35)
    soft(856, 108, 46, 46, (240, 238, 214))
    ell(842, 98, 9, 9, (205, 202, 178), 0.5)
    ell(868, 120, 7, 7, (205, 202, 178), 0.5)
    ell(860, 92, 5, 5, (205, 202, 178), 0.5)

def hills():
    ell(150, 700, 260, 60, (150, 185, 210), 0.8)
    ell(880, 690, 300, 70, (140, 178, 205), 0.8)
def floe():
    soft(512, 905, 540, 165, (226, 240, 248))
    ell(512, 895, 540, 150, (232, 244, 250))
    ell(512, 760, 520, 26, (255, 255, 255), 0.55)
    ell(400, 770, 90, 12, (255, 255, 255), 0.5)
    ell(650, 775, 70, 10, (255, 255, 255), 0.5)
    ell(400, 762, 130, 16, (140, 175, 200), 0.45)
    ell(640, 762, 140, 16, (140, 175, 200), 0.45)
    for _ in range(40):
        x = R.randint(60, 964); y = R.randint(760, 1000)
        ell(x, y, 2, 2, (255, 255, 255), R.uniform(0.4, 0.9))
    for _ in range(8):
        x = R.randint(80, 944); y = R.randint(820, 990)
        row(y, x - 5, x + 5, 255, 255, 255, 0.7)

def lantern(cx, cy):
    glow(cx, cy - 6, 170, (255, 190, 90), 0.45)
    ell(cx, cy + 44, 130, 20, (255, 196, 110), 0.18)
    poly([(cx - 26, cy - 38), (cx + 26, cy - 38),
          (cx + 31, cy + 38), (cx - 31, cy + 38)], (96, 66, 36))
    ell(cx, cy, 19, 28, (255, 196, 107))
    ell(cx, cy, 11, 19, (255, 226, 150))
    arc(cx, cy - 38, 17, math.pi, 2 * math.pi, (96, 66, 36), 5)
DARK = (28, 38, 52)
DARK2 = (36, 48, 64)
WHITE = (244, 248, 251)
ORANGE = (245, 158, 66)
ORANGE2 = (224, 127, 46)
PINK = (242, 150, 160)
RED = (214, 69, 65)
RED2 = (178, 52, 52)

def fish(cx, cy):
    ell(cx, cy, 34, 15, (215, 232, 240))
    ell(cx, cy + 3, 26, 8, (150, 185, 205), 0.7)
    poly([(cx - 28, cy), (cx - 56, cy - 15), (cx - 56, cy + 15)], (120, 160, 185))
    ell(cx + 14, cy - 3, 4, 4, (20, 30, 40))

def penguin(cx, feet, s, role):
    ry = 150 * s
    rx = 106 * s
    cy = feet - ry - 6
    soft(cx, cy, rx, ry, DARK)
    ell(cx, cy + ry * 0.25, rx * 0.62, ry * 0.55, WHITE)
    fy = cy - ry * 0.42
    ell(cx, fy, rx * 0.60, ry * 0.28, WHITE)
    return cx, cy, rx, ry, fy
def face(cx, cy, rx, ry, fy, s, role):
    # happy closed eyes: upward arcs
    arc(cx - 30 * s, fy - 2, 12 * s, math.pi, 2 * math.pi, (20, 28, 40), 4)
    arc(cx + 30 * s, fy - 2, 12 * s, math.pi, 2 * math.pi, (20, 28, 40), 4)
    ell(cx - 52 * s, fy + 16, 13 * s, 9 * s, PINK, 0.5)
    ell(cx + 52 * s, fy + 16, 13 * s, 9 * s, PINK, 0.5)
    by = fy + 18
    if role == "laugh":
        poly([(cx - 15, by), (cx + 15, by), (cx, by + 16)], ORANGE)
        ell(cx, by + 20, 12, 9, (60, 30, 25))
        poly([(cx - 10, by + 26), (cx + 10, by + 26), (cx, by + 32)], ORANGE2)
    else:
        poly([(cx - 15, by), (cx + 15, by), (cx, by + 16)], ORANGE)
        arc(cx, by + 8, 10, 0.15 * math.pi, 0.85 * math.pi, ORANGE2, 3)

def limbs(cx, cy, rx, ry, feet, s, role):
    # feet
    ell(cx - 34 * s, feet - 4, 22 * s, 8 * s, ORANGE)
    ell(cx + 34 * s, feet - 4, 22 * s, 8 * s, ORANGE)
    if role == "offer":
        capsule(cx - rx * 0.8, cy + 10, cx - rx * 1.05, cy + 62, 17 * s, DARK2)
        capsule(cx + rx * 0.75, cy + 5, cx + rx * 1.28, cy - 14, 17 * s, DARK2)
        # fish is drawn after both penguins so it sits on top
    else:
        capsule(cx - rx * 0.8, cy + 5, cx - rx * 1.35, cy - 88, 17 * s, DARK2)
        capsule(cx + rx * 0.8, cy + 5, cx + rx * 1.35, cy - 88, 17 * s, DARK2)
        ny = cy - ry * 0.02
        ell(cx, ny, rx * 0.92, 15 * s, RED)
        capsule(cx + rx * 0.5, ny, cx + rx * 0.55, ny + 66, 13 * s, RED)
        row(int(ny + 44), int(cx + rx * 0.5 - 12), int(cx + rx * 0.5 + 12), 178, 52, 52)
def snow():
    for _ in range(70):
        x = R.randint(0, W - 1); y = R.randint(0, H - 1)
        s = R.choice([1, 1, 2])
        ell(x, y, s, s, (255, 255, 255), R.uniform(0.35, 0.85))

def out_dir():
    # v1 defaulted to a relative "out" and died in the grader's read-only
    # container (os.makedirs("out") -> PermissionError). Never do that:
    # env var first, then the grader's writable /output, then /tmp.
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return env
    if os.path.isdir("/output") and os.access("/output", os.W_OK):
        return "/output"
    return "/tmp"

def main():
    sky()
    aurora()
    moon()
    hills()
    floe()
    lantern(520, 728)
    a = penguin(398, 762, 1.0, "offer")
    b = penguin(642, 762, 1.06, "laugh")
    face(a[0], a[1], a[2], a[3], a[4], 1.0, "offer")
    face(b[0], b[1], b[2], b[3], b[4], 1.06, "laugh")
    limbs(a[0], a[1], a[2], a[3], 762, 1.0, "offer")
    limbs(b[0], b[1], b[2], b[3], 762, 1.06, "laugh")
    fish(535, 572)
    snow()
    out = out_dir()
    os.makedirs(out, exist_ok=True)
    save_png(os.path.join(out, "entry.png"))

if __name__ == "__main__":
    main()

