"""Kingdom-style 5: cold dawn, the column leaves the fort along the riverbank toward the rising sun."""
from kingdom import *
from slidekit import bake, present_slide
import figures3d as F, legionary3d as L, cassius3d as CA, props3d as PR
rng = np.random.default_rng(55)
cv = Canvas()
GY = 192
SUN = (548, 136)
sky(cv, ['1e2642', '2e3a5c', '4e5878', '86809a', 'c49aa0', 'eab69a', 'f8d6aa'], 0, GY, sun=SUN, sun_col=C('ffe2b0'), glow=0.0)
cloudbanks(cv, 501, ((36, 12), (70, 9), (112, 7)), (C('4a4c70'), C('6a6488')), C('f8c8a8'))
sun(cv, SUN[0], SUN[1], C('ffe2b0'), 11)
for k in range(40):
    x, y = rng.integers(0, W), rng.integers(0, 60); cv.img[y, x] = mix(cv.img[y, x], C('ffffff'), 0.5)
hz = C('c8a8b0')
hills(cv, 172, 26, 7, mix(C('7a7896'), hz, 0.45), mix(C('f0c8b0'), hz, 0.3))
treeline(cv, 180, 18, 8, mix(C('4e5878'), hz, 0.35), mix(C('d8b0a8'), hz, 0.2), bumps=5)
mist = np.clip(1 - np.abs(YY - 178) / 9.0, 0, 1)
q = np.floor(mist * 4 + BAY) / 4 * 0.55; cv.img = cv.img * (1 - q[:, :, None]) + q[:, :, None] * C('e0c8c8')
treeline(cv, 188, 22, 9, C('2e3854'), C('8a7a90'), bumps=6)
for (x, h) in ((14 + i * 37 + (i * 53 % 13), 60 + (i * 29 % 25)) for i in range(18) if not 500 < 14 + i * 37 < 590):
    foliage_tree(cv, x, GY - 2, h, ramp('7a7898', '5a5e80', '444a6a', '343a58'), ramp('4a4258', '3a3448', '2a2638'), 900 + x, light=(1, -1), spread=0.9)
for (x, h) in ((236, 46), (252, 38), (420, 52), (436, 40), (604, 58)):
    foliage_tree(cv, x, GY, h, ramp('8a8aa0', '5a6482', '3a4462', '262e48'), ramp('6a5a6a', '4a3e4e', '2e2634'), int(x), light=(1, -1), kind='pine')
foliage_tree(cv, 330, GY, 120, ramp('c8a890', '7a8a7a', '4a5e5e', '2e3e46', '1c2834'), ramp('8a6a5a', '5a4440', '3a2a2c'), 330, light=(1, -1))
# the fort at the left: stake wall, gatehouse with the gate open, dying torches, people watching
wall = np.zeros((H, W), bool)
for x0 in range(0, 170, 6):
    tip = GY - 52 + (x0 * 13 % 5)
    wall |= poly([(x0, GY), (x0 + 6, GY), (x0 + 6, tip + 5), (x0 + 3, tip), (x0, tip + 5)])
gate = poly([(92, GY), (150, GY), (150, GY - 82), (92, GY - 82)])
roof = poly([(86, GY - 80), (156, GY - 80), (121, GY - 104)])
wall |= gate
cv.grad(wall, ((XX % 6) / 6.0) * 0.6 + np.clip((GY - YY) / 140, 0, 0.4), ramp('b08a7a', '7a5e5a', '54404a', '362a36'))
cv.fill(wall & (XX % 6 == 5), C('241c28'))
cv.fill(wall & ((YY == GY - 20) | (YY == GY - 40)), C('3a2c34'))
cv.fill(roof, C('3a2c3a')); cv.fill(rim(roof, 1, 0), C('e8b8a0')); cv.fill(roof & ((XX + YY) % 4 == 0), C('4a3a48'))
door = poly([(108, GY), (134, GY), (134, GY - 40), (108, GY - 40)]) | ellipse(121, GY - 40, 13, 10)
cv.fill(door, C('f0c890')); cv.fill(door & (YY > GY - 12), C('c89060'))
pointlight(cv, 121, GY - 24, 34, C('ffb070'), 0.6)
for tx in (88, 156):
    cv.fill(line((tx, GY - 60), (tx, GY - 50), 1), C('3a2a2a')); flame(cv, tx, GY - 60, 0.6, tx)
    pointlight(cv, tx, GY - 62, 18, C('ff9050'), 0.5)
