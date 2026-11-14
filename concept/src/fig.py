"""Part-based painter for 48-px characters: each body part is a shape with a 5-tone material ramp
and a shading model, then a selective outline (dark on the shadow side, rim light on the lit side)."""
import math
import numpy as np
from PIL import Image, ImageDraw
from kit import C, rgba


def ramp(*hexes):
    return [C(h) for h in hexes]


M = {
    'steel': ramp('22232c', '3e404c', '666a78', '9a9eac', 'd4d8e2'),
    'bronze': ramp('3e2410', '74481c', 'a87530', 'd8a84c', 'ffe196'),
    'gold': ramp('4a300e', '8a5c1a', 'c48e2c', 'eec056', 'fff0b0'),
    'red': ramp('3a0a0a', '68120e', '9c2016', 'c83a24', 'ee6a44'),
    'crest': ramp('4a0808', '7e1410', 'b42418', 'e04430', 'ff8a5a'),
    'skin': ramp('5a3022', '8a5038', 'b87a56', 'daa07a', 'f0c49c'),
    'leather': ramp('24160c', '442a18', '664026', '8a5c38', 'ae7e52'),
    'wood': ramp('2a1a10', '4a301c', '6e4a2c', '96703e', 'bc965e'),
    'linen': ramp('5e5446', '8e8270', 'bcb09a', 'ddd2bc', 'f6eedc'),
    'horse': ramp('1e120c', '3a2216', '5e3a24', '845434', 'a87448'),
    'mane': ramp('0c0808', '1a1210', '2c201a', '3e2e24', '54402e'),
    'ox': ramp('5e5650', '8e8680', 'bcb4ac', 'ddd6ce', 'f6f2ec'),
    'iron': ramp('1a1a20', '34343e', '5a5a66', '8a8a96', 'c0c0cc'),
    'fur': ramp('24201e', '423a34', '665a50', '8e8072', 'b4a698'),
    'blue': ramp('0e1626', '1c2a46', '2e4268', '486490', '7090b8'),
    'robe': ramp('6a6258', '9a9284', 'c4bcac', 'e2dccc', 'faf6ec'),
}


class Fig:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = rgba(w, h)

    def _mask(self, draw_fn):
        im = Image.new('L', (self.w, self.h), 0)
        draw_fn(ImageDraw.Draw(im))
        return np.asarray(im) > 0

    def _paint(self, mask, mat, shade, bbox=None, bias=0.0, light=(-0.75, -0.65), lo=0, hi=4):
        ys, xs = np.nonzero(mask)
        if len(xs) == 0:
            return
        x0, x1 = (xs.min(), xs.max()) if bbox is None else (bbox[0], bbox[2])
        y0, y1 = (ys.min(), ys.max()) if bbox is None else (bbox[1], bbox[3])
        u = (xs - x0) / max(1, x1 - x0)
        v = (ys - y0) / max(1, y1 - y0)
        if shade == 'cyl':           # vertical cylinder, lit from the left
            t = 1 - np.abs(u - 0.28) * 1.35
            t = t * 0.85 + (1 - v) * 0.15
        elif shade == 'hcyl':        # horizontal cylinder (bands, rolls), lit from above
            t = 1 - np.abs(v - 0.3) * 1.4
        elif shade == 'sphere':
            cx, cy = 0.32, 0.3
            t = 1 - np.hypot(u - cx, v - cy) * 1.25
        elif shade == 'flatL':       # flat plane facing left/up
            t = 0.75 - u * 0.35
        elif shade == 'flatR':       # flat plane turned away
            t = 0.35 - u * 0.15
        else:
            t = np.full(len(xs), 0.6)
        t = np.clip(t + bias, 0, 0.999)
        idx = np.clip((lo + t * (hi - lo + 1)).astype(int), lo, hi)
        cols = np.array(M[mat])[idx]
        self.a[ys, xs, :3] = cols
        self.a[ys, xs, 3] = 1

    def poly(self, pts, mat, shade='cyl', **kw):
        m = self._mask(lambda d: d.polygon([tuple(p) for p in pts], fill=255))
        self._paint(m, mat, shade, **kw)
        return m

    def ell(self, box, mat, shade='sphere', **kw):
        m = self._mask(lambda d: d.ellipse(box, fill=255))
        self._paint(m, mat, shade, **kw)
        return m

    def rect(self, box, mat, shade='cyl', **kw):
        m = self._mask(lambda d: d.rectangle(box, fill=255))
        self._paint(m, mat, shade, **kw)
        return m

    def line(self, pts, col, width=1):
        im = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(im).line([tuple(p) for p in pts], fill=255, width=width)
        m = np.asarray(im) > 0
        self.a[m, :3] = col
        self.a[m, 3] = 1

    def px(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x, :3] = col
            self.a[y, x, 3] = 1

    def outline(self, dark=0.5, rim=1.12):
        al = self.a[:, :, 3] > 0.5
        out = self.a.copy()
        pad = np.pad(al, 1)
        right_empty = ~pad[1:-1, 2:]
        below_empty = ~pad[2:, 1:-1]
        left_empty = ~pad[1:-1, :-2]
        above_empty = ~pad[:-2, 1:-1]
        shadow_edge = al & (right_empty | below_empty)
        lit_edge = al & (left_empty | above_empty) & ~shadow_edge
        out[shadow_edge, :3] *= dark
        out[lit_edge, :3] = np.clip(out[lit_edge, :3] * rim, 0, 1)
        self.a = out
        return self.a


