"""Kingdom-style 3: the four grievances, four side-view panels."""
from kingdom import *
from slidekit import bake, present_slide
import figures3d as F, buildings3d as B, props3d as PR, legionary3d as L
rng = np.random.default_rng(33)
PW = 160
final = np.zeros((H, W, 3))
GY = 196

def panel(i, cv):
    final[:, i * PW:(i + 1) * PW] = cv.img[:, i * PW:(i + 1) * PW]

# ------------------------------------------------------------------ north: the empty plinth, the clan, the longship
cv = Canvas(); ox = 0; cx = 80
sky(cv, ['050a1a', '0a1630', '12244a', '1e3a62', '3a5a80'], 0, GY, glow=0.0)
for k in range(3):
    yc = 36 + k * 16 + np.sin(XX / (16 + k * 5) + k) * 8
    a = np.clip(1 - np.abs(YY - yc) / (13 - k * 3), 0, 1) * (YY < yc + 2) * (0.7 + 0.3 * np.sin(XX * 1.3 + k))
    cv.add(np.floor(a * 4 + BAY) / 4 * (0.32 - k * 0.07), C('50f0b0') if k != 1 else C('7aa0ff'))
for j in range(120):
    x, y = rng.integers(0, PW), rng.integers(0, 120); cv.img[y, x] = C('dfe8ff') * rng.uniform(0.5, 1)
hills(cv, 160, 34, 31, C('8a9cc0'), C('f0f6ff'))
treeline(cv, 182, 16, 32, C('2a3e5e'), C('c8d8f0'), bumps=4)
for (x, h) in ((14, 50), (40, 38), (128, 56), (150, 44)):
    t = foliage_tree(cv, x, GY - 1, h, ramp('e8f0ff', '7a9ab8', '3a5878', '22384e'), ramp('5a5a6a', '3a3a4a', '22222e'), x + 7, light=(-1, -1), kind='pine')
    cv.fill(t & ~np.roll(t, 1, 0), C('ffffff'))
plinth = bake('k_plinth_empty', lambda: B.plinth(True), (30, 30), 1.4, 0, pitch=12)
put(cv, plinth, cx, GY + 1, tint=C('c8d8f0'))
cv.glow(cx, GY - plinth.shape[0] - 6, 22, C('50e0b0'), 0.4)
ang_ = np.arctan2(-(YY - (GY - plinth.shape[0] - 2)), XX - cx)
ghost = (np.abs(np.hypot(XX - cx, (YY - (GY - plinth.shape[0] - 2)) * 1.25) - 9) < 1.0 + 2.2 * np.clip((np.pi - ang_) / np.pi, 0, 1)) & (YY < GY - plinth.shape[0] - 1)
cv.fill(ghost & ((XX + YY) % 2 == 0), C('80ffd0'))
north = bake('k_northman', lambda: F.human(body='blue', legs='brown', cloak='grey', head='helmet', beard='linen', arms=('down', 'axe'), axe=True, shield='round'), (40, 62), 0.95, 60)
north2 = bake('k_northman2', lambda: F.human(body='grey', robe=True, cloak='fur' if False else 'brown', head='hood', beard='mane', arms=('chest', 'chest'), kneel=True), (40, 62), 0.95, -60)
put(cv, north, cx + 30, GY + 1, tint=C('c0d0f0'), rim_col=C('a0f0e0'), rim_dir=-1)
put(cv, north2, cx - 30, GY + 1, tint=C('c0d0f0'), rim_col=C('a0f0e0'), rim_dir=1)
grass_strip(cv, GY, C('ffffff'), C('c8d8f0'), C('5a6a88'), 31, h=5)
reflect(cv, GY + 5, C('0e1a34'), dark=0.6, seed=31)
ship = bake('k_longship', B.longship, (90, 46), 0.85, 0, pitch=10)
sb = GY + 15
put(cv, ship, cx + 14, sb, tint=C('a8b8d8'))
rf = ship[::-1].copy()
for j in range(rf.shape[0]):
    rf[j] = np.roll(rf[j], int(round(math.sin(j * 0.9) * 1.2)), 0)
