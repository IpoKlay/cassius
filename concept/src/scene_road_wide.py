"""Imperial Road at dusk, cinematic 640x272 picture, finer detail."""
import os
os.environ['WIDE'] = '1'
import math, random
import numpy as np
from PIL import Image
from kit import *
import sprites as S
from ground import build_ground
from present import present

assert (W, H) == (640, 272)
sc = Scene(seed=11)
rng = random.Random(11)
sc.sun = (1.55, 0.32)
road_c = lambda x: 160 - 0.12 * (x - 320)
bank = lambda x: 232 - 0.12 * (x - 320)

GR = [C('1e3014'), C('2a4216'), C('38561c'), C('4a6c22'), C('62822a'), C('829834'), C('b0aa46')]
DIRT = [C('3a2a20'), C('523a2c'), C('6c4e38'), C('8a6848'), C('aa8660'), C('c4a27a')]
yy, xx = build_ground(sc, road_c, bank, GR, DIRT, 11, road_w=20, blades=11000, blade_tint=C('d8c060'),
                      flowers=[C('e8d070'), C('e09060'), C('f0f0e0'), C('c070a0')], dry=C('8a7a3a'), edge_col=C('4a5420'),
                      cells=(40, 20, 10, 5), n_stones=420, spread=0.6)
# fitted paving of the old imperial road showing through the dirt
for i in range(150):
    x = rng.randint(0, W - 6); y = int(road_c(x) + rng.uniform(-13, 13))
    w = rng.randint(3, 6)
    sc.alb[y:y + 2, x:x + w] = C('8a8078'); sc.alb[y, x:x + w] = C('aca298'); sc.alb[y + 2, x:x + w] = C('4a4038')
    sc.alb[y:y + 3, x + w] = C('3e362e')
# kerb stones along both edges
for x in range(0, W, 5):
    for side in (-1, 1):
        y = int(road_c(x) + side * 20.5)
        if 0 <= y < H - 1 and rng.random() < 0.7:
            sc.alb[y, x:x + 4] = C('9a9088'); sc.alb[y + 1, x:x + 4] = C('5a5048')

P_PINE = [C('142010'), C('1c2e16'), C('2a421c'), C('3e5a22'), C('5a782a'), C('8a9a38'), C('c0b44c')]
P_CYP = [C('0c1810'), C('142616'), C('1e381a'), C('2e5020'), C('4a6c2a'), C('7a9038')]
BARK = [C('2a1c16'), C('4a3326'), C('6e5040')]

# distant aqueduct behind the tree line
sc.add(S.aqueduct(12, 18, 44), 470, 58, cast=False, depth=-50)
# tree line along the top: umbrella pines and cypresses
x = -14
while x < W + 20:
    y = rng.randint(66, 86)
    if rng.random() < 0.42:
        sc.add(S.stone_pine(rng.randint(0, 999), P_PINE, BARK, h=rng.randint(72, 94), fine=0.7), x, y)
        x += rng.randint(36, 56)
    else:
        sc.add(S.cypress(rng.randint(0, 999), P_CYP, h=rng.randint(54, 78)), x, y)
        x += rng.randint(11, 20)
for x in (22, 390, 520):
    sc.add(S.cypress(rng.randint(0, 999), P_CYP, h=rng.randint(62, 80)), x, rng.randint(100, 110))
sc.add(S.stone_pine(42, P_PINE, BARK, h=100, fine=0.7), 610, 122)
sc.add(S.stone_pine(43, P_PINE, BARK, h=90, fine=0.7), 448, 108)

# the camp
sc.add(S.tent(42, 28), 172, 118)
sc.add(S.tent(34, 24), 232, 106)
sc.add(S.tent(34, 24), 118, 106)
sc.add(S.tent(30, 22), 290, 100)
fire, fire_e = S.campfire(3)
sc.add(fire, 232, 134, emissive=fire_e, cast=False)
sc.light(232, 128, 52, (1.0, 0.5, 0.2), 0.42)
for (x, y, f) in ((218, 132, False), (246, 135, True), (230, 141, False)):
    s = S.sitter()
    sc.add(S.flip(s) if f else s, x, y)
sc.add(S.standard(1), 272, 126)
sc.add(S.weapon_rack(), 292, 118)
sc.add(S.crate(), 138, 130); sc.add(S.crate(8, 7), 146, 133); sc.add(S.amphora(), 152, 132); sc.add(S.amphora(), 156, 131)
sc.add(S.crate(10, 8), 312, 126)
sc.add(S.ox(0), 344, 118)
sc.add(S.ox(3), 368, 114)