# ------------------------------------------------------------------ characters (all face right)
def legionary(step=0, carry='pilum', torch=False):
    f = Fig(38, 52)
    fy = 50                                         # feet line
    s = [(0, 0), (2, -2), (0, 0), (-2, 2)][step % 4]
    # pilum (behind everything) / vexillum pole
    if carry == 'pilum':
        f.line([(8, 2), (8, 46)], M['wood'][2], 2)
        f.line([(8, 2), (8, 46)], M['wood'][3], 1)
        f.line([(8, 0), (8, 13)], M['iron'][3], 1)
        f.poly([(7, 2), (9, 2), (8, -2)], 'iron', 'flat')
        f.rect((7, 13, 9, 15), 'iron', 'cyl')
    # far leg (darker), near leg
    for i, (lx, dx) in enumerate(((13, s[0]), (17, s[1]))):
        bias = -0.25 if i == 0 else 0.0
        f.poly([(lx + dx, 36), (lx + 3 + dx, 36), (lx + 3 + dx, 46), (lx + dx, 46)], 'skin', 'cyl', bias=bias)
        f.poly([(lx + dx - 1, 45), (lx + 3 + dx, 45), (lx + 6 + dx, fy), (lx + dx - 1, fy)], 'leather', 'flatL', bias=bias)
        for yy in (43, 45, 47):
            f.line([(lx + dx, yy), (lx + 3 + dx, yy)], M['leather'][1], 1)
    # tunic skirt with folds
    f.poly([(11, 27), (24, 27), (26, 37), (9, 37)], 'red', 'cyl')
    for x in (13, 17, 21):
        f.line([(x, 30), (x - 1, 37)], M['red'][1], 1)
    f.line([(9, 37), (26, 37)], M['red'][0], 1)
    # pteruges strips + apron (balteus)
    for i, x in enumerate(range(11, 25, 2)):
        f.rect((x, 27, x, 32), 'leather', 'flat', bias=0.1 if i % 2 else -0.1)
    for x in (16, 18, 20):
        f.line([(x, 27), (x, 35)], M['leather'][2], 1)
        f.px(x, 29, M['bronze'][4]); f.px(x, 32, M['bronze'][3]); f.px(x, 35, M['bronze'][3])
    # lorica segmentata
    f.poly([(10, 14), (24, 14), (25, 26), (10, 26)], 'steel', 'cyl')
    for yy in range(16, 26, 3):
        f.line([(10, yy), (25, yy)], M['steel'][1], 1)
        f.line([(10, yy + 1), (24, yy + 1)], M['steel'][3], 1)
    f.line([(17, 14), (17, 26)], M['steel'][1], 1)
    f.rect((10, 25, 25, 26), 'leather', 'flat')                 # belt
    for x in range(11, 25, 3):
        f.px(x, 25, M['bronze'][4])
    # shoulder guard on the near shoulder
    f.poly([(9, 13), (17, 12), (18, 17), (10, 19)], 'steel', 'hcyl')
    f.line([(9, 15), (17, 14)], M['steel'][1], 1)
    # neck scarf
    f.rect((14, 12, 22, 13), 'linen', 'flat', bias=0.1)
    # head: face, eye, nose (facing right, visible under the brow)
    f.poly([(15, 4), (23, 4), (25, 8), (24, 12), (16, 13)], 'skin', 'cyl', bias=0.12)
    f.px(25, 8, M['skin'][3]); f.px(24, 9, M['skin'][1])         # nose
    f.px(22, 7, M['mane'][0]); f.px(21, 7, M['skin'][1])        # eye
    f.line([(21, 11), (23, 11)], M['skin'][1], 1)                 # mouth
    # helmet: bowl set back on the head, brow ridge, small cheek guard, flared neck guard
    f.ell((12, 0, 23, 8), 'steel', 'sphere', bias=0.1)
    f.line([(14, 5), (24, 5)], M['bronze'][3], 1)
    f.poly([(16, 6), (18, 6), (18, 12), (16, 12)], 'steel', 'flatL', bias=0.2)
    f.px(17, 8, M['bronze'][4])
    f.poly([(11, 4), (14, 5), (14, 9), (9, 10)], 'steel', 'flatR', bias=0.15)
    f.px(17, 1, M['steel'][4]); f.px(18, 1, M['steel'][4])
    # crest of red horsehair, front to back
    f.poly([(12, 0), (21, -1), (22, 1), (12, 2)], 'crest', 'hcyl')
    f.poly([(13, -3), (20, -4), (21, -1), (13, 0)], 'crest', 'hcyl')
    # near arm holding the pilum
    if carry == 'pilum':
        f.poly([(9, 16), (12, 16), (11, 23), (8, 23)], 'red', 'cyl', bias=-0.1)
        f.poly([(8, 22), (11, 22), (10, 27), (7, 27)], 'skin', 'cyl')
        f.ell((6, 24, 10, 28), 'skin', 'sphere')
    elif carry == 'vexillum':
        f.poly([(9, 16), (12, 16), (12, 21), (9, 21)], 'red', 'cyl', bias=-0.1)
        f.poly([(9, 20), (12, 20), (12, 24), (9, 24)], 'skin', 'cyl')
    if torch:
        f.line([(30, 6), (29, 26)], M['wood'][2], 2)
    # scutum: tall curved shield, face toward the viewer, edge-lit
    f.poly([(20, 13), (33, 12), (34, 43), (21, 44)], 'red', 'cyl', bias=0.05)
    f.line([(20, 13), (33, 12)], M['gold'][3], 1)
    f.line([(21, 44), (34, 43)], M['gold'][1], 1)
    f.line([(20, 13), (21, 44)], M['gold'][4], 1)
    f.line([(33, 12), (34, 43)], M['gold'][1], 1)
    # painted wings & thunderbolts
    for (y1, y2) in ((18, 22), (37, 33)):
        f.line([(23, y1), (27, y2), (31, y1)], M['gold'][3], 1)
    f.line([(27, 15), (27, 41)], M['gold'][2], 1)
    f.ell((24, 24, 30, 31), 'bronze', 'sphere')
    f.px(25, 26, M['bronze'][4])
    f.outline()
    return f.a


