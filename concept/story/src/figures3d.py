"""Parametric 3D people: one model with switches for clothes, headgear, beard and pose."""
import math
import numpy as np
from sdf import *

POSES = {
    'down': ((5.8, 24.6, 0.8), (5.6, 19.6, 1.8)),
    'up': ((7.6, 34.0, 1.0), (8.0, 39.8, 1.6)),
    'forward': ((5.6, 26.2, 3.2), (3.8, 26.4, 6.6)),
    'out': ((7.8, 28.0, 1.0), (10.2, 26.0, 2.4)),
    'sack': ((6.2, 33.0, 1.6), (4.0, 35.8, 1.2)),
    'staff': ((6.2, 26.0, 2.2), (6.0, 23.6, 4.2)),
    'chest': ((5.4, 25.2, 2.6), (1.4, 27.2, 4.6)),
    'axe': ((7.0, 34.6, 1.2), (5.2, 39.0, 2.6)),
}


def human(body='brown', legs='skin', robe=False, cloak=None, head='bare', hair='mane', beard=None,
          arms=('down', 'down'), kneel=False, belt='leather', sleeve=None, scale=1.0, skin='skin',
          sack=False, staff=False, scroll=False, shield=None, spear=False, axe=False, lantern=False,
          mask=False, crown_mat='gold', thin=1.0):
    m = Model()
    s = scale
    dy = -8.5 * s if kneel else 0.0

    def P3(x, y, z, lift=True):
        return (x * s * thin if abs(x) > 0 else x, y * s + (dy if lift else 0), z * s)

    # ---- legs / robe
    if robe:
        if kneel:
            m.add(capsule(P3(0, 24, 0), P3(0, 9, 1.6), 3.7 * s, 5.6 * s), body, 1.0,
                  decal=lambda P, n: (None, np.where(np.mod(np.arctan2(P[:, 0], P[:, 2]) * 2.2, 1) < 0.15, -1.0, 0.0)))
            m.add(ellipsoid((0, 2.6 * s, -1.0 * s), (5.6 * s, 2.6 * s, 6.0 * s)), body, 1.4)
        else:
            m.add(capsule(P3(0, 24, 0), P3(0, 2.4, 0.2), 3.6 * s, 5.4 * s), body, 1.0,
                  decal=lambda P, n: (None, np.where(np.mod(np.arctan2(P[:, 0], P[:, 2]) * 2.2, 1) < 0.15, -1.0, 0.0)))
            for side in (-1, 1):
                m.add(ellipsoid((side * 1.8 * s, 0.7 * s, 2.6 * s), (1.2 * s, 0.8 * s, 1.8 * s)), 'leather', 0.3)
    else:
        for side in (-1, 1):
            if kneel:
                knee = (side * 2.1 * s, 1.4 * s, 4.4 * s)
                m.add(capsule(P3(side * 2.0, 17.0, 0), knee, 1.8 * s, 1.5 * s), legs, 0.6)
                m.add(capsule(knee, (side * 2.1 * s, 1.3 * s, -2.8 * s), 1.4 * s, 1.0 * s), legs, 0.3)
            else:
                knee = P3(side * 2.2, 9.5, 0.5)
                m.add(capsule(P3(side * 2.0, 17.0, 0), knee, 1.75 * s, 1.45 * s), legs, 0.6)
                m.add(capsule(knee, P3(side * 2.2, 2.0, 0.2), 1.45 * s, 1.05 * s), legs, 0.4,
                      decal=lambda P, n: (np.where(P[:, 1] < 3.6 * s, 'leather', ''), np.zeros(len(P))))
                m.add(box(P3(side * 2.2, 0.8, 1.0), (1.2 * s, 0.8 * s, 2.0 * s), 0.6 * s), 'leather', 0.3)
        m.add(capsule(P3(0, 23.0, 0), P3(0, 14.6, 0.1), 4.4 * s, 4.9 * s), body, 0.6,
              decal=lambda P, n: (None, np.where(np.mod(np.arctan2(P[:, 0], P[:, 2]) * 2.6, 1) < 0.18, -1.0, 0.0)))
    # ---- torso, belt
    m.add(ellipsoid(P3(0, 27.6, 0), (4.6 * s * thin, 5.4 * s, 3.4 * s)), body, 0.9)
    if belt:
        m.add(capsule(P3(-4.6, 22.8, 0.5), P3(4.6, 22.8, 0.5), 0.7 * s), belt, 0.5)
    # ---- cloak behind
    if cloak:
        m.add(capsule(P3(0, 31.5, -2.4), P3(0, 3.0 if not kneel else 9.0, -4.0), 4.6 * s, 6.2 * s), cloak, 1.2,
              decal=lambda P, n: (None, np.where(np.mod(P[:, 0] * 0.5 + 0.3, 1.0) < 0.18, -1.2, 0.0)))
        m.add(capsule(P3(-4.6, 31.6, 0.4), P3(4.6, 31.6, 0.4), 1.2 * s), cloak, 0.8)
    # ---- arms
    for side, pose in zip((-1, 1), arms):
        el, ha = POSES[pose]
        sh = P3(side * 4.9, 30.6, 0.0)
        el = P3(side * el[0], el[1], el[2])
        ha = P3(side * ha[0], ha[1], ha[2])
        m.add(capsule(sh, el, 1.45 * s, 1.25 * s), sleeve or body, 0.5)
        m.add(capsule(el, ha, 1.2 * s, 1.0 * s), skin, 0.3)
        m.add(sphere(ha, 1.15 * s), skin, 0.3)
        if sack and side == 1:
            m.add(ellipsoid((ha[0] - 0.4 * s, ha[1] + 1.4 * s, ha[2] - 2.6 * s), (3.4 * s, 2.6 * s, 2.6 * s)), 'sack', 0.5,
                  decal=lambda P, n: (None, np.where(np.mod(P[:, 0] * 1.1, 1.0) < 0.15, -1.0, 0.0)))
        if staff and side == -1:
            m.add(capsule((ha[0], 0.2, ha[2]), (ha[0], 46 * s + dy, ha[2]), 0.45 * s), 'wood', 0.0)
        if spear and side == -1:
            m.add(capsule((ha[0], 0.2, ha[2]), (ha[0], 50 * s + dy, ha[2]), 0.42 * s), 'wood', 0.0,
                  decal=lambda P, n: (np.where(P[:, 1] > 46 * s + dy, 'iron', ''), np.zeros(len(P))))
        if axe and side == 1:
            m.add(capsule(ha, (ha[0] - 3.5 * s, ha[1] + 6.0 * s, ha[2] - 1.0 * s), 0.4 * s), 'wood', 0.0)
            m.add(box((ha[0] - 3.8 * s, ha[1] + 6.4 * s, ha[2] - 1.0 * s), (1.8 * s, 1.2 * s, 0.3 * s), 0.2 * s), 'iron', 0.0)
        if lantern and side == 1:
            m.add(capsule(ha, (ha[0], ha[1] - 2.0 * s, ha[2]), 0.15 * s), 'iron', 0.0)
            m.add(box((ha[0], ha[1] - 3.6 * s, ha[2]), (1.0 * s, 1.4 * s, 1.0 * s), 0.3 * s), 'gold', 0.0)
    if scroll:
        m.add(capsule(P3(-2.6, 27.0, 5.8), P3(2.6, 27.0, 5.8), 0.9 * s), 'linen', 0.0,
              decal=lambda P, n: (np.where(np.abs(P[:, 0]) > 2.2 * s, 'wood', ''), np.zeros(len(P))))
        m.add(sphere(P3(0, 25.6, 6.4), 0.7 * s), 'red', 0.0)          # wax seal
    if shield == 'round':
        m.add(cylinder_z(P3(2.2, 24.0, 6.4), 6.0 * s, 0.45 * s), 'blue', 0.0,
              decal=lambda P, n: (np.where(np.hypot(P[:, 0] - 2.2 * s, P[:, 1] - 24.0 * s - dy) > 5.2 * s, 'iron',
                                           np.where(np.hypot(P[:, 0] - 2.2 * s, P[:, 1] - 24.0 * s - dy) < 1.3 * s, 'bronze', '')),
                                  np.where(np.mod(np.arctan2(P[:, 1] - 24.0 * s - dy, P[:, 0] - 2.2 * s) * 1.27, 1.0) < 0.5, -1.0, 0.0)))
    # ---- neck, head
    m.add(capsule(P3(0, 31.4, 0), P3(0, 33.0, 0.3), 1.5 * s), skin, 0.5)
    m.add(sphere(P3(0, 35.0, 0.4), 2.75 * s), skin, 0.0,
          decal=lambda P, n: (None, np.where((P[:, 1] > 34.8 * s + dy) & (P[:, 1] < 35.6 * s + dy) & (np.abs(np.abs(P[:, 0]) - 1.05 * s) < 0.45 * s) & (P[:, 2] > 2.0 * s), -4.0, 0.0)))
    m.add(sphere(P3(0, 34.4, 3.0), 0.72 * s), skin, 0.3)
    if mask:
        m.add(ellipsoid(P3(0, 35.0, 2.4), (2.6 * s, 3.0 * s, 1.0 * s)), 'bone', 0.2,
              decal=lambda P, n: (None, np.where((np.abs(P[:, 1] - 35.6 * s - dy) < 0.5 * s) & (np.abs(np.abs(P[:, 0]) - 1.1 * s) < 0.55 * s), -5.0, 0.0)))
        for side in (-1, 1):
            m.add(capsule(P3(side * 1.6, 37.4, 0.4), P3(side * 4.2, 41.6, -0.4), 0.45 * s, 0.2 * s), 'bone', 0.3)
    if beard:
        m.add(ellipsoid(P3(0, 32.6, 1.6), (2.4 * s, 2.6 * s, 1.6 * s)), beard, 0.6)
    if head in ('bare', 'crown'):
        hb = sphere(P3(0, 35.6, -0.4), 2.95 * s)
        m.add(lambda P: np.maximum(hb(P), np.minimum(35.8 * s + dy - P[:, 1], 0.2 * s - P[:, 2] * -1.0)), hair, 0.3)
    if head == 'crown':
        c = P3(0, 37.6, -0.1)
        m.add(lambda P: np.maximum(np.abs(np.hypot(P[:, 0] - c[0], P[:, 2] - c[2]) - 2.9 * s) - 0.45 * s, np.abs(P[:, 1] - c[1]) - 0.7 * s), crown_mat, 0.0)
        for k in range(7):
            a = k * 2 * math.pi / 7
            m.add(capsule((c[0] + math.sin(a) * 2.9 * s, c[1], c[2] + math.cos(a) * 2.9 * s),
                          (c[0] + math.sin(a) * 3.0 * s, c[1] + 1.8 * s, c[2] + math.cos(a) * 3.0 * s), 0.38 * s, 0.1 * s), crown_mat, 0.0)
    if head == 'hood':
        hd = sphere(P3(0, 35.6, -0.3), 3.6 * s)
        face = box(P3(0, 34.2, 3.0), (2.3 * s, 2.8 * s, 2.0 * s))
        m.add(lambda P: np.maximum(hd(P), -face(P)), cloak or body, 0.4)
    if head == 'helmet':
        hb = sphere(P3(0, 35.8, -0.3), 3.15 * s)
        m.add(lambda P: np.maximum(hb(P), 35.6 * s + dy - P[:, 1]), 'steel', 0.0)
        m.add(capsule(P3(-3.0, 35.8, 1.0), P3(3.0, 35.8, 1.0), 0.45 * s), 'bronze', 0.2)
    if head == 'cap':
        hb = sphere(P3(0, 36.2, -0.3), 3.0 * s)
        m.add(lambda P: np.maximum(hb(P), 35.9 * s + dy - P[:, 1]), 'leather', 0.0)
    return m


def child(**kw):
    kw.setdefault('scale', 0.68)
    return human(**kw)
