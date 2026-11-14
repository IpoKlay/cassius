#!/usr/bin/env python3
"""Generates every pixel-art sprite, background layer, icon, font and sound used by CASSIUS.
Run from the project root:  python3 tools/gen_assets.py
Everything is procedural so you can tweak palettes/shapes and regenerate."""
import math, os, random, struct, wave, sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
random.seed(7)


def out(path):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def new(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (255,)


def C(r, g, b):
    return (r, g, b, 255)


def strip(frames):
    w, h = frames[0].size
    im = new(w * len(frames), h)
    for i, f in enumerate(frames):
        im.paste(f, (i * w, 0))
    return im


# --------------------------------------------------------------------------
# Region palettes (S = Vermilion Empire, W = Thorncrown, N = Frostbay, E = Duskviolet)
# --------------------------------------------------------------------------
REGIONS = {
    "south": dict(mount=C(126, 84, 92), mount_hi=C(196, 130, 104), far=C(74, 50, 62), far_hi=C(120, 78, 74),
                  mid=C(36, 28, 40), mid_hi=C(84, 56, 58), ground=C(30, 24, 28), dirt=C(58, 42, 38),
                  grass=C(84, 92, 44), grass_hi=C(150, 140, 62), leaf=C(52, 60, 36), leaf_hi=C(140, 120, 56),
                  trunk=C(30, 22, 24)),
    "west": dict(mount=C(66, 108, 98), mount_hi=C(130, 170, 130), far=C(38, 74, 60), far_hi=C(80, 124, 84),
                 mid=C(18, 40, 34), mid_hi=C(48, 86, 56), ground=C(18, 26, 22), dirt=C(46, 44, 30),
                 grass=C(56, 104, 50), grass_hi=C(130, 176, 80), leaf=C(30, 70, 44), leaf_hi=C(96, 150, 74),
                 trunk=C(22, 26, 20)),
    "north": dict(mount=C(140, 166, 196), mount_hi=C(232, 240, 248), far=C(84, 110, 142), far_hi=C(170, 196, 220),
                  mid=C(40, 56, 82), mid_hi=C(120, 150, 184), ground=C(40, 50, 70), dirt=C(86, 100, 124),
                  grass=C(196, 212, 230), grass_hi=C(240, 246, 252), leaf=C(48, 72, 92), leaf_hi=C(214, 228, 240),
                  trunk=C(28, 32, 44)),
    "east": dict(mount=C(92, 58, 120), mount_hi=C(186, 110, 170), far=C(58, 34, 84), far_hi=C(120, 70, 130),
                 mid=C(28, 16, 46), mid_hi=C(84, 46, 96), ground=C(22, 14, 32), dirt=C(52, 34, 62),
                 grass=C(96, 70, 128), grass_hi=C(188, 150, 210), leaf=C(60, 34, 84), leaf_hi=C(170, 110, 180),
                 trunk=C(20, 12, 28)),
}


def periodic(w, comps, seed):
    r = random.Random(seed)
    ph = [(k, a, r.random() * 6.28) for k, a in comps]
    return [sum(a * math.sin(2 * math.pi * k * x / w + p) for k, a, p in ph) for x in range(w)]


def gen_mountains(name, pal, seed):
    w, h = 480, 110
    im = new(w, h)
    prof = periodic(w, [(1, 14), (2, 12), (3, 9), (5, 6), (8, 4), (13, 2), (21, 1.2)], seed)
    for x in range(w):
        top = int(46 - prof[x])
        top = max(4, min(h - 10, top))
        slope = prof[(x + 1) % w] - prof[x - 1]
        for y in range(top, h):
            d = y - top
            c = pal["mount"]
            # sun-facing (rising) slopes get a rim light, dithered
            if slope > 0.25 and d < 10 + (x % 3) and (x + y) % 2 == 0:
                c = pal["mount_hi"]
            elif d < 2:
                c = pal["mount_hi"]
            # fade into haze at the base
            if d > 40 and (x + y) % 2 == 0:
                c = shade(c, 1.12)
            im.putpixel((x, y), c)
    im.save(out(f"bg/{name}_mountains.png"))


def blob_tree(d, x, base, hgt, pal_c, pal_hi, trunk, r, conifer):
    if conifer:
        tiers = max(3, hgt // 7)
        d.rectangle([x, base - hgt // 3, x + 1, base], fill=trunk)
        for t in range(tiers):
            ty = base - hgt // 4 - t * (hgt * 3 // 4) // tiers
            half = max(1, int((tiers - t) * hgt / (tiers * 5.0)) + 1)
            d.polygon([(x - half, ty), (x + 1 + half, ty), (x + 1, ty - hgt // tiers - 3), (x, ty - hgt // tiers - 3)], fill=pal_c)
            d.line([(x - half, ty), (x, ty - hgt // tiers - 3)], fill=pal_hi)
    else:
        d.rectangle([x, base - hgt // 2, x + 1, base], fill=trunk)
        cx, cy = x, base - hgt * 2 // 3
        rad = max(3, hgt // 4)
        for i in range(5):
            ox = r.randint(-rad, rad)
            oy = r.randint(-rad // 2, rad // 2)
            rr = r.randint(rad * 2 // 3, rad)
            d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=pal_c)
            d.arc([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], 180, 280, fill=pal_hi)


def wrap_draw(w, h, fn):
    """draw on a 3x wide canvas and fold so the strip tiles seamlessly"""
    big = new(w * 3, h)
    d = ImageDraw.Draw(big)
    fn(d, w)
    res = new(w, h)
    for k in range(3):
        part = big.crop((k * w, 0, (k + 1) * w, h))
        res.alpha_composite(part)
    return res


def gen_forest(name, pal, seed, far):
    w, h = 480, (70 if far else 120)
    r = random.Random(seed)
    col, hi = (pal["far"], pal["far_hi"]) if far else (pal["mid"], pal["mid_hi"])
    conif = name in ("north", "west")

    def fn(d, w):
        n = 70 if far else 34
        xs = sorted(r.randint(0, w - 1) for _ in range(n))
        for x in xs:
            hgt = r.randint(22, 40) if far else r.randint(50, 100)
            cf = conif if r.random() < 0.75 else not conif
            blob_tree(d, w + x, h, hgt, col, hi, shade(col, 0.8), r, cf)
        # undergrowth band so the base is solid
        prof = periodic(w, [(3, 3), (7, 2), (17, 1.5), (29, 1)], seed + 5)
        for x in range(w):
            top = h - (10 if far else 14) - int(prof[x])
            d.line([(w + x, top), (w + x, h)], fill=col)
            if x % 3 == 0:
                d.point((w + x, top), fill=hi)

    wrap_draw(w, h, fn).save(out(f"bg/{name}_forest_{'far' if far else 'mid'}.png"))


def gen_ground(name, pal):
    w, h = 96, 40
    im = new(w, h)
    r = random.Random(hash(name) & 0xffff)
    for x in range(w):
        for y in range(h):
            c = pal["ground"]
            if y < 2:
                c = pal["grass_hi"] if (x * 7 + y) % 5 < 2 else pal["grass"]
            elif y < 4:
                c = pal["grass"] if (x + y) % 2 == 0 else shade(pal["grass"], 0.7)
            elif y < 12:
                c = pal["dirt"] if (x * 3 + y * 5) % 7 < 3 else shade(pal["dirt"], 0.8)
            elif (x * 5 + y * 3) % 11 == 0:
                c = shade(pal["dirt"], 0.7)
            im.putpixel((x, y), c)
    for _ in range(10):  # pebbles
        x, y = r.randint(0, w - 2), r.randint(5, 11)
        im.putpixel((x, y), shade(pal["dirt"], 1.4))
    im.save(out(f"bg/{name}_ground.png"))
    # grass tufts strip (foreground + decoration), 8 tufts of 12x10
    tu = new(12 * 8, 10)
    d = ImageDraw.Draw(tu)
    for i in range(8):
        for b in range(r.randint(4, 7)):
            bx = i * 12 + r.randint(1, 10)
            bh = r.randint(3, 9)
            lean = r.choice([-1, 0, 0, 1])
            d.line([(bx, 9), (bx + lean, 9 - bh)], fill=pal["grass"] if b % 2 else pal["grass_hi"])
    tu.save(out(f"bg/{name}_tufts.png"))


def gen_trees(name, pal):
    r = random.Random(hash(name) & 0xfff)
    conif = name in ("north", "west")
    for i in range(4):
        w, h = 64, 112
        im = new(w, h)
        d = ImageDraw.Draw(im)
        hgt = r.randint(80, 108)
        cf = conif if i < 3 else not conif
        tr = pal["trunk"]
        if cf:
            d.rectangle([30, h - hgt // 2, 33, h], fill=tr)
            d.line([(30, h - hgt // 2), (30, h)], fill=shade(pal["leaf_hi"], 0.6))
            tiers = 6
            for t in range(tiers):
                ty = h - 20 - t * (hgt - 28) // tiers
                half = 6 + (tiers - t) * 3 + r.randint(-1, 2)
                top = ty - (hgt - 28) // tiers - 8
                d.polygon([(31 - half, ty), (32 + half, ty), (32, top), (31, top)], fill=pal["leaf"])
                d.line([(31 - half, ty), (31, top)], fill=pal["leaf_hi"])
                for k in range(half):
                    if k % 2 == 0:
                        d.point((31 - half + k, ty - k // 2 - 1), fill=pal["leaf_hi"])
                d.line([(31 - half + 2, ty), (32 + half - 2, ty)], fill=shade(pal["leaf"], 0.7))
        else:
            d.rectangle([29, h - hgt * 2 // 3, 34, h], fill=tr)
            d.line([(29, h - hgt * 2 // 3), (29, h)], fill=shade(pal["leaf_hi"], 0.6))
            d.line([(31, h - hgt // 2), (18, h - hgt * 3 // 4)], fill=tr, width=2)
            d.line([(32, h - hgt // 2 - 6), (46, h - hgt * 3 // 4 - 4)], fill=tr, width=2)
            cx, cy = 32, h - hgt + 26
            for k in range(11):
                ox, oy = r.randint(-18, 18), r.randint(-16, 14)
                rr = r.randint(8, 13)
                d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=pal["leaf"])
            for k in range(9):
                ox, oy = r.randint(-18, 16), r.randint(-18, 8)
                rr = r.randint(5, 9)
                d.arc([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], 170, 290, fill=pal["leaf_hi"])
                for q in range(6):
                    px, py = cx + ox - rr + r.randint(0, rr), cy + oy - rr + r.randint(0, rr)
                    if im.getpixel((max(0, min(w - 1, px)), max(0, min(h - 1, py))))[3]:
                        d.point((px, py), fill=pal["leaf_hi"])
        im.save(out(f"props/{name}_tree{i}.png"))


# --------------------------------------------------------------------------
# Characters
# --------------------------------------------------------------------------
RED, RED_D = C(170, 40, 30), C(112, 24, 24)
GOLD, GOLD_D = C(214, 170, 72), C(150, 108, 44)
SKIN = C(220, 168, 120)
STEEL, STEEL_D = C(170, 174, 180), C(96, 100, 112)
WOOD, WOOD_D = C(110, 76, 46), C(70, 46, 30)
BONE = C(232, 224, 204)


def cassius_frame(f, moving):
    im = new(32, 32)
    d = ImageDraw.Draw(im)
    hc, hh, hd = C(78, 50, 36), C(112, 74, 50), C(34, 24, 22)
    bob = [0, 0, 1, 1][f % 4] if not moving else [0, 1, 1, 0, 0, 1, 1, 0][f % 8]
    y0 = bob
    # legs
    for i, bx in enumerate([9, 12, 21, 24]):
        if moving:
            p = f / 8.0 * 2 * math.pi + [0, 3.1, 1.6, 4.7][i]
            off, lift = round(2.4 * math.sin(p)), max(0, round(2 * math.cos(p)))
        else:
            off, lift = 0, 0
        col = hd if i in (1, 2) else hc
        d.line([(bx, 21 + y0), (bx + off, 29 - lift)], fill=col, width=2)
        d.point((bx + off, 30 - lift), fill=hd)
        d.point((bx + off + 1, 30 - lift), fill=hd)
    # tail
    sway = [0, 1, 0, -1][f % 4]
    d.line([(6, 15 + y0), (3 + sway, 22 + y0)], fill=hd, width=2)
    # body
    d.rectangle([6, 14 + y0, 25, 21 + y0], fill=hc)
    d.line([(7, 14 + y0), (24, 14 + y0)], fill=hh)
    d.line([(8, 21 + y0), (23, 21 + y0)], fill=hd)
    # neck + head
    d.polygon([(22, 15 + y0), (26, 15 + y0), (29, 9 + y0), (25, 8 + y0)], fill=hc)
    d.rectangle([26, 7 + y0, 31, 11 + y0], fill=hc)
    d.rectangle([29, 10 + y0, 31, 12 + y0], fill=hh)
    d.point((29, 8 + y0), fill=hd)
    d.line([(25, 6 + y0), (26, 5 + y0)], fill=hc)
    d.line([(22, 14 + y0), (25, 8 + y0)], fill=hd, width=2)  # mane
    d.line([(27, 11 + y0), (19, 12 + y0)], fill=GOLD_D)  # reins
    # saddle cloth
    d.rectangle([12, 13 + y0, 20, 18 + y0], fill=RED)
    d.line([(12, 18 + y0), (20, 18 + y0)], fill=GOLD)
    # cape
    flap = [0, 1, 2, 1][f % 4] if moving else [0, 0, 1, 0][f % 4]
    d.polygon([(14, 6 + y0), (16, 6 + y0), (12, 15 + y0), (8 - flap, 16 + y0 - flap)], fill=RED_D)
    d.line([(14, 6 + y0), (8 - flap, 16 + y0 - flap)], fill=RED)
    # rider
    d.rectangle([14, 6 + y0, 18, 13 + y0], fill=GOLD_D)   # cuirass
    d.line([(14, 6 + y0), (18, 6 + y0)], fill=GOLD)
    d.rectangle([15, 13 + y0, 18, 17 + y0], fill=RED)     # leg/tunic
    d.rectangle([17, 17 + y0, 18, 19 + y0], fill=SKIN)
    d.rectangle([18, 8 + y0, 21, 9 + y0], fill=SKIN)      # arm to reins
    d.rectangle([15, 2 + y0, 18, 5 + y0], fill=SKIN)      # head
    d.rectangle([14, 1 + y0, 18, 3 + y0], fill=GOLD)      # helmet
    d.point((18, 4 + y0), fill=C(40, 30, 30))
    d.rectangle([13, 0 + y0, 19, 0 + y0], fill=RED)       # crest
    d.rectangle([14, -1 + y0 if y0 else 0, 18, 0 + y0], fill=RED)
    return im


def soldier_frame(f, moving, variant):
    im = new(16, 20)
    d = ImageDraw.Draw(im)
    bob = [0, 0, 1, 1][f % 4] if not moving else [0, 1, 0, 0, 1, 0][f % 6]
    step = [-2, -1, 1, 2, 1, -1][f % 6] if moving else 0
    cloth = [RED, RED_D, C(150, 60, 40)][variant]
    d.line([(6, 14), (6 + step, 19)], fill=C(60, 40, 34), width=2)
    d.line([(9, 14), (9 - step, 19)], fill=C(80, 54, 40), width=2)
    d.rectangle([5, 7 + bob, 10, 14 + bob], fill=cloth)
    d.rectangle([5, 7 + bob, 10, 10 + bob], fill=STEEL_D if variant != 2 else WOOD)
    d.line([(5, 7 + bob), (10, 7 + bob)], fill=STEEL)
    d.rectangle([6, 3 + bob, 9, 6 + bob], fill=SKIN)
    d.rectangle([5, 2 + bob, 9, 3 + bob], fill=STEEL)
    d.point((9, 5 + bob), fill=C(40, 30, 30))
    if variant == 0:      # spear + round shield
        d.line([(12, 0), (12, 17 + bob)], fill=WOOD)
        d.point((12, 0), fill=STEEL)
        d.ellipse([8, 8 + bob, 13, 13 + bob], fill=RED_D, outline=GOLD_D)
        d.point((10, 10 + bob), fill=GOLD)
    elif variant == 1:    # scutum
        d.rectangle([9, 6 + bob, 13, 15 + bob], fill=RED, outline=RED_D)
        d.rectangle([11, 10 + bob, 11, 11 + bob], fill=GOLD)
        d.line([(3, 9 + bob), (3, 13 + bob)], fill=STEEL)
    else:                 # archer
        d.arc([8, 3 + bob, 15, 15 + bob], 290, 70, fill=WOOD)
        d.line([(12, 4 + bob), (12, 14 + bob)], fill=BONE)
        d.rectangle([3, 7 + bob, 4, 12 + bob], fill=WOOD_D)
    return im


def ox_frame(f, moving):
    im = new(28, 18)
    d = ImageDraw.Draw(im)
    w, wd = C(236, 232, 222), C(180, 176, 172)
    for i, bx in enumerate([5, 8, 18, 21]):
        off = round(1.6 * math.sin(f / 6.0 * 6.28 + i * 1.6)) if moving else 0
        d.line([(bx, 12), (bx + off, 17)], fill=wd if i % 2 else w, width=2)
    d.rectangle([3, 5, 23, 12], fill=w)
    d.line([(4, 12), (22, 12)], fill=wd)
    d.rectangle([20, 3, 24, 6], fill=w)  # hump
    hb = 1 if (f % 4) >= 2 and not moving else 0
    d.rectangle([22, 6 + hb, 27, 10 + hb], fill=w)
    d.point((26, 7 + hb), fill=C(30, 30, 30))
    d.rectangle([26, 10 + hb, 27, 10 + hb], fill=C(220, 170, 170))
    d.line([(23, 5 + hb), (25, 2 + hb)], fill=BONE)
    d.line([(3, 6), (1, 11)], fill=wd)
    d.line([(10, 5), (14, 5)], fill=RED)  # sacrificial ribbon
    d.line([(12, 5), (12, 9)], fill=RED)
    return im


def cart_frame(f):
    im = new(34, 22)
    d = ImageDraw.Draw(im)
    d.rectangle([3, 6, 27, 14], fill=WOOD)
    d.line([(3, 6), (27, 6)], fill=shade(WOOD, 1.3))
    for x in (9, 15, 21):
        d.line([(x, 7), (x, 14)], fill=WOOD_D)
    d.ellipse([6, 1, 13, 7], fill=C(200, 180, 130))  # sacks
    d.ellipse([12, 0, 20, 7], fill=C(180, 160, 110))
    d.ellipse([19, 2, 25, 7], fill=C(200, 180, 130))
    d.line([(27, 12), (33, 12)], fill=WOOD_D)
    for cx in (9, 22):
        d.ellipse([cx - 5, 11, cx + 5, 21], outline=WOOD_D, fill=None)
        a = f * math.pi / 8
        for k in range(4):
            d.line([(cx, 16), (cx + round(4 * math.cos(a + k * math.pi / 2)), 16 + round(4 * math.sin(a + k * math.pi / 2)))], fill=WOOD_D)
        d.point((cx, 16), fill=GOLD_D)
    return im


def priest_frame(f, ritual):
    im = new(20, 26)
    d = ImageDraw.Draw(im)
    robe, robe_d = C(226, 220, 204), C(160, 152, 140)
    bob = [0, 0, 1, 1][f % 4] if not ritual else 0
    d.polygon([(6, 9 + bob), (13, 9 + bob), (15, 25), (4, 25)], fill=robe)
    d.line([(6, 9 + bob), (4, 25)], fill=robe_d)
    d.line([(10, 12 + bob), (10, 25)], fill=robe_d)
    d.rectangle([7, 4 + bob, 12, 9 + bob], fill=SKIN)
    d.rectangle([6, 2 + bob, 12, 5 + bob], fill=robe)  # hood
    d.line([(6, 2 + bob), (6, 8 + bob)], fill=robe_d)
    d.point((11, 6 + bob), fill=C(40, 30, 30))
    d.line([(6, 14 + bob), (13, 14 + bob)], fill=RED)   # the wet red cord
    d.line([(8, 14 + bob), (8, 19 + bob)], fill=RED)
    if ritual:
        raise_ = [0, 2, 4, 6, 7, 7, 6, 7][f % 8]
        d.line([(6, 11), (3, 12 - raise_)], fill=robe, width=2)
        d.line([(13, 11), (16, 12 - raise_)], fill=robe, width=2)
        d.point((3, 11 - raise_), fill=SKIN)
        d.point((16, 11 - raise_), fill=SKIN)
        if f % 8 >= 4:
            d.point((3, 9 - raise_), fill=GOLD)
            d.point((16, 9 - raise_), fill=GOLD)
    else:
        d.line([(13, 11 + bob), (15, 16 + bob)], fill=robe, width=2)
        d.line([(16, 4), (16, 25)], fill=WOOD_D)  # staff
        d.point((16, 3), fill=GOLD)
    return im


def civilian_frame(f, kind):
    im = new(16, 24)
    d = ImageDraw.Draw(im)
    bob = [0, 0, 1, 1][f % 4]
    cl = [C(120, 92, 60), C(96, 110, 88)][kind]
    d.rectangle([5, 9 + bob, 10, 18 + bob], fill=cl)
    d.line([(5, 9 + bob), (5, 18 + bob)], fill=shade(cl, 0.7))
    d.rectangle([6, 18 + bob, 7, 23], fill=shade(cl, 0.6))
    d.rectangle([9, 18 + bob, 10, 23], fill=shade(cl, 0.6))
    d.rectangle([6, 4 + bob, 9, 8 + bob], fill=SKIN)
    d.point((9, 6 + bob), fill=C(40, 30, 30))
    if kind == 0:
        d.rectangle([5, 3 + bob, 10, 4 + bob], fill=C(150, 60, 50))  # merchant cap
        d.rectangle([11, 12 + bob, 14, 16 + bob], fill=C(200, 180, 130))  # purse/sack
    else:
        d.rectangle([5, 3 + bob, 9, 4 + bob], fill=C(70, 50, 40))
        d.line([(12, 6), (12, 23)], fill=WOOD_D)
    return im


def gen_characters():
    strip([cassius_frame(i, False) for i in range(4)] + [cassius_frame(i, True) for i in range(8)]).save(out("sprites/cassius.png"))
    for v in range(3):
        strip([soldier_frame(i, False, v) for i in range(4)] + [soldier_frame(i, True, v) for i in range(6)]).save(out(f"sprites/soldier{v}.png"))
    strip([ox_frame(i, False) for i in range(4)] + [ox_frame(i, True) for i in range(6)]).save(out("sprites/ox.png"))
    strip([cart_frame(0)] + [cart_frame(i) for i in range(4)]).save(out("sprites/cart.png"))
    strip([priest_frame(i, False) for i in range(4)] + [priest_frame(i, True) for i in range(8)]).save(out("sprites/priest.png"))
    strip([civilian_frame(i, 0) for i in range(4)]).save(out("sprites/merchant.png"))
    strip([civilian_frame(i, 1) for i in range(4)]).save(out("sprites/villager.png"))


# --------------------------------------------------------------------------
# Props
# --------------------------------------------------------------------------
def gen_props():
    r = random.Random(3)
    # shop: worn wooden stall with faded awning
    im = new(84, 60)
    d = ImageDraw.Draw(im)
    d.rectangle([8, 22, 75, 59], fill=WOOD_D)
    for x in range(8, 76, 6):
        d.line([(x, 22), (x, 59)], fill=shade(WOOD_D, 0.7))
    d.rectangle([14, 30, 69, 48], fill=C(26, 18, 16))           # dark interior
    d.rectangle([12, 48, 71, 52], fill=WOOD)                    # counter
    d.line([(12, 48), (71, 48)], fill=shade(WOOD, 1.3))
    for i, x in enumerate(range(18, 66, 8)):                    # goods on shelf
        col = [GOLD, C(180, 80, 60), BONE, C(90, 140, 160), GOLD_D, C(150, 110, 70)][i % 6]
        d.rectangle([x, 43, x + 3, 47], fill=col)
        d.point((x + 1, 42), fill=shade(col, 1.3))
    for x in range(20, 64, 11):                                 # hanging things
        d.line([(x, 30), (x, 35)], fill=C(90, 70, 50))
        d.rectangle([x - 1, 35, x + 1, 38], fill=C(170, 120, 70))
    for i in range(12):                                         # striped awning
        x0 = 4 + i * 6.4
        col = C(150, 52, 40) if i % 2 == 0 else C(206, 190, 150)
        d.polygon([(x0, 26), (x0 + 6.4, 26), (x0 + 5.4 + 2, 12), (x0 + 2, 12)], fill=col)
    d.line([(4, 26), (80, 26)], fill=C(90, 34, 30))
    for x in range(5, 80, 5):
        d.point((x, 27), fill=C(206, 190, 150))
    d.rectangle([6, 12, 8, 59], fill=WOOD)
    d.rectangle([75, 12, 77, 59], fill=WOOD)
    d.rectangle([0, 50, 9, 59], fill=WOOD)                      # crate
    d.rectangle([0, 50, 9, 59], outline=WOOD_D)
    d.line([(0, 50), (9, 59)], fill=WOOD_D)
    d.ellipse([70, 46, 80, 59], fill=C(150, 90, 60))            # amphora
    d.rectangle([73, 42, 77, 47], fill=C(150, 90, 60))
    d.rectangle([40, 14, 44, 20], fill=C(255, 214, 120))        # lantern
    d.rectangle([40, 13, 44, 13], fill=WOOD_D)
    im.save(out("props/shop.png"))

    # tent
    im = new(48, 30)
    d = ImageDraw.Draw(im)
    tan, tan_d = C(150, 118, 84), C(100, 76, 56)
    d.polygon([(2, 29), (24, 3), (46, 29)], fill=tan)
    d.polygon([(24, 3), (46, 29), (30, 29)], fill=tan_d)
    d.polygon([(18, 29), (24, 12), (30, 29)], fill=C(26, 18, 16))
    d.line([(2, 29), (24, 3)], fill=shade(tan, 1.25))
    d.line([(24, 0), (24, 4)], fill=WOOD_D)
    d.rectangle([24, 0, 28, 2], fill=RED)
    im.save(out("props/tent.png"))

    # banner (vexillum) 4 frames 16x44
    frames = []
    for f in range(4):
        im = new(16, 44)
        d = ImageDraw.Draw(im)
        d.line([(3, 2), (3, 43)], fill=WOOD)
        d.rectangle([2, 0, 4, 2], fill=GOLD)
        d.line([(1, 5), (13, 5)], fill=WOOD_D)
        for x in range(1, 13):
            wav = round(math.sin(x * 0.7 + f * 1.57) * 1.2)
            d.line([(x, 6), (x, 17 + wav)], fill=RED if (x + f) % 5 else RED_D)
            d.point((x, 18 + wav), fill=GOLD)
        d.rectangle([5, 9, 8, 12], outline=GOLD)
        d.point((6, 10), fill=GOLD)
        frames.append(im)
    strip(frames).save(out("props/banner.png"))

    # campfire 4 frames 20x20
    frames = []
    for f in range(4):
        im = new(20, 20)
        d = ImageDraw.Draw(im)
        d.line([(3, 18), (16, 15)], fill=WOOD_D, width=2)
        d.line([(3, 15), (16, 18)], fill=WOOD, width=2)
        rr = random.Random(f)
        for k in range(14):
            x = 10 + rr.randint(-4, 4)
            hh = rr.randint(3, 11 - abs(x - 10))
            d.line([(x, 15), (x, 15 - hh)], fill=C(240, 120, 40))
        for k in range(8):
            x = 10 + rr.randint(-2, 2)
            hh = rr.randint(2, 7)
            d.line([(x, 15), (x, 15 - hh)], fill=C(255, 220, 110))
        d.point((10 + rr.randint(-4, 4), rr.randint(0, 4)), fill=C(255, 200, 100))
        frames.append(im)
    strip(frames).save(out("props/campfire.png"))

    # altar 56x40, with 4 flame frames
    frames = []
    for f in range(4):
        im = new(56, 44)
        d = ImageDraw.Draw(im)
        st, st_d, st_h = C(150, 146, 140), C(92, 90, 92), C(206, 200, 190)
        d.rectangle([2, 38, 53, 43], fill=st_d)
        d.rectangle([7, 32, 48, 38], fill=st)
        d.rectangle([13, 16, 42, 32], fill=st)
        d.rectangle([10, 12, 45, 16], fill=st_h)
        d.line([(13, 16), (13, 32)], fill=st_h)
        d.line([(42, 16), (42, 32)], fill=st_d)
        for x in range(17, 40, 5):
            d.rectangle([x, 20, x + 2, 28], outline=st_d)
        d.line([(20, 16), (22, 30)], fill=C(120, 30, 30))  # old blood
        d.rectangle([22, 9, 33, 12], fill=GOLD_D)          # bowl
        rr = random.Random(f + 9)
        for k in range(10):
            x = 27 + rr.randint(-4, 4)
            d.line([(x, 9), (x, 9 - rr.randint(2, 8 - abs(x - 27)))], fill=C(240, 130, 50))
        for k in range(5):
            x = 27 + rr.randint(-2, 2)
            d.line([(x, 9), (x, 9 - rr.randint(1, 5))], fill=C(255, 226, 130))
        d.rectangle([3, 26, 6, 38], fill=st)               # broken columns
        d.rectangle([2, 24, 7, 26], fill=st_h)
        d.rectangle([49, 20, 52, 38], fill=st)
        d.polygon([(49, 20), (52, 20), (52, 17)], fill=st)
        frames.append(im)
    strip(frames).save(out("props/altar.png"))

    # warning sign 4 frames (pulsing) 18x30
    frames = []
    for f in range(4):
        im = new(18, 30)
        d = ImageDraw.Draw(im)
        d.rectangle([8, 12, 9, 29], fill=WOOD_D)
        col = [C(200, 50, 40), C(230, 70, 50), C(255, 110, 70), C(230, 70, 50)][f]
        d.polygon([(9, 0), (17, 13), (0, 13)], fill=col)
        d.polygon([(9, 3), (14, 11), (3, 11)], fill=C(30, 18, 18))
        d.rectangle([8, 5, 9, 8], fill=col)
        d.rectangle([8, 10, 9, 10], fill=col)
        # crossed spears planted beside
        d.line([(2, 29), (6, 14)], fill=WOOD)
        d.line([(15, 29), (11, 14)], fill=WOOD)
        frames.append(im)
    strip(frames).save(out("props/warning.png"))

    # signpost
    im = new(30, 34)
    d = ImageDraw.Draw(im)
    d.rectangle([14, 6, 15, 33], fill=WOOD_D)
    d.polygon([(2, 8), (14, 8), (14, 14), (2, 14), (0, 11)], fill=WOOD)
    d.polygon([(16, 16), (27, 16), (29, 19), (27, 22), (16, 22)], fill=WOOD)
    d.line([(4, 11), (11, 11)], fill=WOOD_D)
    d.line([(18, 19), (25, 19)], fill=WOOD_D)
    im.save(out("props/signpost.png"))

    # misc decoration strip: column, crate, fence, rock1, rock2, bush, supplies, milestone (each 24x24)
    im = new(24 * 8, 24)
    d = ImageDraw.Draw(im)
    st, st_d, st_h = C(150, 146, 140), C(92, 90, 92), C(206, 200, 190)
    d.rectangle([9, 6, 14, 23], fill=st); d.line([(9, 6), (9, 23)], fill=st_h); d.polygon([(9, 6), (14, 6), (14, 2)], fill=st); d.rectangle([7, 21, 16, 23], fill=st_d)
    o = 24; d.rectangle([o + 5, 12, o + 17, 23], fill=WOOD); d.rectangle([o + 5, 12, o + 17, 23], outline=WOOD_D); d.line([(o + 5, 12), (o + 17, 23)], fill=WOOD_D)
    o = 48
    for x in (2, 10, 18):
        d.rectangle([o + x, 10, o + x + 1, 23], fill=WOOD_D)
    d.line([(o, 13), (o + 23, 14)], fill=WOOD); d.line([(o, 19), (o + 23, 18)], fill=WOOD)
    o = 72; d.polygon([(o + 3, 23), (o + 6, 14), (o + 14, 11), (o + 20, 17), (o + 21, 23)], fill=st_d); d.line([(o + 6, 14), (o + 14, 11)], fill=st_h)
    o = 96; d.polygon([(o + 6, 23), (o + 9, 17), (o + 15, 16), (o + 18, 23)], fill=st_d); d.line([(o + 9, 17), (o + 15, 16)], fill=st)
    o = 120
    for k in range(7):
        cx, cy, rr = o + r.randint(6, 18), r.randint(14, 20), r.randint(3, 5)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=C(40, 54, 40))
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 290, fill=C(90, 110, 60))
    o = 144; d.ellipse([o + 3, 13, o + 12, 23], fill=C(200, 180, 130)); d.ellipse([o + 10, 15, o + 19, 23], fill=C(170, 150, 104)); d.rectangle([o + 14, 8, o + 21, 15], fill=WOOD); d.rectangle([o + 14, 8, o + 21, 15], outline=WOOD_D)
    o = 168; d.rectangle([o + 9, 10, o + 14, 23], fill=st); d.arc([o + 9, 7, o + 14, 13], 180, 360, fill=st); d.line([(o + 11, 13), (o + 12, 13)], fill=st_d); d.line([(o + 11, 16), (o + 12, 16)], fill=st_d)
    im.save(out("props/deco.png"))

    # soft light blob for torches / fire (radial, dithered)
    im = new(96, 96)
    for y in range(96):
        for x in range(96):
            dd = math.hypot(x - 47.5, y - 47.5) / 48.0
            a = max(0.0, 1.0 - dd)
            a = a * a
            lv = int(a * 6) / 6.0
            if (a * 6) % 1.0 > ((x % 2) * 2 + (y % 2) * 1 + ((x + y) % 2)) / 4.0:
                lv = min(1.0, lv + 1 / 6.0)
            im.putpixel((x, y), (255, 190, 110, int(255 * lv * 0.55)))
    im.save(out("props/glow.png"))


# --------------------------------------------------------------------------
# Battle sprites
# --------------------------------------------------------------------------
FACTIONS = {
    "south": dict(cloth=C(170, 40, 30), shield=C(196, 56, 40), metal=C(206, 176, 96), skin=SKIN, horse=C(84, 54, 38)),
    "north": dict(cloth=C(84, 106, 140), shield=C(52, 74, 108), metal=C(176, 186, 198), skin=C(232, 204, 184), horse=C(190, 190, 196)),
    "west": dict(cloth=C(92, 72, 42), shield=C(66, 108, 48), metal=C(224, 216, 190), skin=C(112, 156, 72), horse=C(70, 60, 44)),
    "east": dict(cloth=C(78, 42, 120), shield=C(40, 28, 62), metal=C(196, 196, 220), skin=C(206, 186, 206), horse=C(40, 30, 50)),
    "bandit": dict(cloth=C(112, 94, 80), shield=C(92, 62, 42), metal=C(130, 130, 130), skin=SKIN, horse=C(100, 80, 60)),
}
UNIT_TYPES = ["spear", "shield", "archer", "cavalry"]
CW, CH = 16, 16


def unit_frame(t, p, f):
    im = new(CW, CH)
    d = ImageDraw.Draw(im)
    dk = shade(p["cloth"], 0.6)
    if f == 3:  # fallen
        d.rectangle([3, 12, 11, 14], fill=dk)
        d.rectangle([11, 12, 13, 13], fill=shade(p["skin"], 0.7))
        d.point((5, 11), fill=shade(p["shield"], 0.6))
        if t == "cavalry":
            d.rectangle([1, 10, 9, 13], fill=shade(p["horse"], 0.6))
        return im
    step = 1 if f == 1 else 0
    if t == "cavalry":
        hs = p["horse"]
        d.rectangle([2, 8, 11, 11], fill=hs)
        d.line([(2, 8), (11, 8)], fill=shade(hs, 1.3))
        d.rectangle([11, 5, 13, 9], fill=hs)
        d.rectangle([13, 5, 14, 7], fill=hs)
        d.line([(1, 8), (0, 12)], fill=shade(hs, 0.5))
        for i, bx in enumerate((3, 5, 9, 11)):
            off = (1 if (i % 2 == 0) == (f == 1) else -1) if f == 1 else 0
            d.line([(bx, 11), (bx + off, 14)], fill=shade(hs, 0.7))
        d.rectangle([5, 3, 8, 8], fill=p["cloth"])
        d.rectangle([5, 0, 8, 2], fill=p["skin"])
        d.rectangle([5, 0, 8, 0], fill=p["metal"])
        d.ellipse([3, 4, 6, 7], fill=p["shield"])
        if f == 2:
            d.line([(8, 5), (15, 4)], fill=p["metal"])
        else:
            d.line([(9, 6), (11, 0)], fill=p["metal"])
        return im
    # infantry
    d.line([(6, 12), (6 - step, 15)], fill=dk)
    d.line([(8, 12), (8 + step, 15)], fill=dk)
    d.rectangle([5, 6, 9, 12], fill=p["cloth"])
    d.line([(5, 6), (5, 12)], fill=dk)
    d.rectangle([6, 3, 8, 5], fill=p["skin"])
    d.rectangle([5, 2, 9, 3], fill=p["metal"])
    if t == "spear":
        d.ellipse([8, 7, 12, 11], fill=p["shield"])
        d.point((10, 9), fill=p["metal"])
        if f == 2:
            d.line([(7, 7), (15, 7)], fill=WOOD)
            d.point((15, 7), fill=p["metal"])
        else:
            d.line([(13, 0), (13, 13)], fill=WOOD)
            d.point((13, 0), fill=p["metal"])
    elif t == "shield":
        d.rectangle([8, 5, 12, 13], fill=p["shield"])
        d.rectangle([8, 5, 12, 13], outline=shade(p["shield"], 0.6))
        d.point((10, 9), fill=p["metal"])
        if f == 2:
            d.line([(12, 6), (15, 3)], fill=p["metal"])
        else:
            d.line([(3, 8), (3, 11)], fill=p["metal"])
    else:  # archer
        d.arc([8, 2, 14, 13], 290, 70, fill=WOOD)
        d.line([(11, 3), (11, 12)], fill=BONE)
        if f == 2:
            d.line([(7, 7), (14, 7)], fill=BONE)
        d.rectangle([3, 6, 4, 10], fill=WOOD_D)
    return im


def gen_battle():
    names = list(FACTIONS.keys())
    # left half: facing right; right half: the same 16 cells mirrored (so the game never has to flip)
    sheet = new(CW * 4 * 4 * 2, CH * len(names))
    for fi, fn in enumerate(names):
        for ti, t in enumerate(UNIT_TYPES):
            for f in range(4):
                cell = unit_frame(t, FACTIONS[fn], f)
                sheet.paste(cell, ((ti * 4 + f) * CW, fi * CH))
                sheet.paste(cell.transpose(Image.FLIP_LEFT_RIGHT), ((16 + ti * 4 + f) * CW, fi * CH))
    sheet.save(out("battle/units.png"))
    # battlefield ground tiles
    r = random.Random(11)
    for name, base, alt in (("grass", C(70, 92, 52), C(86, 108, 58)), ("mud", C(84, 66, 50), C(100, 80, 58)), ("snow", C(206, 218, 232), C(226, 234, 244)), ("ash", C(70, 52, 88), C(88, 64, 108))):
        im = Image.new("RGBA", (64, 64), base)
        for _ in range(260):
            x, y = r.randint(0, 63), r.randint(0, 63)
            im.putpixel((x, y), alt if r.random() < 0.7 else shade(base, 0.82))
        for _ in range(26):
            x, y = r.randint(0, 62), r.randint(1, 63)
            im.putpixel((x, y), alt); im.putpixel((x, y - 1), shade(alt, 1.15))
        im.save(out(f"battle/{name}.png"))
    # obstacles: rock, bush, stump (16x16 each)
    im = new(48, 16)
    d = ImageDraw.Draw(im)
    d.polygon([(2, 15), (4, 7), (10, 5), (14, 10), (14, 15)], fill=C(110, 108, 110)); d.line([(4, 7), (10, 5)], fill=C(180, 176, 170))
    for k in range(6):
        cx, cy, rr = 16 + r.randint(4, 12), r.randint(7, 12), r.randint(2, 4)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=C(40, 66, 40)); d.point((cx - 1, cy - rr), fill=C(100, 130, 70))
    d.rectangle([37, 9, 43, 15], fill=WOOD_D); d.ellipse([36, 6, 44, 11], fill=WOOD); d.ellipse([38, 7, 42, 10], outline=WOOD_D)
    im.save(out("battle/obstacles.png"))
    # regiment banner icons 4 types, 12x14
    im = new(48, 14)
    d = ImageDraw.Draw(im)
    for i in range(4):
        o = i * 12
        d.rectangle([o + 1, 0, o + 10, 10], fill=(255, 255, 255, 255))
        d.polygon([(o + 1, 10), (o + 10, 10), (o + 10, 13), (o + 5, 11), (o + 1, 13)], fill=(255, 255, 255, 255))
        k = C(30, 22, 22)
        if i == 0:
            d.line([(o + 5, 1), (o + 5, 9)], fill=k); d.point((o + 4, 2), fill=k); d.point((o + 6, 2), fill=k)
        elif i == 1:
            d.rectangle([o + 3, 2, o + 8, 8], outline=k); d.point((o + 5, 5), fill=k)
        elif i == 2:
            d.arc([o + 2, 1, o + 8, 9], 270, 90, fill=k); d.line([(o + 3, 5), (o + 9, 5)], fill=k)
        else:
            d.line([(o + 3, 8), (o + 3, 4)], fill=k); d.line([(o + 3, 4), (o + 6, 2)], fill=k); d.line([(o + 6, 2), (o + 8, 4)], fill=k); d.line([(o + 4, 6), (o + 8, 6)], fill=k); d.line([(o + 8, 6), (o + 8, 8)], fill=k)
    im.save(out("battle/banners.png"))


# --------------------------------------------------------------------------
# UI: coin, item icons
# --------------------------------------------------------------------------
def coin(size):
    im = new(size, size)
    d = ImageDraw.Draw(im)
    s = size / 16.0
    d.ellipse([0, 0, size - 1, size - 1], fill=GOLD_D)
    d.ellipse([s * 1, s * 1, size - 1 - s * 1, size - 1 - s * 1], fill=GOLD)
    d.arc([s, s, size - 1 - s, size - 1 - s], 190, 300, fill=C(250, 226, 150))
    k = C(120, 84, 34)
    # the king in profile: neck, head, nose, spiked crown
    d.rectangle([s * 6.5, s * 10, s * 8.5, s * 12.5], fill=k)
    d.ellipse([s * 5.5, s * 5.5, s * 10, s * 10.5], fill=k)
    d.polygon([(s * 9.6, s * 7.2), (s * 11.4, s * 8.6), (s * 9.6, s * 9.2)], fill=k)
    d.rectangle([s * 5.2, s * 4.6, s * 10.2, s * 5.6], fill=k)
    for cxp in (5.6, 7.7, 9.8):
        d.polygon([(s * (cxp - 0.6), s * 4.8), (s * cxp, s * 2.4), (s * (cxp + 0.6), s * 4.8)], fill=k)
    if size >= 32:
        for a in range(0, 360, 20):
            x = size / 2 + math.cos(math.radians(a)) * (size / 2 - s * 1.6)
            y = size / 2 + math.sin(math.radians(a)) * (size / 2 - s * 1.6)
            d.point((x, y), fill=k)
        d.point((s * 8.6, s * 6.6), fill=GOLD)
    return im


ITEM_ORDER = ["ivory", "serpent_ring", "gem", "gladius", "leather", "grain", "relic_horn", "seed_pouch", "codex", "white_ox", "amber", "silver_cup", "spearheads", "bowstrings", "family_portrait", "salt"]


def gen_ui():
    # the hand-drawn aureus in assets/ui/aureus/ replaces the generated coin when it is there
    for size, name in ((16, "coin.png"), (64, "coin_big.png")):
        src = out("ui/aureus/aureus_%d_obverse.png" % size)
        if os.path.exists(src):
            Image.open(src).save(out("ui/" + name))
        else:
            coin(size).save(out("ui/" + name))
    im = new(16 * len(ITEM_ORDER), 16)
    d = ImageDraw.Draw(im)

    def o(i):
        return i * 16
    x = o(0); d.arc([x + 1, 1, x + 20, 20], 180, 270, fill=BONE, width=3); d.point((x + 2, 10), fill=C(180, 170, 150))
    x = o(1)  # gold serpent ring, coiled
    d.ellipse([x + 3, 4, x + 12, 13], outline=GOLD); d.ellipse([x + 4, 5, x + 11, 12], outline=GOLD_D)
    d.line([(x + 11, 5), (x + 13, 3)], fill=GOLD); d.point((x + 13, 2), fill=C(200, 40, 40)); d.line([(x + 4, 12), (x + 2, 14)], fill=GOLD)
    x = o(2); d.polygon([(x + 8, 2), (x + 13, 7), (x + 8, 14), (x + 3, 7)], fill=C(70, 150, 190)); d.polygon([(x + 8, 2), (x + 3, 7), (x + 8, 7)], fill=C(160, 220, 240)); d.line([(x + 3, 7), (x + 13, 7)], fill=C(40, 100, 140))
    x = o(3); d.line([(x + 3, 13), (x + 12, 3)], fill=STEEL, width=2); d.line([(x + 2, 11), (x + 6, 14)], fill=GOLD_D); d.point((x + 2, 14), fill=WOOD)
    x = o(4); d.polygon([(x + 2, 4), (x + 13, 3), (x + 14, 12), (x + 9, 13), (x + 3, 13)], fill=C(140, 92, 56)); d.line([(x + 4, 6), (x + 11, 6)], fill=C(100, 62, 40))
    x = o(5); d.ellipse([x + 3, 4, x + 12, 14], fill=C(200, 180, 130)); d.rectangle([x + 6, 2, x + 9, 4], fill=C(170, 150, 104)); d.line([(x + 5, 4), (x + 10, 4)], fill=WOOD_D)
    x = o(6); d.arc([x - 2, -4, x + 13, 13], 0, 100, fill=C(130, 160, 180), width=3); d.rectangle([x + 11, 3, x + 14, 5], fill=C(200, 220, 235)); d.point((x + 5, 13), fill=STEEL)
    x = o(7); d.ellipse([x + 4, 6, x + 11, 14], fill=C(120, 100, 60)); d.line([(x + 6, 5), (x + 9, 5)], fill=C(80, 60, 40)); d.point((x + 7, 3), fill=C(110, 170, 70)); d.point((x + 8, 2), fill=C(110, 170, 70)); d.point((x + 9, 3), fill=C(110, 170, 70))
    x = o(8); d.rectangle([x + 3, 3, x + 12, 13], fill=C(70, 40, 100)); d.rectangle([x + 3, 3, x + 12, 13], outline=C(30, 18, 50)); d.rectangle([x + 7, 6, x + 8, 9], fill=C(200, 190, 220)); d.line([(x + 12, 7), (x + 13, 9)], fill=GOLD)
    x = o(9); d.rectangle([x + 2, 6, x + 11, 11], fill=C(236, 232, 222)); d.rectangle([x + 10, 4, x + 13, 8], fill=C(236, 232, 222)); d.line([(x + 11, 3), (x + 13, 2)], fill=BONE); d.line([(x + 3, 11), (x + 3, 14)], fill=C(180, 176, 172)); d.line([(x + 10, 11), (x + 10, 14)], fill=C(180, 176, 172)); d.line([(x + 5, 6), (x + 7, 6)], fill=RED)
    x = o(10); d.ellipse([x + 4, 4, x + 11, 12], fill=C(220, 140, 40)); d.point((x + 6, 6), fill=C(255, 220, 140)); d.point((x + 8, 9), fill=C(120, 60, 20))
    x = o(11); d.polygon([(x + 3, 3), (x + 12, 3), (x + 10, 9), (x + 5, 9)], fill=STEEL); d.rectangle([x + 7, 9, x + 8, 12], fill=STEEL_D); d.rectangle([x + 5, 12, x + 10, 13], fill=STEEL); d.line([(x + 3, 3), (x + 12, 3)], fill=C(230, 232, 240))
    x = o(12)
    for k in range(3):
        d.polygon([(x + 3 + k * 4, 12), (x + 5 + k * 4, 3), (x + 7 + k * 4, 12)], fill=STEEL); d.line([(x + 5 + k * 4, 3), (x + 5 + k * 4, 12)], fill=STEEL_D)
    x = o(13); d.arc([x + 2, 2, x + 16, 14], 100, 260, fill=WOOD); d.line([(x + 8, 2), (x + 8, 14)], fill=BONE); d.ellipse([x + 9, 6, x + 13, 10], outline=BONE)
    x = o(14); d.rectangle([x + 3, 2, x + 12, 13], fill=WOOD); d.rectangle([x + 4, 3, x + 11, 12], fill=C(206, 190, 150)); d.rectangle([x + 5, 6, x + 6, 10], fill=C(120, 60, 60)); d.rectangle([x + 8, 7, x + 9, 10], fill=C(70, 90, 120)); d.point((x + 5, 5), fill=SKIN); d.point((x + 8, 6), fill=SKIN)
    x = o(15); d.polygon([(x + 3, 13), (x + 8, 4), (x + 13, 13)], fill=C(236, 236, 240)); d.line([(x + 8, 4), (x + 5, 10)], fill=C(190, 196, 210))
    im.save(out("ui/items.png"))

    # psychedelic four-realm map (160x100)
    w, h = 160, 100
    im = new(w, h)
    cols = {"north": (90, 190, 255), "south": (255, 80, 60), "west": (90, 240, 120), "east": (200, 90, 255)}
    for y in range(h):
        for x in range(w):
            nx, ny = (x - w / 2) / (w / 2), (y - h / 2) / (h / 2)
            wob = 0.12 * math.sin(x * 0.21 + y * 0.13) + 0.08 * math.sin(y * 0.33 - x * 0.07)
            rr = math.hypot(nx, ny) + wob * 0.5
            if rr > 0.98:
                continue
            if rr < 0.2:
                c = (30, 40, 90)  # inner sea
                if (x + y + int(8 * math.sin(x * 0.4))) % 4 == 0:
                    c = (70, 110, 200)
            else:
                a = math.atan2(ny, nx) + wob
                if -2.356 <= a < -0.785: k = "north"
                elif -0.785 <= a < 0.785: k = "east"
                elif 0.785 <= a < 2.356: k = "south"
                else: k = "west"
                band = int((rr * 9 + math.sin(a * 5) * 0.6 + wob * 4)) % 3
                f = [0.55, 0.8, 1.0][band]
                c = tuple(int(v * f) for v in cols[k])
                if rr > 0.9:
                    c = tuple(int(v * 0.4) for v in c)
            im.putpixel((x, y), c + (255,))
    im.save(out("ui/map.png"))


# --------------------------------------------------------------------------
# Bitmap font (BMFont text format) rendered without anti-aliasing
# --------------------------------------------------------------------------
def gen_font():
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not os.path.exists(path):
        print("font source missing; game falls back to the engine font")
        return
    size = 8
    font = ImageFont.truetype(path, size)
    asc, desc = font.getmetrics()
    line_h = asc + desc + 1
    chars = [chr(c) for c in range(32, 127)] + list("·—’“”…×•")
    W = 256
    x = y = 1
    im = Image.new("L", (W, 128), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    rows = []
    for ch in chars:
        adv = int(round(font.getlength(ch)))
        cw = max(adv, 1) + 1
        if x + cw + 1 > W:
            x = 1
            y += line_h + 1
        d.text((x, y), ch, font=font, fill=255)
        rows.append((ord(ch), x, y, cw, line_h, adv))
        x += cw + 1
    Hh = 1
    while Hh < y + line_h + 2:
        Hh *= 2
    im = im.crop((0, 0, W, Hh))
    rgba = Image.new("RGBA", im.size, (255, 255, 255, 0))
    rgba.putalpha(im.point(lambda v: 255 if v > 100 else 0))
    rgba.save(out("ui/pixel.png"))
    with open(out("ui/pixel.fnt"), "w") as f:
        f.write(f'info face="CassiusPixel" size={size} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=0 padding=0,0,0,0 spacing=1,1 outline=0\n')
        f.write(f"common lineHeight={line_h} base={asc} scaleW={W} scaleH={Hh} pages=1 packed=0 alphaChnl=0 redChnl=4 greenChnl=4 blueChnl=4\n")
        f.write('page id=0 file="pixel.png"\n')
        f.write(f"chars count={len(rows)}\n")
        for cid, cx, cy, cw, chh, adv in rows:
            f.write(f"char id={cid} x={cx} y={cy} width={cw} height={chh} xoffset=0 yoffset=0 xadvance={adv} page=0 chnl=15\n")


# --------------------------------------------------------------------------
# Sounds
# --------------------------------------------------------------------------
SR = 22050


def save_wav(name, data):
    data = np.clip(data, -1, 1)
    pcm = (data * 32000).astype("<i2")
    with wave.open(out(f"audio/{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def t_(sec):
    return np.arange(int(SR * sec)) / SR


def lowpass(x, k):
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += (x[i] - acc) * k
        y[i] = acc
    return y


def gen_audio():
    rng = np.random.default_rng(5)
    t = t_(0.5)
    coin_s = (np.sin(2 * np.pi * 2637 * t) * np.exp(-t * 14) + 0.6 * np.sin(2 * np.pi * 3951 * t) * np.exp(-t * 18) + 0.4 * np.sin(2 * np.pi * 5274 * t) * np.exp(-t * 26)) * 0.5
    d = int(SR * 0.07)
    coin_s[d:] += coin_s[:-d] * 0.7
    save_wav("coin", coin_s)
    t = t_(0.9)
    up = sum(np.sin(2 * np.pi * f * t) * np.exp(-np.maximum(t - i * 0.09, 0) * 9) * (t > i * 0.09) for i, f in enumerate([1047, 1319, 1568, 2093])) * 0.3
    save_wav("upgrade", up)
    t = t_(0.08)
    save_wav("click", np.sin(2 * np.pi * 900 * t) * np.exp(-t * 60) * 0.5)
    t = t_(0.35)
    n = rng.uniform(-1, 1, len(t))
    clash = n * np.exp(-t * 30) * 0.5 + (np.sin(2 * np.pi * 1870 * t) + np.sin(2 * np.pi * 2930 * t) + np.sin(2 * np.pi * 4410 * t)) * np.exp(-t * 16) * 0.16
    save_wav("clash", clash)
    t = t_(0.3)
    n = lowpass(rng.uniform(-1, 1, len(t)), 0.35)
    save_wav("arrow", n * np.sin(np.pi * t / 0.3) ** 2 * 0.6)
    t = t_(0.18)
    save_wav("thud", (np.sin(2 * np.pi * (110 - 200 * t) * t) * np.exp(-t * 26) + lowpass(rng.uniform(-1, 1, len(t)), 0.2) * np.exp(-t * 40)) * 0.7)
    t = t_(2.6)
    f0 = 146.8
    horn = sum(np.sin(2 * np.pi * f0 * k * t + 0.3 * np.sin(2 * np.pi * 5 * t)) / k for k in range(1, 8))
    env = np.minimum(t / 0.35, 1) * np.minimum((2.6 - t) / 0.6, 1)
    save_wav("horn", lowpass(horn * env * 0.22, 0.25) * 2.0)
    t = t_(3.2)
    ch = sum(np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 0.7 * t + i)) for i, f in enumerate([73.4, 110, 146.8, 220, 293.7])) * 0.12
    bell = np.sin(2 * np.pi * 880 * t) * np.exp(-t * 2.2) * 0.25 + np.sin(2 * np.pi * 1318 * t) * np.exp(-t * 3) * 0.12
    save_wav("ritual", (ch * np.minimum(t / 0.8, 1) + bell) * np.minimum((3.2 - t) / 0.8, 1))
    # ambient loop: wind + low drone + sparse lyre notes, 16 s, loop-safe
    L = 16.0
    t = t_(L)
    wind = lowpass(rng.uniform(-1, 1, len(t)), 0.03) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 8.0)) * 1.6
    drone = (np.sin(2 * np.pi * 73.42 * t) + 0.6 * np.sin(2 * np.pi * 110 * t) + 0.3 * np.sin(2 * np.pi * 146.83 * t)) * 0.10 * (0.8 + 0.2 * np.sin(2 * np.pi * t / 4.0))
    lyre = np.zeros_like(t)
    notes = [(0.0, 293.7), (2.0, 349.2), (4.0, 440.0), (6.0, 392.0), (8.0, 293.7), (10.0, 261.6), (12.0, 329.6), (13.0, 293.7)]
    for st, fr in notes:
        tt = np.maximum(t - st, 0)
        lyre += (np.sin(2 * np.pi * fr * tt) + 0.4 * np.sin(2 * np.pi * fr * 2 * tt)) * np.exp(-tt * 1.6) * (t >= st) * 0.10
    amb = wind + drone + lyre
    fade = int(SR * 1.0)
    amb[:fade] = amb[:fade] * np.linspace(0, 1, fade) + amb[-fade:] * np.linspace(1, 0, fade)
    save_wav("ambient", amb[:-fade] * 0.8)
    # battle drums loop 4 s
    t = t_(4.0)
    dr = np.zeros_like(t)
    for st, amp in [(0, 1), (0.5, 0.5), (1.0, 0.8), (1.5, 0.5), (1.75, 0.4), (2.0, 1), (2.5, 0.5), (3.0, 0.8), (3.25, 0.4), (3.5, 0.6)]:
        tt = np.maximum(t - st, 0)
        dr += np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt * 9) * (t >= st) * amp * 0.6
    dr += (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t)) * 0.08
    save_wav("drums", dr)


if __name__ == "__main__":
    for name, pal in REGIONS.items():
        gen_mountains(name, pal, 100 + len(name))
        gen_forest(name, pal, 200 + len(name) * 3, True)
        gen_forest(name, pal, 300 + len(name) * 5, False)
        gen_ground(name, pal)
        gen_trees(name, pal)
    gen_characters()
    gen_props()
    gen_battle()
    gen_ui()
    gen_font()
    gen_audio()
    print("assets written to", os.path.abspath(ROOT))
