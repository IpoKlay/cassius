"""Fine-pixel illustration 2 - the King's decree (960x408, hand-built, no 3D)."""
import os; os.environ.setdefault("HIRES", "1.5")
from illus import *
from slidekit import present_slide
from kingdom import cloudbanks, sun as sundisc, pointlight, mix
rng = np.random.default_rng(2)
cv = Canvas()
SUNX, SUNY = 452, 146
sky = ramp('2a0e30', '4c1438', '74203c', 'a2303a', 'c84a34', 'e47634', 'f4a246', 'fbcf7a')
t = np.clip(YY / 176.0, 0, 1) ** 1.2 + np.clip(1 - np.hypot((XX - SUNX) / 2.2, YY - SUNY) / 260, 0, 1) * 0.35
cv.grad(np.ones((H, W), bool), t, sky)
# towering cloud masses lit from below
n = fbmd(21, cells=(150, 70, 30, 12)); n2 = fbmd(77, cells=(60, 30, 14, 6)); n3 = fbmd(5, cells=(8, 4, 2, 1))
if PAINT:
    pal_c = ramp('3a1234', '5a1a3c', '84304a', 'c05a50', 'f08a58', 'ffc070')
    cumulus(cv, 21, ((44, -20, 260, 30), (40, 300, 680, 34), (88, 40, 300, 20), (96, 520, 660, 18), (122, 150, 360, 12)), pal_c, (SUNX, SUNY), C('ffd890'))
else:
    clouds2(cv, 21, ((36, 26, 0.75), (78, 18, 0.6), (112, 12, 0.5)), ramp('3a1234', '5a1a3c', '7e2a44', 'b44a48', 'e8784c', 'ffb468'), sun=(SUNX, SUNY))
sundisc(cv, SUNX, SUNY, C('ffc070'), 26, 1.3)
RAYS = rays(SUNX, SUNY, 9, None, k=0.32, n=30, reach=520)
# a far city on the hills, towers catching the light
far, ftop = ridge(178, 30, 3, (90, 40, 14))
cv.grad(far, (YY - 140) / 60.0, ramp('c86a5a', 'a04a50', '7a3446'))
for k in range(14):
    x = 20 + k * 22 + rng.integers(-6, 6)
    if abs(x - SUNX) < 70: continue
    y0 = topat(ftop, x) + 4
    hh = rng.integers(8, 22); ww = rng.integers(3, 7)
    tw = poly([(x - ww, y0), (x + ww, y0), (x + ww, y0 - hh), (x, y0 - hh - 5), (x - ww, y0 - hh)])
    cv.fill(tw, C('8a3a48')); cv.fill(rim(tw, 1, 0), C('f0a070'))
mid, mtop = ridge(198, 24, 5, (70, 30, 10))
cv.grad(mid, (YY - 172) / 50.0, ramp('7a2a3c', '5a1e34', '40162a'))
# a river winding across the middle distance, mirroring the sunset
river = poly([(0, 206), (180, 200), (300, 204), (420, 198), (640, 202), (640, 214), (420, 210), (300, 216), (180, 212), (0, 218)])
cv.grad(river, (XX - SUNX) ** 2 / 90000.0, ramp('ffd090', 'f09048', 'c05040', '8a3040'))
cv.fill(river & ((YY % 3) == 0) & (np.abs(XX - SUNX) < 60), C('fff0c0'))
# the altar hill and stepped altar right in front of the sun
hill = poly([(250, 272), (330, 200), (400, 182), (500, 180), (560, 196), (640, 214), (640, 272)])
cv.fill(hill, C('4a1a2a')); cv.fill(rim(hill, 0, -1), C('e07848'))
alt = np.zeros((H, W), bool)
for (hw, y0, y1) in ((76, 182, 170), (60, 170, 158), (46, 158, 146), (32, 146, 134), (20, 134, 124)):
    alt |= (np.abs(XX - SUNX) <= hw) & (YY >= y1) & (YY < y0)
cv.grad(alt, np.clip((XX - SUNX + 76) / 152, 0, 1), ramp('6a2a34', '4a1c2c', '36142a'))
for y_ in (170, 158, 146, 134):
    cv.fill(alt & (YY == y_), C('ffb070'))
