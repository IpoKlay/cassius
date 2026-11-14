"""Kingdom-style 4: rainy night, the fort gate stands open; refugees with lanterns walk in along the river, Cassius waits under the standard."""
from kingdom import *
from slidekit import bake, present_slide
import figures3d as F, buildings3d as B, props3d as PR, cassius3d as CA, legionary3d as L
rng = np.random.default_rng(44)
cv = Canvas()
GY = 194
MOON = (130, 52)
sky(cv, ['060a1a', '0c1430', '16224a', '22305a', '30406a'], 0, GY, glow=0.0)
cloudbanks(cv, 404, ((26, 14), (60, 10), (96, 8)), (C('141c38'), C('1e2848')), C('6a7aa8'), lit_dir=1)
sun(cv, MOON[0], MOON[1], C('b8c8f0'), 9, 0.7)
hills(cv, 166, 22, 41, C('1a2440'), C('3a4a72'))
treeline(cv, 178, 18, 42, C('121a32'), C('2a3858'), bumps=6)
for i in range(14):
    x = 6 + i * 47 + (i * 19 % 13)
    foliage_tree(cv, x, GY - 2, 60 + (i * 31 % 26), ramp('3a4a6a', '2a3654', '1e2842', '141c32'), ramp('2a2a3a', '1e1e2c', '141420'), 700 + i, light=(-1, -1), spread=0.9, kind='pine' if i % 3 == 0 else 'oak')
# the fort on the right: stake wall, gatehouse with towers, gate wide open and lit
FX = 452
wall = np.zeros((H, W), bool)
for x0 in range(FX - 70, W, 6):
    tip = GY - 54 + (x0 * 13 % 5)
    wall |= poly([(x0, GY), (x0 + 6, GY), (x0 + 6, tip + 5), (x0 + 3, tip), (x0, tip + 5)])
towers = poly([(FX - 46, GY), (FX - 22, GY), (FX - 22, GY - 96), (FX - 46, GY - 96)]) | poly([(FX + 22, GY), (FX + 46, GY), (FX + 46, GY - 96), (FX + 22, GY - 96)])
bridge = poly([(FX - 22, GY - 62), (FX + 22, GY - 62), (FX + 22, GY - 74), (FX - 22, GY - 74)])
roofs = poly([(FX - 52, GY - 94), (FX - 16, GY - 94), (FX - 34, GY - 114)]) | poly([(FX + 16, GY - 94), (FX + 52, GY - 94), (FX + 34, GY - 114)])
wall |= towers | bridge
wall &= ~poly([(FX - 22, GY), (FX + 22, GY), (FX + 22, GY - 62), (FX - 22, GY - 62)])
cv.grad(wall, ((XX % 6) / 6.0) * 0.5 + 0.3, ramp('6a5a6a', '4a3e52', '342c40', '221c2e'))
cv.fill(wall & (XX % 6 == 5) & ~towers, C('140e1c'))
cv.fill(towers & ((YY - GY) % 8 == 0), C('1a1424')); cv.fill(towers & (((XX - FX) % 12 == 0) & ~((YY - GY) % 16 < 8)), C('1a1424'))
cv.fill(roofs, C('241a2c')); cv.fill(rim(roofs, -1, 0), C('6a6a98'))
gate_in = poly([(FX - 22, GY), (FX + 22, GY), (FX + 22, GY - 62), (FX - 22, GY - 62)])
cv.grad(gate_in, (YY - (GY - 62)) / 62.0, ramp('ffe0a0', 'ffc070', 'e89850', 'b86a3a'))
cv.fill(gate_in & (YY > GY - 26) & (np.abs(XX - FX - 6) < 10) & (YY < GY - 4 - np.abs(XX - FX - 6)), C('a0603a'))   # tent inside
for sgn in (-1, 1):
    leaf = poly([(FX + sgn * 22, GY), (FX + sgn * 30, GY + 1), (FX + sgn * 30, GY - 60), (FX + sgn * 22, GY - 62)])
    cv.fill(leaf, C('4a2e22')); cv.fill(rim(leaf, -sgn, 0), C('ffb070'))
for wx in (FX - 34, FX + 34):
    cv.fill(poly([(wx - 2, GY - 76), (wx + 2, GY - 76), (wx + 2, GY - 68), (wx - 2, GY - 68)]), C('ffc060'))
