"""Architecture and set pieces for the story slides."""
import math
import numpy as np
from sdf import *


def courses(step=1.6, joint=3.2, bias=-1.2):
    def dec(P, n):
        c = np.mod(P[:, 1] / step, 1.0) < 0.14
        j = np.mod(P[:, 0] / joint + np.floor(P[:, 1] / step) * 0.5, 1.0) < 0.08
        return None, np.where(c | j, bias, 0.0)
    return dec


def temple_front(n_cols=6, span=9.0, col_h=30.0, depth=10.0):
    """steps, a colonnade and a pediment with a frieze"""
    m = Model()
    L = (n_cols - 1) * span
    for i in range(4):                                   # steps
        m.add(box((0, 1.0 + i * 2.0, depth * 0.5 - i * 1.6), (L / 2 + 8 - i * 1.4, 1.0, depth * 0.9 - i * 1.6), 0.15), 'stone', 0.0)
    base = 8.0
    for i in range(n_cols):
        x = -L / 2 + i * span
        m.add(cylinder_y((x, base + col_h / 2, depth * 0.4), 2.2, col_h / 2), 'stone', 0.0,
              decal=lambda P, n: (None, np.where(np.mod(np.arctan2(P[:, 0] - np.round(P[:, 0] / span) * span, P[:, 2]) * 3.8, 1.0) < 0.3, -1.0, 0.0)))
        m.add(box((x, base + col_h + 0.8, depth * 0.4), (3.0, 0.8, 3.0), 0.2), 'stone', 0.2)
        m.add(box((x, base + 0.6, depth * 0.4), (2.9, 0.6, 2.9), 0.2), 'stone', 0.2)
    m.add(box((0, base + col_h / 2, -depth * 0.4), (L / 2 + 2, col_h / 2, 1.5), 0.0), 'tuff', 0.0, decal=courses())   # cella wall
    ent_y = base + col_h + 3.0
    def frieze(P, n):
        band = np.abs(P[:, 1] - ent_y) < 1.0
        tri = np.mod(P[:, 0] * 0.6, 1.0) < 0.5
        return np.where(band & tri, 'gold', ''), np.where(band, -0.5, 0.0)
    m.add(box((0, ent_y, depth * 0.2), (L / 2 + 4, 2.4, depth * 0.62), 0.2), 'stone', 0.0, decal=frieze)
    Hp = 9.0
    k = math.hypot(L / 2 + 5, Hp)
    def ped(P):
        x = np.abs(P[:, 0]); y = P[:, 1] - (ent_y + 2.4)
        tri = (x * Hp + y * (L / 2 + 5) - (L / 2 + 5) * Hp) / k
        return np.maximum(np.maximum(tri, -y), np.abs(P[:, 2] - depth * 0.2) - depth * 0.62)
    def ped_dec(P, n):
        front = n[:, 2] > 0.6
        inner = front & (np.abs(P[:, 0]) < (L / 2) * (1 - (P[:, 1] - ent_y - 2.4) / Hp)) & (P[:, 1] > ent_y + 3.4)
        return np.where(inner, 'tuff', ''), np.zeros(len(P))
    m.add(ped, 'stone', 0.0, decal=ped_dec)
    return m


def throne():
    m = Model()
    m.add(box((0, 5.0, 0), (4.2, 5.0, 3.6), 0.4), 'gold', 0.0)
    m.add(box((0, 13.0, -2.8), (4.2, 8.0, 0.8), 0.4), 'gold', 0.0)
    m.add(box((0, 10.4, 0.2), (3.4, 0.6, 3.0), 0.3), 'red', 0.0)
    for side in (-1, 1):
        m.add(sphere((side * 4.2, 21.6, -2.8), 1.0), 'gold', 0.0)
    return m


def brazier():
    m = Model()
    for k in range(3):
        a = k * 2 * math.pi / 3
        m.add(capsule((math.cos(a) * 2.6, 0, math.sin(a) * 2.6), (0, 7.0, 0), 0.4), 'bronze', 0.0)
    m.add(lambda P: np.maximum(sphere((0, 9.8, 0), 3.4)(P), P[:, 1] - 9.0), 'bronze', 0.0)
    return m


