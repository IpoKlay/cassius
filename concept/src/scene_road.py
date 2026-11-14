"""Frame 1: the Imperial Road at golden dusk. Camp, the column, the river."""
import math, random
import numpy as np
from PIL import Image
from kit import *
import sprites as S
from hud import hud, text

sc = Scene(seed=11)
rng = random.Random(11)
sc.sun = (1.55, 0.32)          # low sun from the west: long shadows to the east

road_c = lambda x: 146 - 0.13 * (x - 240)
bank = lambda x: 214 - 0.13 * (x - 240)

# ----------------------------------------------------------------- ground
yy, xx = np.mgrid[0:H, 0:W]
n1 = fbm(W, H, 3)
n2 = fbm(W, H, 9, cells=(16, 8, 4), wts=(0.5, 0.3, 0.2))
GR = [C('1e3014'), C('2e4618'), C('42601e'), C('5e7a26'), C('869032'), C('b8a844')]
DIRT = [C('3e2c22'), C('5a4030'), C('7a5a40'), C('9a7652'), C('b89468')]
rc = road_c(xx)
dist = np.abs(yy - rc)
edge = 22 + (n2 - 0.5) * 8
is_road = dist < edge
g = band(np.clip(n1 * 1.0 + n2 * 0.15 - 0.08, 0, 0.999), 6, dither=False)
sc.alb[:] = np.array(GR)[np.clip((g * len(GR)).astype(int), 0, len(GR) - 1)]
# dry golden grass toward the bank
dryness = np.clip((yy - rc) / 60, 0, 1)
sc.alb = sc.alb * (1 - dryness[:, :, None] * 0.25) + C('8a7a3a')[None, None, :] * dryness[:, :, None] * 0.25
d = band(np.clip(n1 * 0.7 + n2 * 0.3, 0, 0.999), 5, dither=False)
road_col = np.array(DIRT)[np.clip((d * len(DIRT)).astype(int), 0, len(DIRT) - 1)]
sc.alb[is_road] = road_col[is_road]
# wheel ruts + worn centre
for off in (-8, 8):
    m = (np.abs(yy - (rc + off)) < 1.2) & is_road
    sc.alb[m] = sc.alb[m] * 0.62
    m2 = (np.abs(yy - (rc + off - 1.5)) < 0.6) & is_road
    sc.alb[m2] = sc.alb[m2] * 1.12
# road edge: grass encroaching
em = (np.abs(dist - edge) < 1.5) & (n2 > 0.45)
sc.alb[em] = C('4a5420')
# paving stones peeking through (old imperial road)
for i in range(70):
    x = rng.randint(0, W - 6); y = int(road_c(x) + rng.uniform(-14, 14))
    w = rng.randint(3, 6)
    sc.alb[y:y + 2, x:x + w] = C('8a8078'); sc.alb[y, x:x + w] = C('aca298'); sc.alb[y + 2, x:x + w] = C('4a4038')
# pebbles
for i in range(260):
    x = rng.randint(0, W - 2); y = int(road_c(x) + rng.uniform(-20, 20))
    if 0 <= y < H - 1:
        sc.alb[y, x] = C('c0a888'); sc.alb[y + 1, x] = C('4a3a2e')
# grass blades
for i in range(5200):
    x = rng.randint(0, W - 1); y = rng.randint(14, H - 1)
    if abs(y - road_c(x)) < 21 or y > bank(x) - 1:
        continue
    hgt = rng.randint(1, 4)
    base = sc.alb[y, x]
    for k in range(hgt):
        if y - k >= 0:
            sc.alb[y - k, x] = base * (0.75 + 0.18 * k) + C('d8c060') * 0.06 * k
# wildflowers
for i in range(160):
    x = rng.randint(0, W - 1); y = rng.randint(30, H - 1)
    if abs(y - road_c(x)) < 24 or y > bank(x) - 2:
        continue
    sc.alb[y, x] = rng.choice([C('e8d070'), C('e09060'), C('f0f0e0'), C('c070a0')])

# ----------------------------------------------------------------- props: far trees along the top
P_PINE = [C('142010'), C('22381a'), C('3a5a22'), C('6a8a2c'), C('b8b048')]
P_CYP = [C('0e1a10'), C('1a3018'), C('2e5022'), C('6a8830')]
BARK = [C('2a1c16'), C('4a3326'), C('6e5040')]
x = -10
while x < W + 20:
    kind = rng.random()
    y = rng.randint(64, 84)
    if kind < 0.45:
        sc.add(S.stone_pine(rng.randint(0, 999), P_PINE, BARK, h=rng.randint(70, 92)), x, y)
        x += rng.randint(34, 54)
    else:
        sc.add(S.cypress(rng.randint(0, 999), P_CYP, h=rng.randint(52, 74)), x, y)
        x += rng.randint(12, 22)
# second row, nearer
for x in (14, 300, 420):
    sc.add(S.cypress(rng.randint(0, 999), P_CYP, h=rng.randint(60, 76)), x, rng.randint(92, 100))
sc.add(S.stone_pine(42, P_PINE, BARK, h=96), 470, 112)
sc.add(S.stone_pine(43, P_PINE, BARK, h=88), 352, 100)

# ----------------------------------------------------------------- the camp (north of the road)
sc.add(S.tent(42, 28), 92, 104)
sc.add(S.tent(34, 24), 150, 92)
sc.add(S.tent(34, 24), 40, 92)
fire, fire_e = S.campfire(3)
sc.add(fire, 150, 120, emissive=fire_e, cast=False)
sc.light(150, 114, 52, (1.0, 0.5, 0.2), 0.42)
for (x, y, f) in ((136, 118, False), (164, 121, True), (148, 127, False)):
    s = S.sitter()
    sc.add(S.flip(s) if f else s, x, y)