# the column: Cassius on horseback with the standard ahead, legionaries behind, an ox cart at the tail
def tint_for(x):
    d = abs(x - SUN[0]) / 400
    return mix(C('fff0e0'), C('b8b0c8'), np.clip(d, 0, 1))
horse = bake('k_horse_side', lambda: CA.horse_rider(0.0), (80, 80), 1.0, 0, pitch=10)
vex = bake('k_vex_side', lambda: PR.vexillum_model(0.3), (24, 70), 1.0, 0)
leg = [bake(f'k_leg90_{s}', lambda s=s: L.legionary_model(s), (40, 62), 1.0, 90) for s in (0.0, 0.25, 0.5, 0.75)]
cart = bake('k_cart_side', lambda: PR.cart_model(0.0), (70, 50), 1.0, 0, pitch=12)
ox = bake('k_ox_side', lambda: PR.ox_model(0.3), (70, 50), 1.0, 0, pitch=12)
put(cv, cart, 188, GY + 1, tint=tint_for(188), rim_col=C('ffd8b0'))
put(cv, ox, 236, GY + 1, tint=tint_for(236), rim_col=C('ffd8b0'))
for k in range(9):
    x = 270 + k * 19 + (k % 2) * 3
    put(cv, leg[k % 4], x, GY + 1 + (k % 2), tint=tint_for(x), rim_col=C('ffe0b8'))
put(cv, vex, 456, GY + 1, tint=tint_for(456), rim_col=C('ffe0b8'))
put(cv, leg[1], 446, GY + 1, tint=tint_for(452), rim_col=C('ffe0b8'))
put(cv, horse, 496, GY + 2, tint=tint_for(496), rim_col=C('fff0c8'))
# villagers at the gate watching, a child waving
vil = [bake('k_vil_a', lambda: F.human(body='brown', robe=True, cloak='grey', head='hood', arms=('chest', 'down'), thin=0.92), (40, 62), 0.92, -70),
       bake('k_vil_b', lambda: F.child(body='blue', legs='skin', arms=('down', 'up')), (30, 44), 0.92, -70),
       bake('k_vil_c', lambda: F.human(body='green', legs='skin', head='bare', hair='brown', beard='brown', arms=('down', 'staff'), staff=True), (40, 62), 0.92, -70)]
for (a, x) in zip(vil, (116, 130, 148)):
    put(cv, a, x, GY + 1, tint=C('d8c8c8'), rim_col=C('ffc890'), rim_dir=1)
grass_strip(cv, GY, C('a8b090'), C('4a5a4a'), C('2a2a2e'), 5, h=5, flowers=[C('f0d8e0'), C('e8e0a0')])
# crows rising over the road
for (bx, by, s, f) in ((360, 96, 1.0, 0.2), (378, 88, 0.9, 0.6), (396, 100, 0.8, 0.85)):
    cv.fill(crow(bx, by, s, f), C('2a2a3a'))
reflect(cv, GY + 5, C('2a3450'), dark=0.6, seed=5, streak=(SUN[0], 14, C('ffe0b0')))
pic = cv.save('k5_pic.png')
present_slide(pic, 4, 5, '粮仓快空了。帝国的回复是一道敕令：重开北路，收齐各地所欠，送往大祭场——你的要塞就能分到口粮。七十人，四十五斗粮。出发。').save('k5.png')
