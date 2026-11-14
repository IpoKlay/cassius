"""Illustration 2 - the King's decree: a great altar burning against a red sun, a procession of tribute, a farmer kneeling in dead wheat."""
from illus import *
from slidekit import present_slide
rng = np.random.default_rng(2)
cv = Canvas()
SUNX, SUNY = 452, 150
# sky
sky = ramp('2a0e2e', '4a1236', '6e1a38', '9a2836', 'c2402e', 'e0642c', 'f29438', 'fac25a')
t = np.clip((YY - 0) / 180.0, 0, 1) ** 1.3 + np.clip(1 - np.hypot((XX - SUNX) / 2.2, YY - SUNY) / 260, 0, 1) * 0.35
cv.grad(np.ones((H, W), bool), t, sky)
# cloud streaks
n = fbm(W, H, 21, cells=(160, 60, 20, 8))
n2 = fbm(W, H, 33, cells=(60, 24, 10, 5))
for i, (cy_, th) in enumerate(((40, 7), (70, 4), (100, 6), (124, 3))):
    band_m = (np.abs(YY - cy_ - (n - 0.5) * 40 - np.sin(XX / 37.0 + i) * 4) < th * (n2 * 1.6 - 0.1)) & (n2 > 0.4)
    cv.fill(band_m, C('3a1030') if i < 2 else C('5a1a2e'))
    cv.fill(band_m & ~np.roll(band_m, -1, 0), C('ff9a50') if i > 1 else C('d0583a'))
# sun
cv.glow(SUNX, SUNY, 120, C('ff8a3a'), 0.55)
cv.fill(ellipse(SUNX, SUNY, 40, 40), C('ffe6a0'))
cv.fill(ellipse(SUNX, SUNY, 40, 40) & (np.abs((YY - SUNY) % 9 - 4) < 1) & (YY > SUNY + 6), C('f8b060'))
# far ranges
far, _ = ridge(176, 34, 3, (90, 40, 14))
cv.grad(far, (YY - 140) / 60.0, ramp('b04a4a', '8a3446', '6a2840'))
mid, mtop = ridge(196, 26, 5, (70, 30, 10))
cv.grad(mid, (YY - 170) / 50.0, ramp('6a2238', '4e1a32', '36122a'))
# altar hill and stepped altar right in front of the sun
hill = poly([(250, 272), (330, 200), (400, 180), (500, 178), (560, 196), (640, 214), (640, 272)])
cv.fill(hill, C('2a0e22'))
cv.fill(rim(hill, 0, -1), C('c25a3a'))
alt = np.zeros((H, W), bool)
for k, (hw, y0, y1) in enumerate(((74, 178, 166), (58, 166, 154), (44, 154, 142), (30, 142, 130), (18, 130, 120))):
    alt |= (np.abs(XX - SUNX) <= hw) & (YY >= y1) & (YY < y0)
cv.fill(alt, C('24081c'))
cv.fill(rim(alt, 0, -1), C('ff9a50'))
# stairs on the altar face
cv.fill(alt & (np.abs(XX - SUNX) < 7) & ((YY % 3) == 0), C('5a1e2a'))
# fire and smoke column
smoke = np.zeros((H, W)); 
for i in range(60):
    yy0 = 118 - i * 2.2
    xx0 = SUNX + 2 + max(0, i - 18) ** 1.6 * 0.45 + 4 * math.sin(i * 0.5)
    r = 6 + i * 0.5 + 3 * math.sin(i * 1.3)
    smoke = np.maximum(smoke, np.clip(1 - np.hypot(XX - xx0, (YY - yy0) * 1.2) / r, 0, 1))
smoke *= 0.5 + n2 * 1.1
sm = smoke > 0.35
cv.grad(sm, 1 - (smoke - 0.35) * 1.6, ramp('1e0a18', '3a1424', '5a2030', '7a2c34'))
cv.fill(sm & rim(sm, 1, 1) , C('d86040'))
fire = poly([(SUNX - 16, 121), (SUNX - 10, 104), (SUNX - 5, 112), (SUNX + 1, 92), (SUNX + 6, 108), (SUNX + 11, 100), (SUNX + 16, 121)])
cv.glow(SUNX, 112, 50, C('ffb050'), 0.7)
cv.fill(fire, C('ffd068'))
cv.fill(fire & (YY > 112), C('fff2c0'))
# the king on the top step, arms raised with a staff, the fire behind him
king = figure(SUNX - 22, 120, 30, pose='stand', robe=True, arms_up=True, facing=-1)
king |= line((SUNX - 22 - 5, 118), (SUNX - 22 - 6, 76), 1) | ellipse(SUNX - 28, 76, 2, 2)
king |= poly([(SUNX - 26, 91), (SUNX - 18, 91), (SUNX - 17, 86), (SUNX - 20, 89), (SUNX - 22, 85), (SUNX - 24, 89), (SUNX - 27, 86)])
cv.fill(king, C('120410'))
cv.fill(rim(king, 1, 0), C('ffb060'))
for sx_ in (-56, 56):                                                       # priests on the lower steps
    p = figure(SUNX + sx_ * 0.62, 154, 20, pose='stand', robe=True, hood=True, facing=-1 if sx_ > 0 else 1)
    cv.fill(p, C('1a0616')); cv.fill(rim(p, 0, -1), C('e07848'))
