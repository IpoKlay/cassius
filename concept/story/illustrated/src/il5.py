"""Illustration 5 - cold dawn: the column winds away into misty valleys while those who stay watch from the wall."""
from illus import *
from slidekit import present_slide
rng = np.random.default_rng(5)
cv = Canvas()
SX, SY = 520, 112
cv.grad(np.ones((H, W), bool), np.clip(YY / 150.0, 0, 1) * 0.85 + np.clip(1 - np.hypot((XX - SX) / 2.5, YY - SY) / 300, 0, 1) * 0.3,
        ramp('1a2440', '2a3a5a', '4a5a78', '7a8090', 'b8a890', 'e8c89a', 'fae0b0'))
cv.glow(SX, SY, 90, C('ffd8a0'), 0.45, sx=1.6)
cv.fill(ellipse(SX, SY, 14, 14) & (YY < SY + 2), C('fff4d8'))
n = fbm(W, H, 51, cells=(140, 60, 24, 8))
for (cy_, th, col) in ((52, 4, '3a4664'), (74, 3, '5a5e74'), (100, 3, 'a08a80')):
    m = (np.abs(YY - cy_ - (n - 0.5) * 20) < th * (n * 2 - 0.6)) & (n > 0.45)
    cv.fill(m, C(col)); cv.fill(m & ~np.roll(m, -1, 0), C('f0c8a0'))
# layered ranges with mist between them
layers = [(134, 30, 61, ramp('8a8aa0', '7a7c94')), (152, 26, 62, ramp('6a7088', '5a6080')), (172, 22, 63, ramp('4a5470', '3e4864')), (196, 20, 64, ramp('2e3850', '26304a'))]
tops = []
for i, (y0, amp, seed, pal) in enumerate(layers):
    m, top = ridge(y0, amp, seed, (90 - i * 10, 36, 12))
    cv.grad(m, np.clip((YY - top[None, :]) / 40.0, 0, 1), pal)
    cv.fill(m & ~np.roll(m, 1, 0) & (np.abs(XX - SX) < 200), C('e8c8a0') * (0.9 - i * 0.15) + pal[0] * (0.1 + i * 0.15))
    mist = np.clip(1 - np.abs(YY - (y0 + 4)) / 10.0, 0, 1) * (0.5 + n * 0.6)
    cv.img = cv.img * (1 - (np.floor(mist * 4 + BAY) / 4 * 0.5)[:, :, None]) + (np.floor(mist * 4 + BAY) / 4 * 0.5)[:, :, None] * C('c8c4cc')
    tops.append(top)
# cypress trees on the nearer hills
for (tx, ty, hh) in ((150, 200, 26), (164, 204, 20), (430, 190, 22), (444, 194, 16), (600, 206, 30)):
    tr = ellipse(tx, ty - hh / 2, hh * 0.17, hh / 2)
    cv.fill(tr, C('1a2232')); cv.fill(rim(tr, 1, 0), C('8a7a70'))
mist = np.clip(1 - np.abs(YY - 214) / 14.0, 0, 1) * (0.4 + n * 0.7)
q = np.floor(mist * 4 + BAY) / 4 * 0.45
cv.img = cv.img * (1 - q[:, :, None]) + q[:, :, None] * C('d8d0d0')
# the winding road and the column on it
def road_pt(u):
    x = 240 + u * 300 + math.sin(u * 5.2) * 50
    y = 262 - u * 104 - math.sin(u * 3.0) * 6
    return x, y
ground = poly([(0, 214), (640, 200), (640, 272), (0, 272)])
cv.grad(ground, (YY - 200) / 72.0, ramp('3a4258', '2e364a', '222a3a', '181e2a'))
road = np.zeros((H, W), bool)
prev = road_pt(0)
for u in np.linspace(0.01, 1, 120):
    p = road_pt(u); road |= line(prev, p, max(1, int(9 * (1 - u) + 1))); prev = p
cv.fill(road, C('6a6a78')); cv.fill(road & ((XX + YY * 2) % 5 == 0), C('8a8494'))
col = np.zeros((H, W), bool); spears = np.zeros((H, W), bool)
for k in range(30):
    u = 0.08 + k * 0.029
    x, y = road_pt(u); x += (k % 2 - 0.5) * (6 * (1 - u) + 1)
    h = 30 * (1 - u) ** 1.3 + 5
    if h > 13:
        m = figure(x, y, h, facing=1, helmet=True, shield=True, pack=True, phase=k * 0.29)
        spears |= line((x + h * 0.16, y - h * 0.05), (x + h * 0.24, y - h * 1.45), 1)
    else:
        m = (np.abs(XX - x) <= max(1, h * 0.12)) & (YY <= y) & (YY >= y - h * 0.8)
        m |= ellipse(x, y - h * 0.88, max(0.8, h * 0.08), max(0.8, h * 0.08))
        spears |= line((x + 1, y), (x + 2, y - h * 1.4), 1)
    col |= m