def cassius_mounted(step=0):
    f = Fig(84, 82)
    fy = 80
    s = [(0, 0), (3, -3), (0, 0), (-3, 3)][step % 4]
    # far legs (darker)
    for (lx, dx) in ((22, s[0]), (56, s[1])):
        f.poly([(lx, 52), (lx + 5, 52), (lx + 4 + dx, 74), (lx + 1 + dx, 74)], 'horse', 'cyl', bias=-0.35)
        f.poly([(lx + dx, 73), (lx + 5 + dx, 73), (lx + 6 + dx, fy), (lx + dx - 1, fy)], 'mane', 'flat')
    # tail
    f.poly([(12, 38), (17, 36), (16, 50), (11, 66), (7, 64), (10, 50)], 'mane', 'cyl')
    # barrel, belly, quarters, shoulder
    f.ell((12, 34, 68, 58), 'horse', 'sphere', bias=0.05)
    f.ell((14, 46, 66, 60), 'horse', 'hcyl', bias=-0.25)
    f.ell((13, 35, 33, 54), 'horse', 'sphere', bias=0.12)
    f.ell((50, 36, 68, 54), 'horse', 'sphere', bias=0.08)
    # near legs
    f.poly([(16, 46), (28, 46), (26, 60), (24 - s[0], 74), (20 - s[0], 74), (19, 60)], 'horse', 'cyl')
    f.poly([(55, 50), (62, 50), (61 - s[1], 74), (57 - s[1], 74)], 'horse', 'cyl')
    for lx in (20 - s[0], 57 - s[1]):
        f.poly([(lx - 1, 73), (lx + 5, 73), (lx + 6, fy), (lx - 1, fy)], 'mane', 'flat', bias=0.2)
        f.line([(lx, 72), (lx + 4, 72)], M['linen'][3], 1)
    # neck, head, muzzle, ear, mane
    f.poly([(56, 40), (62, 26), (68, 16), (75, 18), (71, 34), (66, 46)], 'horse', 'cyl', bias=0.05)
    f.poly([(67, 13), (76, 17), (80, 26), (77, 30), (72, 27), (66, 20)], 'horse', 'cyl', bias=0.1)
    f.ell((74, 24, 81, 31), 'horse', 'sphere', bias=-0.08)
    f.px(78, 27, M['mane'][0])
    f.px(71, 19, M['mane'][0]); f.px(72, 19, M['linen'][3])
    f.poly([(66, 12), (68, 8), (70, 13)], 'horse', 'flat')
    f.poly([(56, 38), (61, 25), (67, 13), (66, 20), (61, 31), (58, 40)], 'mane', 'cyl')
    f.line([(68, 18), (74, 27), (79, 27)], M['leather'][1], 1)
    f.line([(70, 16), (70, 25)], M['leather'][1], 1)
    f.px(74, 27, M['gold'][4])
    f.line([(74, 28), (55, 30)], M['leather'][0], 1)
    # saddle cloth with gold fringe
    f.poly([(28, 32), (52, 32), (52, 47), (28, 47)], 'red', 'cyl')
    for x in range(28, 53, 2):
        f.px(x, 47, M['gold'][3]); f.px(x, 48, M['gold'][2])
    f.line([(28, 32), (52, 32)], M['red'][4], 1)
    # cloak streaming back over the horse
    f.poly([(36, 16), (43, 16), (40, 33), (30, 40), (20, 38), (26, 28)], 'red', 'cyl', bias=0.05)
    for (a, b) in (((35, 20), (25, 32)), ((38, 22), (29, 36)), ((33, 25), (23, 36))):
        f.line([a, b], M['red'][1], 1)
    # leg and boot
    f.poly([(42, 30), (47, 30), (48, 42), (43, 42)], 'skin', 'cyl')
    f.poly([(42, 41), (48, 41), (50, 48), (42, 48)], 'leather', 'flatL')
    # pteruges
    for i, x in enumerate(range(38, 50, 2)):
        f.rect((x, 28, x + 1, 34), 'leather', 'flat', bias=0.15 if i % 2 else -0.05)
    # gilded muscle cuirass
    f.poly([(38, 15), (48, 15), (49, 29), (38, 29)], 'gold', 'cyl')
    f.line([(43, 17), (43, 27)], M['gold'][1], 1)
    f.line([(39, 21), (48, 21)], M['gold'][1], 1)
    f.px(40, 19, M['gold'][4]); f.px(45, 19, M['gold'][4])
    f.rect((38, 27, 49, 28), 'red', 'flat', bias=0.2)
    f.px(43, 27, M['gold'][4])
    # arm to the reins
    f.poly([(47, 16), (51, 17), (52, 23), (48, 23)], 'red', 'cyl', bias=-0.05)
    f.poly([(49, 22), (52, 22), (56, 28), (53, 30)], 'skin', 'cyl')
    f.ell((53, 27, 57, 31), 'skin', 'sphere')
    # head
    f.poly([(40, 6), (48, 6), (50, 10), (49, 14), (41, 15)], 'skin', 'cyl', bias=0.12)
    f.px(50, 10, M['skin'][3]); f.px(47, 9, M['mane'][0]); f.line([(46, 13), (48, 13)], M['skin'][1], 1)
    # officer's helmet: bronze bowl, cheek guard, tall plume sweeping back
    f.ell((38, 3, 48, 11), 'bronze', 'sphere', bias=0.05)
    f.poly([(41, 9), (43, 9), (43, 14), (41, 14)], 'bronze', 'flatL', bias=0.15)
    f.line([(39, 8), (49, 8)], M['gold'][4], 1)
    f.poly([(47, 4), (46, 0), (40, 0), (34, 2), (31, 6), (34, 6), (39, 4)], 'crest', 'hcyl')
    f.line([(45, 1), (35, 3)], M['crest'][4], 1)
    f.line([(40, 4), (33, 6)], M['crest'][1], 1)
    f.outline()
    return f.a