put(cv, rf, cx + 14, sb + rf.shape[0], tint=C('4a5878'))
for j in range(220):
    x, y = rng.integers(0, PW), rng.integers(0, H); s = 1 if rng.random() < 0.8 else 2
    cv.img[y:y + s, x:x + s] = mix(cv.img[y, x], C('ffffff'), 0.85)
panel(0, cv)

# ------------------------------------------------------------------ west: stumps where the forest was, the axe, the eyes in the trees
cv = Canvas(); ox = PW; cx = ox + 80
sky(cv, ['1a2a1e', '2a4028', '4a5e30', '7a7a3c', 'a89448'], 0, GY, glow=0.0)
for k in range(10):
    cv.glow(cx + 14 + k * 1.4, 150 - k * 11, 9 + k, C('b0a080'), 0.22)
treeline(cv, 176, 30, 52, C('2a3e24'), C('5a7a3a'), bumps=7)
for (x, h, kd) in ((ox + 4, 150, 'oak'), (ox + 24, 120, 'pine'), (ox + 140, 160, 'oak'), (ox + 156, 118, 'pine')):
    foliage_tree(cv, x, GY - 1, h, ramp('8aa04a', '5a7a34', '3a5626', '22381a', '14240e'), ramp('6a4a2a', '4a3220', '2a1c12'), x, light=(1, -1), kind=kd)
for (x, sc) in ((ox + 44, 1.0), (ox + 60, 1.3), (ox + 72, 0.9), (cx + 2, 1.6), (ox + 104, 1.0), (ox + 116, 1.3), (ox + 124, 0.8)):
    st = bake(f'k_stump_{sc}', lambda: B.stump(2.6, 3.0), (20, 16), sc, 0, pitch=18)
    put(cv, st, x, GY + 1, tint=C('f0e0c0'))
axe = capsule((cx + 4, GY - 14), (cx + 18, GY - 34), 1.2)
cv.fill(axe, C('6a4a2a')); hd = poly([(cx + 2, GY - 16), (cx - 8, GY - 18), (cx - 9, GY - 10), (cx + 2, GY - 9)])
cv.fill(hd, C('8a9aa8')); cv.fill(rim(hd, 0, -1), C('e0eef4'))
logs = bake('k_logpile', lambda: B.logpile(5, 16.0), (40, 24), 1.0, 20, pitch=16)
put(cv, logs, ox + 136, GY + 1, tint=C('e8d8b8'))
cutter = bake('k_cutter', lambda: F.human(body='green', legs='skin', arms=('axe', 'down'), axe=True, head='cap', beard='mane'), (40, 62), 0.92, 90)
leg = bake('k_leg_70', lambda: L.legionary_model(0.0), (40, 62), 1.0, 70)
put(cv, cutter, ox + 30, GY + 1, tint=C('e8e0c8'))
put(cv, leg, ox + 98, GY + 1, tint=C('e8e0c8'))
masked = bake('k_masked', lambda: F.human(body='green', robe=True, cloak='brown', head='hood', mask=True, arms=('down', 'staff'), staff=True), (40, 62), 0.9, -80)
put(cv, masked, ox + 150, GY + 1, tint=C('6a7a5a'))
for (ex, ey) in ((ox + 8, 150), (ox + 146, 142), (ox + 18, 126)):
    cv.fill(ellipse(ex - 2, ey, 0.9, 0.6) | ellipse(ex + 2, ey, 0.9, 0.6), C('e8ff60'))
grass_strip(cv, GY, C('a8c060'), C('4a6a2a'), C('2a2a16'), 52, h=5, flowers=[C('e8d070')])
reflect(cv, GY + 5, C('16241a'), dark=0.6, seed=52)
for j in range(50):
    x, y = rng.integers(ox, ox + PW), rng.integers(60, GY); cv.img[y, x] = rng.choice([C('c8a060'), C('a0b040'), C('d08030')])
