"""Frame 2: the Thorn Woods at misty dawn. An old river altar; the forest is watching."""
import math, random
import numpy as np
from PIL import Image
from kit import *
import sprites as S
from ground import build_ground
from hud import hud, text

sc = Scene(seed=22)
rng = random.Random(22)
sc.sun = (-0.9, 0.5)               # dawn from the east: shadows fall west
road_c = lambda x: 150 + 6 * np.sin(x / 70) - 0.06 * (x - 240)
bank = lambda x: 226 + 3 * np.sin(x / 40) - 0.08 * (x - 240)

GR = [C('14281e'), C('1e3a24'), C('2c4e2a'), C('3e6630'), C('5c8238'), C('86a446')]
DIRT = [C('2a2418'), C('3e3624'), C('544a30'), C('6e623c')]
yy, xx = build_ground(sc, road_c, bank, GR, DIRT, 22, road_w=15, blades=6500, blade_tint=C('b0d070'),
                      flowers=[C('e8e8f0'), C('f0d070'), C('a0c0f0')], edge_col=C('2e5226'))
# moss and roots creeping onto the path
for i in range(90):
    x = rng.randint(0, W - 8); y = int(road_c(x) + rng.choice([-1, 1]) * rng.uniform(8, 14))
    for k in range(rng.randint(4, 12)):
        xx2 = x + k; yy2 = int(y + math.sin(k * 0.8) * 1.5)
        if 0 <= yy2 < H and xx2 < W:
            sc.alb[yy2, xx2] = rng.choice([C('3a2a1e'), C('4a3624'), C('2e5226')])

P_OAK = [C('0c1e14'), C('16301c'), C('224424'), C('345e2c'), C('5a8838')]
P_BIRCH = [C('1a2e14'), C('2a4a1c'), C('44682a'), C('6e9438'), C('a8c050')]
BARK = [C('1c1612'), C('34281e'), C('54402e')]

# deep wood along the top: three rows of big oaks
for row, ybase in enumerate((56, 78, 98)):
    x = -20 + row * 13
    while x < W + 30:
        if row == 2 and 150 < x < 300:
            x += 40
            continue
        R = rng.randint(17, 24) - row * 2
        if rng.random() < 0.3:
            sc.add(S.birch(rng.randint(0, 999), P_BIRCH, h=rng.randint(64, 80)), x, ybase + rng.randint(-4, 4))
        else:
            sc.add(S.oak(rng.randint(0, 999), P_OAK, BARK, R=R), x, ybase + rng.randint(-4, 4))
        x += rng.randint(26, 40)
# near-side trees framing the bottom corners
sc.add(S.oak(901, P_OAK, BARK, R=22), 24, 214)
sc.add(S.birch(902, P_BIRCH, h=86), 452, 200)
# ferns & mushrooms
FERN = [C('1a3418'), C('3a6a28'), C('7aa848')]
for i in range(70):
    x = rng.randint(0, W - 1); y = rng.randint(80, 220)
    if abs(y - road_c(x)) < 20 or y > bank(x) - 4:
        continue
    sc.add(S.tuft(rng.randint(0, 999), FERN, h=rng.randint(5, 8)), x, y, cast=False)
for i in range(18):
    x = rng.randint(0, W - 3); y = rng.randint(100, 210)
    if abs(y - road_c(x)) < 18 or y > bank(x) - 4:
        continue
    m = rgba(3, 3); put(m, 0, 0, C('e04030')); put(m, 1, 0, C('ff6050')); put(m, 2, 0, C('c03020')); put(m, 1, 1, C('e8e0d0')); put(m, 1, 2, C('d0c8b8'))
    sc.add(m, x, y, cast=False)

# the altar in a clearing
alt, alt_e = S.altar(2)
sc.add(alt, 228, 122, emissive=alt_e)
sc.light(228, 100, 70, (1.0, 0.56, 0.24), 0.6)
sc.add(S.priest(), 266, 123)
sc.add(S.column(30, broken=True), 186, 118)
sc.add(S.column(36), 290, 112)
sc.add(S.rock(14, 9, 2, pal=[C('263028'), C('3e4a40'), C('5e6a5a'), C('8a9478')]), 200, 124)
# Thorncrown totems at the treeline, and eyes in the dark
for (x, y) in ((120, 112), (340, 108), (402, 120)):
    sc.add(S.totem(), x, y)
for (x, y) in ((96, 92), (370, 88), (430, 100), (60, 104)):
    e, ee = S.goblin_eyes()
    sc.add(e, x, y, emissive=ee, cast=False, depth=999)

# the column arriving from the west, small
col = [(S.cassius(2), 146, 2)]
for i, x in enumerate(range(118, 36, -14)):
    col.append((S.legionary(i % 4), x, -4 if i % 2 else 5))
col.append((S.ox(2), 30, 4))
for a, x, off in col:
    sc.add(a, x, road_c(x) + off)

REED = [C('1c3018'), C('3a5a28'), C('86a050')]
for i in range(60):
    x = rng.randint(0, W - 1)
    sc.add(S.reeds(rng.randint(0, 999), REED, h=rng.randint(6, 11)), x, bank(x) + 1, cast=False)

sc.compose_items()

amb = C('3a5a78') * 0.62
sun = C('ffe0b0') * 0.62
img = sc.lit(amb, sun, shadow_strength=0.7)
img = sc.glow(img, 228, 104, 36, (1.0, 0.6, 0.25), 0.14)
for (x, y) in ((96, 92), (370, 88), (430, 100), (60, 104)):
    img = sc.glow(img, x + 3, y - 1, 6, (1.0, 0.8, 0.3), 0.25, bands=3)
sky = lambda x, y: C('9ab8c8') * 0.7 + C('f0c0a0') * 0.3 * (x / W)
img = reflect(img, bank, C('2a4858'), refl_amt=0.4, depth_fade=0.6, sky=sky)
# god rays slanting from the east through the canopy
ray = np.sin((xx * -0.75 + yy) * 0.07 + np.sin(xx * 0.01) * 2) * 0.5 + 0.5
ray = np.clip((ray - 0.62) * 2.6, 0, 1) * np.clip((yy - 20) / 60, 0, 1) * 0.13
img = img + C('fff0c8')[None, None, :] * band(ray, 4, dither=False)[:, :, None]
img = fog(img, C('b8ccd8'), 0.36, 70, 175, seed=31)
img = fog(img, C('d0dce4'), 0.3, 185, 260, seed=32)
r2 = random.Random(8)
for i in range(70):                          # pollen motes in the light
    x, y = r2.randint(0, W - 1), r2.randint(24, 245)
    img[y, x] = img[y, x] * 0.4 + C('fff4d0') * 0.7
img = grade(img, C('10243a'), gamma=1.0, sat=1.05, vignette=0.6, contrast=1.12)
im = to_image(img, colors=0)
im = hud(im, [('coin', '58', (240, 200, 110)), ('grain', '61 / 120 grain  (-9 a day)', (230, 214, 168)), ('', '64 men', (230, 214, 168)), ('', 'offerings 2/3', (230, 214, 168))],
         'WASD ride    Shift gallop    F interact    I pack    L ledger    M map', 'Day 2   Leg 2 of 5   Thorncrown Tribes')
text(im, (228, 68), '[F] The altar', col=(255, 242, 210), center=True)
im.save('frame2_forest.png')
im.resize((W * 4, H * 4), Image.NEAREST).save('frame2_forest_4x.png')