cv.fill(alt & (np.abs(XX - SUNX) < 7) & ((YY % 3) < 0.7), C('7a3038'))
blocks = alt & ((((YY - 124) % 4) < 0.67) | ((((XX - SUNX) + 6 * (np.floor((YY - 124) / 4) % 2)) % 12) < 0.67)) & (np.abs(XX - SUNX) >= 7)
cv.fill(blocks, C('2a0e1e'))
cv.fill(alt & (n3 > 0.62) & ~blocks, C('5a2432'))
# braziers along the stairs, banners on the corners
for (bx, by) in ((SUNX - 70, 170), (SUNX + 70, 170), (SUNX - 42, 146), (SUNX + 42, 146)):
    cv.fill(poly([(bx - 3, by), (bx + 3, by), (bx + 2, by - 6), (bx - 2, by - 6)]), C('3a1a1a'))
    cv.fill(poly([(bx - 3, by - 6), (bx, by - 15), (bx + 3, by - 6)]), C('ffd070'))
    cv.glow(bx, by - 9, 18, C('ffa040'), 0.6)
for (bx, by) in ((SUNX - 76, 182), (SUNX + 76, 182)):
    cv.fill(line((bx, by), (bx, by - 44), 1), C('3a1a1a'))
    fl = poly([(bx, by - 44), (bx + 10 * np.sign(bx - SUNX), by - 42), (bx + 10 * np.sign(bx - SUNX), by - 24), (bx, by - 28)])
    cv.fill(fl, C('b02028')); cv.fill(rim(fl, 1, 0), C('ff8050'))
# fire and smoke column
smoke = np.zeros((H, W))
for i in range(64):
    yy0 = 118 - i * 2.2
    xx0 = SUNX + 2 + max(0, i - 18) ** 1.6 * 0.45 + 4 * math.sin(i * 0.5)
    r = 6 + i * 0.5 + 3 * math.sin(i * 1.3)
    smoke = np.maximum(smoke, np.clip(1 - np.hypot(XX - xx0, (YY - yy0) * 1.2) / r, 0, 1))
smoke *= 0.5 + n2 * 1.1
sm = smoke > 0.3
cv.grad(sm, 1 - (smoke - 0.3) * 1.5, ramp('2e1220', '4a1c2c', '6a2a34', '8a3a3a'))
cv.fill(sm & rim(sm, 1, 1), C('f07a48'))
cv.glow(SUNX, 112, 60, C('ffb050'), 0.8)
fire = poly([(SUNX - 18, 125), (SUNX - 12, 104), (SUNX - 6, 113), (SUNX + 1, 88), (SUNX + 7, 108), (SUNX + 12, 98), (SUNX + 18, 125)])
cv.fill(fire, C('ffc058')); cv.fill(fire & (YY > 108) & (np.abs(XX - SUNX) < 10), C('fff6d0'))
# the king on the top step: purple robe, gold crown, staff raised
kx = SUNX - 22
king = figure(kx, 124, 32, pose='stand', robe=True, arms_up=True, facing=-1)
cv.fill(king, C('5a2a6a')); cv.fill(rim(king, 1, 0), C('ffb070'))
cv.fill(ellipse(kx - 1, 95, 4, 2.5) & (YY < 96), C('ffd860'))
cv.fill(line((kx - 5, 122), (kx - 6, 78), 1), C('e0b050')); cv.fill(ellipse(kx - 6, 78, 2, 2), C('fff0a0'))
for sx_ in (-58, 58):
    p = figure(SUNX + sx_ * 0.62, 158, 20, pose='stand', robe=True, hood=True, arms_up=True, facing=-1 if sx_ > 0 else 1)
    cv.fill(p, C('d8c8b0')); cv.fill(rim(p, 1, 0), C('fff0d0'))