panel(1, cv)

# ------------------------------------------------------------------ east: the tower that keeps the calendar, and the red comet
cv = Canvas(); ox = 2 * PW; cx = ox + 80
sky(cv, ['08041a', '160a2e', '281244', '40205a', '603070'], 0, GY, glow=0.0)
for j in range(220):
    x, y = rng.integers(ox, ox + PW), rng.integers(0, 170); cv.img[y, x] = rng.choice([C('ffffff'), C('d8c8ff'), C('ffd8f0')]) * rng.uniform(0.4, 1)
for k in range(46):
    cv.glow(ox + 138 - k * 1.5, 26 + k * 0.7, 5 - k * 0.07, C('ff4040'), 0.6 - k * 0.011)
cv.fill(ellipse(ox + 139, 26, 2, 2), C('fff0e0'))
hills(cv, 176, 22, 61, C('3a1e52'), C('8a60b0'))
treeline(cv, 186, 12, 62, C('24123a'), C('6a4090'), bumps=4)
tower = bake('k_watchtower', B.watchtower, (40, 100), 1.6, 0, pitch=10)
put(cv, tower, cx + 10, GY + 1, tint=C('d8c0f0'))
for (wy) in (GY - tower.shape[0] + 30, GY - 60):
    cv.glow(cx + 10, wy, 14, C('ffb060'), 0.35)
for (sx, hh) in ((ox + 20, 14), (ox + 30, 9), (ox + 140, 16), (ox + 128, 8)):
    cr = poly([(sx - 3, GY), (sx + 3, GY), (sx + 1, GY - hh), (sx - 1, GY - hh)])
    cv.fill(cr, C('8a50d0')); cv.fill(cr & (XX < sx), C('e0b0ff')); cv.glow(sx, GY - hh / 2, 12, C('a060ff'), 0.3)
astro = bake('k_astro', lambda: F.human(body='purple', robe=True, cloak='violet', head='hood', arms=('up', 'down'), belt='gold', sleeve='purple'), (40, 62), 0.9, 30)
clerk = bake('k_eclerk', lambda: F.human(body='violet', robe=True, cloak='purple', head='hood', arms=('forward', 'forward'), scroll=True), (40, 62), 0.9, 90)
put(cv, astro, cx - 34, GY + 1, tint=C('e0d0ff'), rim_col=C('ff9090'), rim_dir=1)
put(cv, clerk, cx - 56, GY + 1, tint=C('b8a8d8'))
grass_strip(cv, GY, C('a080c0'), C('4a2a64'), C('1e1030'), 61, h=5)
reflect(cv, GY + 5, C('140a24'), dark=0.62, seed=61, streak=(ox + 120, 8, C('ff7070')))
panel(2, cv)

# ------------------------------------------------------------------ below: the old altar on the surface, the hollow underneath
cv = Canvas(); ox = 3 * PW; cx = ox + 80
SG = 92
sky(cv, ['2a1a3a', '5a2e4a', 'a05a4a', 'e09a5a'], 0, SG, glow=0.0)
treeline(cv, SG - 2, 16, 72, C('3a2030'), C('a06050'), bumps=5)
alt = bake('k_altarstone', B.altar_stone, (60, 40), 1.0, 0, pitch=10)
put(cv, alt, cx, SG + 1, tint=C('f0c8b0'))
flame(cv, cx, SG - alt.shape[0] + 2, 1.2, 3); pointlight(cv, cx, SG - alt.shape[0] - 4, 30, C('ffa050'), 0.7)
pri = bake('k_priest_r', lambda: F.human(body='linen', robe=True, cloak='linen', head='hood', arms=('up', 'up'), belt='red'), (40, 62), 0.75, -60)
put(cv, pri, cx + 34, SG + 1, tint=C('f0d0c0'))
grass_strip(cv, SG, C('c8a060'), C('6a5a30'), C('3a2a1a'), 72, h=4)
under = YY >= SG + 4
n = fbm(W, H, 74, cells=(30, 14, 6, 3))
strata = ((YY - SG) / 11.0 + n * 1.6) % 3
pals = [ramp('6a4a2e', '5a3e26', '3a2818'), ramp('7a5a36', '5a4026', '3e2a1a'), ramp('4e3a2a', '3a2a1e', '241a12')]
for k in range(3):
    cv.grad(under & (np.floor(strata) == k), np.clip((YY - SG) / 180.0, 0, 1), pals[k])
