"""3D clay models for the scene props, rendered the same way as the characters."""
import math
import numpy as np
from sdf import *


def ox_model(stride=0.0):
    m = Model()
    def coat(P, n):
        garland = (np.abs(P[:, 0] - 6.6) < 0.9) & (P[:, 1] > 17.2)
        beads = garland & (np.mod(P[:, 2] * 1.3, 1.0) < 0.5)
        mm = np.where(beads, 'gold', np.where(garland, 'red', ''))
        return mm, np.zeros(len(P))
    m.add(ellipsoid((0, 14.0, 0), (10.5, 5.4, 4.8)), 'oxwhite', 0.0, decal=coat)
    m.add(ellipsoid((6.2, 16.2, 0), (4.2, 4.6, 4.4)), 'oxwhite', 2.0, decal=coat)          # hump/shoulder
    m.add(ellipsoid((-7.0, 14.6, 0), (4.6, 5.0, 4.4)), 'oxwhite', 2.0)
    m.add(ellipsoid((5.6, 11.0, 0), (3.2, 3.4, 2.2)), 'oxwhite', 1.4)                     # dewlap
    for side in (-1, 1):
        z = side * 2.4
        sw = stride * side
        m.add(capsule((6.0, 11.0, z), (6.4 + sw, 5.0, z), 1.7, 1.2), 'oxwhite', 1.0)
        m.add(capsule((6.4 + sw, 5.0, z), (6.6 + sw * 1.4, 1.0, z), 1.1, 0.9), 'oxwhite', 0.3)
        m.add(capsule((6.6 + sw * 1.4, 1.0, z), (7.0 + sw * 1.4, 0.4, z), 1.0), 'dark', 0.2)
        m.add(capsule((-7.0, 11.0, z), (-7.6 - sw, 5.0, z), 2.0, 1.2), 'oxwhite', 1.0)
        m.add(capsule((-7.6 - sw, 5.0, z), (-7.4 - sw * 1.4, 1.0, z), 1.1, 0.9), 'oxwhite', 0.3)
        m.add(capsule((-7.4 - sw * 1.4, 1.0, z), (-7.0 - sw * 1.4, 0.4, z), 1.0), 'dark', 0.2)
    # lowered head with curving horns
    def head_dec(P, n):
        eye = (np.abs(P[:, 0] - 12.6) < 0.5) & (np.abs(P[:, 1] - 13.4) < 0.5) & (np.abs(P[:, 2]) > 1.4)
        return None, np.where(eye, -5.0, 0.0)
    m.add(capsule((10.2, 15.0, 0), (14.6, 11.0, 0), 2.6, 1.9), 'oxwhite', 1.4, decal=head_dec)
    m.add(sphere((15.0, 10.4, 0), 1.9), 'skin', 0.6,
          decal=lambda P, n: (None, np.where((P[:, 0] > 16.2) & (np.abs(P[:, 2]) > 0.5), -2.5, 0.4)))
    for side in (-1, 1):
        m.add(capsule((11.6, 15.6, side * 1.6), (11.2, 17.2, side * 3.8), 0.75, 0.45), 'linen', 0.3)
        m.add(capsule((11.2, 17.2, side * 3.8), (12.6, 18.8, side * 4.2), 0.45, 0.2), 'linen', 0.0)
        m.add(ellipsoid((11.0, 15.2, side * 2.6), (0.6, 0.9, 1.0)), 'oxwhite', 0.2)       # ears
    m.add(capsule((-10.8, 16.0, 0), (-12.0, 8.0, 0.3), 0.6, 0.45), 'oxwhite', 0.4)
    m.add(sphere((-12.0, 7.4, 0.3), 0.9), 'mane', 0.0)
    return m


def cart_model(t=0.0):
    m = Model()
    def plank(P, n):
        return None, np.where(np.mod(P[:, 1] * 0.9, 1.0) < 0.22, -2.0, 0.0) + np.where(np.mod(P[:, 0] * 0.25, 1.0) < 0.08, -1.5, 0.0)
    m.add(box((0, 9.5, 0), (10.0, 2.6, 4.6), 0.4), 'wood', 0.0, decal=plank)
    for x in (-9.6, 9.6):
        m.add(box((x, 12.0, 0), (0.5, 1.8, 4.6), 0.2), 'wood', 0.0)
    for (x, z, r) in ((-6.0, -1.5, 3.0), (-1.5, 1.6, 3.2), (3.2, -1.0, 3.1), (7.0, 1.8, 2.6), (-3.0, -2.6, 2.6), (1.0, -0.2, 2.8)):
        m.add(ellipsoid((x, 12.4 + r * 0.55, z), (r, r * 0.8, r * 0.9)), 'sack', 0.6,
              decal=lambda P, n: (None, np.where(np.mod(P[:, 0] * 1.1 + P[:, 2] * 0.7, 1.0) < 0.15, -1.0, 0.0)))
    for z in (-5.4, 5.4):
        m.add(torus_z((0, 6.0, z), 5.0, 0.7), 'wood', 0.0)
        m.add(cylinder_z((0, 6.0, z), 1.0, 0.9), 'iron', 0.0)
        for k in range(6):
            a = t + k * math.pi / 3
            m.add(capsule((0, 6.0, z), (math.cos(a) * 4.6, 6.0 + math.sin(a) * 4.6, z), 0.35), 'wood', 0.0)
    m.add(capsule((10.0, 8.5, -2.4), (18.0, 7.6, -2.4), 0.45), 'wood', 0.0)
    m.add(capsule((10.0, 8.5, 2.4), (18.0, 7.6, 2.4), 0.45), 'wood', 0.0)
    m.add(capsule((10.6, 14.0, 4.8), (10.6, 16.5, 4.8), 0.2), 'iron', 0.0)
    m.add(box((10.6, 13.0, 4.8), (0.7, 0.9, 0.7), 0.2), 'gold', 0.0)
    return m