# procession up the hill: porters with sacks, oxen, banners
path = [(-10, 236), (120, 224), (230, 206), (330, 188), (380, 178)]
def on_path(u):
    seg = min(int(u * (len(path) - 1)), len(path) - 2); f = u * (len(path) - 1) - seg
    a, b = path[seg], path[seg + 1]
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
proc = np.zeros((H, W), bool)
for i in range(34):
    u = i / 34 + rng.uniform(-0.006, 0.006)
    x, y = on_path(u)
    h = 26 - u * 13
    if i % 7 == 3:
        bx = x; hh = h * 0.5
        proc |= ellipse(bx, y - hh * 0.9, hh * 1.1, hh * 0.55) | ellipse(bx + hh * 1.0, y - hh * 1.1, hh * 0.35, hh * 0.3)
        for lx in (-0.7, -0.4, 0.4, 0.7):
            proc |= line((bx + lx * hh, y - hh * 0.6), (bx + lx * hh, y), 1)
        proc |= line((bx + hh * 1.1, y - hh * 1.35), (bx + hh * 1.5, y - hh * 1.7), 1)
    elif i % 9 == 5:
        proc |= figure(x, y, h, facing=1, spear=h * 7, phase=i * 0.37)
        proc |= poly([(x + h * 0.25, y - h * 1.5), (x + h * 0.25 + h * 0.5, y - h * 1.45), (x + h * 0.25 + h * 0.5, y - h * 1.05), (x + h * 0.25, y - h * 1.1)])
    else:
        proc |= figure(x, y, h, facing=1, pack=(i % 2 == 0), phase=i * 0.37, hood=(i % 3 == 0))
road = np.zeros((H, W), bool)
for a, b in zip(path, path[1:]):
    road |= line(a, b, 3)
ground = poly([(0, 236), (120, 226), (230, 208), (330, 190), (400, 182), (400, 272), (0, 272)])
cv.fill(ground, C('2e0e22'))
cv.fill(rim(ground, 0, -1) & (XX < 380), C('8a3438'))
# dry furrows converging on the altar, cracked earth with lit lips
field = (ground | hill) & ~alt
for k in range(-26, 27):
    fx0 = SUNX + k * 34
    fur = line((fx0, 272), (SUNX + k * 3.2, 186), 1) & field & (YY > 186)
    cv.fill(fur, C('22081a'))
    cv.fill(np.roll(fur, 1, 1) & field & ~fur & (YY > 186), C('4a1828'))
for i in range(70):
    x0, y0 = rng.integers(160, 640), rng.integers(206, 250)
    L = rng.integers(3, 9); a = rng.uniform(-0.6, 0.6)
    cr = line((x0, y0), (x0 + L * math.cos(a), y0 + L * math.sin(a) * 0.4), 1)
    cv.fill(cr & field, C('16050f')); cv.fill(np.roll(cr, -1, 0) & field & ~cr, C('6a2a30'))
cv.fill(road & ground, C('4a1a2a'))
# a dead tree on the ridge, red standards lining the last stretch of the road
tree = capsule((532, 214), (538, 168), 3) | capsule((537, 186), (558, 166), 2) | capsule((538, 176), (520, 156), 2) | capsule((557, 167), (568, 160), 1) | capsule((522, 158), (516, 146), 1) | capsule((538, 168), (542, 150), 1.5)
cv.fill(tree, C('16060f')); cv.fill(rim(tree, -1, 0), C('c25a3a'))
for (bx, by, hh) in ((300, 196, 30), (340, 188, 26), (372, 182, 22)):
    pole = line((bx, by), (bx, by - hh), 1)
    flag = poly([(bx, by - hh), (bx + 7, by - hh), (bx + 7, by - hh + 12), (bx + 3.5, by - hh + 9), (bx, by - hh + 12)])
    cv.fill(pole, C('16060f')); cv.fill(flag, C('9a1a1a')); cv.fill(rim(flag, 1, 0), C('ff7040'))
