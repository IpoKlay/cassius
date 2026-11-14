"""Frame 3: the Fjord Road at night. Frostbay's oath-stone; their shield-wall bars the road."""
import math, random
import numpy as np
from PIL import Image
from kit import *
import sprites as S
from ground import build_ground
from hud import hud, text

sc = Scene(seed=33)
rng = random.Random(33)
sc.sun = (0.55, 0.45)              # high cold moon
road_c = lambda x: 150 - 0.1 * (x - 240)
bank = lambda x: 222 - 0.1 * (x - 240)

SN = [C('5a6a8a'), C('7486a8'), C('92a4c4'), C('b4c4dc'), C('d4e0f0')]
TRACK = [C('3e4a62'), C('56627e'), C('6e7c98'), C('8a98b2')]
yy, xx = build_ground(sc, road_c, bank, SN, TRACK, 33, road_w=18, blades=0, stones=False, edge_col=C('a8b8d0'))
# sparkle in the snow
for i in range(900):
    x, y = rng.randint(0, W - 1), rng.randint(20, H - 1)
    if y < bank(x) - 1:
        sc.alb[y, x] = C('ffffff') if rng.random() < 0.5 else C('dce8ff')
# boot and hoof prints along the road
for i in range(220):
    x = rng.randint(0, W - 2); y = int(road_c(x) + rng.uniform(-12, 12))
    sc.alb[y, x] = TRACK[0]; sc.alb[y, x + 1] = TRACK[1]
# dead grass poking through
for i in range(160):
    x = rng.randint(0, W - 1); y = rng.randint(30, H - 1)
    if abs(y - road_c(x)) < 20 or y > bank(x) - 3:
        continue
    sc.add(S.tuft(rng.randint(0, 999), [C('4a4a3a'), C('7a7458'), C('a89c78')], n=3, h=4), x, y, cast=False)

# pine forest heavy with snow
for row, ybase in enumerate((54, 76, 98)):
    x = -16 + row * 11
    while x < W + 20:
        if row == 2 and 190 < x < 300:
            x += 30
            continue
        sc.add(S.snow_pine(rng.randint(0, 999), h=rng.randint(56, 74) - row * 4), x, ybase + rng.randint(-5, 5))
        x += rng.randint(16, 28)
sc.add(S.snow_pine(77, h=84), 458, 236)
sc.add(S.snow_pine(78, h=78), 16, 244)

# the oath-stone and its fire
rs, rs_e = S.runestone(True)
sc.add(rs, 246, 122, emissive=rs_e)
sc.light(246, 102, 46, (0.35, 0.65, 1.0), 0.5)
fire, fire_e = S.campfire(5)
sc.add(fire, 214, 126, emissive=fire_e, cast=False)
sc.light(214, 118, 56, (1.0, 0.55, 0.25), 0.9)
for (x, y) in ((196, 118), (232, 110), (268, 116)):
    sc.add(S.rock(12, 8, x, pal=[C('2a2c38'), C('44485a'), C('62687e'), C('e8f0ff')]), x, y)

# Frostbay shield-wall across the road, east side
for i, off in enumerate((-22, -8, 6, 20)):
    x = 372 + (7 if i % 2 else 0)
    sc.add(S.flip(S.northman(i % 4, torch=(i in (0, 3)))), x, road_c(x) + off)
for i, off in enumerate((-15, -1, 13)):
    x = 398 + (6 if i % 2 else 0)
    sc.add(S.flip(S.northman(i % 4)), x, road_c(x) + off)
for (x, off) in ((372, -22), (379, 20)):
    fl, fe = S.torch_flame(2)
    sc.add(fl, x - 7, road_c(x) + off - 16, emissive=fe, cast=False, depth=road_c(x) + off + 1)
    sc.light(x - 7, road_c(x) + off - 18, 50, (1.0, 0.6, 0.28), 0.9)

# the column, halted, torches lit
col = [(S.cassius(0), 300, 1)]
for i, x in enumerate(range(270, 150, -15)):
    col.append((S.legionary(0, torch=(i % 3 == 0)), x, -5 if i % 2 else 6))
col.append((S.legionary(0, carry='vexillum'), 284, -8))
col.append((S.ox(0), 132, 4))
col.append((S.cart(0), 96, 5))
for a, x, off in col:
    sc.add(a, x, road_c(x) + off)
for i, x in enumerate(range(270, 150, -15)):
    if i % 3 == 0:
        off = -5 if i % 2 else 6
        fl, fe = S.torch_flame(i)
        sc.add(fl, x + 5, road_c(x) + off - 21, emissive=fe, cast=False, depth=road_c(x) + off + 1)
        sc.light(x + 5, road_c(x) + off - 22, 44, (1.0, 0.58, 0.26), 0.8)
sc.light(112, road_c(112) - 10, 26, (1.0, 0.7, 0.3), 0.5)

sc.compose_items()

amb = C('2a3a6a') * 0.75
moon = C('8aa4d8') * 0.55
img = sc.lit(amb, moon, shadow_strength=0.75)
for (x, y, r, c, s) in sc.lights:
    if c[0] > 0.9:
        img = sc.glow(img, x, y, 12, (1.0, 0.65, 0.3), 0.25, bands=3)
img = sc.glow(img, 246, 104, 22, (0.4, 0.75, 1.0), 0.18, bands=4)
# frozen river: pale ice with dark cracks, little reflection
ice = lambda x, y: C('3a4c72') + C('8aa0c8') * 0.25 * (0.5 + 0.5 * math.sin(x * 0.03 + y * 0.11))
img = reflect(img, bank, C('34466a'), refl_amt=0.18, depth_fade=0.8, sky=ice)
for i in range(26):                              # cracks
    x, y = rng.randint(0, W - 20), rng.randint(int(bank(240)) + 4, H - 4)
    if y <= bank(x) + 2:
        continue
    for k in range(rng.randint(6, 18)):
        x += 1; y += rng.choice([-1, 0, 0, 1])
        if 0 <= x < W and bank(x) + 2 < y < H:
            img[y, x] = img[y, x] * 0.55
            if 0 <= y - 1:
                img[y - 1, x] = img[y - 1, x] * 0.9 + C('c8d8f0') * 0.15
img = fog(img, C('8098c8'), 0.25, 40, 120, seed=41)
# falling snow (with motion streaks), denser near the camera
r2 = random.Random(9)
for i in range(520):
    x, y = r2.randint(0, W - 2), r2.randint(20, 249)
    big = r2.random() < 0.18
    img[y, x] = img[y, x] * 0.25 + C('f4f8ff') * 0.9
    if big:
        img[y, x + 1] = img[y, x + 1] * 0.3 + C('f4f8ff') * 0.8
        if y + 1 < H:
            img[y + 1, x] = img[y + 1, x] * 0.5 + C('dce6ff') * 0.5
img = grade(img, C('0c1430'), gamma=1.05, sat=1.05, vignette=0.6, contrast=1.12)
im = to_image(img, colors=0)
im = hud(im, [('coin', '31', (240, 200, 110)), ('grain', '38 / 120 grain  (-9 a day)', (230, 120, 100)), ('', '67 men', (230, 214, 168)), ('', 'offerings 3/3', (230, 214, 168))],
         'WASD ride    Shift gallop    F interact    I pack    L ledger    M map', 'Day 3   Leg 3 of 5   Frostbay Clans')
text(im, (380, 92), '[F] Speak', col=(255, 242, 210), center=True)
im.save('frame3_snow.png')
im.resize((W * 4, H * 4), Image.NEAREST).save('frame3_snow_4x.png')