cav = ellipse(cx, 196, 70, 46) | ellipse(cx - 30, 214, 46, 30) | ellipse(cx + 34, 180, 38, 28)
cav &= (n < 0.7) | (YY > 220)
cv.fill(cav & under, C('08060a'))
cv.fill(outline(cav) & under, C('2a1c14'))
for k in range(14):
    sx = cx - 64 + k * 9 + rng.integers(-2, 3)
    tops_ = np.nonzero(cav[:, sx])[0]
    if len(tops_):
        ty = tops_[0]; Ln = rng.integers(4, 14)
        cv.fill(poly([(sx - 2, ty - 1), (sx + 2, ty - 1), (sx, ty + Ln)]), C('2a1c14'))
cr = np.zeros((H, W), bool); px, py = cx + 2, SG + 4
while py < 152:
    nx, ny = px + rng.integers(-3, 4), py + rng.integers(4, 9)
    cr |= line((px, py), (nx, ny), 2); px, py = nx, ny
cv.fill(cr, C('080406')); cv.fill(np.roll(cr, 1, 1) & ~cr & under, C('ffb060') * 0.55)
# an underground lake at the bottom of the hollow, reflecting the miner's lantern
LG = 236
miner = bake('k_miner', lambda: F.human(body='brown', legs='brown', head='cap', beard='mane', arms=('forward', 'down'), lantern=True), (40, 62), 0.8, 90)
put(cv, miner, cx - 40, LG + 1, tint=C('d8b090'), rim_col=C('ffc070'), rim_dir=1)
pointlight(cv, cx - 30, LG - 16, 34, C('ffb050'), 0.9)
cv.fill(ellipse(cx - 31, LG - 16, 1.2, 1.6), C('fff0b0'))
ledge = poly([(ox, LG), (cx - 18, LG), (cx - 12, LG + 4), (ox, LG + 4)])
cv.fill(ledge, C('3a2a1e')); cv.fill(rim(ledge, 0, -1), C('8a6a4a'))
lake = (YY > LG + 2) & cav
src = cv.img.copy()
for y in range(LG + 3, H):
    d = y - (LG + 2); sy = LG + 2 - d
    off = int(round(math.sin(d * 0.9) * (0.6 + d * 0.05)))
    row = np.roll(src[max(sy, 0)], off, 0)
    m = lake[y]
    cv.img[y][m] = row[m] * 0.55 + C('0a1018') * 0.45
cv.glow(cx + 40, 214, 16, C('a0c0d0'), 0.3); cv.fill(ellipse(cx + 40, 216, 1.5, 1), C('e0f0ff'))
panel(3, cv)

for i in range(1, 4):
    final[:, i * PW - 1:i * PW + 1] = C('120e0a'); final[:, i * PW - 1] = C('8a6a3a')
img = Image.fromarray((np.clip(final, 0, 1) * 255).astype(np.uint8)); img.save('k3_pic.png')
labels = [(80, 10, '北 · 霜湾', (210, 228, 255)), (240, 10, '西 · 荆冠', (200, 240, 180)), (400, 10, '东 · 暮紫', (236, 206, 255)), (560, 10, '古祭坛之下', (255, 220, 170))]
present_slide(img, 2, 5, '北方说帝国夺走了先祖的号角。西方的森林被砍去建祭坛和军营。东方掌管历法，却不肯公开今年的凶兆。而矿工说，古祭坛底下的地是空的。', labels=labels).save('k3.png')
