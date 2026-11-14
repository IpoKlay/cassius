"""Tiny SDF 'clay' renderer: model a figure from smooth 3D primitives, light it, then pixelise it
into hand-pixel style (majority-vote downsample, hue-shifted ramps, warm outline, specular pops)."""
import math
import numpy as np
from PIL import Image


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0


# hue-shifted ramps (dark -> light), sampled from the reference palette where possible
RAMPS = {
    'skin': ['5a2e20', '8e5233', 'b16c43', 'd08a5a', 'e9a87b', 'f6cca4'],
    'red': ['3e0e14', '651b19', '902722', 'b04433', 'd0603f', 'ee8a5a'],
    'steel': ['26262e', '3e3e46', '62616a', '8a8a90', 'b3b7b7', 'e8ece8'],
    'gold': ['5a3410', '8a5418', 'bb7926', 'ebab32', 'fad141', 'fdfb95'],
    'bronze': ['4a2a12', '7a4a1c', 'a76d2c', 'ca963a', 'eec060', 'fff0b0'],
    'leather': ['2e1810', '45231d', '64392a', '824c32', 'a5623d', 'c48058'],
    'wood': ['3a2014', '5a3422', '7a4a2e', '9a6440', 'b88054', 'd4a070'],
    'linen': ['6a5e50', '9a8e7c', 'c4b8a0', 'e0d6c0', 'f4eedc', 'fffcf0'],
    'horse': ['3a1e14', '5c3020', '7e4428', 'a05c34', 'c27a48', 'dc9a62'],
    'mane': ['1a100c', '2a1a14', '3c2820', '54382a', '6c4a36', '8a6046'],
    'iron': ['22222a', '3a3a44', '5a5a64', '82828c', 'b0b0b8', 'e4e4ea'],
    'oxwhite': ['5e4e48', '8a7a70', 'b4a89a', 'd6ccbc', 'eee6d6', 'fffaf0'],
    'tent': ['3e2618', '5e3c26', '84583a', 'a8774e', 'c89a68', 'e2bc88'],
    'stone': ['2e2a2e', '4a4448', '6e666a', '948a88', 'b8aea6', 'ddd4c8'],
    'sack': ['5a4630', '826a4a', 'a88c64', 'c8ae82', 'e0caa0', 'f4e4c0'],
    'dark': ['0e0a0a', '160f0e', '1e1412', '281a16', '30201a', '3a261e'],
    'tuff': ['3e2a26', '5e4038', '84604e', 'a88068', 'c8a084', 'e0c0a0'],
    'terra': ['4a2014', '742e1a', '9c4426', 'be5e34', 'd87e4c', 'eea070'],
}
RAMPS = {k: np.array([hexc(h) for h in v]) for k, v in RAMPS.items()}
OUTLINE = hexc('3c2621')
MATS = list(RAMPS.keys())


# ------------------------------------------------------------------ primitives (P: (N,3))
def sphere(c, r):
    c = np.array(c, float)
    return lambda P: np.linalg.norm(P - c, axis=1) - r


def ellipsoid(c, rad):
    c = np.array(c, float); rad = np.array(rad, float)
    def f(P):
        q = (P - c) / rad
        k0 = np.linalg.norm(q, axis=1)
        k1 = np.linalg.norm(q / rad, axis=1)
        return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)
    return f


def capsule(a, b, ra, rb=None):
    a = np.array(a, float); b = np.array(b, float); rb = ra if rb is None else rb
    ba = b - a
    L2 = ba @ ba
    def f(P):
        pa = P - a
        h = np.clip((pa @ ba) / L2, 0, 1)
        return np.linalg.norm(pa - h[:, None] * ba, axis=1) - (ra + (rb - ra) * h)
    return f


def box(c, half, r=0.0):
    c = np.array(c, float); half = np.array(half, float)
    def f(P):
        q = np.abs(P - c) - half + r
        return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(axis=1), 0) - r
    return f


