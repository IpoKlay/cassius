"""Illustration 4 - the gate opened: warm light spilling into a cold rainy night, refugees walking into it, Cassius in the gateway."""
from illus import *
from slidekit import present_slide
rng = np.random.default_rng(4)
cv = Canvas()
GX, GY = 320, 206                    # gate centre bottom
# night sky with torn clouds and a hidden moon
cv.grad(np.ones((H, W), bool), YY / 200.0, ramp('080c1c', '0e1428', '141c36', '1c2640', '263048'))
n = fbm(W, H, 41, cells=(120, 50, 20, 8))
cv.glow(470, 46, 70, C('8090c0'), 0.4)
cv.fill(ellipse(470, 46, 12, 12), C('dfe6ff'))
cl = (n > 0.5) & (np.hypot(XX - 470, YY - 46) > 20)
cv.grad(cl & (YY < 150), 1 - (n - 0.5) * 3, ramp('3a4664', '2a3450', '1c2440', '141a30'))
cv.fill(cl & (YY < 150) & ~np.roll(cl, -1, 0) & ~np.roll(cl, -2, 0) & (np.hypot(XX - 470, YY - 46) < 90) & (n > 0.53), C('8a96bc'))
# far hills
far, _ = ridge(190, 20, 7, (80, 30, 10))
cv.fill(far, C('121a2c'))
# the fort: towers, palisade walls, gatehouse
wall = poly([(0, 150), (640, 150), (640, 214), (0, 214)])
stakes = np.zeros((H, W), bool)
for x in range(0, W, 7):
    tip = 140 + (x * 7919 % 5)
    stakes |= poly([(x, 214), (x + 6, 214), (x + 6, tip + 6), (x + 3, tip), (x, tip + 6)])
wallm = (stakes | wall) & ~((XX > GX - 60) & (XX < GX + 60))
cv.grad(wallm, (XX % 7) / 7.0, ramp('2a2a34', '1e1e28', '14141c'))
cv.fill(wallm & (XX % 7 == 6), C('0a0a10'))
for (tx, w_) in ((GX - 74, 30), (GX + 74, 30)):
    tw = poly([(tx - w_ / 2, 214), (tx + w_ / 2, 214), (tx + w_ / 2 - 2, 96), (tx - w_ / 2 + 2, 96)])
    roof = poly([(tx - w_ / 2 - 6, 98), (tx + w_ / 2 + 6, 98), (tx, 70)])
    cv.grad(tw, (XX - tx + w_ / 2) / w_, ramp('3a3440', '2a2632', '1c1a24', '121018'))
    cv.fill(tw & (YY % 6 == 0), C('0e0c14'))
    cv.fill(roof, C('1a1420')); cv.fill(rim(roof, 1 if tx < GX else -1, 0), C('ff9a50'))
    cv.fill(poly([(tx - 3, 130), (tx + 3, 130), (tx + 3, 140), (tx - 3, 140)]), C('ffb060'))
    cv.glow(tx, 135, 18, C('ff9040'), 0.3)
    # torches on the tower tops
    cv.glow(tx + (12 if tx > GX else -12), 102, 26, C('ff8a30'), 0.6)
    cv.fill(poly([(tx + (12 if tx > GX else -12) - 2, 102), (tx + (12 if tx > GX else -12) + 2, 102), (tx + (12 if tx > GX else -12), 94)]), C('ffe080'))
lintel = poly([(GX - 60, 214), (GX + 60, 214), (GX + 60, 112), (GX - 60, 112)]) & ~poly([(GX - 34, 214), (GX + 34, 214), (GX + 34, 128), (GX - 34, 128)])
cv.grad(lintel, (YY - 112) / 100.0, ramp('2e2a32', '201c26', '16121a'))
cv.fill(lintel & ((XX - GX) % 9 == 0), C('0e0a10'))
# light inside the gate: the camp, fires, tents, people
inside = poly([(GX - 34, 214), (GX + 34, 214), (GX + 34, 128), (GX - 34, 128)])
cv.grad(inside, (YY - 128) / 86.0, ramp('ffe0a0', 'ffc070', 'f0a050', 'd07a3a'))
tents = poly([(GX - 34, 196), (GX - 16, 170), (GX + 2, 196)]) | poly([(GX + 6, 196), (GX + 22, 176), (GX + 34, 190), (GX + 34, 196)])
cv.fill(tents & inside, C('b06a3a')); cv.fill(rim(tents, 0, -1) & inside, C('ffe8b0'))
cv.fill(inside & (YY > 196), C('c07040'))
# open gate leaves swung inward, seen edge-on
for sgn in (-1, 1):
    leaf = poly([(GX + sgn * 34, 214), (GX + sgn * 26, 210), (GX + sgn * 26, 134), (GX + sgn * 34, 128)])
    cv.fill(leaf, C('4a2e1e')); cv.fill(rim(leaf, -sgn, 0), C('ffc080'))