def tent_model(Wd=9.0, Ht=10.0, L=8.0):
    m = Model()
    k = math.hypot(Wd, Ht)
    def tent(P):
        x, y, z = np.abs(P[:, 0]), P[:, 1], P[:, 2]
        tri = (x * Ht + y * Wd - Wd * Ht) / k
        return np.maximum(np.maximum(tri, np.abs(z) - L), -y)
    def dec(P, n):
        x, y, z = P[:, 0], P[:, 1], P[:, 2]
        front = n[:, 2] > 0.6
        door = front & (np.abs(x) < (1 - y / Ht) * Wd * 0.38) & (y < Ht * 0.62)
        seam = (~front) & (np.mod(z * 0.36, 1.0) < 0.1)
        seam2 = (~front) & (np.mod(y * 0.5, 1.0) < 0.1)
        ridge = y > Ht - 0.6
        mm = np.where(door, 'dark', '')
        bias = np.where(seam | seam2, -1.5, 0.0) + np.where(ridge, 1.0, 0.0)
        return mm, bias
    m.add(tent, 'tent', 0.0, decal=dec)
    m.add(capsule((0, Ht - 0.2, L + 0.4), (0, Ht + 2.2, L + 0.4), 0.3), 'wood', 0.0)
    m.add(capsule((0, Ht - 0.2, -L - 0.4), (0, Ht + 2.2, -L - 0.4), 0.3), 'wood', 0.0)
    for zs in (-1, 1):
        for xs in (-1, 1):
            m.add(capsule((xs * Wd * 0.5, Ht * 0.5, zs * L * 0.7), (xs * (Wd + 3.0), 0.3, zs * (L + 1.5)), 0.12), 'linen', 0.0)
    return m


def vexillum_model(wave=0.0):
    m = Model()
    m.add(capsule((0, 0, 0), (0, 40, 0), 0.5), 'wood', 0.0)
    for y in (16.0, 19.0, 22.0):
        m.add(cylinder_z((0, y, 0.35), 1.4, 0.35), 'gold', 0.0)
    m.add(capsule((-6.5, 34.0, 0), (6.5, 34.0, 0), 0.45), 'wood', 0.0)
    def banner(P):
        q = P - np.array([0, 28.0, 0.3 + 0.0])
        q[:, 2] -= np.sin(q[:, 0] * 0.45 + wave) * 0.6
        return box((0, 0, 0), (6.0, 5.8, 0.25), 0.15)(q)
    def bdec(P, n):
        x, y = P[:, 0], P[:, 1] - 28.0
        fringe = y < -5.0
        border = (np.abs(x) > 5.2) | (y > 5.0)
        emblem = (np.hypot(x, y - 0.5) < 2.2) & (np.hypot(x, y - 0.5) > 1.2)
        text = (np.abs(y + 3.2) < 0.4) & (np.abs(x) < 3.8) & (np.mod(x, 1.6) < 1.0)
        mm = np.where(fringe | border | emblem | text, 'gold', '')
        return mm, np.zeros(len(P))
    m.add(banner, 'red', 0.0, decal=bdec)
    # eagle: body, spread wings, head
    m.add(ellipsoid((0, 41.4, 0), (1.2, 1.6, 1.0)), 'gold', 0.4)
    m.add(sphere((0.8, 43.0, 0), 0.75), 'gold', 0.3)
    for side in (-1, 1):
        m.add(ellipsoid((side * 2.6, 42.4, 0), (2.4, 0.7, 0.9)), 'gold', 0.5)
        m.add(ellipsoid((side * 4.2, 43.4, 0), (1.2, 0.6, 0.7)), 'gold', 0.4)
    return m


def column_model(h=20.0, broken=True):
    m = Model()
    def flute(P, n):
        a = np.arctan2(P[:, 0], P[:, 2])
        return None, np.where(np.mod(a * 12 / math.pi, 1.0) < 0.25, -1.0, 0.0)
    def shaft(P):
        d = cylinder_y((0, h / 2, 0), 2.4, h / 2)(P)
        if broken:
            cut = P[:, 1] - (h - 2.0 + np.sin(P[:, 0] * 1.3) * 1.2 + P[:, 2] * 0.4)
            d = np.maximum(d, cut)
        return d
    m.add(shaft, 'stone', 0.0, decal=flute)
    m.add(box((0, 0.8, 0), (3.4, 0.8, 3.4), 0.3), 'stone', 0.3)
    m.add(box((0, 2.0, 0), (2.9, 0.5, 2.9), 0.3), 'stone', 0.3)
    return m