def ox48(step=0):
    f = Fig(64, 40)
    fy = 38
    s = [(0, 0), (2, -2), (0, 0), (-2, 2)][step % 4]
    for (lx, dx) in ((14, s[0]), (44, s[1])):
        f.poly([(lx, 24), (lx + 5, 24), (lx + 4 + dx, fy - 2), (lx + 1 + dx, fy - 2)], 'ox', 'cyl', bias=-0.35)
        f.rect((lx + dx, fy - 2, lx + 4 + dx, fy), 'mane', 'flat')
    f.poly([(8, 12), (11, 13), (9, 26), (6, 30), (5, 27)], 'ox', 'cyl', bias=-0.2)     # tail
    f.ell((6, 8, 52, 32), 'ox', 'sphere', bias=0.1)
    f.ell((8, 20, 50, 33), 'ox', 'hcyl', bias=-0.2)
    f.ell((36, 2, 52, 16), 'ox', 'sphere', bias=0.15)                              # hump
    for (lx, dx) in ((11, -s[0]), (40, -s[1])):
        f.poly([(lx, 26), (lx + 6, 26), (lx + 5 + dx, fy - 2), (lx + 1 + dx, fy - 2)], 'ox', 'cyl')
        f.rect((lx + dx, fy - 2, lx + 5 + dx, fy), 'mane', 'flat', bias=0.2)
    # head lowered
    f.poly([(48, 10), (58, 12), (62, 22), (58, 26), (50, 22)], 'ox', 'cyl', bias=0.1)
    f.ell((56, 20, 63, 27), 'skin', 'sphere', bias=0.2)
    f.px(60, 23, M['mane'][0]); f.px(55, 15, M['mane'][0])
    f.poly([(50, 11), (47, 6), (49, 5), (53, 10)], 'linen', 'cyl', bias=0.2)       # horns, curving forward
    f.line([(49, 5), (52, 3)], M['linen'][3], 1)
    # sacrificial garland and fillet
    for i, x in enumerate(range(24, 44, 2)):
        f.ell((x, 8 + (i % 2), x + 3, 11 + (i % 2)), 'red' if i % 3 else 'gold', 'sphere')
    f.line([(36, 10), (38, 28)], M['red'][3], 1)
    f.outline()
    return f.a


