"""Slide 2: the King calls the Great Sacrifice. Blood-red sunset, tribute piling at the temple steps."""
from slidekit import *
import math, random
from kit import *
import sprites as S
import figures3d as F
import buildings3d as B
import props3d as PR

sc = Scene(seed=21)
rng = random.Random(21)
sc.sun = (-1.4, 0.32)           # low sun from the east (right): shadows fall left
yy, xx = np.mgrid[0:H, 0:W]

# paved forum: large flagstones with worn joints, darker toward the steps
n1 = fbm(W, H, 4, cells=(48, 24, 12, 6))
FL = [C('5a4a44'), C('6e5c52'), C('84705e'), C('9a846c'), C('b09a7e')]
g = band(np.clip(0.45 + (n1 - 0.5) * 0.7, 0, 0.999), len(FL), dither=False)
sc.alb[:] = np.array(FL)[(g * len(FL)).astype(int)]
for y in range(0, H, 15):
    off = (y // 15) % 2 * 13
    sc.alb[y, :] = sc.alb[y, :] * 0.8
    for x in range(off, W, 26):
        sc.alb[y:y + 15, x] = sc.alb[y:y + 15, x] * 0.84
# a few cracked and sunken stones
for i in range(40):
    x, y = rng.randint(0, W - 20), rng.randint(0, H - 12)
    sc.alb[y:y + rng.randint(6, 13), x:x + rng.randint(10, 24)] *= rng.choice([0.88, 1.08])
# dry withered grass creeping between the stones at the edges
for i in range(2600):
    x = rng.randint(0, W - 1); y = rng.randint(0, H - 1)
    if 140 < x < 500 and y < 200:
        continue
    sc.alb[y, x] = rng.choice([C('6a6030'), C('8a7a3a'), C('5a5028')])

# temple at the top, flanked by statues of the King
sc.add(bake('temple6', lambda: B.temple_front(6, 9.0, 30.0, 10.0), (200, 110), 2.0, 0, pitch=16), 320, 112)
throne = bake('throne', B.throne, (24, 32), 1.7, 0, pitch=14)
sc.add(throne, 320, 100, depth=114)
king = bake('king', lambda: F.human(body='purple', robe=True, cloak='red', head='crown', beard='linen', arms=('out', 'down'), staff=True, belt='gold', sleeve='purple'), (40, 62), 1.3, 10)
sc.add(king, 320, 104, depth=115)
pri = bake('priest_up', lambda: F.human(body='linen', robe=True, cloak='linen', head='hood', arms=('up', 'up'), belt='red'), (40, 62), 1.2, 20)
sc.add(pri, 290, 106, depth=115); sc.add(pri[:, ::-1].copy(), 350, 106, depth=115)
leg = sprite('legionary1'); legf = sprite('legionary2', flip=True)
for x in (232, 254):
    sc.add(leg, x, 116)
for x in (386, 408):
    sc.add(legf, x, 116)
# herald reading the decree on the lowest step
herald = bake('herald', lambda: F.human(body='red', legs='skin', cloak='gold', head='bare', hair='brown', arms=('forward', 'forward'), scroll=True), (40, 62), 1.2, 15)
sc.add(herald, 320, 142)
# colonnade wings and pedestals framing the forum
colm = sprite('column')
plin = bake('plinth_full', lambda: B.plinth(False), (30, 30), 1.9, 20, pitch=22)
for x in (40, 80, 120, 520, 560, 600):
    sc.add(bake('col_whole', lambda: PR.column_model(26.0, False), (20, 52), 2.2, 10), x, 86)
for x in (160, 480):
    sc.add(plin, x, 96)
    sc.add(braz_pre if False else bake('brazier', B.brazier, (14, 22), 1.8, 0), x, 76, depth=97)
# braziers either side of the steps
braz = bake('brazier', B.brazier, (14, 22), 1.8, 0)
fires = []
for x in (196, 444):
    sc.add(braz, x, 124)
    fl = rgba(16, 20); fe = rgba(16, 20); r = random.Random(x)
    for k in range(40):
        x0 = 8 + r.randint(-4, 4); h = r.randint(3, 14 - abs(x0 - 8) * 2) if abs(x0 - 8) < 5 else 2
        for yy2 in range(19 - h, 19):
            t = (19 - yy2) / max(1, h)
            c = C('fff2b0') if t < 0.3 else C('ffb040') if t < 0.65 else C('e2502a')
            put(fl, x0, yy2, c); put(fe, x0, yy2, c * 0.8)
    sc.add(fl, x, 124 - 18, emissive=fe, cast=False, depth=125)
    sc.light(x, 100, 80, (1.0, 0.5, 0.22), 0.7)
    fires.append((x, 100))
# hanging banners between the outer columns
for x in (226, 414):
    b = rgba(14, 40)
    for yy2 in range(40):
        for x2 in range(14):
            c = C('8a1c16') if 2 < x2 < 12 else C('d8a038')
            if yy2 > 34 and (x2 + yy2) % 3 == 0:
                continue
            put(b, x2, yy2, c * (0.75 + 0.25 * (x2 < 7)))
    for (x2, y2) in ((6, 10), (7, 10), (5, 11), (8, 11), (6, 12), (7, 12), (6, 14), (7, 14), (6, 16), (7, 16)):
        put(b, x2, y2, C('f0c048'))
    sc.add(b, x, 84, cast=False, depth=60)

# the tribute: grain carts, sacks, amphorae, the white ox, cattle
cart = sprite('cart'); ox = sprite('ox'); oxf = sprite('ox', flip=True)
sc.add(cart, 110, 150); sc.add(ox, 150, 152)
sc.add(bake('cart_r', lambda: PR.cart_model(0.9), (80, 54), 1.9, 40, origin=(3.0, -1.0)), 540, 150)
sc.add(oxf, 500, 154)
sack = bake('sack', lambda: (lambda m: (m.add(__import__('sdf').ellipsoid((0, 3.0, 0), (3.6, 3.2, 3.2)), 'sack', 0.0), m)[1])(__import__('sdf').Model()), (14, 12), 1.8, 0, pitch=24)
amph = sprite('amphora')
for i in range(26):
    x = rng.choice([rng.randint(200, 280), rng.randint(360, 440)]); y = rng.randint(132, 146)
    sc.add(sack if rng.random() < 0.7 else amph, x, y)
# the crowd: kneeling farmers seen from behind, porters with sacks, a mother with a child
kneel_back = bake('kneel_back', lambda: F.human(body='brown', legs='brown', kneel=True, arms=('forward', 'forward'), beard='mane'), (40, 62), 1.15, 200)
kneel_back2 = bake('kneel_back2', lambda: F.human(body='grey', robe=True, cloak='brown', head='hood', kneel=True, arms=('chest', 'chest')), (40, 62), 1.15, 160)
kneel_back3 = bake('kneel_back3', lambda: F.human(body='sack', legs='skin', kneel=True, arms=('forward', 'forward'), head='cap'), (40, 62), 1.15, 185)
porter = bake('porter', lambda: F.human(body='sack', legs='skin', arms=('down', 'sack'), sack=True, head='cap'), (40, 62), 1.15, 160)
porter2 = bake('porter2', lambda: F.human(body='brown', legs='skin', arms=('down', 'sack'), sack=True, head='bare', hair='mane', beard='mane'), (40, 62), 1.15, 200)
mother = bake('mother', lambda: F.human(body='grey', robe=True, cloak='blue', head='hood', arms=('chest', 'down'), thin=0.92), (40, 62), 1.15, 180)
kid = bake('kid', lambda: F.child(body='blue', legs='skin', arms=('down', 'up')), (30, 44), 1.15, 190)
crowd = [kneel_back, kneel_back2, kneel_back3]
for row, y in enumerate((178, 200, 224, 250)):
    for i in range(9 - row % 2):
        x = 150 + i * 42 + (21 if row % 2 else 0) + rng.randint(-6, 6)
        sc.add(crowd[(i + row) % 3], x, y + rng.randint(-3, 3))
sc.add(porter, 300, 162); sc.add(porter2, 352, 166); sc.add(porter, 254, 168)
sc.add(mother, 70, 220); sc.add(kid, 88, 224)
sc.add(bake('kneel_side', lambda: F.human(body='brown', legs='brown', kneel=True, arms=('forward', 'forward'), beard='mane'), (40, 62), 1.15, 250), 600, 214)
sc.add(sprite('legionary0'), 40, 172); sc.add(sprite('legionary3', flip=True), 604, 176)

sc.compose_items()
amb = C('3a3a7c') * 0.72
sun = C('ff9a66') * 0.92
img = sc.lit(amb, sun, shadow_strength=0.92)
for (x, y) in fires:
    img = sc.glow(img, x, y, 36, (1.0, 0.55, 0.2), 0.14)
# smoke drifting from the braziers
img = fog(img, C('6a4a50'), 0.35, 0, 90, seed=12)
img = fog(img, C('e8906a'), 0.16, 150, 272, seed=13)
# dust motes in the red light
r2 = random.Random(3)
for i in range(70):
    x, y = r2.randint(0, W - 1), r2.randint(0, H - 1)
    img[y, x] = img[y, x] * 0.4 + C('ffc890') * 0.7
img = grade(img, C('1c1438'), gamma=1.05, sat=1.0, vignette=0.6, contrast=1.16)
pic = to_image(img, colors=0)
pic.save('slide2_pic.png')
out = present_slide(pic, 1, 5, '收成连续三年歉收。国王宣布举行一场大祭，派出账官四处征收：粮食、牲畜，还有圣物。')
out.save('slide2.png')
