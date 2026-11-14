import os; os.environ["WIDE"] = "1"
HI = float(os.environ.get("HIRES", "1"))
PAINT = os.environ.get("STYLE") == "paint"
"""2D pixel-illustration toolkit: painted shapes, dithered gradients, silhouettes with rim light.
Everything is drawn directly at 640x272 - no game sprites, no 3D bakes."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from kit import C, fbm
DW, DH = 640, 272                       # design units: every scene is laid out on a 640x272 grid
W, H = int(DW * HI), int(DH * HI)        # real pixels

B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
BAY = np.tile(B4, (H // 4 + 1, W // 4 + 1))[:H, :W]
YY, XX = [a / HI for a in np.mgrid[0:H, 0:W].astype(float)]


def ramp(*hexes):
    return np.array([C(h) for h in hexes])


def dgrad(t, pal, dither=True, amt=1.0):
    """map field t (0..1) onto palette with ordered dithering between steps"""
    n = len(pal)
    v = np.clip(t, 0, 0.9999) * (n - 1)
    if PAINT:                                     # smooth painted gradient instead of dithered steps
        i0 = np.floor(v).astype(int); f = (v - i0)[..., None]
        i1 = np.clip(i0 + 1, 0, n - 1)
        return pal[i0] * (1 - f) + pal[i1] * f
    if dither:
        v = v + (BAY - 0.5) * amt
    i = np.clip(np.floor(v + 0.5), 0, n - 1).astype(int)
    return pal[i]


class Canvas:
    def __init__(self, bg=(0, 0, 0)):
        self.img = np.zeros((H, W, 3)) + np.array(bg)

    def fill(self, m, col, a=1.0):
        m = m.astype(bool)
        col = np.asarray(col, float)
        if col.ndim == 3:
            self.img[m] = self.img[m] * (1 - a) + col[m] * a
        else:
            self.img[m] = self.img[m] * (1 - a) + col * a

    def grad(self, m, t, pal, dither=True, amt=1.0):
        self.fill(m, dgrad(t, pal, dither, amt))

    def add(self, field, col):
        self.img = np.clip(self.img + field[:, :, None] * np.asarray(col)[None, None, :], 0, 1)

    def glow(self, x, y, r, col, k=1.0, sx=1.0):
        d = np.hypot((XX - x) / sx, YY - y) / r
        f = np.clip(1 - d, 0, 1) ** 2 * k
        if not PAINT:
            f = np.floor(f * 6 + BAY * 0.9) / 6                  # banded, dithered falloff
        self.add(f, col)

    def save(self, path):
        im = Image.fromarray((np.clip(self.img, 0, 1) * 255).astype(np.uint8))
        im.save(path)
        return im


# ------------------------------------------------------------------ masks
def poly(pts):
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon([(float(x) * HI, float(y) * HI) for x, y in pts], fill=255)
    return np.asarray(im) > 127


def ellipse(x, y, rx, ry):
    return ((XX - x) / max(rx, 0.5)) ** 2 + ((YY - y) / max(ry, 0.5)) ** 2 <= 1


def capsule(a, b, r):
    ax, ay = a; bx, by = b
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy + 1e-9
    t = np.clip(((XX - ax) * vx + (YY - ay) * vy) / L2, 0, 1)
    return np.hypot(XX - (ax + t * vx), YY - (ay + t * vy)) <= r


def line(a, b, w=1):
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).line([(a[0] * HI, a[1] * HI), (b[0] * HI, b[1] * HI)], fill=255, width=max(1, int(round(w * HI))))
    return np.asarray(im) > 127


def rim(m, dx, dy, w=None):
    """pixels of mask m whose neighbour toward the light (dx,dy) is outside the mask"""
    if w is None:
        w = max(1, int(round(HI * 0.8))) if PAINT else 1
    out = np.zeros_like(m)
    for k in range(1, w + 1):
        sh = np.roll(np.roll(m, -dy * k, 0), -dx * k, 1)
        out |= m & ~sh
    return out


def outline(m):
    d = m.copy()
    for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        d |= np.roll(np.roll(m, oy, 0), ox, 1)
    return d & ~m


def ridge(y0, amp, seed, cells=(80, 30, 12), rough=1.0):
    """mountain/hill silhouette: mask of everything below a noisy ridgeline"""
    rng = np.random.default_rng(seed)
    x = np.arange(W) / HI
    h = np.zeros(W)
    for i, c in enumerate(cells):
        pts = rng.random(int(DW // c) + 3)
        h += np.interp(x / c, np.arange(len(pts)), pts) * (rough / (i + 1))
    h = (h - h.min()) / (h.max() - h.min() + 1e-9)
    top = y0 - h * amp
    return YY >= top[None, :], top


# ------------------------------------------------------------------ figures
def figure(x, gy, h, pose='walk', facing=1, cloak=False, spear=None, pack=False, staff=False,
           hood=False, helmet=False, crest=False, arms_up=False, child=None, robe=False, phase=0.0, shield=False, lean=0.0):
    """a person as a silhouette mask; h = height in px, gy = ground y"""
    f = facing
    u = h / 100.0
    m = np.zeros((H, W), bool)
    hip = (x + lean * 10 * u * f, gy - 50 * u)
    sh_ = (x + lean * 22 * u * f, gy - 80 * u)
    head = (sh_[0] + 2 * u * f, gy - 91 * u)
    m |= ellipse(head[0], head[1], 6.0 * u, 7.0 * u)
    if hood:
        m |= poly([(head[0] - 8 * u * f, head[1] + 6 * u), (head[0] - 6 * u * f, head[1] - 8 * u), (head[0] + 4 * u * f, head[1] - 9 * u), (head[0] + 7 * u * f, head[1] + 2 * u)])
    if helmet:
        m |= ellipse(head[0], head[1] - 2 * u, 7.2 * u, 6.5 * u)
        if crest:
            m |= poly([(head[0] - 9 * u, head[1] - 7 * u), (head[0] + 9 * u, head[1] - 7 * u), (head[0] + 7 * u, head[1] - 14 * u), (head[0] - 7 * u, head[1] - 14 * u)])
    m |= capsule(sh_, hip, 9.5 * u)                                              # torso
    m |= capsule((sh_[0], sh_[1] - 4 * u), head, 3.5 * u)                         # neck
    s = math.sin(phase * 2 * math.pi)
    if pose == 'walk':
        k1 = (hip[0] + (10 + 8 * s) * u * f, gy - 24 * u); k2 = (hip[0] - (6 + 8 * s) * u * f, gy - 25 * u)
        m |= capsule(hip, k1, 5 * u) | capsule(k1, (k1[0] + 4 * u * f * s, gy - 2 * u), 4 * u)
        m |= capsule(hip, k2, 5 * u) | capsule(k2, (k2[0] - 6 * u * f, gy - 2 * u), 4 * u)
    elif pose == 'kneel':
        k = (hip[0] + 14 * u * f, gy - 18 * u)
        m |= capsule(hip, k, 5.5 * u) | capsule(k, (k[0], gy - 2 * u), 4.5 * u)
        m |= capsule(hip, (hip[0] - 4 * u * f, gy - 4 * u), 5.5 * u) | capsule((hip[0] - 4 * u * f, gy - 4 * u), (hip[0] - 22 * u * f, gy - 2 * u), 4 * u)
    else:
        m |= capsule(hip, (hip[0] + 4 * u, gy - 2 * u), 5 * u) | capsule(hip, (hip[0] - 4 * u, gy - 2 * u), 5 * u)
    if robe or cloak:
        m |= poly([(sh_[0] - 9 * u, sh_[1]), (sh_[0] + 9 * u, sh_[1]), (hip[0] + 16 * u, gy - (2 if robe else 22) * u), (hip[0] - 16 * u - 8 * u * f * (1 if cloak else 0), gy - (2 if robe else 20) * u)])
    # arms
    hand_f = None
    if arms_up:
        for sgn in (1, -1):
            e = (sh_[0] + 12 * u * sgn, sh_[1] - 14 * u); hnd = (sh_[0] + 15 * u * sgn, sh_[1] - 34 * u)
            m |= capsule((sh_[0] + 5 * u * sgn, sh_[1] + 2 * u), e, 3.5 * u) | capsule(e, hnd, 3 * u)
        hand_f = (sh_[0] + 15 * u * f, sh_[1] - 34 * u)
    else:
        e = (sh_[0] + 8 * u * f, sh_[1] + 18 * u); hand_f = (sh_[0] + 14 * u * f, sh_[1] + 30 * u)
        if spear or staff:
            e = (sh_[0] + 10 * u * f, sh_[1] + 14 * u); hand_f = (sh_[0] + 18 * u * f, sh_[1] + 10 * u)
        m |= capsule((sh_[0] + 3 * u * f, sh_[1] + 2 * u), e, 3.5 * u) | capsule(e, hand_f, 3 * u)
        e2 = (sh_[0] - 8 * u * f - 4 * s * u * f, sh_[1] + 18 * u)
        m |= capsule((sh_[0] - 3 * u * f, sh_[1] + 2 * u), e2, 3.5 * u) | capsule(e2, (e2[0] - 2 * u * f, sh_[1] + 32 * u), 3 * u)
    if pack:
        m |= ellipse(sh_[0] - 12 * u * f, sh_[1] + 10 * u, 11 * u, 13 * u)
    if shield:
        m |= ellipse(sh_[0] + 12 * u * f, sh_[1] + 24 * u, 8 * u, 22 * u)
    if spear:
        top = (hand_f[0] + 6 * u * f, gy - spear * u)
        m |= line((hand_f[0] - 2 * u * f, gy - 4 * u), top, max(1, int(round(1.6 * u))))
        m |= poly([(top[0] - 2.5 * u, top[1] + 6 * u), (top[0] + 2.5 * u, top[1] + 6 * u), (top[0], top[1] - 6 * u)])
    if staff:
        m |= line((hand_f[0], gy - 2 * u), (hand_f[0] + 2 * u * f, gy - 118 * u), max(1, int(round(2 * u))))
    if child is not None:
        m |= figure(x - child * u * f, gy, h * 0.55, pose='walk', facing=f, phase=phase + 0.5)
    return m


def crow(x, y, s=1.0, flap=0.0):
    w = 6 * s
    up = math.sin(flap * 2 * math.pi) * 3 * s
    return line((x - w, y - up), (x, y), 1) | line((x, y), (x + w, y - up), 1) | ellipse(x, y, 1.2 * s, 0.8 * s)


def topat(top, x):
    return top[int(np.clip(x * HI, 0, W - 1))]


def fbmd(seed, cells=(48, 24, 12, 6)):
    """noise with cell sizes given in design units"""
    return fbm(W, H, seed, cells=tuple(max(2, int(c * HI)) for c in cells))


def rays(cx, cy, seed, col, k=0.25, n=26, reach=420):
    """god rays fanning out from a light source"""
    rng = np.random.default_rng(seed)
    a = np.arctan2(YY - cy, XX - cx)
    f = np.zeros_like(a)
    for i in range(n):
        a0 = rng.uniform(-math.pi, math.pi); w = rng.uniform(0.01, 0.05)
        f += np.exp(-((np.angle(np.exp(1j * (a - a0)))) / w) ** 2) * rng.uniform(0.3, 1)
    d = np.hypot(XX - cx, YY - cy)
    f = np.clip(f, 0, 1) * np.clip(1 - d / reach, 0, 1) ** 1.5 * k
    return f if PAINT else np.floor(f * 8 + BAY * 0.9) / 8


def put_px(cv, x, y, col, a=1.0):
    """plot one design-unit point (fills the real pixels it covers)"""
    xi, yi = int(x * HI), int(y * HI)
    s = max(1, int(round(HI * (0.7 if PAINT else 1))))
    if 0 <= yi < H and 0 <= xi < W:
        cv.img[yi:yi + s, xi:xi + s] = cv.img[yi:yi + s, xi:xi + s] * (1 - a) + np.asarray(col) * a


def clouds2(cv, seed, banks, pal, sun=None, sun_k=0.6):
    """billowing cloud banks: puffy tops, shaded top-to-bottom, rims lit toward the sun.
    banks: (centre_y, thickness, coverage)"""
    big = fbmd(seed, cells=(120, 60, 26, 10)); puff = fbmd(seed + 1, cells=(18, 9, 4, 2))
    for i, (cy_, th, cov) in enumerate(banks):
        off = (big - 0.5) * th * 2.2
        top = cy_ - th * (0.4 + puff * 0.9) + off
        bot = cy_ + th * 0.35 + off * 0.5 + (puff - 0.5) * th * 0.3
        m = (YY > top) & (YY < bot) & (big > 1 - cov)
        t = np.clip((YY - top) / np.maximum(bot - top, 1), 0, 1)
        if sun is not None:
            near = np.clip(1 - np.hypot(XX - sun[0], (YY - sun[1]) * 1.5) / 360, 0, 1)
            t = np.clip(t * (0.55 + near * sun_k) + near * 0.25, 0, 1)
        cv.grad(m, t, pal)
        edge = m & ~np.roll(m, -1, 0)
        cv.fill(edge, pal[-1])
        topedge = m & ~np.roll(m, 1, 0)
        cv.fill(topedge, pal[min(2, len(pal) - 1)])


def cumulus(cv, seed, banks, pal, sun, rimcol, lobes=26):
    """puffy cloud banks built from overlapping lobes; flat-ish bases, lit on the sun side.
    banks: (y_base, x0, x1, height)"""
    rng = np.random.default_rng(seed)
    for (yb, x0, x1, hh) in banks:
        m = np.zeros((H, W), bool); shade = np.zeros((H, W))
        for i in range(lobes):
            cx_ = rng.uniform(x0, x1); r = rng.uniform(0.35, 1.0) * hh
            cy_ = yb - r * rng.uniform(0.3, 0.9)
            lm = ellipse(cx_, cy_, r * 1.5, r) & (YY < yb + hh * 0.1)
            # each lobe shaded toward the sun, drawn back to front
            lt = np.clip(0.55 + ((XX - cx_) * (sun[0] - cx_) + (YY - cy_) * (sun[1] - cy_)) /
                         (r * 1.5 * (np.hypot(sun[0] - cx_, sun[1] - cy_) + 1e-6)) * 0.45, 0, 1)
            lt = lt * 0.7 + np.clip((YY - (cy_ - r)) / (2 * r), 0, 1) * 0.3
            new = lm & ~m
            shade[lm] = lt[lm]
            m |= lm
        near = np.clip(1 - np.hypot(XX - sun[0], YY - sun[1]) / 420, 0, 1)
        cv.grad(m, np.clip(shade * 0.75 + near * 0.35, 0, 1), pal)
        cv.fill(m & ~np.roll(m, -int(max(1, 2 * HI)), 0), rimcol)