# the column, marching east
col = [(S.cart(2), 150, 6), (S.ox(1), 186, 4)]
for i, x in enumerate(range(208, 330, 13)):
    col.append((S.legionary(i % 4), x, -5 if i % 2 else 6))
col.append((S.legionary(1, carry='vexillum'), 340, 0))
col.append((S.cassius(1), 374, 2))
for a, x, off in col:
    sc.add(a, x, road_c(x) + off)
sc.light(166, road_c(166) - 8, 34, (1.0, 0.7, 0.3), 0.9)

# south verge
sc.add(S.column(26, broken=True), 438, road_c(438) + 32)
sc.add(S.rock(16, 10, 4), 458, road_c(458) + 38)
sc.add(S.rock(10, 7, 8), 210, road_c(210) + 42)
sc.add(S.rock(12, 8, 5), 560, road_c(560) + 30)
REED = [C('2c3a1a'), C('5a6a2a'), C('a89a4a')]
for i in range(110):
    x = rng.randint(0, W - 1)
    sc.add(S.reeds(rng.randint(0, 999), REED, h=rng.randint(7, 12)), x, bank(x) + 1, cast=False)
for i in range(70):
    x = rng.randint(0, W - 1); y = int(rng.uniform(road_c(x) + 26, bank(x) - 6))
    sc.add(S.tuft(rng.randint(0, 999), [C('3a4418'), C('6a6c26'), C('b0a040')]), x, y, cast=False)
skiff = rgba(30, 8)
for x in range(30):
    for y in range(8):
        if y >= 2 and abs(x - 15) < 15 - (7 - y) * 1.2:
            put(skiff, x, y, S.WOOD[1] if y > 3 else S.WOOD[3])
for x in range(3, 27):
    put(skiff, x, 3, S.WOOD[0])
sc.add(skiff, 540, bank(540) + 14, cast=False, depth=999)

sc.compose_items()
amb = C('383c88') * 0.62
sun = C('ffa860') * 1.15
img = sc.lit(amb, sun, shadow_strength=0.9)
img = sc.glow(img, 232, 126, 30, (1.0, 0.55, 0.2), 0.08)
img = sc.glow(img, 166, road_c(166) - 7, 14, (1.0, 0.75, 0.35), 0.35)
left_edge = sc.obj & ~np.roll(sc.obj, 1, axis=1)
img[left_edge] = img[left_edge] * 1.18 + C('ffb070') * 0.06
sky = lambda x, y: C('e88a5a') * (1 - x / W) * 0.9 + C('5a3c7a') * (x / W) + C('ffd0a0') * 0.25 * max(0, 1 - abs(x - 80) / 110)
img = reflect(img, bank, C('1a2c50'), refl_amt=0.34, depth_fade=0.6, sky=sky)
img = fog(img, C('e0b0a0'), 0.22, 190, 262, seed=7)
ray = np.sin((xx * 0.55 + yy) * 0.06) * 0.5 + 0.5
ray = np.clip((ray - 0.7) * 3, 0, 1) * np.clip(1 - xx / 560, 0, 1) * 0.07
img = img + C('ffc890')[None, None, :] * band(ray, 4, dither=False)[:, :, None]
r2 = random.Random(5)
for i in range(60):
    x, y = r2.randint(0, W - 2), r2.randint(70, 260)
    img[y, x] = img[y, x] * 0.2 + C('fff0a0') * 1.2
for i in range(14):
    x, y = 232 + r2.randint(-10, 10), 120 - r2.randint(0, 30)
    img[y, x] = C('ffb050') * 1.3
img = grade(img, C('201c50'), gamma=1.05, sat=1.05, vignette=0.45, contrast=1.15)
pic = to_image(img, colors=0)
pic.save('wide_road_picture.png')

top = [('coin', '40', (240, 204, 120)), ('grain', '45 / 120 粮   每日 -9', (232, 216, 176)), ('', '70 人', (232, 216, 176)), ('', '祭品 2/3', (232, 216, 176))]
hints = 'WASD 骑行    Shift 疾驰    F 交互    I 行囊    L 账本    M 地图'
for name, (sw, sh), notch in (('screen_1080p', (1920, 1080), False), ('screen_macbook_air13', (2560, 1664), True)):
    canvas, k = present(pic, sw, sh, top, '第 1 天   第 1 段 / 共 5 段', '帝国大道', hints, prompt=((272, 82), '[F] 扎营'), notch=notch)
    canvas.save(f'{name}.png')
    print(name, 'scale', k)
