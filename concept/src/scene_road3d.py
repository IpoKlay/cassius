"""Imperial Road at dusk - every character and prop baked from 3D clay models into pixel art."""
import os
os.environ['WIDE'] = '1'
import math, random
import numpy as np
from PIL import Image
from kit import *
import sprites as S
from ground import build_ground
from present import present

SP = '/home/claude/renders/sprites3d'


def L(name, flip=False):
    a = np.asarray(Image.open(f'{SP}/{name}.png').convert('RGBA'), dtype=float) / 255.0
    return a[:, ::-1].copy() if flip else a


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
sc.add(L('aqueduct'), 480, 84, cast=False, depth=-50)
x = -20
while x < W + 30:
    y = rng.randint(84, 104)
    if rng.random() < 0.45:
        sc.add(S.stone_pine(rng.randint(0, 999), P_PINE, BARK, h=rng.randint(118, 140), R=40, tw=5, fine=0.55), x, y)
        x += rng.randint(56, 80)
    else:
        sc.add(S.cypress(rng.randint(0, 999), P_CYP, h=rng.randint(96, 124), w=26), x, y)
        x += rng.randint(18, 30)

# ---- camp
sc.add(L('tent_big'), 160, 142)
sc.add(L('tent_small'), 258, 128)
sc.add(L('crate'), 210, 150); sc.add(L('crate'), 224, 154); sc.add(L('amphora'), 236, 150); sc.add(L('amphora'), 242, 152)
sc.add(L('crate'), 300, 134)
fire = L('campfire')
fire_e = np.zeros_like(fire)
flames = rgba(fire.shape[1], fire.shape[0] + 16)
flames_e = rgba(fire.shape[1], fire.shape[0] + 16)
rf = random.Random(7)
cx = fire.shape[1] // 2
for k in range(70):
    x0 = cx + rf.randint(-6, 6)
    hgt = rf.randint(3, 20 - abs(x0 - cx) * 2) if abs(x0 - cx) < 8 else 3
    base = flames.shape[0] - 9
    for y in range(base - hgt, base):
        t = (base - y) / max(1, hgt)
        c = C('fff2b0') if t < 0.3 and abs(x0 - cx) < 3 else C('ffb040') if t < 0.65 else C('e2502a')
        put(flames, x0, y, c); put(flames_e, x0, y, c * 0.75)
sc.add(fire, 66, 150, cast=False)
sc.add(flames, 66, 150 - 4, emissive=flames_e, cast=False, depth=151)
sc.light(66, 136, 92, (1.0, 0.5, 0.2), 0.5)
sc.add(L('legionary1', flip=True), 40, 152)
sc.add(L('legionary2'), 94, 150)

# ---- the column, marching east
sc.add(L('cart'), 46, road_c(46) + 8)
sc.add(L('ox'), 104, road_c(104) + 6)
for i, x in enumerate(range(150, 400, 36)):
    sc.add(L(f'legionary{i % 4}'), x, road_c(x) + (-11 if i % 2 else 9))
xs = 420
sc.add(L('vexillum'), xs - 9, road_c(xs) - 4, depth=road_c(xs) - 3)
sc.add(L('legionary3'), xs, road_c(xs) - 2)
sc.add(L('cassius'), 486, road_c(486) + 4)
sc.light(64, road_c(64) - 14, 30, (1.0, 0.7, 0.3), 0.6)

# ---- south verge
sc.add(L('column'), 584, road_c(584) + 52)
sc.add(L('rock2'), 612, road_c(612) + 62)
sc.add(L('rock0'), 210, road_c(210) + 58)
sc.add(L('rock1'), 40, road_c(40) + 52)
REED = [C('2c3a1a'), C('5a6a2a'), C('a89a4a')]
for i in range(90):
    x = rng.randint(300, W - 1)
    sc.add(S.reeds(rng.randint(0, 999), REED, h=rng.randint(12, 20)), x, bank(x) + 1, cast=False)
for i in range(60):
    x = rng.randint(0, W - 1); y = int(rng.uniform(road_c(x) + 36, min(H - 2, bank(x) - 8)))
    sc.add(S.tuft(rng.randint(0, 999), [C('3a4418'), C('6a6c26'), C('b0a040')], h=rng.randint(6, 11), w=14), x, y, cast=False)

sc.compose_items()
amb = C('3c4090') * 0.66
sun = C('ffaa64') * 1.05
img = sc.lit(amb, sun, shadow_strength=0.9)
img = sc.glow(img, 66, 132, 46, (1.0, 0.55, 0.2), 0.1)
left_edge = sc.obj & ~np.roll(sc.obj, 1, axis=1)
img[left_edge] = img[left_edge] * 1.12 + C('ffb070') * 0.04
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
    x, y = 66 + r2.randint(-12, 12), 116 - r2.randint(0, 40)
    img[y, x] = C('ffb050') * 1.3
img = grade(img, C('201c50'), gamma=1.05, sat=1.05, vignette=0.45, contrast=1.12)
pic = to_image(img, colors=0)
pic.save('road3d_picture.png')
top = [('coin', '40', (240, 204, 120)), ('grain', '45 / 120 粮   每日 -9', (232, 216, 176)), ('', '70 人', (232, 216, 176)), ('', '祭品 2/3', (232, 216, 176))]
hints = 'WASD 骑行    Shift 疾驰    F 交互    I 行囊    L 账本    M 地图'
for name, (sw, sh), notch in (('road3d_1080p', (1920, 1080), False), ('road3d_macbook_air13', (2560, 1664), True)):
    canvas, k = present(pic, sw, sh, top, '第 1 天   第 1 段 / 共 5 段', '帝国大道', hints, prompt=((66, 96), '[F] 扎营'), notch=notch)
    canvas.save(f'{name}.png')
    print(name, k)
