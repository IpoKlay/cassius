"""Hand-shaded pixel sprites for the concept frames (3/4 top-down, Eastward/Kingdom density)."""
import math, random
import numpy as np
from kit import rgba, put, rect, C, canopy, trunk, flip, band

K = C('1a1214')
STEEL = [C('2f2f38'), C('5a5c66'), C('8c8e98'), C('c9cbd2')]
GOLD = [C('6b4a1a'), C('a8782a'), C('dcae4a'), C('ffe39a')]
RED = [C('4a0d0d'), C('7a1712'), C('b0271a'), C('e0503a')]
SKIN = [C('7a4a34'), C('b47a58'), C('dca07a')]
LEATH = [C('2e1d12'), C('5a3a22'), C('85583a')]
WOOD = [C('2e1f14'), C('5b3c24'), C('86603c'), C('b08860')]
CLOTH = [C('5e4a36'), C('8e7454'), C('b89e78'), C('dcc8a2')]


def legionary(step=0, carry='pilum', tunic=RED, shield=True, torch=False):
    a = rgba(14, 22)
    o = 2  # top padding
    # pilum on the near shoulder (slanted back)
    if carry == 'pilum':
        for i in range(17):
            x, y = 1 + i * 0.25, o + i
            put(a, int(x), int(y), WOOD[2] if i > 2 else STEEL[3])
        put(a, 1, o - 1, STEEL[3]); put(a, 1, o - 2, STEEL[2])
    if carry == 'vexillum':
        for y in range(0, o + 15):
            put(a, 2, y, WOOD[2])
    # legs (caligae)
    l1, l2 = [(0, 0), (1, -1), (0, 0), (-1, 1)][step % 4]
    for (lx, off) in ((4 + l1, 0), (7 + l2, 0)):
        for y in range(o + 13, o + 18):
            put(a, lx, y, SKIN[1] if y < o + 16 else LEATH[0])
            put(a, lx + 1, y, SKIN[0] if y < o + 16 else LEATH[1])
        put(a, lx, o + 18, LEATH[0]); put(a, lx + 1, o + 18, LEATH[0]); put(a, lx + 2, o + 18, LEATH[1])
    # tunic skirt + pteruges
    rect(a, 3, o + 10, 9, o + 12, tunic[2])
    for x in range(3, 10):
        put(a, x, o + 12, tunic[1] if x % 2 else tunic[2])
        put(a, x, o + 13, LEATH[1] if x % 2 == 0 else (0, 0, 0)) if x % 2 == 0 else None
    a[o + 13, 3:10:2, 3] = 1
    put(a, 3, o + 10, tunic[1]); put(a, 3, o + 11, tunic[1])
    # lorica segmentata
    rect(a, 3, o + 6, 9, o + 9, STEEL[1])
    for y, c in ((o + 6, STEEL[3]), (o + 7, STEEL[2]), (o + 8, STEEL[1]), (o + 9, STEEL[2])):
        for x in range(3, 10):
            put(a, x, y, c if x < 8 else STEEL[0] if y % 2 else STEEL[1])
    rect(a, 3, o + 10, 9, o + 10, LEATH[1])            # belt
    put(a, 6, o + 10, GOLD[2])
    # head + helmet (Imperial Gallic) facing right
    rect(a, 5, o + 2, 8, o + 5, SKIN[2])
    put(a, 5, o + 4, SKIN[1]); put(a, 5, o + 5, SKIN[1]); put(a, 8, o + 4, K); put(a, 8, o + 3, SKIN[2])
    rect(a, 4, o + 0, 8, o + 2, STEEL[2])
    put(a, 5, o + 0, STEEL[3]); put(a, 6, o + 0, STEEL[3]); put(a, 4, o + 2, STEEL[0]); put(a, 4, o + 3, STEEL[1]); put(a, 4, o + 4, STEEL[1])
    put(a, 9, o + 2, STEEL[2])                           # brow guard
    put(a, 3, o + 3, STEEL[1]); put(a, 3, o + 4, STEEL[0])  # neck guard
    for x, y, c in ((4, o - 1, RED[1]), (5, o - 2, RED[2]), (6, o - 2, RED[3]), (7, o - 2, RED[2]), (8, o - 1, RED[1]), (5, o - 1, RED[2]), (6, o - 1, RED[2]), (7, o - 1, RED[1])):
        put(a, x, y, c)
    # near arm + hand on the pilum
    put(a, 2, o + 7, STEEL[2]); put(a, 2, o + 8, SKIN[1]); put(a, 2, o + 9, SKIN[2])
    if shield:
        # curved scutum on the far side, its face toward us, edge-lit
        x0, y0 = 7, o + 5
        for y in range(y0, y0 + 10):
            for x in range(x0, x0 + 5):
                c = RED[2]
                if x == x0 + 4:
                    c = RED[0]
                elif x == x0 + 3:
                    c = RED[1]
                if y in (y0, y0 + 9) or x == x0:
                    c = GOLD[2] if x < x0 + 3 else GOLD[1]
                put(a, x, y, c)
        put(a, x0 + 2, y0 + 4, GOLD[3]); put(a, x0 + 2, y0 + 5, GOLD[2]); put(a, x0 + 1, y0 + 4, GOLD[1])
        for y in (y0 + 2, y0 + 7):
            put(a, x0 + 1, y, GOLD[1]); put(a, x0 + 2, y, GOLD[1])
    if torch:
        for y in range(o + 2, o + 10):
            put(a, 11, y, WOOD[1])
        put(a, 11, o + 1, WOOD[0])
    return a