def cyl_shell(center, R, thick, half_h, half_ang):
    """curved shield: part of a vertical cylinder wall, opening toward +z"""
    c = np.array(center, float)
    def f(P):
        q = P - c
        rr = np.hypot(q[:, 0], q[:, 2])
        ang = np.arctan2(q[:, 0], q[:, 2])
        d_r = np.abs(rr - R) - thick
        d_a = (np.abs(ang) - half_ang) * R
        d_y = np.abs(q[:, 1]) - half_h
        d = np.stack([d_r, d_a, d_y], 1)
        return np.linalg.norm(np.maximum(d, 0), axis=1) + np.minimum(d.max(axis=1), 0)
    return f


def torus_z(c, R, r):
    """ring standing in the x-y plane (a wheel seen from the side), axis along z"""
    c = np.array(c, float)
    def f(P):
        q = P - c
        return np.hypot(np.hypot(q[:, 0], q[:, 1]) - R, q[:, 2]) - r
    return f


def cylinder_y(c, r, half_h):
    c = np.array(c, float)
    def f(P):
        q = P - c
        d = np.stack([np.hypot(q[:, 0], q[:, 2]) - r, np.abs(q[:, 1]) - half_h], 1)
        return np.linalg.norm(np.maximum(d, 0), axis=1) + np.minimum(d.max(axis=1), 0)
    return f


def cylinder_z(c, r, half_l):
    c = np.array(c, float)
    def f(P):
        q = P - c
        d = np.stack([np.hypot(q[:, 0], q[:, 1]) - r, np.abs(q[:, 2]) - half_l], 1)
        return np.linalg.norm(np.maximum(d, 0), axis=1) + np.minimum(d.max(axis=1), 0)
    return f


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


class Model:
    def __init__(self):
        self.parts = []        # (sdf, material, blend, decal)

    def add(self, sdf, mat, blend=0.0, decal=None):
        self.parts.append((sdf, mat, blend, decal))

    def eval(self, P):
        d = np.full(len(P), 1e9)
        best = np.full(len(P), 1e9)
        mat = np.zeros(len(P), int)
        for i, (f, m, k, _) in enumerate(self.parts):
            di = f(P)
            closer = di < best
            best = np.where(closer, di, best)
            mat = np.where(closer, i, mat)
            d = smin(d, di, k) if k > 0 else np.minimum(d, di)
        return d, mat


def render(model, size, scale=1.0, ss=4, yaw=35, pitch=28, light=(-0.55, 0.75, 0.55), origin=(0, 0)):
    """orthographic camera looking down at `pitch`, model rotated by `yaw` toward camera-right"""
    W, H = size
    ws, hs = W * ss, H * ss
    yr, pr = math.radians(yaw), math.radians(pitch)
    # camera basis in world: forward looks down and into the scene
    fwd = np.array([0, -math.sin(pr), -math.cos(pr)])
    up = np.array([0, math.cos(pr), -math.sin(pr)])
    right = np.array([1.0, 0, 0])
    # model rotation (yaw about y)
    Ry = np.array([[math.cos(yr), 0, math.sin(yr)], [0, 1, 0], [-math.sin(yr), 0, math.cos(yr)]])
    js, is_ = np.mgrid[0:hs, 0:ws]
    u = ((is_ + 0.5) / ss - W / 2) / scale + origin[0]
    v = ((hs - js - 0.5) / ss) / scale + origin[1]
    O = (u.reshape(-1, 1) * right + v.reshape(-1, 1) * up) - fwd * 80
    D = np.tile(fwd, (len(O), 1))
    Rt = Ry.T
    t = np.zeros(len(O))
    hit = np.zeros(len(O), bool)
    alive = np.ones(len(O), bool)
    for step in range(140):
        idx = np.nonzero(alive)[0]
        if len(idx) == 0:
            break
        P = (O[idx] + D[idx] * t[idx, None]) @ Rt.T
        d, _ = model.eval(P)
        t[idx] += d * 0.9
        h = d < 0.02
        hit[idx[h]] = True
        alive[idx[h]] = False
        alive[idx[t[idx] > 200]] = False
    Phit = (O + D * t[:, None]) @ Rt.T
    idx = np.nonzero(hit)[0]
    P = Phit[idx]
    d0, mat = model.eval(P)
    e = 0.05
    n = np.zeros((len(P), 3))
    for k in range(3):
        o = np.zeros(3); o[k] = e
        n[:, k] = model.eval(P + o)[0] - model.eval(P - o)[0]
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    n_w = n @ Ry.T                                  # normals back to world space for lighting
    L = np.array(light, float); L /= np.linalg.norm(L)
    diff = np.clip(n_w @ L, 0, 1)
    ao = np.clip(model.eval(P + n * 1.2)[0] / 1.2, 0, 1) ** 0.6
    view = -fwd
    Hh = L + view; Hh /= np.linalg.norm(Hh)
    spec = np.clip(n_w @ Hh, 0, 1) ** 24
    rim = np.clip(1 - np.abs(n_w @ view), 0, 1) ** 3
    lum = 0.18 + 0.72 * diff * (0.55 + 0.45 * ao) + 0.12 * rim * (n_w[:, 1] > -0.2)
    lum *= 0.75 + 0.25 * ao
    # per-part material + decal pass
    names = np.array([model.parts[i][1] for i in mat])
    tone_bias = np.zeros(len(P))
    for i, (_, m, _, decal) in enumerate(model.parts):
        if decal is not None:
            sel = mat == i
            if sel.any():
                newm, bias = decal(P[sel], n[sel])
                if newm is not None:
                    names[sel] = np.where(newm != '', newm, names[sel])
                tone_bias[sel] += bias
    shiny = np.isin(names, ['steel', 'gold', 'bronze', 'iron'])
    sheen = np.isin(names, ['horse', 'mane', 'leather'])
    lum = lum + np.where(shiny, spec * 0.9, np.where(sheen, spec * 0.45, spec * 0.15))
    lum = 0.5 + (lum - 0.5) * 1.18          # a touch more contrast, like hand-shaded sprites
    tone = np.clip(np.round(lum * 5 + tone_bias), 0, 5).astype(int)
    # high-res buffers
    mat_img = np.full(ws * hs, -1)
    tone_img = np.zeros(ws * hs, int)
    mat_img[idx] = np.array([MATS.index(x) for x in names])
    tone_img[idx] = tone
    return mat_img.reshape(hs, ws), tone_img.reshape(hs, ws), (W, H, ss)