def gatehouse(w=34.0, tower_h=34.0, wall_h=24.0):
    m = Model()
    def tower(x):
        m.add(box((x, tower_h / 2, 0), (6.0, tower_h / 2, 6.0), 0.2), 'stone', 0.0, decal=courses(2.0, 4.0))
        for k in range(-1, 2):
            for side in (-1, 1):
                m.add(box((x + k * 4.0, tower_h + 1.4, side * 5.2), (1.3, 1.4, 0.8), 0.1), 'stone', 0.0)
                m.add(box((x + side * 5.2, tower_h + 1.4, k * 4.0), (0.8, 1.4, 1.3), 0.1), 'stone', 0.0)
        m.add(box((x, tower_h * 0.62, 6.1), (0.8, 2.0, 0.2), 0.1), 'dark', 0.0)                      # arrow slit
    tower(-w / 2); tower(w / 2)
    # arch over the gate with an opening
    arch_w = w / 2 - 6.0
    def arch(P):
        b = box((0, wall_h / 2 + 3, 0), (arch_w, wall_h / 2 + 3, 4.8), 0.1)(P)
        hole = np.maximum(np.hypot(P[:, 0], np.maximum(P[:, 1] - 12.0, 0)) - 7.2, -P[:, 1])
        return np.maximum(b, -hole)
    m.add(arch, 'stone', 0.0, decal=courses(2.0, 4.0))
    m.add(box((0, wall_h + 3.8, 0), (arch_w, 0.8, 5.2), 0.1), 'stone', 0.2)
    # open timber gate leaves swung inward
    for side in (-1, 1):
        m.add(box((side * 7.0, 9.0, -4.0 - 3.4), (0.6, 9.0, 3.4), 0.1), 'wood', 0.0,
              decal=lambda P, n: (None, np.where(np.mod(P[:, 2] * 0.7, 1.0) < 0.15, -1.5, 0.0)))
    # banner over the gate
    m.add(box((0, wall_h - 2.0, 5.0), (3.0, 4.6, 0.2), 0.1), 'red', 0.0,
          decal=lambda P, n: (np.where((np.abs(P[:, 0]) > 2.4) | (P[:, 1] < wall_h - 6.0) | (np.hypot(P[:, 0], P[:, 1] - wall_h + 1.6) < 1.2), 'gold', ''), np.zeros(len(P))))
    return m


def palisade(L=40.0, h=20.0):
    m = Model()
    def stakes(P):
        x = np.mod(P[:, 0], 2.2) - 1.1
        d = np.hypot(x, P[:, 2]) - 1.0
        top = P[:, 1] - (h - np.abs(x) * 1.6 + np.sin(np.floor(P[:, 0] / 2.2) * 2.3) * 0.8)
        return np.maximum(np.maximum(d, top), np.maximum(-P[:, 1], np.abs(P[:, 0] - L / 2) - L / 2))
    m.add(stakes, 'wood', 0.0, decal=lambda P, n: (None, np.where(np.mod(P[:, 1] * 0.35, 1) < 0.08, -1.5, 0.0)))
    m.add(box((L / 2, h * 0.55, 1.2), (L / 2, 0.5, 0.4), 0.1), 'wood', 0.0)
    m.add(box((L / 2, h * 0.25, 1.2), (L / 2, 0.5, 0.4), 0.1), 'wood', 0.0)
    return m


