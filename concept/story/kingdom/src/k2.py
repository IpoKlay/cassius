"""Kingdom-style 2: the King's decree at sunset - temple, tribute piling up, porters and oxen walking in along the river."""
from kingdom import *
from slidekit import bake, present_slide
import sdf, figures3d as F, buildings3d as B, props3d as PR
rng = np.random.default_rng(22)
cv = Canvas()
GY = 194
SUN = (392, 140)
sky(cv, ['2a1030', '521838', '8a2438', 'c03c38', 'e86a3e', 'f8a85a', 'fcd690'], 0, GY, sun=SUN, sun_col=C('ffc070'), glow=0.0)
cloudbanks(cv, 202, ((30, 12), (62, 9), (102, 7)), (C('5a1a3a'), C('7a2440')), C('ffa060'))
sun(cv, SUN[0], SUN[1], C('ffb060'), 18, 1.2)
hz = C('e0805a')
hills(cv, 168, 24, 21, mix(C('8a3048'), hz, 0.35), mix(C('ffb070'), hz, 0.2))
treeline(cv, 178, 16, 22, mix(C('5a2038'), hz, 0.25), mix(C('e08060'), hz, 0.3), bumps=5)
# withered trees: dry crowns and bare branches
def dead_tree(x, gy, h, col, lit):
    m = capsule((x, gy), (x + 2, gy - h * 0.7), max(1.5, h * 0.05))
    r2 = np.random.default_rng(int(x))
    for k in range(6):
        y0 = gy - h * r2.uniform(0.35, 0.7); a = r2.uniform(-1, 1)
        x1, y1 = x + a * h * 0.35, y0 - h * r2.uniform(0.15, 0.35)
        m |= capsule((x + 1, y0), (x1, y1), max(1, h * 0.025))
        m |= capsule((x1, y1), (x1 + a * h * 0.1, y1 - h * 0.1), 0.7)
    cv.fill(m, col); cv.fill(rim(m, 1, 0), lit)
for i in range(16):
    x = 8 + i * 41 + (i * 17 % 11)
    if abs(x - SUN[0]) < 40: continue
    if i % 3 == 0:
        dead_tree(x, GY - 2, 50 + i * 3 % 20, C('3a1428'), C('c86048'))
    else:
        foliage_tree(cv, x, GY - 2, 56 + (i * 23 % 24), ramp('d88a50', 'a85a3a', '7a3a32', '52222c'), ramp('6a2a2a', '4a1c24', '30121a'), 300 + i, light=(1, -1), spread=0.85)