x, y = road_pt(0.96)                                                       # the standard at the head of the column
std = line((x, y), (x, y - 26), 1) | poly([(x - 4, y - 25), (x + 4, y - 25), (x + 4, y - 15), (x, y - 17), (x - 4, y - 15)])
cv.fill(col | std | spears, C('141a26'))
cv.fill(spears & (np.roll(spears, 1, 0) ^ spears), C('c0b0a0'))
cv.fill(rim(col, 1, 0) & (YY < 250), C('f0c890'))
cv.fill(std & (YY > y - 25) & (YY < y - 14), C('b02020'))
# the cart near the tail
cx_, cy_ = road_pt(0.02)
cart = poly([(cx_ - 30, cy_ - 16), (cx_ + 4, cy_ - 16), (cx_ + 4, cy_ - 6), (cx_ - 30, cy_ - 6)]) | ellipse(cx_ - 24, cy_ - 4, 6, 6) | ellipse(cx_ - 4, cy_ - 4, 6, 6)
cart |= ellipse(cx_ - 14, cy_ - 20, 15, 6) & (YY < cy_ - 16)
cv.fill(cart, C('141a26')); cv.fill(rim(cart, 1, 0) | rim(cart, 0, -1), C('d8b080'))
# foreground: the palisade walkway, a woman and a child watching, the child waving
wall = poly([(0, 228), (250, 240), (270, 272), (0, 272)])
stakes = np.zeros((H, W), bool)
for x0 in range(-4, 250, 11):
    yb = 228 + x0 * 0.05
    tip = yb - 40 + (x0 * 31 % 7)
    stakes |= poly([(x0, 272), (x0 + 10, 272), (x0 + 10, tip + 8), (x0 + 5, tip), (x0, tip + 8)])
cv.fill(stakes, C('1c1a20')); cv.fill(rim(stakes, 1, 0), C('8a6a5a')); cv.fill(stakes & (XX % 11 == 10), C('0c0a10'))
walk = poly([(0, 250), (270, 256), (290, 272), (0, 272)])
cv.fill(walk, C('100e14')); cv.fill(rim(walk, 0, -1), C('6a5a58'))
woman = figure(118, 262, 96, pose='stand', facing=1, hood=True, robe=True)
child = figure(160, 262, 54, pose='stand', facing=1, arms_up=False)
child |= capsule((160, 222), (172, 206), 2.6) | capsule((172, 206), (176, 192), 2.2) | ellipse(176, 190, 3, 3)     # waving
cv.fill(woman | child, C('08080e'))
cv.fill(rim(woman | child, 1, 0) | rim(woman | child, 1, -1), C('f8d0a0'))
# a milestone and frosted grass tufts beside the road
ms = poly([(470, 246), (482, 246), (480, 222), (476, 218), (472, 222)])
cv.fill(ms, C('5a5a68')); cv.fill(rim(ms, 1, 0), C('e8d0b0')); cv.fill(ms & (YY == 230) & (XX > 472) & (XX < 480), C('2a2a34'))
for i in range(90):
    gx_, gy_ = rng.integers(300, 640), rng.integers(222, 272)
    if not road[gy_, gx_]:
        for j in range(3):
            cv.img[gy_ - j, gx_ + (j * (i % 3 - 1)) // 2] = C('8a8a9a') if j < 2 else C('d8d0c0')
# empty granary sacks slumped on the walkway
for (sx_, sy_) in ((30, 262), (52, 264)):
    sk = ellipse(sx_, sy_ - 6, 11, 8) & (YY < sy_) | ellipse(sx_, sy_ - 2, 13, 3)
    cv.fill(sk, C('2a2426')); cv.fill(rim(sk, 1, -1), C('a08070'))
# crows over the road, breath of mist near the ground
for (bx, by, s, f) in ((380, 80, 1.2, 0.2), (400, 70, 1.0, 0.6), (420, 86, 0.9, 0.9), (300, 96, 0.8, 0.4)):
    cv.fill(crow(bx, by, s, f), C('1a1e2c'))
pic = cv.save('il5_pic.png')
present_slide(pic, 4, 5, '粮仓快空了。帝国的回复是一道敕令：重开北路，收齐各地所欠，送往大祭场——你的要塞就能分到口粮。七十人，四十五斗粮。出发。').save('il5.png')