def priest48():
    f = Fig(30, 52)
    f.poly([(9, 14), (21, 14), (26, 50), (4, 50)], 'robe', 'cyl')
    for x in (10, 14, 18, 22):
        f.line([(x, 20), (x - 1 + (x > 15) * 2, 50)], M['robe'][1], 1)
    f.line([(4, 50), (26, 50)], M['robe'][0], 1)
    f.poly([(8, 2), (20, 1), (22, 10), (20, 18), (9, 18)], 'robe', 'cyl', bias=0.05)  # hood
    f.poly([(13, 5), (20, 5), (21, 11), (19, 15), (14, 15)], 'skin', 'cyl')
    f.px(18, 9, M['mane'][0]); f.px(21, 10, M['skin'][2]); f.line([(17, 13), (19, 13)], M['skin'][1], 1)
    f.line([(14, 15), (19, 15)], M['linen'][1], 1)                                     # grey beard
    f.line([(15, 16), (18, 17)], M['linen'][2], 1)
    # the wet red cord
    f.line([(8, 27), (24, 27)], M['red'][3], 2)
    f.line([(12, 28), (11, 40)], M['red'][2], 1); f.line([(13, 28), (13, 37)], M['red'][1], 1)
    f.px(11, 41, M['red'][4]); f.px(11, 42, M['red'][3])                                # drip
    # arms raising a bowl
    f.poly([(19, 16), (24, 15), (27, 8), (24, 7), (21, 12)], 'robe', 'cyl', bias=0.1)
    f.ell((23, 5, 29, 9), 'skin', 'sphere')
    f.ell((21, 1, 30, 6), 'gold', 'sphere')
    f.outline()
    return f.a