def torch_flame(t=0):
    a = rgba(5, 7)
    e = rgba(5, 7)
    pts = [(2, 6), (2, 5), (1, 5), (3, 5), (2, 4), (1, 4), (2, 3), (3, 4), (2, 2), (2, 1)]
    for i, (x, y) in enumerate(pts[: 8 + t % 3]):
        c = C('ffe7a0') if i < 3 else C('ff9a3a') if i < 7 else C('e0402a')
        put(a, x, y, c); put(e, x, y, c * 1.4)
    return a, e


def cassius(step=0):
    a = rgba(36, 36)
    o = 4
    hc = [C('2a1810'), C('4e2e1c'), C('74462a'), C('9a6440')]
    # far legs
    lp = [(1, -1), (0, 0), (-1, 1), (0, 0)][step % 4]
    for i, (bx, near) in enumerate(((10, False), (12, True), (22, False), (24, True))):
        sw = lp[i % 2]
        col = hc[1] if not near else hc[2]
        for y in range(o + 19, o + 28):
            put(a, bx + (sw if y > o + 23 else 0), y, col)
            put(a, bx + 1 + (sw if y > o + 23 else 0), y, hc[0] if not near else hc[1])
        put(a, bx + sw, o + 28, K); put(a, bx + 1 + sw, o + 28, K); put(a, bx + 2 + sw, o + 28, K)
    # tail
    for i, (x, y) in enumerate(((7, o + 13), (6, o + 14), (5, o + 16), (5, o + 18), (4, o + 20), (4, o + 22), (5, o + 23))):
        put(a, x, y, hc[0]); put(a, x + 1, y, hc[1] if i % 2 else hc[0])
    # barrel
    for y in range(o + 12, o + 21):
        for x in range(7, 27):
            dy = (y - (o + 16)) / 4.6
            dx = (x - 17) / 10.5
            if dx * dx + dy * dy <= 1.0:
                c = hc[2]
                if dy < -0.55:
                    c = hc[3]
                elif dy > 0.5:
                    c = hc[1]
                if dx > 0.8 or dx < -0.85:
                    c = hc[1]
                put(a, x, y, c)
    # neck + head
    neck = [(24, o + 12), (25, o + 11), (26, o + 10), (27, o + 9), (28, o + 8), (28, o + 9), (27, o + 10), (26, o + 11), (25, o + 12), (25, o + 13), (26, o + 13), (27, o + 12), (28, o + 11), (29, o + 10), (29, o + 9)]
    for x, y in neck:
        put(a, x, y, hc[2])
    for x in range(24, 30):
        for y in range(o + 9, o + 15):
            if (x - 24) + (o + 15 - y) <= 7 and (x - 24) - (y - o - 9) >= -2:
                put(a, x, y, hc[2] if x > 25 else hc[1])
    rect(a, 28, o + 6, 32, o + 9, hc[2]); rect(a, 31, o + 8, 33, o + 11, hc[2])
    put(a, 33, o + 11, hc[1]); put(a, 32, o + 11, hc[1]); put(a, 33, o + 10, K)
    put(a, 30, o + 7, K); put(a, 28, o + 5, hc[1]); put(a, 29, o + 4, hc[2])
    for x in range(28, 33):
        put(a, x, o + 6, hc[3])
    for i in range(8):                                   # mane
        put(a, 24 + i * 0.6, o + 13 - i, K if i % 2 else hc[0])
        put(a, 23 + i * 0.6, o + 13 - i, hc[0])
    put(a, 30, o + 9, GOLD[1]); put(a, 29, o + 9, LEATH[0]); put(a, 28, o + 10, LEATH[0])  # bridle
    for x in range(20, 29):
        put(a, x, o + 10 + (x - 20) * 0.0, LEATH[0]) if x % 2 == 0 else None
    # saddle cloth
    rect(a, 13, o + 12, 20, o + 18, RED[2])
    for x in range(13, 21):
        put(a, x, o + 12, RED[3]); put(a, x, o + 18, GOLD[2] if x % 2 else GOLD[1]); put(a, x, o + 19, GOLD[1] if x % 2 == 0 else (0, 0, 0)) if x % 2 == 0 else None
    put(a, 20, o + 13, RED[1]); put(a, 20, o + 14, RED[1])
    # cloak streaming back
    cl = [(9, o + 7), (8, o + 8), (7, o + 9), (6, o + 11), (6, o + 12), (7, o + 13), (8, o + 14)]
    for y in range(o + 5, o + 16):
        x_start = 15 - (y - (o + 5)) * 0.9
        for x in range(int(x_start), 15):
            c = RED[2] if (x + y) % 5 else RED[1]
            if x == int(x_start):
                c = RED[3]
            put(a, x, y, c)
    for y in range(o + 7, o + 15, 2):
        put(a, 13 - (y - o - 7) // 2, y, RED[0])
    # rider legs
    for y in range(o + 13, o + 21):
        put(a, 18, y, SKIN[1] if y < o + 18 else LEATH[0]); put(a, 17, y, SKIN[0] if y < o + 18 else LEATH[1])
    # pteruges
    for x in range(14, 20):
        for y in range(o + 11, o + 14):
            put(a, x, y, LEATH[2] if x % 2 else LEATH[1])
    # muscle cuirass
    rect(a, 14, o + 4, 19, o + 10, GOLD[1])
    for y in range(o + 4, o + 11):
        put(a, 18, y, GOLD[2]); put(a, 19, y, GOLD[0])
        put(a, 17, y, GOLD[2] if y < o + 8 else GOLD[1])
    put(a, 17, o + 5, GOLD[3]); put(a, 18, o + 6, GOLD[3]); put(a, 16, o + 7, GOLD[2])
    rect(a, 14, o + 10, 19, o + 10, RED[1])              # sash
    put(a, 15, o + 10, RED[3])
    # arm to the reins
    put(a, 19, o + 6, RED[2]); put(a, 20, o + 7, SKIN[2]); put(a, 21, o + 8, SKIN[2]); put(a, 22, o + 9, SKIN[1])
    # head, helmet, transverse crest (centurion)
    rect(a, 15, o + 0, 18, o + 3, SKIN[2])
    put(a, 15, o + 2, SKIN[1]); put(a, 15, o + 3, SKIN[1]); put(a, 18, o + 1, K); put(a, 19, o + 2, SKIN[1])
    rect(a, 14, o - 2, 18, o + 0, GOLD[2])
    put(a, 15, o - 2, GOLD[3]); put(a, 16, o - 2, GOLD[3]); put(a, 14, o + 0, GOLD[0]); put(a, 14, o + 1, GOLD[1]); put(a, 19, o + 0, GOLD[1])
    for i, x in enumerate(range(12, 21)):
        hgt = 3 - abs(x - 16) // 2
        for k in range(hgt):
            put(a, x, o - 3 - k, RED[3] if k == hgt - 1 else RED[2])
        put(a, x, o - 3, RED[1])
    return a


def ox(step=0):
    a = rgba(30, 20)
    w = [C('6c625c'), C('a69c94'), C('d8d0c6'), C('f4eee6')]
    for i, bx in enumerate((6, 9, 19, 22)):
        sw = [(1, 0, -1, 0)[step % 4], (-1, 0, 1, 0)[step % 4]][i % 2]
        for y in range(12, 18):
            put(a, bx + (sw if y > 14 else 0), y, w[1] if i % 2 else w[0]); put(a, bx + 1 + (sw if y > 14 else 0), y, w[0])
        put(a, bx + sw, 18, K); put(a, bx + sw + 1, 18, K)
    for y in range(5, 14):
        for x in range(4, 25):
            dy = (y - 9) / 4.4
            dx = (x - 14) / 10.2
            if dx * dx + dy * dy <= 1:
                c = w[2]
                if dy < -0.5:
                    c = w[3]
                elif dy > 0.45:
                    c = w[1]
                put(a, x, y, c)
    rect(a, 20, 3, 24, 6, w[2]); put(a, 21, 3, w[3]); put(a, 22, 3, w[3])
    rect(a, 23, 6, 28, 11, w[2]); rect(a, 26, 9, 29, 12, w[1]); put(a, 28, 11, C('c08080')); put(a, 26, 8, K)
    put(a, 23, 5, C('e8dcc0')); put(a, 22, 4, C('e8dcc0')); put(a, 22, 3, C('c8b890'))
    put(a, 27, 5, C('e8dcc0')); put(a, 28, 4, C('c8b890'))
    put(a, 4, 7, w[1]); put(a, 3, 9, w[1]); put(a, 3, 11, w[0]); put(a, 2, 13, w[0])
    for x in range(12, 18):                              # garland
        put(a, x, 5 + (1 if x % 3 == 0 else 0), RED[2] if x % 2 else RED[3])
    for y in range(6, 11):
        put(a, 15, y, RED[2] if y % 2 else C('e0c050'))
    return a


def cart(t=0):
    a = rgba(38, 26)
    for y in range(8, 17):
        for x in range(4, 31):
            c = WOOD[2]
            if y == 8:
                c = WOOD[3]
            elif y == 16:
                c = WOOD[0]
            elif x in (4, 13, 22, 30):
                c = WOOD[1]
            put(a, x, y, c)
    for x in range(4, 31):
        if x % 3 == 0:
            put(a, x, 12, WOOD[1])
    sacks = [(8, 5, 5), (14, 4, 5), (20, 5, 5), (26, 5, 4), (11, 2, 4), (18, 2, 4)]
    for (cx, cy, r) in sacks:
        for y in range(cy - r, cy + r):
            for x in range(cx - r, cx + r):
                if ((x - cx) / r) ** 2 + ((y - cy) / (r * 0.9)) ** 2 <= 1 and y < 9 + (cy - 2):
                    c = CLOTH[2]
                    if (x - cx) < -r * 0.3 and (y - cy) < 0:
                        c = CLOTH[3]
                    elif (x - cx) > r * 0.35 or (y - cy) > r * 0.4:
                        c = CLOTH[1]
                    put(a, x, y, c)
        put(a, cx, cy - r + 1, CLOTH[0])
    for x in range(31, 37):
        put(a, x, 13, WOOD[1])
    for (cx, cy) in ((10, 19), (25, 19)):
        for ang in range(0, 360, 8):
            r = 5.6
            put(a, int(cx + math.cos(math.radians(ang)) * r), int(cy + math.sin(math.radians(ang)) * r), WOOD[0])
            put(a, int(cx + math.cos(math.radians(ang)) * (r - 1)), int(cy + math.sin(math.radians(ang)) * (r - 1)), WOOD[1])
        for k in range(6):
            ang = t * 0.3 + k * math.pi / 3
            for rr in range(1, 5):
                put(a, int(round(cx + math.cos(ang) * rr)), int(round(cy + math.sin(ang) * rr)), WOOD[1])
        put(a, cx, cy, GOLD[1])
    # hanging lantern
    put(a, 31, 6, K); put(a, 31, 7, K); rect(a, 30, 8, 32, 10, C('ffd27a')); put(a, 31, 11, WOOD[0])
    return a


def tent(w=40, h=28, leather=None):
    lt = leather or [C('4a3424'), C('7a5a3c'), C('a07a52'), C('c8a272')]
    a = rgba(w + 8, h + 3)
    ridge_y = 2
    fx0, fx1 = 4, 4 + w // 2          # front gable (facing camera-left), roof plane to the right
    apex = (fx0 + (fx1 - fx0) // 2, ridge_y)
    for y in range(ridge_y, h + 1):
        t = (y - ridge_y) / (h - ridge_y)
        half = int(t * (fx1 - fx0) / 2)
        for x in range(apex[0] - half, apex[0] + half + 1):
            c = lt[2]
            if x == apex[0] - half:
                c = lt[3]
            if (x - apex[0]) % 5 == 0:
                c = lt[1]
            put(a, x, y, c)
        # roof plane to the right
        for x in range(apex[0] + half + 1, apex[0] + half + 1 + (w - (fx1 - fx0)) + 0):
            c = lt[1] if (y + x // 6) % 6 else lt[0]
            if y == ridge_y + int((x - apex[0]) * 0.0):
                c = lt[2]
            put(a, x, y, c)
    # door opening
    for y in range(int(h * 0.45), h + 1):
        t = (y - h * 0.45) / (h * 0.55)
        half = int(1 + t * 4)
        for x in range(apex[0] - half, apex[0] + half + 1):
            put(a, x, y, C('140c0a'))
    put(a, apex[0], ridge_y - 1, WOOD[1]); put(a, apex[0], ridge_y - 2, WOOD[2])
    for x in range(apex[0], apex[0] + w - (fx1 - fx0) + half - 2):
        put(a, x, ridge_y, lt[3])
    return a


def standard(t=0):
    a = rgba(16, 52)
    for y in range(6, 52):
        put(a, 7, y, WOOD[2]); put(a, 8, y, WOOD[1])
    # eagle
    for x, y, c in ((7, 0, GOLD[3]), (6, 1, GOLD[2]), (7, 1, GOLD[3]), (8, 1, GOLD[2]), (4, 2, GOLD[1]), (5, 2, GOLD[2]), (6, 2, GOLD[2]), (7, 2, GOLD[2]), (8, 2, GOLD[2]), (9, 2, GOLD[2]), (10, 2, GOLD[1]),
                    (3, 3, GOLD[1]), (11, 3, GOLD[1]), (6, 3, GOLD[1]), (7, 3, GOLD[2]), (8, 3, GOLD[1]), (7, 4, GOLD[1]), (6, 5, GOLD[2]), (7, 5, GOLD[2]), (8, 5, GOLD[2])):
        put(a, x, y, c)
    for x in range(2, 14):
        put(a, x, 9, WOOD[1])
    for x in range(2, 14):
        wav = round(math.sin(x * 0.6 + t) * 1.0)
        for y in range(10, 23 + wav):
            c = RED[2]
            if x == 2:
                c = RED[3]
            if (x + t) % 6 == 0:
                c = RED[1]
            put(a, x, y, c)
        put(a, x, 23 + wav, GOLD[2]); put(a, x, 24 + wav, GOLD[1] if x % 2 else (0, 0, 0)) if x % 2 else None
    for x, y in ((6, 13), (7, 13), (8, 13), (6, 14), (8, 14), (6, 15), (7, 15), (8, 15), (7, 17), (7, 18), (5, 18), (9, 18)):
        put(a, x, y, GOLD[2])
    for y in (26, 30, 34):
        for x in range(5, 11):
            put(a, x, y, GOLD[1] if x in (5, 10) else GOLD[2])
        put(a, 7, y - 1, GOLD[3])
    return a


def campfire(t=0):
    a = rgba(22, 20)
    e = rgba(22, 20)
    st = [C('3a3436'), C('6a6266'), C('9a9094')]
    for ang in range(0, 360, 30):
        x = int(11 + math.cos(math.radians(ang)) * 8)
        y = int(15 + math.sin(math.radians(ang)) * 3.5)
        put(a, x, y, st[1]); put(a, x + 1, y, st[0]); put(a, x, y - 1, st[2])
    for i in range(10):
        put(a, 6 + i, 14 + (i % 3 == 0), WOOD[1]); put(a, 6 + i, 15, WOOD[0])
    for i in range(8):
        put(a, 8 + i, 12 + i // 3, WOOD[2])
    r = random.Random(t)
    for k in range(26):
        x = 11 + r.randint(-4, 4)
        hgt = r.randint(2, 11 - abs(x - 11) * 2) if abs(x - 11) < 5 else 2
        for y in range(13 - hgt, 13):
            f = (13 - y) / max(1, hgt)
            c = C('fff2b0') if f < 0.3 and abs(x - 11) < 3 else C('ffb040') if f < 0.6 else C('e2502a')
            put(a, x, y, c); put(e, x, y, c * 0.7)
    for k in range(4):
        x, y = 11 + r.randint(-5, 5), r.randint(0, 5)
        put(a, x, y, C('ffcf70')); put(e, x, y, C('ffcf70') * 0.8)
    return a, e


def crate(w=9, h=8):
    a = rgba(w, h)
    rect(a, 0, 0, w - 1, h - 1, WOOD[2])
    for x in range(w):
        put(a, x, 0, WOOD[3]); put(a, x, h - 1, WOOD[0])
    for y in range(h):
        put(a, 0, y, WOOD[3]); put(a, w - 1, y, WOOD[1])
    for i in range(min(w, h)):
        put(a, i * (w - 1) // (h - 1), i, WOOD[1])
    return a


def amphora():
    a = rgba(7, 12)
    cl = [C('6a3020'), C('a4522c'), C('cc7a46')]
    for y in range(2, 12):
        r = [1, 1, 2, 3, 3, 3, 3, 2, 1, 1][y - 2]
        for x in range(3 - r, 4 + r):
            put(a, x, y, cl[2] if x < 3 else cl[1] if x < 5 else cl[0])
    put(a, 3, 0, cl[1]); put(a, 3, 1, cl[1]); put(a, 1, 2, cl[0]); put(a, 5, 2, cl[0])
    return a


def rock(w, h, seed, pal=None):
    pal = pal or [C('3a3638'), C('5e585a'), C('86807c'), C('b0aaa2')]
    r = np.random.default_rng(seed)
    a = rgba(w, h)
    for y in range(h):
        for x in range(w):
            dx, dy = (x - w / 2) / (w / 2), (y - h * 0.6) / (h * 0.6)
            n = 0.15 * math.sin(x * 1.3 + seed) + 0.12 * math.sin(y * 1.7 + seed * 2)
            if dx * dx + dy * dy < 1 + n and y < h:
                lam = -dx * 0.6 - dy * 0.8
                i = 0 if lam < -0.35 else 1 if lam < 0.1 else 2 if lam < 0.55 else 3
                if y == h - 1:
                    i = 0
                put(a, x, y, pal[i])
    return a


def tuft(seed, pal, n=None, h=6, w=9):
    r = random.Random(seed)
    a = rgba(w, h + 1)
    for k in range(n or r.randint(4, 7)):
        x = r.randint(1, w - 2)
        hh = r.randint(2, h)
        lean = r.choice([-1, 0, 0, 1])
        for i in range(hh):
            put(a, int(x + lean * i / hh), h - i, pal[1] if i < hh - 1 else pal[2])
        put(a, x, h, pal[0])
    return a


def stone_pine(seed, pal, bark, h=86, fine=1.0, R=26, tw=3):
    """umbrella pine: tall bare curving trunk, flat wide crown"""
    r = random.Random(seed)
    can, mask = canopy(R, seed, pal, squash=0.42, n_clusters=int(34 * (R / 26) ** 2), fine=fine)
    cw = can.shape[1]
    a = rgba(cw + 6, h)
    lean = r.choice([-1, 1]) * r.uniform(0.05, 0.12)
    top = can.shape[0] // 2
    for y in range(top, h):
        t = (h - y)
        x = int(a.shape[1] / 2 + lean * t)
        for k in range(tw):
            put(a, x + k - tw // 2, y, bark[2] if k == 0 else bark[0] if k == tw - 1 else bark[1])
        if y % 5 == 0:
            put(a, x, y, bark[0])
    cx = int(a.shape[1] / 2 + lean * (h - top)) - cw // 2
    # branch stubs into the crown
    for k in (-1, 1):
        for i in range(int(7 * R / 26)):
            put(a, cx + cw // 2 + k * i, top + int(6 * R / 26) - i // 2, bark[1])
    for y in range(can.shape[0]):
        for x in range(cw):
            if can[y, x, 3] > 0.5 and 0 <= cx + x < a.shape[1]:
                a[y, cx + x] = can[y, x]
    return a


def cypress(seed, pal, h=70, w=18):
    r = np.random.default_rng(seed)
    a = rgba(w, h)
    yy, xx = np.mgrid[0:h, 0:w]
    cxw = w / 2
    t = yy / h
    halfw = (w / 2 - 1.5) * np.sin(np.clip(t, 0, 1) * math.pi * 0.95) ** 0.7 * (0.55 + 0.45 * t)
    jag = np.sin(yy * 1.7 + seed) * 0.8 + np.sin(yy * 0.6) * 0.6
    inside = np.abs(xx - cxw) < halfw + jag * 0.4 * w / 18
    inside &= yy < h - 3
    lam = -(xx - cxw) / np.maximum(halfw, 1) * 0.7 + 0.25
    lam += np.sin(yy * 0.9 * 18 / w + xx * 0.7 * 18 / w) * 0.25
    q = np.clip(band(np.clip(lam * 0.5 + 0.5, 0, 0.999), 4), 0, 0.999)
    idx = (q * len(pal)).astype(int)
    for i, c in enumerate(pal):
        m = inside & (idx == i)
        a[m, :3] = c
        a[m, 3] = 1
    for y in range(h - 5, h):
        put(a, int(cxw), y, C('3a2618')); put(a, int(cxw) - 1, y, C('5a3a24'))
    return a


def oak(seed, pal, bark, R=20, h=None, fine=1.0):
    can, mask = canopy(R, seed, pal, squash=0.8, fine=fine)
    cw, ch = can.shape[1], can.shape[0]
    th = h or int(R * 1.1)
    a = rgba(cw, ch + th - 6)
    trunk(a, cw // 2, ch - 10, ch + th - 7, 5, bark, None)
    for x in range(cw):
        for y in range(ch):
            if can[y, x, 3] > 0.5:
                a[y, x] = can[y, x]
    return a


def priest(t=0):
    a = rgba(14, 24)
    robe = [C('7a7268'), C('b4ab9c'), C('e2dacb'), C('fbf6ea')]
    for y in range(8, 23):
        w = 3 + (y - 8) // 3
        for x in range(7 - w, 7 + w):
            c = robe[2]
            if x == 7 - w:
                c = robe[3]
            elif x >= 7 + w - 2:
                c = robe[1]
            if (x - 7) % 4 == 2 and y > 12:
                c = robe[1]
            put(a, x, y, c)
    for x in range(2, 13):
        put(a, x, 23, robe[0])
    rect(a, 5, 3, 8, 7, SKIN[2]); put(a, 8, 5, K); put(a, 5, 6, SKIN[1])
    rect(a, 4, 1, 9, 3, robe[2]); put(a, 4, 4, robe[2]); put(a, 4, 5, robe[1]); put(a, 4, 6, robe[1]); put(a, 4, 2, robe[3])
    for x in range(4, 11):
        put(a, x, 13, RED[2])
    for y in range(13, 19):
        put(a, 6, y, RED[2] if y % 2 else RED[1])
    put(a, 6, 19, RED[3])
    # arms raised with a bowl
    put(a, 10, 9, robe[2]); put(a, 11, 8, robe[2]); put(a, 11, 7, SKIN[2]); rect(a, 10, 5, 13, 6, GOLD[1]); put(a, 11, 5, GOLD[3])
    return a


def altar(t=0):
    a = rgba(62, 46)
    e = rgba(62, 46)
    st = [C('3c383a'), C('6e686a'), C('9e9692'), C('cfc6bc')]
    # stepped base seen from 3/4: top surfaces lit, fronts mid, right sides dark
    def block(x0, y0, w, d, hgt):
        for y in range(y0 - d, y0):                  # top face
            for x in range(x0 + (y0 - y) // 2, x0 + w + (y0 - y) // 2):
                put(a, x, y, st[3] if (x + y) % 7 else st[2])
        for y in range(y0, y0 + hgt):                 # front face
            for x in range(x0, x0 + w):
                put(a, x, y, st[2] if (x // 6 + y // 3) % 2 or y % 3 else st[1])
            for x in range(x0 + w, x0 + w + d // 2):  # side face
                put(a, x, y - (x - x0 - w), st[0] if (x + y) % 3 else st[1])
    block(2, 34, 54, 6, 8)
    block(8, 28, 42, 5, 6)
    block(16, 18, 26, 4, 10)
    # carved frieze on the top block
    for x in range(18, 40, 4):
        put(a, x, 21, st[0]); put(a, x + 1, 22, st[0]); put(a, x, 23, st[0])
    # old blood on the front
    for y in range(18, 30):
        put(a, 24 + (y % 2), y, C('5a1410') if y < 26 else C('3a0c0a'))
    # bronze brazier bowl with fire
    rect(a, 23, 9, 34, 11, GOLD[1]); rect(a, 24, 12, 33, 13, GOLD[0]); put(a, 24, 9, GOLD[3]); put(a, 25, 9, GOLD[2])
    r = random.Random(t + 4)
    for k in range(30):
        x = 28 + r.randint(-5, 5)
        hh = r.randint(2, 12 - abs(x - 28) * 2) if abs(x - 28) < 6 else 1
        for y in range(9 - hh, 9):
            f = (9 - y) / max(1, hh)
            c = C('fff3b8') if f < 0.35 and abs(x - 28) < 3 else C('ffae3c') if f < 0.7 else C('d8452a')
            put(a, x, y, c); put(e, x, y, c * 0.75)
    # offerings: bowls and a cloth
    for (cx, cy) in ((10, 30), (48, 30)):
        rect(a, cx - 2, cy - 1, cx + 2, cy, GOLD[1]); put(a, cx - 1, cy - 2, C('ddc070')); put(a, cx, cy - 2, C('a0d050'))
    return a, e


def column(h=34, broken=False):
    a = rgba(12, h)
    st = [C('3c383a'), C('6e686a'), C('9e9692'), C('cfc6bc')]
    for y in range(3, h - 3):
        for x in range(2, 10):
            c = st[2] if x < 5 else st[1] if x < 8 else st[0]
            if x in (3, 6) :
                c = st[3] if x == 3 else st[1]
            put(a, x, y, c)
    rect(a, 1, h - 3, 10, h - 1, st[1]); rect(a, 1, h - 3, 10, h - 3, st[3])
    if broken:
        for x in range(2, 10):
            for y in range(0, 3 + (x * 7) % 4):
                a[y, x, 3] = 0
    else:
        rect(a, 1, 0, 10, 2, st[2]); rect(a, 1, 0, 10, 0, st[3])
    return a


def reeds(seed, pal, h=10):
    r = random.Random(seed)
    a = rgba(10, h + 1)
    for k in range(r.randint(5, 8)):
        x = r.randint(1, 8)
        hh = r.randint(h // 2, h)
        lean = r.uniform(-0.25, 0.25)
        for i in range(hh):
            put(a, int(x + lean * i), h - i, pal[1] if i < hh - 2 else pal[2])
        if r.random() < 0.5:
            put(a, int(x + lean * hh), h - hh, C('6a4a2a')); put(a, int(x + lean * hh), h - hh + 1, C('6a4a2a'))
    return a


def sitter(tunic=RED):
    a = rgba(10, 12)
    rect(a, 2, 7, 7, 10, tunic[2]); put(a, 7, 8, tunic[1]); put(a, 7, 9, tunic[1])
    rect(a, 3, 4, 6, 7, STEEL[2]); put(a, 6, 5, STEEL[1])
    rect(a, 3, 0, 6, 3, SKIN[2]); put(a, 3, 2, SKIN[1]); rect(a, 3, 0, 6, 0, C('3a2a20'))
    rect(a, 1, 10, 8, 11, LEATH[1])
    put(a, 7, 6, SKIN[2]); put(a, 8, 6, SKIN[2])
    return a


def weapon_rack():
    a = rgba(22, 20)
    for x in (2, 19):
        for y in range(6, 20):
            put(a, x, y, WOOD[1])
    for x in range(1, 21):
        put(a, x, 7, WOOD[2]); put(a, x, 14, WOOD[1])
    for i, x in enumerate(range(4, 18, 3)):
        for y in range(0, 18):
            put(a, x + (y > 8) * 0, y, WOOD[2] if y > 2 else STEEL[3])
    # two scuta leaning
    for k, x0 in enumerate((3, 11)):
        for y in range(9, 20):
            for x in range(x0, x0 + 6):
                c = RED[2] if x < x0 + 4 else RED[1]
                if y in (9, 19) or x == x0:
                    c = GOLD[2]
                put(a, x, y, c)
        put(a, x0 + 2, 14, GOLD[3])
    return a


def birch(seed, pal, h=80):
    r = random.Random(seed)
    can, mask = canopy(16, seed, pal, squash=1.15)
    cw, ch = can.shape[1], can.shape[0]
    a = rgba(cw, h)
    bx = cw // 2
    for y in range(ch // 2, h):
        for k in range(3):
            c = C('e8e2d6') if k == 0 else C('bdb6a8') if k == 1 else C('7a7468')
            if (y * 7 + k) % 9 == 0 or (y % 11 == 3 and k < 2):
                c = C('2a2422')
            put(a, bx - 1 + k, y, c)
    for y in range(ch):
        for x in range(cw):
            if can[y, x, 3] > 0.5:
                a[y, x] = can[y, x]
    return a


def totem(seed=0):
    """Thorncrown pole with a bone mask and hanging charms"""
    a = rgba(14, 34)
    for y in range(6, 34):
        put(a, 6, y, WOOD[1]); put(a, 7, y, WOOD[0])
        if y % 4 == 0:
            put(a, 6, y, WOOD[2])
    bone = [C('8a8070'), C('c8bea8'), C('ece4d0')]
    for y in range(0, 10):
        w = [3, 4, 5, 5, 5, 4, 4, 3, 2, 1][y]
        for x in range(7 - w, 7 + w):
            c = bone[2] if x < 6 else bone[1] if x < 9 else bone[0]
            put(a, x, y + 4, c)
    put(a, 4, 8, K); put(a, 5, 8, K); put(a, 8, 8, K); put(a, 9, 8, K)
    put(a, 6, 11, K); put(a, 7, 11, K)
    for x, y in ((2, 4), (1, 3), (0, 1), (11, 4), (12, 3), (13, 1)):
        put(a, x, y, bone[1])                            # antlers
    for k, x in enumerate((3, 10)):
        for y in range(15, 22):
            put(a, x, y, C('6a5a3a'))
        put(a, x, 22, C('c04030') if k else C('e0c060')); put(a, x, 23, bone[1])
    return a


def goblin_eyes():
    a = rgba(6, 2)
    e = rgba(6, 2)
    for x in (0, 1, 4, 5):
        put(a, x, 0, C('ffd060')); put(e, x, 0, C('ffd060') * 0.9)
    return a, e


def runestone(glow=True):
    a = rgba(18, 40)
    e = rgba(18, 40)
    st = [C('2a2c34'), C('4a4c58'), C('6e7280'), C('9aa0b0')]
    for y in range(40):
        t = y / 40
        half = 5 + t * 3 + (1 if y < 4 else 0) * -2
        for x in range(int(9 - half), int(9 + half)):
            c = st[2] if x < 7 else st[1] if x < 12 else st[0]
            if x == int(9 - half):
                c = st[3]
            if (x * 5 + y * 3) % 17 == 0:
                c = st[0]
            put(a, x, y, c)
    for y in range(36, 40):
        for x in range(1, 17):
            if a[y, x, 3] > 0:
                put(a, x, y, st[0])
    # carved runic band
    path = [(7, 8), (7, 9), (7, 10), (8, 11), (9, 12), (10, 12), (10, 13), (10, 14), (9, 15), (8, 16), (8, 17), (8, 18), (9, 19), (10, 20), (10, 21), (9, 22), (8, 23), (8, 24), (8, 25), (9, 26), (10, 27), (10, 28), (9, 29), (8, 30)]
    for (x, y) in path:
        c = C('8ad4ff') if glow else st[0]
        put(a, x, y, c)
        if glow:
            put(e, x, y, C('6ac0ff') * 0.9)
    for (x, y) in ((6, 12), (11, 17), (6, 21), (11, 25)):
        put(a, x, y, C('8ad4ff') if glow else st[0])
        if glow:
            put(e, x, y, C('6ac0ff') * 0.7)
    # snow cap
    for x in range(4, 14):
        if a[0, x, 3] > 0 or a[1, x, 3] > 0:
            put(a, x, 0 if a[0, x, 3] > 0 else 1, C('f0f6ff'))
            put(a, x, 1 if a[0, x, 3] > 0 else 2, C('c8d4e8'))
    return a, e


def northman(step=0, torch=False):
    """Frostbay oathshield: tall, fur-cloaked, round shield, bearded"""
    a = rgba(16, 28)
    fur = [C('3a3432'), C('6a605a'), C('9a8e84')]
    cloth = [C('1e2a40'), C('2e4262'), C('46628a')]
    sh = [C('1a2a40'), C('2c4466'), C('4a6a94'), C('a8b4c4')]
    o = 2
    for (lx) in (5, 9):
        for y in range(o + 18, o + 25):
            put(a, lx, y, fur[0]); put(a, lx + 1, y, fur[1] if y > o + 21 else cloth[1])
    rect(a, 4, o + 9, 11, o + 18, cloth[1])
    for y in range(o + 9, o + 19):
        put(a, 4, y, cloth[2]); put(a, 11, y, cloth[0])
    rect(a, 3, o + 8, 12, o + 10, fur[1])
    for x in range(3, 13):
        put(a, x, o + 8, fur[2] if x % 2 else fur[1])
    rect(a, 4, o + 14, 11, o + 14, C('4a3020'))
    # head: helm and braided beard
    rect(a, 5, o + 2, 9, o + 7, SKIN[2]); put(a, 9, o + 4, K); put(a, 5, o + 4, SKIN[1])
    rect(a, 5, o + 5, 9, o + 8, C('c0905a')); put(a, 7, o + 8, C('c0905a')); put(a, 7, o + 9, C('a07040'))
    rect(a, 4, o + 0, 9, o + 2, STEEL[2]); put(a, 5, o + 0, STEEL[3]); put(a, 4, o + 2, STEEL[0])
    put(a, 3, o - 1, C('e0d8c0')); put(a, 3, o - 2, C('e0d8c0')); put(a, 10, o - 1, C('e0d8c0')); put(a, 10, o - 2, C('e0d8c0'))
    # round shield on the near side
    cx, cy, r = 11, o + 16, 4.3
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            dd = math.hypot(x - cx, (y - cy) * 1.05)
            if dd <= r:
                c = sh[2] if x < cx else sh[1]
                if dd > r - 1:
                    c = sh[3] if x < cx else sh[0]
                if abs(x - cx) < 0.6 or abs(y - cy) < 0.6:
                    c = C('d8dce4')
                put(a, x, y, c)
    put(a, cx, cy, GOLD[2])
    if torch:
        for y in range(o + 2, o + 14):
            put(a, 2, y, WOOD[1])
    else:
        for y in range(o - 4, o + 18):
            put(a, 2, y, WOOD[2])
        put(a, 2, o - 5, STEEL[3]); put(a, 1, o - 3, STEEL[2]); put(a, 3, o - 3, STEEL[2])
    return a


def snow_pine(seed, h=64):
    r = np.random.default_rng(seed)
    a = rgba(34, h)
    G = [C('0c1a1e'), C('16282c'), C('20383a'), C('2e4a48')]
    SN = [C('a8b8d0'), C('d4e0f0'), C('f6faff')]
    cx = 17
    tiers = 6
    for t in range(tiers):
        top = int(2 + t * (h - 12) / tiers)
        bot = int(top + (h - 12) / tiers + 6)
        maxw = 4 + t * 2.4
        for y in range(top, min(bot, h - 4)):
            frac = (y - top) / max(1, bot - top)
            w = maxw * frac + 1
            jag = int(r.integers(-1, 2))
            for x in range(int(cx - w) + (jag if frac > 0.8 else 0), int(cx + w) + 1):
                rel = (x - cx) / max(w, 1)
                c = G[2] if rel < -0.2 else G[1] if rel < 0.4 else G[0]
                if frac > 0.85:
                    c = G[0]
                put(a, x, y, c)
            if frac < 0.45:                                 # snow on the upper face of each tier
                for x in range(int(cx - w), int(cx + w * 0.6) + 1):
                    if r.random() < 0.85:
                        put(a, x, y, SN[2] if x < cx - w * 0.3 else SN[1])
            elif frac < 0.6 and r.random() < 0.5:
                put(a, int(cx - w), y, SN[1])
    for y in range(h - 6, h):
        put(a, cx, y, C('3a2a22')); put(a, cx - 1, y, C('5a4030'))
    return a


def aqueduct(n_arches=9, arch_w=16, h=40):
    """distant aqueduct: two tiers of arches, lit from the west"""
    w = n_arches * arch_w + 4
    a = rgba(w, h)
    st = [C('4a3a3a'), C('7a6258'), C('a88a74'), C('d0b296')]
    def tier(y0, y1, aw, top_band):
        for y in range(y0, y1):
            for x in range(0, w):
                put(a, x, y, st[2] if (x // 3 + y // 2) % 5 else st[1])
        for x in range(w):
            for y in range(y0, y0 + top_band):
                put(a, x, y, st[3] if y == y0 else st[2])
        for i in range(w // aw):
            cx = i * aw + aw // 2 + 2
            r = aw // 2 - 3
            for y in range(y0 + top_band + 1, y1):
                for x in range(cx - r, cx + r + 1):
                    dy = y - (y0 + top_band + 1 + r)
                    if dy >= 0 or (x - cx) ** 2 + dy * dy <= r * r:
                        put(a, x, y, C('1c1418') if x > cx - r + 1 else st[0])
            for y in range(y0 + top_band + 1, y1):
                put(a, cx + r + 1, y, st[3])
    tier(0, h // 2, arch_w // 2 + 2, 3)
    tier(h // 2, h, arch_w, 2)
    return a