# procession up the hill, colourful cloaks catching the low light
path = [(-10, 240), (120, 228), (230, 208), (330, 190), (380, 182)]
def on_path(u):
    seg = min(int(u * (len(path) - 1)), len(path) - 2); f = u * (len(path) - 1) - seg
    a, b = path[seg], path[seg + 1]
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
ground = poly([(0, 240), (120, 230), (230, 210), (330, 192), (400, 184), (400, 272), (0, 272)])
cv.grad(ground, (YY - 184) / 88.0, ramp('6a2a30', '54202c', '3e1824', '2a1018'))
road = np.zeros((H, W), bool)
for a, b in zip(path, path[1:]):
    road |= line(a, b, 4)
cv.fill(road & ground, C('8a4038'))
field = (ground | hill) & ~alt & ~road
for k in range(-30, 31):
    fx0 = SUNX + k * 30
    fur = line((fx0, 272), (SUNX + k * 3.0, 188), 1) & field & (YY > 188)
    cv.fill(fur, C('3a1420')); cv.fill(np.roll(fur, 1, 1) & field & ~fur, C('7a3a38'))
for i in range(90):
    x0, y0 = rng.uniform(160, 640), rng.uniform(204, 262)
    st = ellipse(x0, y0, rng.uniform(0.8, 2.2), rng.uniform(0.6, 1.2)) & field
    cv.fill(st, C('5a2a2c')); cv.fill(st & ~np.roll(st, 1, 0), C('c06a48'))
CLO = [C('3a5a8a'), C('8a2a2a'), C('6a6a3a'), C('7a4a2a'), C('4a3a6a'), C('a07a3a'), C('2a6a5a')]
for i in range(40):
    u = i / 40 + rng.uniform(-0.006, 0.006)
    x, y = on_path(u)
    h = 28 - u * 15
    if i % 7 == 3:
        hh = h * 0.5
        ox_ = ellipse(x, y - hh * 0.9, hh * 1.1, hh * 0.55) | ellipse(x + hh * 1.0, y - hh * 1.1, hh * 0.35, hh * 0.3)
        for lx in (-0.7, -0.4, 0.4, 0.7):
            ox_ |= line((x + lx * hh, y - hh * 0.6), (x + lx * hh, y), 1)
        cv.fill(ox_, C('c8b8a0') if i % 2 else C('6a4030')); cv.fill(rim(ox_, 1, 0), C('ffd0a0'))
        continue
    m = figure(x, y, h, facing=1, pack=(i % 2 == 0), phase=i * 0.37, hood=(i % 3 == 0), spear=(h * 6 if i % 9 == 5 else None))
    cv.fill(m, CLO[i % len(CLO)] * 0.8); cv.fill(rim(m, 1, 0) | rim(m, 0, -1), C('ffb878'))
    if i % 2 == 0:
        cv.fill(ellipse(x - h * 0.13, y - h * 0.72, h * 0.12, h * 0.14), C('d8b880'))    # sacks of grain
# foreground: dead wheat field, a kneeling farmer offering an empty basket
fg = poly([(0, 244), (90, 238), (200, 246), (330, 252), (470, 248), (640, 240), (640, 272), (0, 272)])
cv.grad(fg, (YY - 238) / 34.0, ramp('5a2a24', '3e1a1c', '2a1014'))
wheat = np.zeros((H, W), bool); ears = []
for (x0, cnt, hmin, hmax) in ((20, 40, 60, 130), (585, 44, 70, 150), (300, 18, 18, 40), (470, 14, 14, 36)):
    for k in range(cnt):
        bx = x0 + rng.integers(-30, 36); top = 272 - rng.integers(hmin, hmax)
        bend = rng.uniform(-1, 1) * 14
        pts = [(bx + bend * (s ** 2), 272 - (272 - top) * s) for s in np.linspace(0, 1, 12)]
        for a, b in zip(pts, pts[1:]):
            wheat |= line(a, b, 1)
        ex, ey = pts[-1]; dr = 1 if bend > 0 else -1
        for j in range(6):
            ears.append(ellipse(ex + dr * j * 1.6, ey + j * 2.2, 1.8, 2.4))