def rock_model(seed=0, size=4.0):
    r = np.random.default_rng(seed)
    m = Model()
    for i in range(6):
        c = (r.uniform(-1, 1) * size * 0.6, size * 0.45 + r.uniform(-0.4, 0.6) * size * 0.4, r.uniform(-1, 1) * size * 0.5)
        m.add(ellipsoid(c, (size * r.uniform(0.5, 0.8), size * r.uniform(0.4, 0.6), size * r.uniform(0.5, 0.8))), 'stone', size * 0.35,
              decal=lambda P, n: (None, np.where(np.mod(P[:, 0] * 0.9 + P[:, 1] * 1.7, 1.0) < 0.12, -1.0, 0.0)))
    m.add(lambda P: -P[:, 1] - 0.0 + 0.0 * P[:, 0] + 1e3 * 0, 'stone', 0.0) if False else None
    return m


def crate_model(s=3.0):
    m = Model()
    def dec(P, n):
        q = np.abs(P - np.array([0, s, 0]))
        edge = (np.sort(q, axis=1)[:, 1] > s * 0.78)
        cross = (np.abs(np.abs(P[:, 0]) - np.abs(P[:, 1] - s)) < 0.35) & (np.abs(n[:, 2]) > 0.6)
        return None, np.where(edge | cross, -1.6, 0.0)
    m.add(box((0, s, 0), (s, s, s), 0.25), 'wood', 0.0, decal=dec)
    return m


def amphora_model():
    m = Model()
    m.add(ellipsoid((0, 4.4, 0), (2.2, 3.2, 2.2)), 'terra', 0.0)
    m.add(capsule((0, 6.5, 0), (0, 9.2, 0), 1.0, 0.7), 'terra', 0.8)
    m.add(capsule((0, 4.4, 0), (0, 0.6, 0), 1.4, 0.4), 'terra', 1.0)
    for side in (-1, 1):
        m.add(torus_z((side * 1.2, 8.0, 0), 0.9, 0.25), 'terra', 0.0)
    return m


def campfire_model():
    m = Model()
    for k in range(9):
        a = k * 2 * math.pi / 9
        m.add(ellipsoid((math.cos(a) * 5.0, 0.8, math.sin(a) * 5.0), (1.3, 1.0, 1.1)), 'stone', 0.2)
    for k in range(4):
        a = k * math.pi / 4 + 0.3
        m.add(capsule((math.cos(a) * 4.0, 0.9, math.sin(a) * 4.0), (-math.cos(a) * 1.0, 2.6, -math.sin(a) * 1.0), 0.6), 'wood', 0.2,
              decal=lambda P, n: (np.where(np.hypot(P[:, 0], P[:, 2]) < 2.2, 'dark', ''), np.zeros(len(P))))
    return m


def aqueduct_model(n=7, span=14.0, h1=16.0, h2=12.0, depth=3.0):
    m = Model()
    L = n * span
    def body(P):
        x, y, z = P[:, 0], P[:, 1], P[:, 2]
        lower = box((L / 2, h1 / 2, 0), (L / 2, h1 / 2, depth))(P)
        upper = box((L / 2, h1 + h2 / 2, 0), (L / 2, h2 / 2, depth * 0.85))(P)
        cap = box((L / 2, h1 + h2 + 1.0, 0), (L / 2, 1.0, depth))(P)
        d = np.minimum(np.minimum(lower, upper), cap)
        # big arches below, small arches above (subtract cylinders along z)
        xm = np.mod(x, span) - span / 2
        a1 = np.maximum(np.hypot(xm, np.maximum(y - (h1 - span * 0.36), 0)) - span * 0.34, y - h1 + 1.2)
        a1 = np.maximum(np.hypot(xm, np.maximum(y - (h1 - span * 0.36), 0)) - span * 0.34, -1e9)
        xm2 = np.mod(x, span / 2) - span / 4
        a2 = np.hypot(xm2, np.maximum(y - (h1 + h2 * 0.45), 0)) - span * 0.16
        a2 = np.where(y < h1 + 0.6, 1e9, a2)
        d = np.maximum(d, -a1)
        d = np.maximum(d, -np.where(y > h1 + h2 - 0.8, 1e9, a2))
        return d
    def dec(P, n):
        courses = np.mod(P[:, 1] * 0.45, 1.0) < 0.1
        joints = np.mod(P[:, 0] * 0.22 + np.floor(P[:, 1] * 0.45) * 0.5, 1.0) < 0.05
        inner = n[:, 2] < 0.5
        return None, np.where(courses | joints, -1.2, 0.0) + np.where(inner, -1.0, 0.0)
    m.add(body, 'tuff', 0.0, decal=dec)
    return m