def pixelise(mat_img, tone_img, dims, outline=True, cov=0.45):
    W, H, ss = dims
    out = np.zeros((H, W, 4))
    for y in range(H):
        for x in range(W):
            m = mat_img[y * ss:(y + 1) * ss, x * ss:(x + 1) * ss].ravel()
            t = tone_img[y * ss:(y + 1) * ss, x * ss:(x + 1) * ss].ravel()
            ok = m >= 0
            if ok.mean() < cov:
                continue
            code = m[ok] * 10 + t[ok]
            vals, cnt = np.unique(code, return_counts=True)
            c = vals[cnt.argmax()]
            mm, tt = c // 10, c % 10
            # take the mean tone of that material in the block, rounded, for smoother ramps
            tt = int(round(t[ok][m[ok] == mm].mean()))
            out[y, x, :3] = RAMPS[MATS[mm]][tt]
            out[y, x, 3] = 1
            out[y, x, 3] = 1
    # inner contour: where two materials meet, darken the lower/right pixel one ramp step (part separation)
    mid = np.full((H, W), -1)
    for y in range(H):
        for x in range(W):
            m = mat_img[y * ss:(y + 1) * ss, x * ss:(x + 1) * ss].ravel()
            m = m[m >= 0]
            if len(m) and out[y, x, 3] > 0:
                v, c = np.unique(m, return_counts=True)
                mid[y, x] = v[c.argmax()]
    for y in range(1, H):
        for x in range(1, W):
            if mid[y, x] < 0:
                continue
            for (yy, xx) in ((y - 1, x), (y, x - 1)):
                if mid[yy, xx] >= 0 and mid[yy, xx] != mid[y, x]:
                    out[y, x, :3] = out[y, x, :3] * 0.72 + OUTLINE * 0.28
                    break
    if outline:
        a = out[:, :, 3] > 0
        pad = np.pad(a, 1)
        ring = (~a) & (pad[1:-1, :-2] | pad[1:-1, 2:] | pad[:-2, 1:-1] | pad[2:, 1:-1])
        out[ring, :3] = OUTLINE
        out[ring, 3] = 1
    return out


def save(arr, path, scale=1):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), 'RGBA')
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)
    return im