E = np.any(ears, axis=0)
cv.fill(wheat, C('6a3a24')); cv.fill(E, C('b07838')); cv.fill(rim(E, 1, -1) | rim(wheat, 1, 0), C('ffc070'))
farmer = poly([(52, 272), (58, 238), (70, 206), (84, 188), (98, 182), (110, 186), (116, 196), (112, 206), (126, 214), (132, 226), (120, 232), (108, 226), (104, 244), (120, 252), (146, 254), (150, 266), (146, 272)])
farmer |= ellipse(104, 184, 12, 13) | poly([(94, 175), (108, 170), (120, 178), (122, 192), (114, 196), (106, 186)])
farmer |= capsule((106, 204), (128, 216), 6) | capsule((128, 216), (154, 196), 5) | ellipse(156, 194, 5, 4)
cv.grad(farmer, np.clip((XX - 52) / 100.0 + (n3 - 0.5) * 0.3, 0, 1), ramp('2e2030', '42283a', '5a3238', '7a4036'))
cv.fill(rim(farmer, 1, 0) | rim(farmer, 1, -1), C('ffa060'))
folds = farmer & (line((70, 268), (82, 214), 1) | line((92, 270), (96, 226), 1) | line((60, 250), (72, 210), 1) | line((112, 246), (130, 252), 1))
cv.fill(folds, C('2a1e2e'))
cv.fill(farmer & ellipse(113, 190, 4, 5.5), C('2a1820'))               # face in the hood's shadow
cv.fill(farmer & ellipse(115.5, 191, 2, 4), C('b06a4a')); cv.fill(farmer & ellipse(116.5, 190, 0.8, 2.5), C('ffb070'))

cv.fill(ellipse(152, 196, 3.2, 3) | ellipse(158, 193, 3, 2.6), C('d8986a'))
basket = poly([(144, 172), (190, 172), (184, 196), (150, 196)])
basket |= (np.abs(np.hypot(XX - 167, (YY - 172) * 1.4) - 22) < 1.5) & (YY < 172)
cv.fill(basket, C('8a5a2a')); cv.fill(basket & (((XX + YY) % 5 == 0) | ((XX - YY) % 5 == 0)), C('5a3418'))
cv.fill(rim(basket, 1, 0), C('ffc070'))
for (bx, by, s, f) in ((380, 60, 1.4, 0.1), (404, 44, 1.1, 0.4), (520, 70, 1.3, 0.7), (548, 52, 1.0, 0.2), (300, 82, 0.9, 0.55), (330, 66, 1.0, 0.3)):
    cv.fill(crow(bx, by, s, f), C('2a0e1e'))
# a crowd kneeling at the altar's foot
for i in range(46):
    x = SUNX - 120 + i * 5.4 + rng.uniform(-2, 2); y = 186 + (i % 3) * 3 + rng.uniform(0, 2)
    if abs(x - SUNX) < 82 and y < 190: y = 190 + (i % 2) * 3
    m = figure(x, y, 11 + (i % 3), pose='kneel', facing=1 if x < SUNX else -1, hood=(i % 2 == 0))
    cv.fill(m, CLO[i % len(CLO)] * 0.6); cv.fill(rim(m, 0, -1), C('ffb070'))
# light: god rays and floating chaff in the air
RAYS = RAYS * np.clip((196 - YY) / 30, 0, 1)
cv.img = np.clip(cv.img + RAYS[:, :, None] * C('ffc080')[None, None, :] * (1 - sm[:, :, None] * 0.6), 0, 1)
for i in range(420):
    x, y = rng.uniform(250, 640), rng.uniform(40, 240)
    d = math.hypot(x - SUNX, y - SUNY)
    if d < 260 and rng.random() < 1 - d / 260:
        put_px(cv, x, y, C('ffe0a0'), 0.7)
pic = cv.save('h2_pic.png')
present_slide(pic, 1, 5, '收成连续三年歉收。国王宣布举行一场大祭，派出账官四处征收：粮食、牲畜，还有圣物。').save('h2.png')
raise SystemExit
ref = cv.img.copy()
Image.fromarray((ref * 255).astype(np.uint8)).save('o2_ref.png')
detail = np.asarray(Image.fromarray((np.ones((H, W)) * 255).astype(np.uint8)).resize((paint.OW, paint.OH))) / 255.0
out = paint.paint(ref, seed=2)
paint.save(out, 'o2_paint.png')
