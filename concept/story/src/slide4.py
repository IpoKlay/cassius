"""Slide 4: the border fort at dusk. Cassius opens the gate to the refugees."""
from slidekit import *
import math, random
from kit import *
import sprites as S
import figures3d as F
import buildings3d as B
from ground import build_ground
from fx import flame, torch_on

sc = Scene(seed=41)
rng = random.Random(41)
sc.sun = (1.3, 0.3)
road_c = lambda x: 120 + (x - 320) * 0.0
GR = [C('1c2414'), C('283418'), C('34441c'), C('445622'), C('586a2a'), C('768236')]
DIRT = [C('2e2420'), C('44342a'), C('5c4636'), C('765a42'), C('907050')]
yy, xx = np.mgrid[0:H, 0:W]
# ground: trampled mud in front of the gate, grass beyond
n1 = fbm(W, H, 5, cells=(40, 20, 10, 5))
g = band(np.clip(0.45 + (n1 - 0.5) * 0.7, 0, 0.999), len(GR), dither=False)
sc.alb[:] = np.array(GR)[(g * len(GR)).astype(int)]
mud = (np.abs(xx - 320 - (yy - 100) * 0.15) < 34 + (yy - 100) * 0.55) & (yy > 96)
d = band(np.clip(0.4 + (n1 - 0.5) * 0.8, 0, 0.999), len(DIRT), dither=False)
sc.alb[mud] = np.array(DIRT)[(d * len(DIRT)).astype(int)][mud]
for i in range(400):                                  # cart ruts and puddles
    x = int(320 + rng.uniform(-30, 30)); y = rng.randint(100, H - 1)
    sc.alb[y, x] = DIRT[0]