# the banner above the gate
pole = line((GX, 128), (GX, 70), 1) | line((GX - 12, 76), (GX + 12, 76), 1)
flag = poly([(GX - 11, 77), (GX + 11, 77), (GX + 11, 104), (GX, 98), (GX - 11, 104)])
cv.fill(pole, C('2a1a10')); cv.fill(flag, C('a01c1c'))
cv.fill(rim(flag, 0, 1), C('e05030')); cv.fill(ellipse(GX, 86, 4, 4) & ~ellipse(GX, 86, 2, 2), C('e8c060'))
cv.fill(poly([(GX - 4, 70), (GX + 4, 70), (GX, 62)]), C('e8c060'))
cv.glow(GX, 90, 30, C('ff6a30'), 0.25)
cv.glow(GX, 190, 140, C('ff9a4a'), 0.35, sx=1.5)
# Cassius in the gateway, arm out, cloak and crest against the light
cas = figure(GX + 4, 212, 50, pose='stand', facing=-1, helmet=True, cloak=True)
cas |= ellipse(GX + 3, 166, 8, 6) & (YY < 166)
cas |= capsule((GX - 2, 176), (GX - 16, 186), 2.5) | capsule((GX - 16, 186), (GX - 26, 182), 2)
cv.fill(cas, C('120a0c'))
cv.fill(rim(cas, 0, -1) & (YY < 172), C('ff7a3a'))
# muddy road with puddles reflecting the light, widening toward us
road = poly([(GX - 34, 214), (GX + 34, 214), (GX + 200, 272), (GX - 200, 272)])
ground = YY >= 214
cv.grad(ground, (YY - 214) / 58.0, ramp('1c1a22', '16141c', '100e14'))
cv.grad(road, (YY - 214) / 58.0, ramp('5a3a2a', '3a2820', '2a1e1a', '1e1618'))
for (px, py, rx, ry) in ((GX - 14, 228, 18, 3), (GX + 30, 240, 26, 4), (GX - 50, 254, 34, 5), (GX + 10, 264, 44, 5)):
    pm = ellipse(px, py, rx, ry)
    cv.fill(pm, C('241c28'))
    refl = pm & (np.abs(XX - GX) < 22 + (py - 214) * 0.9)
    cv.fill(refl, C('d08048')); cv.fill(refl & ((YY % 2 == 0) | ((XX + YY) % 3 == 0)), C('ffc878'))
    cv.fill(pm & ~refl & ((XX + YY) % 4 == 0), C('3a3448'))
# refugees walking in, from big foreground silhouettes to small ones at the gate
people = []
for i, (x, gy, h, kw) in enumerate((
        (GX - 20, 216, 20, dict(pack=True)), (GX + 18, 218, 22, dict(staff=True, hood=True)), (GX - 46, 222, 26, dict(child=14)),
        (GX + 52, 226, 30, dict(pack=True, hood=True)), (GX - 96, 236, 42, dict(cloak=True, hood=True, staff=True)),
        (GX + 110, 242, 48, dict(pack=True)), (GX - 10, 246, 52, dict(child=16, hood=True)),
        (GX - 170, 272, 96, dict(pack=True, hood=True, cloak=True)), (GX + 176, 272, 104, dict(staff=True, hood=True, cloak=True)),
        (GX + 60, 272, 74, dict(child=22, cloak=True)))):
    m = figure(x, gy, h, facing=1 if x < GX else -1, phase=i * 0.31, **kw)
    m &= ~((XX - x) ** 2 > 0) | True
    people.append((h, m))
people.sort(key=lambda p: p[0])
for h, m in people:
    k = np.clip((h - 20) / 90, 0, 1)
    cv.fill(m, C('1e1418') * (1 - k) + C('08060a') * k)
    cv.fill(rim(m, 0, -1) | (rim(m, 1, 0) & (XX < GX)) | (rim(m, -1, 0) & (XX > GX)), C('ffb060') * (1 - k * 0.2))
# a mother carrying a baby, close in the left corner, looking up
mom = figure(80, 272, 120, pose='stand', facing=1, hood=True, robe=True)
mom |= ellipse(96, 186, 10, 8)
cv.fill(mom, C('06040a')); cv.fill(rim(mom, 1, 0) | rim(mom, 0, -1), C('ffa050'))
# rain
for i in range(900):
    x, y = rng.integers(0, W), rng.integers(0, H)
    L = rng.integers(3, 7)
    for k in range(L):
        yy_, xx_ = y + k, x - k // 2
        if 0 <= yy_ < H and 0 <= xx_ < W:
            cv.img[yy_, xx_] = cv.img[yy_, xx_] * 0.55 + C('a0b4d8') * 0.45
pic = cv.save('il4_pic.png')
present_slide(pic, 3, 5, '卡西乌斯驻守一座边境要塞。难民来时，他打开城门，许下承诺：只要军旗还在，你们就能留下。').save('il4.png')