sc.add(S.standard(1), 190, 112)
sc.add(S.weapon_rack(), 208, 104)
sc.add(S.crate(), 58, 116); sc.add(S.crate(8, 7), 66, 119); sc.add(S.amphora(), 72, 118); sc.add(S.amphora(), 76, 117)
sc.add(S.crate(10, 8), 232, 112)
# picketed spare horse
sc.add(S.flip(S.cassius(0))[:, :, :] * np.array([1, 1, 1, 1]) if False else S.ox(0), 262, 104)

# ----------------------------------------------------------------- the column on the road (marching east)
def on_road(x, off=0):
    return road_c(x) + off
col = []
col.append((S.cart(2), 70, 6))
col.append((S.ox(1), 106, 4))
for i, x in enumerate(range(128, 236, 13)):
    col.append((S.legionary(i % 4), x, -5 if i % 2 else 6))
col.append((S.legionary(1, carry='vexillum'), 246, 0))
col.append((S.cassius(1), 280, 2))
for a, x, off in col:
    sc.add(a, x, on_road(x, off))
# lantern on the cart
sc.light(86, on_road(86, 6) - 14, 34, (1.0, 0.7, 0.3), 0.9)

# ----------------------------------------------------------------- south verge: milestone, reeds, rocks
sc.add(S.column(26, broken=True), 340, on_road(340, 30))
sc.add(S.rock(16, 10, 4), 360, on_road(360, 36))
sc.add(S.rock(10, 7, 8), 120, on_road(120, 40))
REED = [C('2c3a1a'), C('5a6a2a'), C('a89a4a')]
for i in range(70):
    x = rng.randint(0, W - 1)
    sc.add(S.reeds(rng.randint(0, 999), REED, h=rng.randint(7, 12)), x, bank(x) + 1, cast=False)
for i in range(40):
    x = rng.randint(0, W - 1); y = int(rng.uniform(road_c(x) + 26, bank(x) - 6))
    sc.add(S.tuft(rng.randint(0, 999), [C('3a4418'), C('6a6c26'), C('b0a040')]), x, y, cast=False)
# a moored skiff
skiff = rgba(30, 8)
for x in range(30):
    for y in range(8):
        if y >= 2 and abs(x - 15) < 15 - (7 - y) * 1.2:
            put(skiff, x, y, S.WOOD[1] if y > 3 else S.WOOD[3])
for x in range(3, 27):
    put(skiff, x, 3, S.WOOD[0])
sc.add(skiff, 420, bank(420) + 12, cast=False, depth=999)

sc.compose_items()

# ----------------------------------------------------------------- light, water, air
amb = C('383c88') * 0.62
sun = C('ffa860') * 1.15
img = sc.lit(amb, sun, shadow_strength=0.9)
img = sc.glow(img, 150, 110, 30, (1.0, 0.55, 0.2), 0.08)
img = sc.glow(img, 86, on_road(86, 6) - 13, 14, (1.0, 0.75, 0.35), 0.35)
# warm rim on everything facing the sun: brighten the left edge of objects
left_edge = sc.obj & ~np.roll(sc.obj, 1, axis=1)
img[left_edge] = img[left_edge] * 1.18 + C('ffb070') * 0.06
sky = lambda x, y: C('e88a5a') * (1 - x / W) * 0.9 + C('5a3c7a') * (x / W) + C('ffd0a0') * 0.25 * max(0, 1 - abs(x - 60) / 90)
img = reflect(img, bank, C('1a2c50'), refl_amt=0.34, depth_fade=0.6, sky=sky)
# sky colour in the water near the far side (dusk)
wm = yy > bank(xx)
img = fog(img, C('e0b0a0'), 0.22, 170, 236, seed=7)
# god rays from the low sun (diagonal, additive, dithered)
ray = np.sin((xx * 0.55 + yy) * 0.06) * 0.5 + 0.5
ray = np.clip((ray - 0.7) * 3, 0, 1) * np.clip(1 - xx / 420, 0, 1) * 0.07
img = img + C('ffc890')[None, None, :] * band(ray, 4, dither=False)[:, :, None]
# fireflies + embers
r2 = random.Random(5)
for i in range(40):
    x, y = r2.randint(0, W - 1), r2.randint(60, 240)
    img = img
    img[y, x] = img[y, x] * 0.2 + C('fff0a0') * 1.2
    if r2.random() < 0.4 and x + 1 < W:
        img[y, x + 1] = img[y, x + 1] * 0.6 + C('ffe080') * 0.4
for i in range(14):
    x, y = 150 + r2.randint(-10, 10), 104 - r2.randint(0, 30)
    img[y, x] = C('ffb050') * 1.3
img = grade(img, C('201c50'), gamma=1.05, sat=1.05, vignette=0.55, contrast=1.15)
im = to_image(img, colors=0)
im = hud(im, [('coin', '40', (240, 200, 110)), ('grain', '45 / 120 grain  (-9 a day)', (230, 214, 168)), ('', '70 men', (230, 214, 168)), ('', 'offerings 2/3', (230, 214, 168))],
         'WASD ride    Shift gallop    F interact    I pack    L ledger    M map', 'Day 1   Leg 1 of 5   Vermilion Empire')
text(im, (240, 60), 'THE IMPERIAL ROAD', col=(252, 232, 190), center=True, scale=2)
text(im, (190, 92), '[F] Make camp', col=(255, 242, 210), center=True)
im.save('frame1_road.png')
im.resize((W * 4, H * 4), Image.NEAREST).save('frame1_road_4x.png')