for i in range(9):
    x, y = rng.randint(250, 390), rng.randint(140, 260)
    for k in range(rng.randint(8, 16)):
        sc.alb[y + k // 6, x + k % 12] = C('283048')
for i in range(5000):
    x = rng.randint(0, W - 1); y = rng.randint(0, H - 1)
    if mud[y, x]:
        continue
    for k in range(rng.randint(1, 4)):
        if y - k >= 0:
            sc.alb[y - k, x] = sc.alb[y, x] * (0.8 + 0.12 * k)

# the fort: palisade both sides of a stone gatehouse
gate = bake('gatehouse', B.gatehouse, (140, 90), 1.9, 0, pitch=14)
sc.add(gate, 320, 100)
pal = bake('palisade', B.palisade, (70, 44), 1.8, 0, pitch=14)
for x in range(-20, 230, pal.shape[1] - 2):
    sc.add(pal, x + pal.shape[1] // 2, 96)
for x in range(410, W + 40, pal.shape[1] - 2):
    sc.add(pal, x + pal.shape[1] // 2, 96)
# inside the walls: the granary, tents, smoke - the fort the refugees are entering
sc.add(bake('granary', B.granary, (80, 50), 1.7, 24, pitch=18), 120, 70, depth=60)
sc.add(sprite('tent_small'), 500, 66, depth=60)
sc.add(sprite('tent_big'), 590, 76, depth=61)
for x in (272, 368):
    torch_on(sc, x, 40, 101, seed=x, light=0.7, radius=60)
sc.light(320, 96, 70, (1.0, 0.62, 0.3), 0.9)            # firelight spilling out of the gateway
for x in (60, 170, 470, 580):
    torch_on(sc, x, 66, 99, seed=x, light=0.6, radius=46)
    pole = rgba(2, 30); pole[:, :, :3] = C('5a3a24'); pole[:, :, 3] = 1
    sc.add(pole, x, 96, depth=98)

# Cassius beside the open gate, legionaries holding torches
sc.add(sprite('cassius', flip=True), 412, 150)
for (x, y, f) in ((236, 134, False), (396, 130, True)):
    sc.add(sprite('legionary2', flip=f), x, y)
    torch_on(sc, x + (-8 if f else 8), y - 50, y + 1, seed=x)
sc.add(bake('vexillum', lambda: __import__('props3d').vexillum_model(0.4), (24, 70), 1.45, 12), 384, 128)

# the refugees streaming in: families, carts, bundles, a goat-less, hungry procession
people = [
    bake('ref_mother', lambda: F.human(body='grey', robe=True, cloak='blue', head='hood', arms=('chest', 'down'), thin=0.92), (40, 62), 1.15, 190),
    bake('ref_old', lambda: F.human(body='brown', robe=True, cloak='grey', head='bare', hair='linen', beard='linen', arms=('down', 'staff'), staff=True), (40, 62), 1.15, 175),
    bake('ref_man_sack', lambda: F.human(body='sack', legs='skin', arms=('down', 'sack'), sack=True, head='cap', beard='mane'), (40, 62), 1.15, 185),
    bake('ref_woman', lambda: F.human(body='red', robe=True, cloak='brown', head='hood', arms=('chest', 'chest'), thin=0.9), (40, 62), 1.1, 200),
    bake('ref_youth', lambda: F.human(body='green', legs='skin', arms=('sack', 'down'), sack=False, head='bare', hair='brown'), (40, 62), 1.05, 170),
]
kid = bake('ref_kid', lambda: F.child(body='blue', legs='skin', arms=('down', 'up')), (30, 44), 1.15, 190)
kid2 = bake('ref_kid2', lambda: F.child(body='red', legs='skin', arms=('up', 'down')), (30, 44), 1.15, 170)
cart = bake('handcart', B.handcart, (40, 26), 2.0, 160, pitch=20)
spots = [(300, 150), (338, 160), (290, 182), (350, 190), (318, 214), (276, 230), (360, 236), (330, 262), (250, 258), (392, 264), (300, 268)]
for i, (x, y) in enumerate(spots):
    sc.add(people[i % len(people)], x + rng.randint(-4, 4), y)
sc.add(kid, 312, 186); sc.add(kid2, 342, 222); sc.add(kid, 268, 264)
sc.add(cart, 252, 206); sc.add(cart[:, ::-1].copy(), 392, 214)
# bundles and a dropped sack by the gate; a little shrine outside the walls
sack = bake('sack', None, (14, 12), 1.8, 0)
for (x, y) in ((214, 150), (224, 154), (430, 168)):
    sc.add(sack, x, y)
sc.add(bake('altar_small', B.altar_stone, (60, 40), 1.4, 20, pitch=24), 560, 214)
fl, fe = flame(14, 18, 5)
sc.add(fl, 560, 196, emissive=fe, cast=False, depth=215)
sc.light(560, 186, 60, (1.0, 0.55, 0.25), 0.6)
sc.add(sprite('rock2'), 110, 238); sc.add(sprite('rock0'), 520, 262); sc.add(sprite('rock1'), 160, 214)
P_PINE = [C('101a10'), C('16261a'), C('22381e'), C('344e26'), C('4c6a2e'), C('6e8838'), C('9aa448')]
BARK = [C('201612'), C('3a2a20'), C('584032')]
sc.add(S.oak(77, P_PINE, BARK, R=30, fine=0.6), 40, 272)
sc.add(S.oak(78, P_PINE, BARK, R=26, fine=0.6), 620, 268)

sc.compose_items()
amb = C('3a4280') * 0.85
sun = C('ff8a5a') * 0.5
img = sc.lit(amb, sun, shadow_strength=0.8)
for (x, y, r, c, s) in sc.lights:
    img = sc.glow(img, x, y, 10, (1.0, 0.65, 0.3), 0.22, bands=3)
img = fog(img, C('7a6a9a'), 0.28, 100, 272, seed=44)
r2 = random.Random(9)
for i in range(30):
    x, y = r2.randint(0, W - 1), r2.randint(0, 120)
    img[y, x] = img[y, x] * 0.3 + C('ffb060') * 0.9
img = grade(img, C('0e1230'), gamma=1.05, sat=1.05, vignette=0.6, contrast=1.14)
pic = to_image(img, colors=0)
pic.save('slide4_pic.png')
out = present_slide(pic, 3, 5, '卡西乌斯驻守一座边境要塞。难民来时，他打开城门，许下承诺：只要军旗还在，你们就能留下。')
out.save('slide4.png')
