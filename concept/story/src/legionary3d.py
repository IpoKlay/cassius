import numpy as np
from sdf import *


def legionary_model(stride=0.0):
    m = Model()
    # legs (stride swings them along z)
    for side, sw in ((-1, stride), (1, -stride)):
        hip = (side * 2.0, 17.0, 0.0)
        knee = (side * 2.2, 9.5, 0.6 + sw)
        ankle = (side * 2.2, 2.0, 0.2 + sw * 1.6)
        m.add(capsule(hip, knee, 1.75, 1.45), 'skin', 0.6)
        m.add(capsule(knee, ankle, 1.45, 1.05), 'skin', 0.4,
              decal=lambda P, n: (np.where(P[:, 1] < 4.6, 'leather', ''), np.where((P[:, 1] < 4.6) & (np.round(P[:, 1] * 1.3) % 2 == 0), -1.0, 0.0)))
        m.add(box((side * 2.2, 0.8, 1.0 + sw * 1.6), (1.2, 0.8, 2.0), 0.6), 'leather', 0.3)
    # tunic skirt flaring out, with pteruges strips over it
    m.add(capsule((0, 21.0, 0), (0, 14.2, 0.1), 4.3, 4.6), 'red', 0.5,
          decal=lambda P, n: (np.where(P[:, 1] > 17.6, np.where((np.round(np.arctan2(P[:, 0], P[:, 2]) * 4.5) % 2) == 0, 'leather', ''), ''),
                              np.where(P[:, 1] < 14.8, -1.5, 0.0)))
    # belt with bronze studs
    m.add(capsule((-4.9, 21.3, 0.4), (4.9, 21.3, 0.4), 0.85), 'leather', 0.6,
          decal=lambda P, n: (np.where(np.round(P[:, 0] * 0.9) % 2 == 0, 'bronze', ''), np.zeros(len(P))))
    # apron straps hanging at the front
    for x in (-1.0, 0.0, 1.0):
        m.add(capsule((x, 20.8, 4.6), (x, 15.2, 5.3), 0.45), 'leather', 0.0,
              decal=lambda P, n: (np.where(np.round(P[:, 1] * 0.8) % 2 == 0, 'bronze', ''), np.zeros(len(P))))
    # torso: lorica segmentata as banded steel
    m.add(ellipsoid((0, 25.8, 0), (5.1, 5.2, 3.6)), 'steel', 0.8,
          decal=lambda P, n: (None, np.where((np.mod(P[:, 1] - 21.0, 2.1) < 0.75), -2.5, 0.0)))
    # shoulder guards (stacked curved plates)
    for side in (-1, 1):
        m.add(ellipsoid((side * 4.9, 29.0, 0), (2.8, 2.2, 3.2)), 'steel', 0.6,
              decal=lambda P, n: (None, np.where(np.mod(P[:, 1] - 27.0, 1.3) < 0.35, -2.0, 0.0)))
    # neck + scarf
    m.add(capsule((0, 30.0, 0), (0, 32.4, 0.3), 1.5), 'skin', 0.5)
    m.add(capsule((-2.2, 30.4, 0.6), (2.2, 30.4, 0.6), 1.0), 'linen', 0.4)
    # head
    m.add(sphere((0, 34.6, 0.4), 2.75), 'skin', 0.0,
          decal=lambda P, n: (None, np.where((P[:, 1] > 34.4) & (P[:, 1] < 35.2) & (np.abs(np.abs(P[:, 0]) - 1.05) < 0.45) & (P[:, 2] > 2.2), -4.0, 0.0)))
    m.add(sphere((0, 34.0, 3.0), 0.75), 'skin', 0.3)                                   # nose
    # helmet: bowl, brow ridge, cheek guards, neck guard, crest
    bowl = sphere((0, 35.7, -0.4), 3.15)
    m.add(lambda P: np.maximum(bowl(P), 35.7 - P[:, 1]), 'steel', 0.0)
    m.add(capsule((-3.0, 35.8, 1.0), (3.0, 35.8, 1.0), 0.5), 'bronze', 0.2)
    for side in (-1, 1):
        m.add(box((side * 2.75, 33.4, 0.2), (0.3, 1.5, 1.1), 0.25), 'steel', 0.15)
    m.add(box((0, 34.0, -2.9), (3.0, 0.8, 0.8), 0.4), 'steel', 0.4)
    m.add(ellipsoid((0, 39.2, -0.4), (0.95, 1.7, 3.5)), 'red', 0.4,
          decal=lambda P, n: (None, np.where(np.mod(P[:, 2] * 2.0, 1.0) < 0.3, -1.0, 0.0)))
    # right arm (viewer's left) holding the pilum
    sh_r, el_r, ha_r = (-5.6, 28.4, 0.2), (-7.4, 23.4, 1.2), (-8.2, 20.4, 2.6)
    m.add(capsule(sh_r, el_r, 1.45, 1.25), 'red', 0.4)
    m.add(capsule(el_r, ha_r, 1.2, 1.0), 'skin', 0.3)
    m.add(sphere(ha_r, 1.2), 'skin', 0.3)
    m.add(capsule((-8.4, 0.3, 2.7), (-8.4, 41.5, 2.7), 0.42), 'wood', 0.0,
          decal=lambda P, n: (np.where(P[:, 1] > 34.0, 'iron', ''), np.zeros(len(P))))
    m.add(capsule((-8.4, 41.0, 2.7), (-8.4, 43.8, 2.7), 0.5, 0.05), 'iron', 0.0)
    # left arm behind the shield
    m.add(capsule((5.6, 28.4, 0.2), (6.8, 23.4, 2.4), 1.45, 1.25), 'red', 0.4)
    # scutum: curved, painted, gold rim, bronze boss, thunderbolt wings
    sc_c = (5.0, 19.0, -6.6)
    def shield_decal(P, n):
        q = P - np.array(sc_c)
        ang = np.arctan2(q[:, 0], q[:, 2]) * 10.8
        y = q[:, 1]
        rim = (np.abs(ang) > 4.2) | (np.abs(y) > 8.9)
        wings = ((np.abs(np.abs(y) - 4.6 + np.abs(ang) * 0.45) < 0.55) & (np.abs(ang) < 4.5)) | ((np.abs(ang) < 0.5) & (np.abs(y) > 2.5) & (np.abs(y) < 9))
        mm = np.where(rim | wings, 'gold', '')
        back = n[:, 2] < -0.2
        mm = np.where(back, 'leather', mm)
        return mm, np.zeros(len(P))
    m.add(cyl_shell(sc_c, 10.8, 0.5, 9.6, 0.43), 'red', 0.0, decal=shield_decal)
    bx = sc_c[0] + 10.8 * np.sin(0.0); bz = sc_c[2] + 10.8 * np.cos(0.0)
    m.add(sphere((sc_c[0], sc_c[1], sc_c[2] + 11.4), 1.6), 'bronze', 0.0)
    return m


if __name__ == '__main__':
    import sys
    mdl = legionary_model(0.0)
    mi, ti, dims = render(mdl, (40, 60), scale=1.25, ss=6, yaw=32, pitch=16, origin=(0.5, -1.0))
    px = pixelise(mi, ti, dims)
    save(px, '/tmp/leg3d.png')
    from PIL import Image
    ref = Image.open('/mnt/user-data/uploads/48e145ba-image.png').convert('RGBA').crop((24, 14, 63, 79))
    a = Image.open('/tmp/leg3d.png')
    s = 10
    out = Image.new('RGB', (a.width * s + ref.width * s + 60, ref.height * s + 20), (92, 98, 84))
    out.paste(a.resize((a.width * s, a.height * s), Image.NEAREST), (10, out.height - 10 - a.height * s), a.resize((a.width * s, a.height * s), Image.NEAREST))
    out.paste(ref.resize((ref.width * s, ref.height * s), Image.NEAREST), (a.width * s + 40, 10), ref.resize((ref.width * s, ref.height * s), Image.NEAREST))
    out.save('/tmp/leg3d_cmp.png')