def granary(open_door=True):
    m = Model()
    W, D, H = 16.0, 10.0, 14.0
    def walls(P):
        b = box((0, H / 2 + 2, 0), (W, H / 2, D), 0.1)(P)
        door = box((0, 7.0, D), (3.6, 6.0, 2.0))(P)
        return np.maximum(b, -door) if open_door else b
    m.add(walls, 'tuff', 0.0, decal=courses(1.8, 3.6))
    m.add(box((0, 1.0, 0), (W + 1, 1.0, D + 1), 0.1), 'stone', 0.0)                                   # raised floor
    k = math.hypot(D + 2, 7.0)
    def roof(P):
        z = np.abs(P[:, 2]); y = P[:, 1] - (H + 2)
        tri = (z * 7.0 + y * (D + 2) - (D + 2) * 7.0) / k
        return np.maximum(np.maximum(tri, -y), np.abs(P[:, 0]) - W - 1.5)
    m.add(roof, 'terra', 0.0, decal=lambda P, n: (None, np.where(np.mod(P[:, 0] * 0.7, 1) < 0.2, -1.5, 0.0)))
    m.add(box((0, 7.0, D - 1.0), (3.5, 5.9, 0.5), 0.0), 'dark', 0.0)                                   # dark interior
    for (x, z) in ((-1.6, D - 1.6), (1.8, D - 2.2)):
        m.add(ellipsoid((x, 3.6, z), (1.6, 1.6, 1.4)), 'sack', 0.4)                                    # the last sacks
    return m


def watchtower():
    m = Model()
    m.add(cylinder_y((0, 22, 0), 6.0, 22), 'violet', 0.0, decal=courses(2.4, 3.0, -1.0))
    m.add(cylinder_y((0, 45, 0), 7.2, 1.2), 'violet', 0.2)
    k = math.hypot(7.4, 14.0)
    m.add(lambda P: np.maximum((np.hypot(P[:, 0], P[:, 2]) * 14.0 + (P[:, 1] - 46.0) * 7.4 - 7.4 * 14.0) / k, 46.0 - P[:, 1]), 'purple', 0.0,
          decal=lambda P, n: (None, np.where(np.mod(np.arctan2(P[:, 0], P[:, 2]) * 2.5, 1) < 0.15, -1.5, 0.0)))
    m.add(box((0, 33.0, 6.0), (1.5, 3.0, 0.4), 0.3), 'gold', 0.0)                                      # lit window
    m.add(box((0, 16.0, 6.0), (1.1, 2.2, 0.4), 0.3), 'gold', 0.0)
    m.add(box((0, 3.6, 6.0), (2.2, 3.6, 0.4), 0.3), 'dark', 0.0)
    for k2 in range(3):                                   # hanging sigils
        a = -0.6 + k2 * 0.6
        m.add(capsule((math.sin(a) * 7.2, 44, math.cos(a) * 7.2), (math.sin(a) * 7.4, 38, math.cos(a) * 7.4), 0.15), 'gold', 0.0)
        m.add(cylinder_z((math.sin(a) * 7.4, 37, math.cos(a) * 7.4), 1.0, 0.15), 'gold', 0.0)
    return m


def longship():
    m = Model()
    def hull(P):
        e = ellipsoid((0, 4.0, 0), (20.0, 6.0, 5.0))(P)
        return np.maximum(e, P[:, 1] - 4.6)
    def hull_dec(P, n):
        strakes = np.mod(P[:, 1] * 0.8, 1.0) < 0.2
        return None, np.where(strakes, -1.5, 0.0)
    m.add(hull, 'wood', 0.0, decal=hull_dec)
    m.add(capsule((18.0, 3.0, 0), (22.4, 10.6, 0), 0.9, 0.6), 'wood', 0.6)                            # prow
    m.add(ellipsoid((22.8, 11.4, 0), (1.6, 1.0, 0.7)), 'wood', 0.4)                                    # beast head
    m.add(capsule((-18.0, 3.0, 0), (-21.6, 9.4, 0), 0.9, 0.5), 'wood', 0.6)
    for k in range(-3, 4):                                                                              # shields on the rail
        m.add(cylinder_z((k * 4.6, 4.2, 5.0), 1.8, 0.25), ['blue', 'red', 'linen', 'blue', 'gold', 'red', 'blue'][k + 3], 0.0)
    m.add(capsule((0, 4.0, 0), (0, 26.0, 0), 0.5), 'wood', 0.0)
    m.add(box((0, 18.0, 0.6), (8.0, 6.4, 0.2), 0.2), 'linen', 0.0,
          decal=lambda P, n: (np.where(np.mod(P[:, 0] * 0.25, 1.0) < 0.5, 'red', ''), np.zeros(len(P))))
    return m


