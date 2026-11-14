"""Slide 5: cold dawn. The granary is nearly empty; the writ is read; seventy men march north."""
from slidekit import *
import math, random
from kit import *
import sprites as S
import figures3d as F
import buildings3d as B
import props3d as PR
from ground import build_ground
from fx import flame, torch_on

sc = Scene(seed=51)
rng = random.Random(51)
sc.sun = (-1.5, 0.28)                    # dawn from the east (right)
road_c = lambda x: 196 - 0.22 * (x - 320)
bank = lambda x: 400 + x * 0
GR = [C('1e2a1e'), C('2a3a24'), C('384a2a'), C('4a5e32'), C('60743c'), C('80904a')]
DIRT = [C('2e2824'), C('443a32'), C('5c4e42'), C('766452'), C('907c66')]
yy, xx = build_ground(sc, road_c, bank, GR, DIRT, 51, road_w=26, blades=8000, blade_tint=C('c0c8a0'),
                      cells=(48, 24, 12, 6), n_stones=300, spread=0.6, edge_col=C('3a4a2a'))
# frost on the grass
for i in range(1200):
    x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
    if abs(y - road_c(x)) > 28:
        sc.alb[y, x] = sc.alb[y, x] * 0.75 + C('d8e4f0') * 0.25

# the fort's corner on the left: palisade, granary with its doors open
pal = bake('palisade', B.palisade, (70, 44), 1.8, 0, pitch=14)
for x in range(-30, 180, pal.shape[1] - 2):
    sc.add(pal, x + pal.shape[1] // 2, 74)
gate = bake('gatehouse', B.gatehouse, (140, 90), 1.9, 0, pitch=14)
sc.add(gate, 236, 82)
sc.add(bake('granary_open', B.granary, (80, 50), 2.2, 30, pitch=18), 96, 150)
# the quartermaster with an almost empty sack, a few sacks on the ground
qm = bake('quartermaster', lambda: F.human(body='brown', legs='skin', arms=('chest', 'down'), head='bare', hair='linen', beard='linen'), (40, 62), 1.15, 40)
sc.add(qm, 150, 168)
sack = bake('sack', None, (14, 12), 1.8, 0)
for (x, y) in ((132, 170), (166, 176)):
    sc.add(sack, x, y)
# refugees watching from the parapet and by the gate
watch = [bake('ref_mother', None, (40, 62), 1.15, 190), bake('ref_old', None, (40, 62), 1.15, 175), bake('ref_woman', None, (40, 62), 1.1, 200)]
kid = bake('ref_kid', None, (30, 44), 1.15, 190)
for i, x in enumerate((190, 214, 272, 296)):
    sc.add(watch[i % 3][:, ::-1].copy() if i % 2 else watch[i % 3], x, 104)
sc.add(kid, 284, 106)

# the column formed up on the road, heading out north-east
for i in range(12):
    x = 300 + (i // 2) * 34 + (i % 2) * 10
    off = -9 if i % 2 else 9
    sc.add(sprite(f'legionary{i % 4}'), x, road_c(x) + off)
sc.add(sprite('vexillum'), 512, road_c(520) - 2, depth=road_c(520) - 3)
sc.add(sprite('legionary3'), 520, road_c(520) - 1)
sc.add(sprite('cassius'), 566, road_c(566) + 6)
sc.add(sprite('cart'), 262, road_c(262) + 6)
sc.add(sprite('ox'), 300 - 34, road_c(266) + 30) if False else None
# the imperial messenger, reading the writ aloud
herald = bake('herald', None, (40, 62), 1.2, 15)
sc.add(herald[:, ::-1].copy(), 560, road_c(560) + 40)
horse_m = sprite('cassius')
# a milestone pointing north
sc.add(sprite('column'), 612, road_c(612) + 34)
sc.add(sprite('rock1'), 460, 260); sc.add(sprite('rock2'), 30, 250)
P_PINE = [C('121c16'), C('1a2a1e'), C('263a26'), C('344c2e'), C('4a6236'), C('667c44'), C('8a9a5a')]
BARK = [C('201612'), C('3a2a20'), C('584032')]
for (x, y) in ((420, 70), (470, 64), (530, 72), (590, 60), (640, 70), (370, 60)):
    sc.add(S.cypress(rng.randint(0, 999), P_PINE[:6], h=rng.randint(70, 96), w=22), x, y)
# a dying campfire from the night
fire = sprite('campfire')
sc.add(fire, 200, 230, cast=False)
fl, fe = flame(10, 10, 3, 12)
sc.add(fl, 200, 226, emissive=fe, cast=False, depth=231)
sc.light(200, 220, 40, (1.0, 0.5, 0.2), 0.45)

sc.compose_items()
amb = C('5a6a9a') * 0.85
sun = C('ffc898') * 0.78
img = sc.lit(amb, sun, shadow_strength=0.8)
img = sc.glow(img, 200, 220, 18, (1.0, 0.55, 0.25), 0.2, bands=3)
# low dawn mist rolling over the fields, thinning toward the road
img = fog(img, C('d8c8d0'), 0.32, 20, 150, seed=52)
img = fog(img, C('e4dce4'), 0.22, 180, 272, seed=53)
# first light from the east
ray = np.sin((xx * -0.6 + yy) * 0.04) * 0.5 + 0.5
ray = np.clip((ray - 0.68) * 3, 0, 1) * np.clip((xx - 200) / 440, 0, 1) * 0.16
img = img + C('ffe0b0')[None, None, :] * band(ray, 4, dither=False)[:, :, None]
r2 = random.Random(2)
for i in range(16):                        # crows over the field
    x, y = r2.randint(300, 620), r2.randint(10, 60)
    img[y, x - 1:x + 2] = C('141014'); img[y - 1, x - 2] = C('141014'); img[y - 1, x + 2] = C('141014')
img = grade(img, C('1c1c40'), gamma=1.0, sat=1.0, vignette=0.55, contrast=1.12)
pic = to_image(img, colors=0)
pic.save('slide5_pic.png')
out = present_slide(pic, 4, 5, '粮仓快空了。帝国的回复是一道敕令：重开北路，收齐各地所欠，送往大祭场——你的要塞就能分到口粮。七十人，四十五斗粮。出发。')
out.save('slide5.png')