def vexillum(t=0.0, h=78):
    """standard on a pole: gilded eagle, crossbar, red banner with gold fringe and SPQR-ish device"""
    f = Fig(30, h)
    f.line([(14, 8), (14, h - 1)], M['wood'][2], 2)
    f.line([(14, 8), (14, h - 1)], M['wood'][3], 1)
    # eagle with spread wings
    f.ell((11, 0, 18, 6), 'gold', 'sphere')
    f.poly([(4, 4), (12, 2), (13, 6), (6, 8)], 'gold', 'cyl')
    f.poly([(16, 2), (25, 4), (23, 8), (16, 6)], 'gold', 'cyl', bias=-0.1)
    f.px(17, 2, M['gold'][0])
    f.rect((12, 6, 17, 8), 'gold', 'hcyl')
    # crossbar and banner
    f.rect((3, 12, 26, 13), 'wood', 'hcyl')
    pts = [(4, 14), (26, 14)]
    for x in range(26, 3, -2):
        pts.append((x, 38 + round(math.sin(x * 0.45 + t) * 1.5)))
    f.poly(pts, 'red', 'cyl')
    for x in range(4, 27, 2):
        y = 38 + round(math.sin(x * 0.45 + t) * 1.5)
        f.px(x, y + 1, M['gold'][3]); f.px(x, y + 2, M['gold'][2])
    f.line([(8, 18), (22, 18)], M['gold'][3], 1)
    f.ell((11, 21, 18, 29), 'gold', 'sphere', bias=-0.1)
    f.ell((13, 23, 16, 27), 'red', 'flat')
    f.line([(8, 32), (22, 32)], M['gold'][3], 1)
    for x in (6, 23):
        f.line([(x, 15), (x + 1, 36)], M['red'][1], 1)
    # phalerae discs down the pole
    for y in (46, 53, 60):
        f.ell((11, y, 17, y + 5), 'gold', 'sphere')
    f.outline()
    return f.a
