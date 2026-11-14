import random
import numpy as np
from kit import rgba, put, C


def flame(w=16, h=20, seed=0, n=40):
    fl = rgba(w, h); fe = rgba(w, h); r = random.Random(seed)
    cx = w // 2
    for k in range(n):
        x0 = cx + r.randint(-w // 3, w // 3)
        hh = r.randint(3, max(4, h - 4 - abs(x0 - cx) * 2))
        for y in range(h - 1 - hh, h - 1):
            t = (h - 1 - y) / max(1, hh)
            c = C('fff2b0') if t < 0.3 and abs(x0 - cx) < 3 else C('ffb040') if t < 0.65 else C('e2502a')
            put(fl, x0, y, c); put(fe, x0, y, c * 0.8)
    return fl, fe


def torch_on(sc, x, y_top, depth, seed=0, light=0.8, radius=56):
    fl, fe = flame(8, 12, seed, 14)
    sc.add(fl, x, y_top, emissive=fe, cast=False, depth=depth)
    sc.light(x, y_top - 6, radius, (1.0, 0.58, 0.26), light)