def plinth(empty=True):
    m = Model()
    m.add(box((0, 2.0, 0), (5.0, 2.0, 5.0), 0.3), 'stone', 0.0)
    m.add(box((0, 7.0, 0), (3.4, 3.0, 3.4), 0.3), 'stone', 0.0,
          decal=lambda P, n: (None, np.where((np.abs(P[:, 1] - 7.0) < 0.5) & (n[:, 2] > 0.5), -2.0, 0.0)))
    m.add(box((0, 10.6, 0), (4.0, 0.6, 4.0), 0.2), 'stone', 0.2)
    if empty:
        m.add(box((0, 11.3, 0), (1.6, 0.2, 1.0), 0.1), 'dark', 0.0)                                    # a clean rectangle where the horn sat
    return m


def stump(r=2.6, h=3.0):
    m = Model()
    m.add(capsule((0, 0, 0), (0, h, 0), r, r * 0.9), 'wood', 0.0,
          decal=lambda P, n: (np.where(P[:, 1] > h + r * 0.75, 'sack', ''), np.where(np.mod(np.hypot(P[:, 0], P[:, 2]) * 1.2, 1) < 0.25, -1.0, 0.0)))
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        m.add(capsule((math.cos(a) * r * 0.7, 0.8, math.sin(a) * r * 0.7), (math.cos(a) * (r + 2.2), 0.2, math.sin(a) * (r + 2.2)), 0.8, 0.3), 'wood', 0.8)
    return m


def logpile(n=5, L=16.0):
    m = Model()
    rows = [(0, 1.5), (3.1, 1.5), (1.55, 4.1)]
    for i in range(n):
        x, y = [(-3.1, 1.5), (0, 1.5), (3.1, 1.5), (-1.55, 4.1), (1.55, 4.1), (0, 6.7)][i]
        m.add(cylinder_z((x, y, 0), 1.5, L / 2), 'wood', 0.0,
              decal=lambda P, n: (np.where(np.abs(n[:, 2]) > 0.7, 'sack', ''), np.where(np.mod(np.hypot(P[:, 0] - np.round(P[:, 0] / 3.1) * 3.1, P[:, 1]) * 1.4, 1) < 0.25, -1.0, 0.0)))
    return m


def handcart():
    m = Model()
    m.add(box((0, 6.0, 0), (5.0, 1.8, 3.2), 0.3), 'wood', 0.0)
    for (x, z, r, mat) in ((-2.0, -1.0, 2.2, 'sack'), (1.6, 0.8, 2.0, 'linen'), (0.0, -0.6, 1.8, 'brown')):
        m.add(ellipsoid((x, 8.4 + r * 0.4, z), (r, r * 0.8, r * 0.9)), mat, 0.5)
    for z in (-3.6, 3.6):
        m.add(torus_z((0.4, 4.0, z), 3.4, 0.5), 'wood', 0.0)
    m.add(capsule((5.0, 6.6, -2.0), (10.0, 4.0, -2.0), 0.35), 'wood', 0.0)
    m.add(capsule((5.0, 6.6, 2.0), (10.0, 4.0, 2.0), 0.35), 'wood', 0.0)
    return m


def altar_stone():
    m = Model()
    m.add(box((0, 1.4, 0), (11.0, 1.4, 8.0), 0.3), 'stone', 0.0, decal=courses(1.4, 3.0))
    m.add(box((0, 4.2, 0), (8.6, 1.4, 6.0), 0.3), 'stone', 0.0, decal=courses(1.4, 3.0))
    m.add(box((0, 8.4, 0), (5.4, 2.8, 4.0), 0.3), 'stone', 0.0, decal=courses(1.4, 2.6))
    m.add(lambda P: np.maximum(sphere((0, 12.6, 0), 2.8)(P), P[:, 1] - 12.2), 'bronze', 0.0)
    return m
