import random
import numpy as np
from kit import *


def build_ground(sc, road_c, bank, GR, DIRT, seed, road_w=22, blades=5200, blade_tint=C('d8c060'),
                 flowers=None, stones=True, ruts=True, edge_col=None, dry=None, cells=(48, 24, 12, 6), n_stones=260, spread=1.0):
    rng = random.Random(seed)
    yy, xx = np.mgrid[0:H, 0:W]
    n1 = fbm(W, H, seed + 3, cells=cells)
    n2 = fbm(W, H, seed + 9, cells=(16, 8, 4), wts=(0.5, 0.3, 0.2))
    rc = road_c(xx)
    dist = np.abs(yy - rc)
    edge = road_w + (n2 - 0.5) * 8
    is_road = dist < edge
    gv = n1 * 1.0 + n2 * 0.15 - 0.08
    gv = gv.mean() + (gv - gv.mean()) * spread
    g = band(np.clip(gv, 0, 0.999), len(GR), dither=False)
    sc.alb[:] = np.array(GR)[np.clip((g * len(GR)).astype(int), 0, len(GR) - 1)]
    if dry is not None:
        dryness = np.clip((yy - rc) / 60, 0, 1)
        sc.alb = sc.alb * (1 - dryness[:, :, None] * 0.25) + dry[None, None, :] * dryness[:, :, None] * 0.25
    d = band(np.clip(n1 * 0.7 + n2 * 0.3, 0, 0.999), len(DIRT), dither=False)
    road_col = np.array(DIRT)[np.clip((d * len(DIRT)).astype(int), 0, len(DIRT) - 1)]
    sc.alb[is_road] = road_col[is_road]
    if ruts:
        for off in (-road_w * 0.36, road_w * 0.36):
            m = (np.abs(yy - (rc + off)) < 1.2) & is_road
            sc.alb[m] = sc.alb[m] * 0.62
            m2 = (np.abs(yy - (rc + off - 1.5)) < 0.6) & is_road
            sc.alb[m2] = sc.alb[m2] * 1.12
    em = (np.abs(dist - edge) < 1.5) & (n2 > 0.45)
    sc.alb[em] = edge_col if edge_col is not None else GR[1]
    if stones:
        for i in range(n_stones):
            x = rng.randint(0, W - 2); y = int(road_c(x) + rng.uniform(-road_w, road_w))
            if 0 <= y < H - 1:
                sc.alb[y, x] = DIRT[-1] * 1.15; sc.alb[y + 1, x] = DIRT[0]
    for i in range(blades):
        x = rng.randint(0, W - 1); y = rng.randint(14, H - 1)
        if abs(y - road_c(x)) < road_w - 1 or y > bank(x) - 1:
            continue
        hgt = rng.randint(1, 4)
        base = sc.alb[y, x].copy()
        for k in range(hgt):
            if y - k >= 0:
                sc.alb[y - k, x] = base * (0.75 + 0.18 * k) + blade_tint * 0.06 * k
    if flowers:
        for i in range(160):
            x = rng.randint(0, W - 1); y = rng.randint(30, H - 1)
            if abs(y - road_c(x)) < road_w + 2 or y > bank(x) - 2:
                continue
            sc.alb[y, x] = rng.choice(flowers)
    return yy, xx