cv.fill(proc, C('16060f'))
cv.fill(rim(proc, 1, 0), C('e07040'))
# foreground: cracked dry earth, dead wheat, a kneeling farmer with an empty basket
fg = poly([(0, 244), (90, 238), (200, 246), (330, 252), (470, 248), (640, 240), (640, 272), (0, 272)])
cv.fill(fg, C('120610'))
for i in range(40):
    x0 = rng.integers(0, W); y0 = rng.integers(250, 272)
    cv.fill(line((x0, y0), (x0 + rng.integers(-8, 8), y0 + rng.integers(1, 5)), 1), C('3a1420'))
cv.fill(rim(fg, 0, -1), C('6a2430'))
wheat = np.zeros((H, W), bool); ears = []
for (x0, cnt, hmin, hmax) in ((20, 14, 70, 130), (585, 16, 80, 150)):
    for k in range(cnt):
        bx = x0 + rng.integers(-24, 30); top = 272 - rng.integers(hmin, hmax)
        bend = rng.uniform(-1, 1) * 14
        pts = [(bx + bend * (s ** 2), 272 - (272 - top) * s) for s in np.linspace(0, 1, 12)]
        for a, b in zip(pts, pts[1:]):
            wheat |= line(a, b, 2)
        ex, ey = pts[-1]
        droop = 1 if bend > 0 else -1
        for j in range(6):                                                   # a drooping, empty ear
            ears.append(ellipse(ex + droop * j * 1.6, ey + j * 2.2, 1.8, 2.4) | line((ex + droop * j * 1.6, ey + j * 2.2), (ex + droop * (j * 1.6 + 5), ey + j * 2.2 - 4), 1))
E = np.any(ears, axis=0)
cv.fill(wheat | E, C('0e040a'))
cv.fill(rim(E, 1, -1), C('d0703a'))
cv.fill(rim(wheat, 1, 0) & (YY < 230) & ((XX + YY) % 3 == 0), C('6a2024'))
farmer = poly([(52, 272), (58, 238), (70, 206), (84, 188), (98, 182), (110, 186), (116, 196), (112, 206), (126, 214), (132, 226), (120, 232), (108, 226), (104, 244), (120, 252), (146, 254), (150, 266), (146, 272)])
farmer |= ellipse(104, 184, 12, 13)                          # hood
farmer |= poly([(94, 175), (108, 170), (120, 178), (122, 192), (114, 196), (106, 186)])    # hood peak, head bowed
farmer |= capsule((106, 204), (128, 216), 6) | capsule((128, 216), (154, 196), 5) | ellipse(156, 194, 5, 4)    # arms raised forward
basket = poly([(144, 172), (190, 172), (184, 196), (150, 196)])
basket |= (np.abs(np.hypot(XX - 167, (YY - 172) * 1.4) - 22) < 1.5) & (YY < 172)
cv.fill(farmer | basket, C('0c0308'))
cv.fill(rim(farmer | basket, 1, 0) | rim(farmer, 1, -1), C('f08a4a'))
cv.fill(basket & (YY > 174) & (((XX + YY) % 5 == 0) | ((XX - YY) % 5 == 0)), C('4a1a1c'))
cv.fill(basket & (YY > 174) & (YY < 174), C('2a0c14'))
cv.fill(ellipse(168, 202, 0.7, 0.7) | ellipse(163, 210, 0.7, 0.7) | ellipse(170, 219, 0.7, 0.7), C('ffc070'))  # a few last grains falling
# crows circling the smoke
for (x, y, s, f) in ((380, 60, 1.4, 0.1), (404, 44, 1.1, 0.4), (520, 70, 1.3, 0.7), (548, 52, 1.0, 0.2), (300, 82, 0.9, 0.55)):
    cv.fill(crow(x, y, s, f), C('1a0612'))
# heat haze specks and ash drifting
for i in range(140):
    x, y = rng.integers(300, 640), rng.integers(10, 200)
    if rng.random() < 0.6: cv.img[y, x] = cv.img[y, x] * 0.5 + C('ffd090') * 0.5
pic = cv.save('il2_pic.png')
present_slide(pic, 1, 5, '收成连续三年歉收。国王宣布举行一场大祭，派出账官四处征收：粮食、牲畜，还有圣物。').save('il2.png')