# the temple, backlit, with braziers and banners
temple = bake('k_temple_big', lambda: B.temple_front(6, 9.0, 30.0, 10.0), (280, 160), 2.3, 0, pitch=8)
put(cv, temple, 196, GY + 1, tint=C('e8b8a8'))
tw = temple.shape[1]
for bx in (196 - tw // 2 + 6, 196 + tw // 2 - 6):
    br = bake('k_brazier', B.brazier, (14, 22), 1.6, 0)
    put(cv, br, bx, GY + 1, tint=C('d8a898'))
    flame(cv, bx, GY - br.shape[0] + 2, 1.0, bx)
    pointlight(cv, bx, GY - br.shape[0] - 2, 40, C('ffa050'), 0.7)
for bx in (196 - 56, 196 + 56):                                           # long red banners hanging from the entablature
    top = GY - temple.shape[0] + 40
    ban = poly([(bx - 7, top), (bx + 7, top), (bx + 7, top + 70), (bx, top + 62), (bx - 7, top + 70)])
    cv.fill(ban, C('9a1c22')); cv.fill(ban & (XX == bx + 6), C('d84a34')); cv.fill(ban & (np.abs(YY - top - 10) < 2), C('e8b050'))
# the king on the top step, priests beside him
king = bake('k_king', lambda: F.human(body='purple', robe=True, cloak='red', head='crown', beard='linen', arms=('up', 'down'), staff=True, belt='gold', sleeve='purple'), (40, 62), 1.0, 0)
pri = bake('k_priest', lambda: F.human(body='linen', robe=True, cloak='linen', head='hood', arms=('up', 'up'), belt='red'), (40, 62), 0.95, 0)
step_y = GY - 15
put(cv, pri, 160, step_y, tint=C('f0d0c0')); put(cv, pri[:, ::-1], 232, step_y, tint=C('f0d0c0'))
put(cv, king, 196, step_y - 2, tint=C('fff0e0'), rim_col=C('ffc080'))
pointlight(cv, 196, step_y - 30, 30, C('ffd090'), 0.35)
# tribute piled at the foot of the steps
sack = bake('k_sack', lambda: (lambda m: (m.add(sdf.ellipsoid((0, 3.0, 0), (3.6, 3.2, 3.2)), 'sack', 0.0), m)[1])(sdf.Model()), (14, 12), 1.6, 0, pitch=20)
amph = bake('k_amph', PR.amphora_model, (14, 22), 1.3, 0)
crate = bake('k_crate', lambda: PR.crate_model(3.0), (16, 16), 1.3, 20)
for (a, x, dy) in ((crate, 300, 0), (sack, 312, 0), (sack, 322, 0), (sack, 317, -8), (amph, 332, 0), (amph, 340, 1), (crate, 292, 0), (sack, 298, -11)):
    put(cv, a, x, GY + 1 + dy, tint=C('f0c0a8'), rim_col=C('ffb070'), rim_dir=1)
# the ledger officer counting, porters and an ox cart coming in from the right
clerk = bake('k_clerk', lambda: F.human(body='red', legs='skin', cloak='gold', head='bare', hair='brown', arms=('forward', 'forward'), scroll=True), (40, 62), 1.0, 90)
put(cv, clerk, 356, GY + 1, tint=C('f8d8c0'), rim_col=C('ffc890'), rim_dir=1)
porters = [bake('k_porter_a', lambda: F.human(body='sack', legs='skin', arms=('down', 'sack'), sack=True, head='cap'), (40, 62), 0.95, -90),
           bake('k_porter_b', lambda: F.human(body='brown', legs='skin', arms=('down', 'sack'), sack=True, head='bare', hair='mane', beard='mane'), (40, 62), 0.95, -90),
           bake('k_porter_c', lambda: F.human(body='green', legs='skin', robe=False, head='hood', arms=('down', 'sack'), sack=True, thin=0.9), (40, 62), 0.92, -90)]
for i, x in enumerate((384, 408, 440, 462, 590, 614)):
    put(cv, porters[i % 3], x, GY + 1, tint=mix(C('ffe0c8'), C('d8a8a0'), min(1, abs(x - SUN[0]) / 300)), rim_col=C('ffb070'), rim_dir=-1 if x > SUN[0] else 1)
ox = bake('k_ox_l', lambda: PR.ox_model(0.6), (70, 50), 1.0, 180, pitch=12)
cart = bake('k_cart_l', lambda: PR.cart_model(0.4), (70, 50), 1.0, 180, pitch=12)
put(cv, ox, 498, GY + 1, tint=C('f0c8b0'), rim_col=C('ffb070'), rim_dir=-1)
put(cv, cart, 548, GY + 1, tint=C('f0c8b0'), rim_col=C('ffb070'), rim_dir=-1)
grass_strip(cv, GY, C('d8a060'), C('7a4a30'), C('3a1e1e'), 22, h=5)
# dead wheat along the bank
for i in range(70):
    x = rng.integers(330, 640) if i < 50 else rng.integers(0, 120)
    h = rng.integers(6, 14); lean = rng.choice([-1, 1])
    cv.fill(line((x, GY + 1), (x + lean, GY - h), 1), C('8a5a34'))
    cv.fill(ellipse(x + lean * 2, GY - h + 2, 0.8, 1.8), C('c88a48'))
for (bx, by, s, f) in ((420, 70, 1.0, 0.1), (436, 62, 0.9, 0.5), (300, 84, 0.8, 0.8)):
    cv.fill(crow(bx, by, s, f), C('2a0e20'))
reflect(cv, GY + 5, C('3a1428'), dark=0.62, seed=2, streak=(SUN[0], 16, C('ffc070')))
pic = cv.save('k2_pic.png')
present_slide(pic, 1, 5, '收成连续三年歉收。国王宣布举行一场大祭，派出账官四处征收：粮食、牲畜，还有圣物。').save('k2.png')
