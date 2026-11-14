"""Imperial Road at dusk, 640x272 cinematic picture, 48-px characters."""
import os
os.environ['WIDE'] = '1'
import math, random
import numpy as np
from PIL import Image
from kit import *
import sprites as S
import fig as F
from ground import build_ground
from present import present

sc = Scene(seed=12)
rng = random.Random(12)
sc.sun = (1.5, 0.3)
road_c = lambda x: 188 - 0.09 * (x - 320)
bank = lambda x: 256 - 0.16 * (x - 320)

GR = [C('1e3014'), C('2a4216'), C('38561c'), C('4a6c22'), C('62822a'), C('829834'), C('b0aa46')]
DIRT = [C('3a2a20'), C('523a2c'), C('6c4e38'), C('8a6848'), C('aa8660'), C('c4a27a')]
yy, xx = build_ground(sc, road_c, bank, GR, DIRT, 12, road_w=30, blades=9000, blade_tint=C('d8c060'),
                      flowers=[C('e8d070'), C('e09060'), C('f0f0e0'), C('c070a0')], dry=C('8a7a3a'), edge_col=C('4a5420'),
                      cells=(64, 32, 16, 8), n_stones=500, spread=0.6)
# longer grass blades at this scale
for i in range(5000):
    x = rng.randint(0, W - 1); y = rng.randint(4, H - 1)
    if abs(y - road_c(x)) < 31 or y > bank(x) - 2:
        continue
    hgt = rng.randint(2, 6); lean = rng.choice([-1, 0, 0, 1])
    base = sc.alb[y, x].copy()
    for k in range(hgt):
        xx2 = x + (lean if k > hgt // 2 else 0)
        if 0 <= y - k and xx2 < W:
            sc.alb[y - k, xx2] = base * (0.72 + 0.12 * k) + C('e0c860') * 0.05 * k
# imperial paving: fitted polygonal stones with mortar joints
for i in range(260):
    x = rng.randint(0, W - 10); y = int(road_c(x) + rng.uniform(-24, 22))
    w = rng.randint(5, 10); h = rng.randint(3, 5)
    sc.alb[y:y + h, x:x + w] = C('857a70'); sc.alb[y, x:x + w] = C('aa9e92'); sc.alb[y:y + h, x] = C('9a8e84')
    sc.alb[y + h - 1, x:x + w] = C('5a5048'); sc.alb[y:y + h, x + w - 1] = C('5e544c')
for x in range(0, W, 7):
    for side in (-1, 1):
        y = int(road_c(x) + side * 30.5)
        if 0 <= y < H - 2:
            sc.alb[y, x:x + 6] = C('a0968c'); sc.alb[y + 1, x:x + 6] = C('6a6058'); sc.alb[y + 2, x:x + 6] = C('3e3630')

P_PINE = [C('142010'), C('1c2e16'), C('2a421c'), C('3e5a22'), C('5a782a'), C('8a9a38'), C('c0b44c')]
P_CYP = [C('0c1810'), C('142616'), C('1e381a'), C('2e5020'), C('4a6c2a'), C('7a9038')]
BARK = [C('2a1c16'), C('4a3326'), C('6e5040')]

sc.add(S.aqueduct(9, 30, 70), 470, 78, cast=False, depth=-50)
x = -20
while x < W + 30:
    y = rng.randint(84, 104)
    if rng.random() < 0.45:
        sc.add(S.stone_pine(rng.randint(0, 999), P_PINE, BARK, h=rng.randint(118, 140), R=40, tw=5, fine=0.55), x, y)
        x += rng.randint(56, 80)
    else:
        sc.add(S.cypress(rng.randint(0, 999), P_CYP, h=rng.randint(96, 124), w=26), x, y)
        x += rng.randint(18, 30)

# camp
sc.add(S.tent(84, 56), 150, 140)
sc.add(S.tent(66, 46), 250, 126)
fire = rgba(40, 34); fire_e = rgba(40, 34)
for i in range(18):
    put(fire, 8 + i, 28 + (i % 3 == 0), S.WOOD[1]); put(fire, 8 + i, 29, S.WOOD[0]); put(fire, 30 - i, 27 + i // 6, S.WOOD[2])
for ang in range(0, 360, 20):
    xs, ys = int(20 + math.cos(math.radians(ang)) * 15), int(30 + math.sin(math.radians(ang)) * 4)
    put(fire, xs, ys, C('6a6266')); put(fire, xs + 1, ys, C('3a3436')); put(fire, xs, ys - 1, C('9a9094'))
rf = random.Random(7)
for k in range(60):
    x0 = 20 + rf.randint(-8, 8)
    hgt = rf.randint(3, 22 - abs(x0 - 20) * 2) if abs(x0 - 20) < 9 else 3
    for y in range(27 - hgt, 27):
        t = (27 - y) / max(1, hgt)
        c = C('fff2b0') if t < 0.3 and abs(x0 - 20) < 4 else C('ffb040') if t < 0.65 else C('e2502a')
        put(fire, x0, y, c); put(fire_e, x0, y, c * 0.7)
sc.add(fire, 66, 146, emissive=fire_e, cast=False)
sc.light(66, 134, 90, (1.0, 0.5, 0.2), 0.45)
sc.add(S.flip(F.legionary(0)), 40, 146)
sc.add(F.legionary(2, carry=None), 94, 146)
sc.add(S.crate(16, 14), 196, 150); sc.add(S.crate(13, 12), 210, 154); sc.add(S.crate(14, 12), 290, 136)

# the column, marching east
col = [(F.ox48(1), 96, 6)]
for i, x in enumerate(range(150, 400, 36)):
    col.append((F.legionary(i % 4), x, -11 if i % 2 else 9))
col.append((F.legionary(1, carry='vexillum'), 424, -2))
col.append((F.cassius_mounted(1), 490, 4))
for a, x, off in col:
    sc.add(a, x, road_c(x) + off)
flag = F.vexillum(1.4, 80)
sc.add(flag, 420, road_c(424) - 2 - 22, depth=road_c(424) - 1)

# south verge
sc.add(S.column(52, broken=True), 584, road_c(584) + 52)
sc.add(S.rock(26, 16, 4), 612, road_c(612) + 60)
sc.add(S.rock(18, 12, 8), 210, road_c(210) + 58)
sc.add(S.rock(14, 10, 9), 40, road_c(40) + 50)
REED = [C('2c3a1a'), C('5a6a2a'), C('a89a4a')]
for i in range(90):
    x = rng.randint(300, W - 1)
    sc.add(S.reeds(rng.randint(0, 999), REED, h=rng.randint(12, 20)), x, bank(x) + 1, cast=False)
for i in range(60):
    x = rng.randint(0, W - 1); y = int(rng.uniform(road_c(x) + 36, min(H - 2, bank(x) - 8)))
    sc.add(S.tuft(rng.randint(0, 999), [C('3a4418'), C('6a6c26'), C('b0a040')], h=rng.randint(6, 11), w=14), x, y, cast=False)

sc.compose_items()
amb = C('383c88') * 0.62
sun = C('ffa860') * 1.15
img = sc.lit(amb, sun, shadow_strength=0.9)
img = sc.glow(img, 66, 130, 46, (1.0, 0.55, 0.2), 0.1)
left_edge = sc.obj & ~np.roll(sc.obj, 1, axis=1)
img[left_edge] = img[left_edge] * 1.15 + C('ffb070') * 0.05
sky = lambda x, y: C('e88a5a') * (1 - x / W) * 0.9 + C('5a3c7a') * (x / W) + C('ffd0a0') * 0.25 * max(0, 1 - abs(x - 380) / 140)
img = reflect(img, bank, C('1a2c50'), refl_amt=0.36, depth_fade=0.55, sky=sky)
img = fog(img, C('e0b0a0'), 0.2, 200, 272, seed=7)
ray = np.sin((xx * 0.55 + yy) * 0.045) * 0.5 + 0.5
ray = np.clip((ray - 0.7) * 3, 0, 1) * np.clip(1 - xx / 560, 0, 1) * 0.07
img = img + C('ffc890')[None, None, :] * band(ray, 4, dither=False)[:, :, None]
r2 = random.Random(5)
for i in range(50):
    x, y = r2.randint(0, W - 2), r2.randint(60, 262)
    img[y, x] = img[y, x] * 0.2 + C('fff0a0') * 1.2
for i in range(18):
    x, y = 66 + r2.randint(-12, 12), 114 - r2.randint(0, 40)
    img[y, x] = C('ffb050') * 1.3
img = grade(img, C('201c50'), gamma=1.05, sat=1.05, vignette=0.45, contrast=1.15)
pic = to_image(img, colors=0)
pic.save('road48_picture.png')

top = [('coin', '40', (240, 204, 120)), ('grain', '45 / 120 粮   每日 -9', (232, 216, 176)), ('', '70 人', (232, 216, 176)), ('', '祭品 2/3', (232, 216, 176))]
hints = 'WASD 骑行    Shift 疾驰    F 交互    I 行囊    L 账本    M 地图'
for name, (sw, sh), notch in (('road48_1080p', (1920, 1080), False), ('road48_macbook_air13', (2560, 1664), True)):
    canvas, k = present(pic, sw, sh, top, '第 1 天   第 1 段 / 共 5 段', '帝国大道', hints, prompt=((66, 92), '[F] 扎营'), notch=notch)
    canvas.save(f'{name}.png')
    print(name, k)