# night: darken everything drawn so far, then light it again
ambient(cv, C('8890c0') * 0.62)
pointlight(cv, FX, GY - 30, 90, C('ffa860'), 0.9)
for tx in (FX - 54, FX + 54, FX - 70 - 60, 600):
    cv.fill(line((tx, GY - 66 if abs(tx - FX) < 60 else GY - 52), (tx, GY - 56 if abs(tx - FX) < 60 else GY - 42), 1), C('3a2a2a'))
    ty = GY - 66 if abs(tx - FX) < 60 else GY - 52
    flame(cv, tx, ty, 0.8, tx); pointlight(cv, tx, ty - 4, 34, C('ff9040'), 0.75)
# the standard above the gate
vex = bake('k_vex_front', lambda: PR.vexillum_model(0.5), (24, 70), 1.0, 0)
put(cv, vex, FX, GY - 74, tint=C('ffc8a0'))
# Cassius on horseback at the gate, legionaries holding torches
horse = bake('k_horse_left', lambda: CA.horse_rider(0.0), (80, 80), 1.0, 180, pitch=10)
put(cv, horse, FX - 52, GY + 2, tint=C('d8b0a0'), rim_col=C('ffb070'), rim_dir=1)
legl = bake('k_leg_m90', lambda: L.legionary_model(0.0), (40, 62), 1.0, -90)
for x in (FX + 70, FX + 100):
    put(cv, legl, x, GY + 1, tint=C('a8a0c0'), rim_col=C('ff9a50'), rim_dir=-1)
# refugees walking in from the left, lanterns and torches in hand
ref = [bake('k_ref_a', lambda: F.human(body='grey', robe=True, cloak='blue', head='hood', arms=('chest', 'down'), thin=0.92), (40, 62), 0.95, 90),
       bake('k_ref_b', lambda: F.human(body='brown', robe=True, cloak='grey', head='bare', hair='linen', beard='linen', arms=('down', 'staff'), staff=True), (40, 62), 0.95, 90),
       bake('k_ref_c', lambda: F.human(body='sack', legs='skin', arms=('down', 'sack'), sack=True, head='cap', beard='mane'), (40, 62), 0.95, 90),
       bake('k_ref_d', lambda: F.human(body='red', robe=True, cloak='brown', head='hood', arms=('forward', 'down'), lantern=True, thin=0.9), (40, 62), 0.95, 90),
       bake('k_ref_kid', lambda: F.child(body='blue', legs='skin', arms=('down', 'up')), (30, 44), 0.95, 90),
       bake('k_ref_e', lambda: F.human(body='green', legs='skin', arms=('sack', 'down'), head='bare', hair='brown'), (40, 62), 0.95, 90)]
cartr = bake('k_handcart_r', B.handcart, (40, 26), 1.6, 90, pitch=14)
line_up = [(0, 60), (4, 74), (3, 96), (2, 118), (1, 140), (5, 196), (0, 214), (4, 228), (3, 250), (2, 276), (1, 300), (5, 326), (0, 346), (3, 368)]
for i, (k, x) in enumerate(line_up):
    near_gate = np.clip(1 - abs(x - FX) / 260, 0, 1)
    tint = mix(C('7880a8'), C('f0c8a8'), near_gate)
    put(cv, ref[k], x, GY + 1, tint=tint, rim_col=mix(C('8a9ac8'), C('ffb070'), near_gate), rim_dir=1)
    if k == 3:
        pointlight(cv, x + 9, GY - 22, 22, C('ffb050'), 0.7)
        cv.fill(ellipse(x + 9, GY - 21, 1.5, 2), C('fff0b0'))
put(cv, cartr, 168, GY + 1, tint=C('8088b0'), rim_col=C('9aa8d0'))
grass_strip(cv, GY, C('5a6a6a'), C('2a3438'), C('16181e'), 44, h=5)
reflect(cv, GY + 5, C('0e1428'), dark=0.6, seed=4, streak=(FX, 18, C('ffc070')))
# rain
for i in range(650):
    x, y = rng.integers(0, W), rng.integers(0, H)
    for k in range(rng.integers(3, 6)):
        yy_, xx_ = y + k, x - k // 3
        if 0 <= yy_ < H and 0 <= xx_ < W:
            cv.img[yy_, xx_] = cv.img[yy_, xx_] * 0.72 + C('8aa0d0') * 0.28
for i in range(260):                                                 # rain rings on the water
    x, y = rng.integers(2, W - 4), rng.integers(GY + 8, H)
    cv.img[y, x - 1:x + 2] = cv.img[y, x - 1:x + 2] * 0.5 + C('b0c0e0') * 0.5
pic = cv.save('k4_pic.png')
present_slide(pic, 3, 5, '卡西乌斯驻守一座边境要塞。难民来时，他打开城门，许下承诺：只要军旗还在，你们就能留下。').save('k4.png')
