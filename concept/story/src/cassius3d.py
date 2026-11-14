import numpy as np
from sdf import *


def band(P, axis, lo, hi):
    return (P[:, axis] > lo) & (P[:, axis] < hi)


def horse_rider(gait=0.0):
    m = Model()
    # ---------------- horse (head toward +x)
    def barrel_decal(P, n):
        x, y, z = P[:, 0], P[:, 1], P[:, 2]
        cloth = (np.abs(x + 0.5) < 6.2) & (y > 20.5)
        edge = cloth & ((np.abs(x + 0.5) > 5.3) | (y < 21.6))
        girth = (np.abs(x - 4.2) < 0.7) & ~cloth
        mm = np.where(edge, 'gold', np.where(cloth, 'red', np.where(girth, 'leather', '')))
        bias = np.where(cloth & (np.mod(x, 2.2) < 0.5), -1.0, 0.0)
        return mm, bias
    m.add(ellipsoid((0, 22.5, 0), (11.0, 6.0, 5.0)), 'horse', 0.0, decal=barrel_decal)
    def chest_decal(P, n):
        strap = np.abs(P[:, 1] - (21.5 + (P[:, 0] - 9) * 0.6)) < 0.6
        return np.where(strap & (P[:, 0] > 7.5), 'gold', ''), np.zeros(len(P))
    m.add(ellipsoid((8.6, 21.6, 0), (5.2, 6.0, 4.4)), 'horse', 2.2, decal=chest_decal)
    m.add(ellipsoid((-9.0, 23.3, 0), (6.2, 6.4, 5.0)), 'horse', 2.2)
    # legs: front pair at x~8.5, hind pair at x~-9.5 ; gait swings one front leg up
    lift = 0.6 + gait
    for side in (-1, 1):
        z = side * 2.5
        if side == 1:      # near front leg mid-stride (knee lifted forward)
            k = (11.4, 12.2, z); f = (10.6, 5.6, z); hf = (11.0, 4.6, z)
        else:
            k = (8.8, 9.6, z); f = (8.9, 2.6, z); hf = (9.2, 0.9, z)
        m.add(capsule((8.0, 18.0, z), k, 1.8, 1.0), 'horse', 1.2)
        m.add(capsule(k, f, 0.85, 0.65), 'horse', 0.3,
              decal=lambda P, n: (np.where(P[:, 1] < 4.6, 'linen', ''), np.zeros(len(P))))
        m.add(capsule(f, hf, 1.05, 1.1), 'mane', 0.2)
        # hind legs
        hk = (-11.2, 9.5, z) if side == 1 else (-10.5, 9.0, z)
        hfx = (-10.2, 2.6, z) if side == 1 else (-9.6, 2.4, z)
        m.add(capsule((-9.5, 20.0, z), (-11.0, 13.5, z), 2.3, 1.3), 'horse', 1.4)
        m.add(capsule((-11.0, 13.5, z), hk, 1.15, 0.8), 'horse', 0.4)
        m.add(capsule(hk, hfx, 0.8, 0.65), 'horse', 0.3)
        m.add(capsule(hfx, (hfx[0] + 0.4, 0.8, z), 1.05, 1.1), 'mane', 0.2)
    # neck, head, muzzle, ears, eye
    m.add(capsule((10.0, 25.5, 0), (15.6, 35.5, 0), 3.5, 2.1), 'horse', 2.0)
    def head_decal(P, n):
        x, y, z = P[:, 0], P[:, 1], P[:, 2]
        bridle = (np.abs(x - 17.0) < 0.45) | (np.abs(y - (31.2 + (x - 20.5) * -0.35)) < 0.4)
        eye = (np.abs(x - 17.8) < 0.6) & (np.abs(y - 35.2) < 0.55) & (np.abs(z) > 1.2)
        mm = np.where(bridle, 'gold', '')
        return mm, np.where(eye, -5.0, 0.0)
    m.add(capsule((15.8, 36.4, 0), (22.6, 30.4, 0), 2.1, 1.35), 'horse', 0.8, decal=head_decal)
    m.add(ellipsoid((17.2, 34.0, 0), (2.5, 2.4, 1.8)), 'horse', 0.8)
    m.add(sphere((22.8, 30.2, 0), 1.35), 'horse', 0.6,
          decal=lambda P, n: (None, np.where((P[:, 0] > 23.4) & (np.abs(P[:, 2]) > 0.4), -3.0, -0.5)))
    for side in (-1, 1):
        m.add(capsule((15.4, 38.4, side * 0.9), (14.8, 41.0, side * 1.0), 0.6, 0.15), 'horse', 0.2)
    # mane, forelock, tail
    m.add(capsule((9.4, 29.2, 0), (15.0, 38.6, 0), 1.25, 0.9), 'mane', 0.4,
          decal=lambda P, n: (None, np.where(np.mod(P[:, 0] * 1.6, 1.0) < 0.35, -1.0, 0.0)))
    m.add(capsule((-14.6, 26.0, 0), (-17.4, 18.0, 0.4), 1.7, 1.4), 'mane', 0.8)
    m.add(capsule((-17.4, 18.0, 0.4), (-16.2, 10.0, 0.6), 1.4, 0.7), 'mane', 0.4)
    # ---------------- rider (faces +x)
    hipx = -0.6
    for side in (-1, 1):
        z = side * 3.1
        knee = (hipx + 4.2, 25.6, side * 5.6)
        ank = (hipx + 3.2, 19.0, side * 5.8)
        m.add(capsule((hipx, 29.4, z), knee, 1.7, 1.45), 'red', 0.5)
        m.add(capsule(knee, ank, 1.3, 1.0), 'skin', 0.3,
              decal=lambda P, n: (np.where(P[:, 1] < 22.6, 'leather', ''), np.where((P[:, 1] < 22.6) & (np.mod(P[:, 1] * 1.4, 1) < 0.35), -1.0, 0.0)))
        m.add(capsule(ank, (ank[0] + 1.8, 18.2, ank[2]), 0.9), 'leather', 0.3)
    # pteruges skirt over the saddle
    m.add(capsule((hipx, 31.0, 0), (hipx, 28.6, 0), 3.5, 4.0), 'leather', 0.6,
          decal=lambda P, n: (None, np.where(np.mod(np.arctan2(P[:, 2], P[:, 0]) * 4.0, 1.0) < 0.4, -1.5, 0.3)))
    # gilded muscle cuirass with a red cincture
    def cuirass_decal(P, n):
        x, y, z = P[:, 0], P[:, 1], P[:, 2]
        sash = np.abs(y - 33.0) < 0.5
        pec = (np.abs(y - 36.4) < 0.35) & (x > 1.2)
        mm = np.where(sash, 'red', '')
        return mm, np.where(pec, -1.5, 0.0)
    m.add(ellipsoid((hipx + 0.4, 36.0, 0), (3.2, 4.4, 3.5)), 'gold', 0.8, decal=cuirass_decal)
    for side in (-1, 1):
        m.add(ellipsoid((hipx + 0.2, 38.6, side * 3.2), (1.8, 1.4, 1.6)), 'gold', 0.4)
    # cloak hanging off the shoulders, back over the horse
    m.add(capsule((hipx - 2.0, 38.6, 0), (hipx - 6.8, 29.6, 0), 2.2, 3.6), 'red', 0.8,
          decal=lambda P, n: (None, np.where(np.mod(P[:, 2] * 0.9 + P[:, 1] * 0.2, 1.0) < 0.3, -1.0, 0.0)))
    # arms reaching for the reins
    for side in (-1, 1):
        sh = (hipx + 0.4, 38.0, side * 3.5)
        el = (hipx + 2.6, 34.4, side * 3.9)
        ha = (hipx + 5.8, 32.6, side * 1.6)
        m.add(capsule(sh, el, 1.2, 1.0), 'skin', 0.4)
        m.add(capsule(el, ha, 1.0, 0.85), 'skin', 0.3)
        m.add(capsule(ha, (12.8, 30.6, side * 1.2), 0.25), 'leather', 0.0)      # reins
    # neck, head, helmet with cheek guards and a sweeping red plume
    m.add(capsule((hipx + 0.6, 39.6, 0), (hipx + 0.9, 41.0, 0), 1.2), 'skin', 0.4)
    m.add(sphere((hipx + 1.0, 42.5, 0), 2.55), 'skin', 0.0,
          decal=lambda P, n: (None, np.where((np.abs(P[:, 1] - 42.9) < 0.5) & (P[:, 0] > hipx + 2.4) & (np.abs(P[:, 2]) > 0.4), -4.0, 0.0)))
    hb = sphere((hipx + 0.6, 43.9, -0.1), 2.65)
    m.add(lambda P: np.maximum(hb(P), 44.1 - P[:, 1]), 'steel', 0.0)
    m.add(capsule((hipx - 1.6, 44.1, 0), (hipx + 3.0, 44.1, 0), 0.4), 'gold', 0.0)
    m.add(ellipsoid((hipx - 0.4, 47.0, 0), (3.6, 1.7, 0.9)), 'red', 0.5,
          decal=lambda P, n: (None, np.where(np.mod(P[:, 0] * 1.4, 1.0) < 0.35, -1.0, 0.0)))
    m.add(capsule((hipx - 3.0, 46.6, 0), (hipx - 5.2, 44.0, 0), 1.0, 0.5), 'red', 0.6)
    return m


if __name__ == '__main__':
    import sys
    from PIL import Image
    yaw = float(sys.argv[1]) if len(sys.argv) > 1 else -35
    mdl = horse_rider()
    mi, ti, dims = render(mdl, (52, 70), scale=1.32, ss=6, yaw=yaw, pitch=14, origin=(1.0, -1.5))
    px = pixelise(mi, ti, dims)
    a = save(px, '/tmp/cas3d.png')
    leg = Image.open('/tmp/leg3d.png')
    ref = Image.open('/mnt/user-data/uploads/48e145ba-image.png').convert('RGBA').crop((24, 14, 63, 79))
    s = 8
    ims = [leg, a, ref]
    Wt = sum(i.width * s + 40 for i in ims); Ht = max(i.height for i in ims) * s + 20
    out = Image.new('RGB', (Wt, Ht), (92, 98, 84))
    x = 10
    for i in ims:
        b = i.resize((i.width * s, i.height * s), Image.NEAREST)
        out.paste(b, (x, Ht - 10 - b.height), b); x += b.width + 40
    out.save('/tmp/cas3d_cmp.png')
