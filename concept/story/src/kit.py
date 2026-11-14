"""Kingdom-fidelity pixel renderer for Cassius concept frames (Hades-style 3/4 view).
Pipeline: albedo + baked shading -> silhouette shadows -> banded lighting -> river reflection
-> fog / particles -> grade -> 4x nearest upscale."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import os
W, H = (640, 272) if os.environ.get('WIDE') else (480, 270)
B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
BAY = np.tile(B4, (H // 4 + 1, W // 4 + 1))[:H, :W]


def C(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0


def vnoise(w, h, cell, seed):
    r = np.random.default_rng(seed)
    gw, gh = w // cell + 3, h // cell + 3
    g = (r.random((gh, gw)) * 255).astype(np.uint8)
    im = Image.fromarray(g).resize((gw * cell, gh * cell), Image.BICUBIC)
    return np.asarray(im, dtype=float)[:h, :w] / 255.0


def fbm(w, h, seed, cells=(48, 24, 12, 6), wts=(0.45, 0.28, 0.17, 0.1)):
    return sum(vnoise(w, h, c, seed + i * 17) * wt for i, (c, wt) in enumerate(zip(cells, wts)))


def band(v, n, dither=True, yx=None):
    """quantise 0..1 into n steps, ordered-dithered"""
    if dither:
        v = np.asarray(v, dtype=float)
        if yx is not None:
            b = B4[yx[0] % 4, yx[1] % 4]
        elif v.shape == BAY.shape:
            b = BAY
        else:
            b = np.tile(B4, (v.shape[0] // 4 + 1, v.shape[1] // 4 + 1))[:v.shape[0], :v.shape[1]]
        return np.floor(v * n + b) / n
    return np.floor(v * n) / n


class Scene:
    def __init__(self, seed=1):
        self.alb = np.zeros((H, W, 3))
        self.emi = np.zeros((H, W, 3))
        self.shadow = np.zeros((H, W))
        self.obj = np.zeros((H, W), bool)
        self.lights = []          # (x, y, radius, color, strength)
        self.items = []           # (depth, x, y, rgba, emissive, cast)
        self.rng = random.Random(seed)
        self.sun = (1.0, 0.45)    # shadow offset per pixel of height
        self.ground_h = np.zeros((H, W))

    # ------------------------------------------------------------- items
    def add(self, rgba, x, y, emissive=None, cast=True, depth=None):
        """rgba: float array (h,w,4); (x,y) = bottom-centre (feet) in screen px"""
        h, w = rgba.shape[:2]
        self.items.append((y if depth is None else depth, int(round(x - w / 2)), int(round(y - h)), rgba, emissive, cast, int(round(y))))

    def light(self, x, y, r, col, s=1.0):
        self.lights.append((x, y, r, np.array(col), s))

    def compose_items(self):
        for depth, x0, y0, rgba, emi, cast, feet in sorted(self.items, key=lambda t: t[0]):
            h, w = rgba.shape[:2]
            if cast:
                ys, xs = np.nonzero(rgba[:, :, 3] > 0.5)
                hgt = (y0 + h) - (y0 + ys)        # height above feet line
                sx = np.round(x0 + xs + hgt * self.sun[0]).astype(int)
                sy = np.round(feet + hgt * self.sun[1] - (h - 1 - ys) * 0.0).astype(int) - 1
                sy = np.round((y0 + h - 1) + hgt * self.sun[1]).astype(int)
                for dx, dy in ((0, 0), (1, 0), (0, 1)):
                    xx, yy = sx + dx, sy + dy
                    ok = (xx >= 0) & (xx < W) & (yy >= 0) & (yy < H)
                    self.shadow[yy[ok], xx[ok]] = np.maximum(self.shadow[yy[ok], xx[ok]], 1.0 * (~self.obj[yy[ok], xx[ok]]))
            ys, xs = np.nonzero(rgba[:, :, 3] > 0.5)
            X, Y = x0 + xs, y0 + ys
            ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
            self.alb[Y[ok], X[ok]] = rgba[ys[ok], xs[ok], :3]
            self.obj[Y[ok], X[ok]] = True
            self.shadow[Y[ok], X[ok]] = 0.0
            if emi is not None:
                m = emi[ys[ok], xs[ok], 3] > 0.5
                self.emi[Y[ok][m], X[ok][m]] = emi[ys[ok][m], xs[ok][m], :3]

    # ------------------------------------------------------------- light
    def lit(self, ambient, sun_col, shadow_strength=0.85):
        yy, xx = np.mgrid[0:H, 0:W]
        L = np.zeros((H, W, 3)) + ambient
        sh = band(np.clip(self.shadow, 0, 1), 1, dither=False)
        L += sun_col[None, None, :] * (1 - sh * shadow_strength)[:, :, None]
        for (x, y, r, col, s) in self.lights:
            d = np.hypot(xx - x, (yy - y) * 1.35) / r
            f = np.clip(1 - d, 0, 1) ** 1.6
            f = band(f, 5)
            L += col[None, None, :] * (f * s)[:, :, None]
        out = self.alb * L + self.emi
        return out

    def glow(self, img, x, y, r, col, s=0.5, bands=5):
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.hypot(xx - x, (yy - y) * 1.15) / r
        f = np.clip(1 - d, 0, 1) ** 2
        f = band(f, bands)
        return img + np.array(col)[None, None, :] * (f * s)[:, :, None]


def reflect(img, bank, tint, depth_fade=0.55, seed=3, refl_amt=0.62, sky=None):
    """river below the bank line: sky colour + ripple bands + reflections of what stands on the bank"""
    out = img.copy()
    r = np.random.default_rng(seed)
    for x in range(W):
        b = int(bank(x))
        for y in range(b, H):
            d = y - b
            wob = int(round(math.sin(y * 1.9 + x * 0.05) * (0.6 + d * 0.06)))
            sy = b - 1 - int(d * 1.05)
            sx = min(W - 1, max(0, x + wob))
            base = tint if sky is None else sky(x, y)
            # ripple bands: alternating slightly lighter/darker horizontal strips
            rip = math.sin(y * 0.9 + math.sin(x * 0.045 + y * 0.2) * 2.2)
            base = base * (1.0 + 0.10 * (1 if rip > 0.55 else -1 if rip < -0.6 else 0))
            if sy >= 0 and d < 70:
                k = min(1.0, d / 70.0)
                amt = refl_amt * (1 - k * depth_fade)
                col = img[sy, sx] * amt + base * (1 - amt)
            else:
                col = base
            out[y, x] = col
    for i in range(int(W * 0.9)):
        x = r.integers(0, W - 6)
        b = int(bank(x))
        if b + 3 >= H:
            continue
        y = r.integers(b + 2, H)
        L = r.integers(2, 7)
        out[y, x:x + L] = out[y, x:x + L] * 0.55 + np.array([1.0, 0.92, 0.82]) * 0.45
    for x in range(W):          # wet dark mud edge, then a pale foam line
        b = int(bank(x))
        if b + 2 >= H:
            continue
        out[b - 1, x] = out[b - 1, x] * 0.55
        out[b, x] = out[b, x] * 0.4 + np.array([0.85, 0.85, 0.9]) * 0.45
        if (x // 3 + int(math.sin(x * 0.3) * 2)) % 4 == 0:
            out[b + 2, x] = out[b + 2, x] * 0.5 + 0.4
    return out


def fog(img, col, amount, y0, y1, seed=5, scroll=0):
    n = fbm(W + 64, H, seed, cells=(64, 32, 16), wts=(0.55, 0.3, 0.15))[:, scroll:scroll + W]
    yy = np.arange(H)[:, None]
    bandy = np.clip((yy - y0) / 30, 0, 1) * np.clip((y1 - yy) / 30, 0, 1)
    a = np.clip((n - 0.42) * 2.6, 0, 1) * bandy * amount
    a = band(a, 6, dither=False)
    return img * (1 - a[:, :, None]) + np.array(col)[None, None, :] * a[:, :, None]


def grade(img, lift, gamma=1.0, sat=1.0, vignette=0.35, contrast=1.0):
    img = np.clip(img, 0, None)
    img = img / (1 + img * 0.15)                       # gentle roll-off for fire
    g = img.mean(axis=2, keepdims=True)
    img = g + (img - g) * sat
    img = np.clip(img, 0, 1)
    img = np.clip((img - 0.5) * contrast + 0.5, 0, 1) ** gamma
    lum = img.mean(axis=2, keepdims=True)
    k = (1 - lum) ** 3 * 0.38                          # tint only the shadows
    img = img * (1 - k) + np.array(lift)[None, None, :] * k
    yy, xx = np.mgrid[0:H, 0:W]
    v = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    img = img * (1 - vignette * np.clip(v - 0.55, 0, 1)[:, :, None])
    return np.clip(img, 0, 1)


def to_image(img, colors=96):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    if colors:
        im = im.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    return im


# ------------------------------------------------------------------ sprite helpers
def rgba(w, h):
    return np.zeros((h, w, 4))


def put(a, x, y, c, alpha=1.0):
    x, y = int(round(x)), int(round(y))
    h, w = a.shape[:2]
    if 0 <= x < w and 0 <= y < h:
        a[y, x, :3] = c
        a[y, x, 3] = alpha


def rect(a, x0, y0, x1, y1, c):
    a[max(0, y0):y1 + 1, max(0, x0):x1 + 1, :3] = c
    a[max(0, y0):y1 + 1, max(0, x0):x1 + 1, 3] = 1


def from_ascii(rows, pal):
    h, w = len(rows), max(len(r) for r in rows)
    a = rgba(w, h)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                put(a, x, y, pal[ch])
    return a


def flip(a):
    return a[:, ::-1].copy()


def canopy(R, seed, leaf, ldir=(-0.6, -0.8), squash=0.85, n_clusters=None, highlight=None, snow=None, tones=5, fine=1.0):
    """leafy canopy patch: many shaded leaf clusters, jagged edge, lit from ldir"""
    r = np.random.default_rng(seed)
    size = int(R * 2 + 8)
    a = rgba(size, size)
    cx = cy = size / 2
    n = int((n_clusters or int(R * 1.3) + 6) / (fine * fine))
    pts = []
    for i in range(n):
        ang = r.random() * 6.283
        rad = R * math.sqrt(r.random()) * 0.78
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad * squash, r.uniform(R * 0.28 * fine, R * 0.48 * fine)))
    yy, xx = np.mgrid[0:size, 0:size]
    best = np.full((size, size), -9.0)
    shade = np.zeros((size, size))
    for (px, py, pr) in pts:
        dx, dy = (xx - px) / pr, (yy - py) / pr
        d2 = dx * dx + dy * dy
        jag = 0.12 * np.sin(np.arctan2(dy, dx) * 7 + px) + 0.08 * np.sin(np.arctan2(dy, dx) * 13 + py)
        inside = d2 < (1 + jag) ** 2
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        lam = np.clip(-(dx * ldir[0] + dy * ldir[1]) * 0.55 + nz * 0.55, 0, 1)
        # whole-canopy term: top-left of the crown brighter, bottom darker (occlusion)
        gx, gy = (xx - cx) / R, (yy - cy) / (R * squash)
        glob = np.clip(0.55 - (gx * ldir[0] + gy * ldir[1]) * -0.35 - np.clip(gy, 0, 1) * 0.45, 0, 1)
        val = lam * 0.55 + glob * 0.45
        upd = inside & (py + 0 > best - 999)
        # later clusters that sit lower are drawn on top (painter)
        upd = inside
        shade[upd] = val[upd]
        best[upd] = py
    mask = best > -9
    q = band(np.clip(shade, 0, 0.999), tones)
    leaf = [np.array(c) for c in leaf]       # dark -> light
    idx = np.clip((q * len(leaf)).astype(int), 0, len(leaf) - 1)
    for i, c in enumerate(leaf):
        m = mask & (idx == i)
        a[m, :3] = c
        a[m, 3] = 1
    # speckle highlights on lit edges & dark holes
    for _ in range(int(R * R * 0.35 / fine)):
        x, y = r.integers(1, size - 1), r.integers(1, size - 1)
        if mask[y, x] and idx[y, x] >= len(leaf) - 2 and r.random() < 0.6:
            a[y, x, :3] = highlight if highlight is not None else leaf[-1] * 1.12
        elif mask[y, x] and idx[y, x] <= 1 and r.random() < 0.3:
            a[y, x, :3] = leaf[0] * 0.7
    if snow is not None:
        top = np.zeros(size, int) + size
        for x in range(size):
            col = np.nonzero(mask[:, x])[0]
            if len(col):
                for y in col:
                    if (y == col[0] or not mask[y - 1, x]) and r.random() < 0.95:
                        for k in range(r.integers(1, 3)):
                            if y + k < size and mask[y + k, x]:
                                a[y + k, x, :3] = snow if k == 0 else snow * 0.85
    return a, mask


def trunk(a, x, y0, y1, w, bark, rng):
    """tapered trunk with bark lines"""
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        ww = int(round(w * (0.7 + 0.3 * t)))
        for k in range(ww):
            xx = x - ww // 2 + k
            c = bark[1]
            if k == 0:
                c = bark[2]
            elif k >= ww - 2:
                c = bark[0]
            if (y * 3 + k * 5) % 7 == 0:
                c = bark[0]
            put(a, xx, y, c)
    # root flare
    put(a, x - w // 2 - 1, y1, bark[0]); put(a, x + (w + 1) // 2, y1, bark[0])
    put(a, x - w // 2 - 2, y1, bark[0])
