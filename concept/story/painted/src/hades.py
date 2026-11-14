"""Hades-like finishing pass for the painted (non-pixel) illustrations:
ink linework from colour edges, painted texture, bloom, glowing motes, grain."""
import math, sys
import numpy as np
from PIL import Image
from scipy import ndimage


def _g(a, s):
    return np.stack([ndimage.gaussian_filter(a[..., c], s) for c in range(3)], -1)


def ink(img, strength=1.0, thick=2, thresh=0.06, col=(0.12, 0.05, 0.12)):
    sm = np.stack([ndimage.median_filter(img[..., c], size=7) for c in range(3)], -1)
    sm = _g(sm, 1.0)
    e = np.zeros(img.shape[:2])
    for c in range(3):
        gx = ndimage.sobel(sm[..., c], 1); gy = ndimage.sobel(sm[..., c], 0)
        e = np.maximum(e, np.hypot(gx, gy))
    e = np.clip((e - thresh) / (thresh * 2.5), 0, 1)
    e = ndimage.maximum_filter(e, size=thick)
    e = ndimage.gaussian_filter(e, 0.6)
    line = img * 0.28 + np.array(col) * 0.72
    return img * (1 - e[..., None] * 0.85 * strength) + line * e[..., None] * 0.85 * strength


def texture(img, seed=0, amt=0.05):
    rng = np.random.default_rng(seed)
    H, W = img.shape[:2]
    lo = ndimage.gaussian_filter(rng.random((H, W)), 18); lo = (lo - lo.mean()) / (lo.std() + 1e-9)
    # brushy streaks: noise smeared diagonally
    n = rng.random((H, W))
    k = np.zeros((1, 15)); k[0, :] = 1 / 15
    st = ndimage.convolve(n, k); st = ndimage.rotate(st, 25, reshape=False, mode='reflect')
    st = (st - st.mean()) / (st.std() + 1e-9)
    lum = img.mean(-1)
    hatch = ((np.add.outer(np.arange(H), np.arange(W)) % 7) == 0) & (lum < 0.22) & (rng.random((H, W)) > 0.35)
    out = img * (1 + (lo * 0.6 + st * 0.4)[..., None] * amt)
    out[hatch] *= 0.82
    return out


def bloom(img, k=0.45):
    lum = img.max(-1)
    hi = img * np.clip((lum - 0.62) / 0.38, 0, 1)[..., None]
    return img + (_g(hi, 6) * 0.6 + _g(hi, 22) * 0.5 + _g(hi, 60) * 0.35) * k


def motes(img, seed, n, box, col, size=(1.5, 4.5), soft=True):
    rng = np.random.default_rng(seed)
    H, W = img.shape[:2]
    layer = np.zeros((H, W))
    x0, y0, x1, y1 = box
    for i in range(n):
        x, y = rng.uniform(x0, x1) * W, rng.uniform(y0, y1) * H
        r = rng.uniform(*size)
        ix, iy = int(x), int(y)
        R = int(r * 3) + 2
        ys, xs = np.mgrid[max(0, iy - R):min(H, iy + R), max(0, ix - R):min(W, ix + R)]
        d = np.hypot(xs - x, ys - y)
        layer[ys, xs] = np.maximum(layer[ys, xs], np.clip(1 - d / r, 0, 1) ** 0.8 * rng.uniform(0.5, 1))
    glow = ndimage.gaussian_filter(layer, 4) * 2.2
    return img + (layer[..., None] * 0.9 + glow[..., None]) * np.array(col)


def grade(img, sat=1.15, lift=(0.02, 0.0, 0.04), vign=0.3, seed=0):
    g = img.mean(-1, keepdims=True)
    img = g + (img - g) * sat
    img = img + np.array(lift) * (1 - img)
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    v = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    img = img * (1 - vign * np.clip(v - 0.55, 0, 1)[..., None])
    rng = np.random.default_rng(seed)
    img = img + (rng.random(img.shape[:2]) - 0.5)[..., None] * 0.025
    return np.clip(img, 0, 1)


def finish(path_in, path_out, seed, mote_sets=(), ink_k=1.0, bloom_k=0.45, sat=1.15):
    img = np.asarray(Image.open(path_in).convert('RGB')).astype(float) / 255
    img = ink(img, ink_k)
    img = texture(img, seed)
    for ms in mote_sets:
        img = motes(img, seed + len(ms), *ms)
    img = bloom(np.clip(img, 0, 1), bloom_k)
    img = grade(img, sat=sat, seed=seed)
    im = Image.fromarray((img * 255).astype(np.uint8))
    im.save(path_out)
    return im
