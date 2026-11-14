"""Illustration 3 - four grievances as four tall panels."""
import os; os.environ.setdefault('HIRES', '1.5')
from illus import *
from slidekit import present_slide
rng = np.random.default_rng(3)
PW = 160
final = np.zeros((H, W, 3))

def panel(i, cv):
    x0 = i * PW
    final[:, int(x0 * HI):int((x0 + PW) * HI)] = cv.img[:, int(x0 * HI):int((x0 + PW) * HI)]

# ------------------------------------------------------------------ north: the empty plinth under the aurora
cv = Canvas(); ox = 0; cx = ox + 80
cv.grad(np.ones((H, W), bool), YY / 200.0, ramp('060a1e', '0a1430', '10204a', '183062', '24406e'))
for k in range(3):                                                    # aurora curtains
    yc = 40 + k * 18 + np.sin((XX - ox) / (18 + k * 6) + k) * 10
    a = np.clip(1 - np.abs(YY - yc) / (14 - k * 3), 0, 1) * ((YY < yc + 2))
    streak = (0.6 + 0.4 * np.sin(XX * 1.7 + k)) * a
    cv.add(np.floor(streak * 4 + BAY) / 4 * (0.35 - k * 0.08), C('50f0b0') if k != 1 else C('80a0ff'))
for j in range(140):
    x, y = rng.integers(ox, ox + PW), rng.integers(0, 120); put_px(cv, x, y, C('dfe8ff') * rng.uniform(0.5, 1))
mtn, _ = ridge(150, 50, 31, (40, 16, 6))
cv.grad(mtn, (YY - 100) / 60.0, ramp('6a7c9e', '4a5a80', '2e3c62'))
cv.fill(mtn & ~np.roll(mtn, 2, 0), C('e8f0ff'))
cv.fill(mtn & ~np.roll(mtn, 4, 0) & ~np.roll(mtn, 2, 0) & ((XX + YY) % 2 < 0.67), C('b8c8e8'))
sea = YY >= 160
cv.grad(sea, (YY - 168) / 50.0, ramp('1a2c50', '142444', '0e1a36'))
cv.fill(sea & ((YY % 5 < 0.67) & (np.sin(XX * 0.7 + YY) > 0.5)), C('3e5a88'))
ship = poly([(ox + 100, 172), (ox + 136, 172), (ox + 140, 166), (ox + 132, 170), (ox + 104, 170), (ox + 96, 166)]) | line((ox + 118, 170), (ox + 118, 148), 1) | poly([(ox + 111, 150), (ox + 125, 150), (ox + 125, 163), (ox + 111, 163)])
pass
cliff = poly([(ox - 4, 196), (ox + 40, 188), (ox + 92, 184), (ox + 130, 190), (ox + 164, 200), (ox + 164, 272), (ox - 4, 272)])
cv.grad(cliff, (YY - 180) / 90.0, ramp('d8e4f4', '9aaccc', '5a6c90', '2e3a5a', '1a2440'))
cv.fill(rim(cliff, 0, -1), C('ffffff'))
plinth = poly([(cx - 22, 196), (cx + 22, 196), (cx + 18, 186), (cx - 18, 186)]) | poly([(cx - 14, 186), (cx + 14, 186), (cx + 12, 150), (cx - 12, 150)]) | poly([(cx - 18, 150), (cx + 18, 150), (cx + 16, 144), (cx - 16, 144)])
cv.grad(plinth, (XX - cx + 16) / 36.0, ramp('9aaccc', '6a7c9e', '3e4c70', '28324e'))
cv.fill(plinth & (YY < 146), C('f0f6ff'))
cv.fill(line((cx - 3, 160), (cx + 2, 176), 1) | line((cx + 2, 176), (cx - 1, 186), 1), C('1e2640'))
ang_ = np.arctan2(-(YY - 140), XX - cx)                                # a curled horn: thick at the mouth, tapering to the tip
thick = 1.0 + 3.5 * np.clip((np.pi - ang_) / np.pi, 0, 1)
ghost = (np.abs(np.hypot(XX - cx, (YY - 140) * 1.25) - 14) < thick) & (YY < 141)
ghost |= ellipse(cx - 14, 138, 4.5, 3)
cv.fill(ghost & ((XX + YY) % 2 < 0.67), C('70f0c0'))
cv.glow(cx, 132, 34, C('40c0a0'), 0.35)
kneel = figure(cx - 46, 206, 46, pose='kneel', facing=1, hood=True, cloak=True)
kneel |= figure(cx + 48, 208, 52, pose='stand', facing=-1, cloak=True, spear=150)
kneel |= ellipse(cx + 50, 160, 10, 3) & (YY < 161)                       # fur-lined shoulders
cv.fill(kneel, C('0c1224')); cv.fill(rim(kneel, 0, -1) | rim(kneel, 1, 0) & (XX < cx), C('9ad8ff'))
for j in range(260):
    x, y = rng.integers(ox, ox + PW), rng.integers(0, DH)
    s = 1 if rng.random() < 0.8 else 2
    for (a_, b_) in ((0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)): put_px(cv, x + a_, y + b_, C('ffffff') * rng.uniform(0.6, 1))
# ---- enrich: fur-cloaked clan in colour, longhouses on the far shore, braziers, snow-laden pines
cv.fill(kneel, C('34405e'))
cv.fill(kneel & (n_ := fbmd(301, cells=(6, 3, 2, 1)) > 0.6), C('4a5878'))
cv.fill(kneel & ((YY > 156) & (YY < 166)) & (XX > cx + 36), C('8a6a4a'))      # fur mantle
cv.fill(kneel & ((YY > 160) & (YY < 168)) & (XX < cx - 30), C('7a5a3e'))
cv.fill(rim(kneel, 0, -1) | (rim(kneel, 1, 0) & (XX < cx)) | (rim(kneel, -1, 0) & (XX > cx)), C('a8e8ff'))
for (hx, hw) in ((ox + 8, 16), (ox + 30, 12), (ox + 136, 14)):
    hb = poly([(hx - hw / 2, 168), (hx + hw / 2, 168), (hx + hw / 2, 162), (hx - hw / 2, 162)]) & ~kneel
    hr = poly([(hx - hw / 2 - 2, 162), (hx + hw / 2 + 2, 162), (hx, 155)]) & ~kneel
    cv.fill(hb, C('3a3040')); cv.fill(hr, C('dfe8f8')); cv.fill(hr & (YY > 160), C('8a9ab8'))
    cv.fill(ellipse(hx, 165, 1.2, 1.2) & ~kneel, C('ffc060')); cv.glow(hx, 165, 8, C('ff9a40'), 0.35)
    for k in range(6):
        cv.fill(ellipse(hx + 2 + k * 0.8, 152 - k * 4, 1.5 + k * 0.4, 1.5 + k * 0.3) & ~kneel, C('8090b0'))
for bx in (cx - 24, cx + 24):
    b = poly([(bx - 3, 196), (bx + 3, 196), (bx + 4, 184), (bx - 4, 184)])
    cv.fill(b, C('2a2a38')); cv.fill(poly([(bx - 4, 184), (bx, 172), (bx + 4, 184)]), C('ffb040'))
    cv.fill(poly([(bx - 2, 184), (bx, 177), (bx + 2, 184)]), C('fff0b0')); cv.glow(bx, 180, 26, C('ff9040'), 0.45)
for (px_, ph_, fl) in ((ox + 2, 110, 1), (ox + 158, 120, -1)):
    for k in range(9):
        yk = 272 - k * ph_ / 10; w = (ph_ / 6.5) * (1 - k / 10)
        tri = poly([(px_ - w, yk), (px_ + w, yk), (px_, yk - ph_ / 6)])
        cv.fill(tri, C('12203a')); cv.fill(tri & ~np.roll(tri, 2, 0), C('f0f6ff')); cv.fill(tri & ~np.roll(tri, 4, 0) & ~np.roll(tri, 2, 0), C('a8b8d8'))
panel(0, cv)

# ------------------------------------------------------------------ west: the axe in the last great stump
cv = Canvas(); ox = PW; cx = ox + 80
cv.grad(np.ones((H, W), bool), YY / 220.0, ramp('2a3a1e', '3e5226', '5a6a30', '7a7a3a', '9a8a44'))
# distant smoke of the camp, through a gap in the trees
for k in range(12):
    cv.glow(cx + 10 + k * 1.5, 120 - k * 9, 10 + k, C('a09878'), 0.25)
far = np.zeros((H, W), bool)
for k in range(9):
    sx = ox + 6 + k * 18 + rng.integers(-4, 4)
    if abs(sx - cx - 10) < 18: continue
    far |= poly([(sx - 3, 200), (sx + 3, 200), (sx + 2, 60), (sx - 2, 60)]) | ellipse(sx, 70, 10, 26)
cv.fill(far, C('2a3a22'))
near = np.zeros((H, W), bool)
for sx, w in ((ox + 6, 14), (ox + 152, 16)):
    near |= poly([(sx - w, 272), (sx + w, 272), (sx + w * 0.6, 0), (sx - w * 0.6, 0)])
cv.fill(near, C('0e160c')); cv.fill(rim(near, 1, 0) & (XX < cx) | rim(near, -1, 0) & (XX > cx), C('3a4a24'))
ground = YY >= 200
cv.grad(ground, (YY - 200) / 72.0, ramp('4a4a26', '3a3a1e', '2a2a16', '1a1a0e'))
for (sx, sy, r) in ((ox + 40, 214, 7), (ox + 120, 210, 6), (ox + 70, 206, 4), (ox + 104, 204, 4), (ox + 20, 226, 9)):
    st = ellipse(sx, sy, r, r * 0.4) | ((np.abs(XX - sx) <= r) & (YY > sy) & (YY < sy + r * 0.8))
    cv.fill(st, C('3a2a18')); cv.fill(ellipse(sx, sy, r, r * 0.4), C('c8a070')); cv.fill(ellipse(sx, sy, r * 0.5, r * 0.2), C('9a7048'))
# the great stump with the axe
gs = poly([(cx - 46, 272), (cx + 46, 272), (cx + 36, 226), (cx - 36, 226)]) | poly([(cx - 60, 272), (cx - 40, 250), (cx - 34, 272)]) | poly([(cx + 60, 272), (cx + 40, 252), (cx + 34, 272)])
cv.grad(gs, (XX - cx + 46) / 92.0, ramp('6a4a2a', '4a321e', '2e1e12', '1e140c'))
top = ellipse(cx, 226, 36, 10)
cv.fill(top, C('d8b07a'))
for r in range(4, 36, 5):
    cv.fill((np.abs(np.hypot((XX - cx) / r, (YY - 226) / (r * 10 / 36)) - 1) < 0.08) & top, C('a8804a'))
handle = capsule((cx + 6, 222), (cx + 30, 168), 2.2)
head = poly([(cx + 9, 214), (cx - 10, 210), (cx - 14, 224), (cx + 6, 226)])
cv.fill(line((cx - 16, 226), (cx + 10, 228), 2), C('3a2210'))       # the cut it sits in
cv.fill(handle, C('5a3a1e')); cv.fill(rim(handle, -1, 0), C('b08050'))
cv.fill(head, C('6a7a88')); cv.fill(rim(head, 0, -1) | rim(head, -1, 0), C('e0eef4')); cv.fill(head & (YY > 222), C('3a4450'))
# totem with antlers and watching eyes in the dark trunks
tot = poly([(ox + 136, 210), (ox + 146, 210), (ox + 145, 120), (ox + 137, 120)])
tot |= line((ox + 137, 122), (ox + 126, 104), 2) | line((ox + 130, 110), (ox + 124, 112), 1) | line((ox + 145, 122), (ox + 156, 104), 2) | line((ox + 152, 110), (ox + 158, 112), 1)
cv.fill(tot, C('1a1a10')); cv.fill(ellipse(ox + 141, 134, 4, 5), C('d8d0b8')); cv.fill(ellipse(ox + 139, 133, 0.8, 0.8) | ellipse(ox + 143, 133, 0.8, 0.8), C('101008'))
for (ex, ey) in ((ox + 8, 150), (ox + 152, 176), (ox + 10, 112)):
    cv.fill(ellipse(ex - 2, ey, 0.9, 0.6) | ellipse(ex + 2, ey, 0.9, 0.6), C('e8ff60'))
for j in range(60):                                                   # sawdust and falling leaves
    x, y = rng.integers(ox, ox + PW), rng.integers(80, 260); put_px(cv, x, y, rng.choice([C('c8a060'), C('8a9a3a'), C('b0702a')]))
# ---- enrich: light shafts through the canopy, the legion camp in the clearing, ferns, a felled trunk, a watcher with antlers
shaft = rays(cx + 30, -40, 52, None, k=0.35, n=16, reach=320) * (YY < 200)
cv.img = np.clip(cv.img + shaft[:, :, None] * C('f0e8a0')[None, None, :], 0, 1)
for (tx, tw_) in ((cx + 4, 9), (cx + 18, 7), (cx + 30, 8)):
    tent = poly([(tx - tw_, 200), (tx + tw_, 200), (tx, 190)])
    cv.fill(tent, C('c8b090')); cv.fill(tent & (XX > tx), C('9a8060')); cv.fill(line((tx, 190), (tx, 186), 1), C('5a3a2a'))
cv.fill(poly([(cx + 40, 200), (cx + 40, 184), (cx + 46, 186), (cx + 40, 189)]), C('b02020'))
log = capsule((ox + 4, 256), (ox + 46, 262), 4.5)
cv.fill(log, C('6a4a2a')); cv.fill(log & ~np.roll(log, 2, 0), C('a07848')); cv.fill(ellipse(ox + 46, 262, 4, 4.5), C('d8b07a')); cv.fill(ellipse(ox + 46, 262, 2, 2.2), C('a8804a'))
for i in range(26):
    fx, fy = rng.uniform(ox + 2, ox + PW - 2), rng.uniform(234, 270)
    for k in range(-3, 4):
        cv.fill(line((fx, fy), (fx + k * 1.6, fy - 6 + abs(k)), 1), C('4a7a2a') if k % 2 else C('6a9a3a'))
for i in range(10):
    mx_, my_ = rng.uniform(ox + 4, ox + PW - 4), rng.uniform(222, 268)
    cv.fill(ellipse(mx_, my_ - 2, 2.2, 1.4) & (YY < my_ - 1.5), C('c03a2a')); cv.fill(line((mx_, my_ - 1.5), (mx_, my_), 1), C('e8d8b8'))
    put_px(cv, mx_ - 1, my_ - 2.6, C('ffffff'))
wat = figure(ox + 150, 214, 34, pose='stand', facing=-1, cloak=True, hood=True)
wat |= line((ox + 146, 182), (ox + 140, 172), 1) | line((ox + 146, 182), (ox + 154, 172), 1) | line((ox + 142, 176), (ox + 138, 176), 1) | line((ox + 152, 176), (ox + 157, 175), 1)
cv.fill(wat, C('2a3a1e')); cv.fill(rim(wat, -1, 0), C('a8c060')); cv.fill(ellipse(ox + 147, 186, 2.6, 3.2), C('d8d0b0'))
put_px(cv, ox + 146, 186, C('101008')); put_px(cv, ox + 148, 186, C('101008'))
panel(1, cv)

# ------------------------------------------------------------------ east: the tower that hides the omen
cv = Canvas(); ox = 2 * PW; cx = ox + 80
cv.grad(np.ones((H, W), bool), YY / 260.0, ramp('0a0418', '180a2e', '2a1244', '42205a', '5e2e6a'))
for j in range(260):
    x, y = rng.integers(ox, ox + PW), rng.integers(0, 200); put_px(cv, x, y, rng.choice([C('ffffff'), C('d8c8ff'), C('ffd8f0')]) * rng.uniform(0.4, 1))
# red comet
for k in range(60):
    x = ox + 128 - k * 1.5; y = 30 + k * 0.7
    cv.glow(x, y, 6 - k * 0.08, C('ff4040'), 0.6 - k * 0.009)
cv.fill(ellipse(ox + 129, 30, 2.5, 2.5), C('fff0e0'))
cv.glow(ox + 129, 30, 14, C('ff6060'), 0.5)
moon = ellipse(ox + 40, 52, 18, 18) & ~ellipse(ox + 48, 46, 16, 16)
cv.fill(moon, C('e8d8ff'))
hills, _ = ridge(220, 30, 41, (50, 20, 8))
cv.grad(hills, (YY - 190) / 80.0, ramp('2a1440', '1e0e30', '120820'))
# crystals on the hills
for (sx, sy, hh) in ((ox + 18, 228, 14), (ox + 30, 232, 9), (ox + 140, 226, 16), (ox + 128, 232, 8)):
    cr = poly([(sx - 3, sy), (sx + 3, sy), (sx + 1, sy - hh), (sx - 1, sy - hh)])
    cv.fill(cr, C('8a50d0')); cv.fill(cr & (XX < sx), C('e0b0ff')); cv.glow(sx, sy - hh / 2, 12, C('a060ff'), 0.25)
tower = poly([(cx - 16, 240), (cx + 16, 240), (cx + 11, 70), (cx - 11, 70)]) | poly([(cx - 18, 72), (cx + 18, 72), (cx + 18, 62), (cx - 18, 62)]) | poly([(cx - 15, 62), (cx + 15, 62), (cx, 24)])
cv.grad(tower, (XX - cx + 16) / 32.0, ramp('6a4a8a', '4a3268', '30204a', '1e1232'))
cv.fill(rim(tower, -1, 0), C('b090d8'))
for wy in (110, 150, 190):
    cv.fill(poly([(cx - 3, wy), (cx + 3, wy), (cx + 3, wy + 9), (cx - 3, wy + 9)]), C('ffcc70') if wy != 150 else C('1a1028'))
cv.glow(cx, 114, 16, C('ffb060'), 0.3)
# astrologer on the balcony, drawing a curtain across the window
bal = poly([(cx - 22, 82), (cx + 22, 82), (cx + 20, 86), (cx - 20, 86)])
cv.fill(bal, C('1e1232'))
ast = figure(cx + 4, 82, 22, pose='stand', robe=True, hood=True, facing=1)
ast |= capsule((cx + 6, 66), (cx + 18, 56), 1.4)                     # pointing up at the comet
cv.fill(ast, C('140a24')); cv.fill(rim(ast, 1, -1), C('ff8080'))
curtain = poly([(cx - 10, 64), (cx - 2, 64), (cx - 3, 82), (cx - 11, 82)])
cv.fill(curtain, C('7a1a3a'))
# a clerk below, sealing the scroll
clerk = figure(cx - 34, 248, 30, pose='stand', robe=True, facing=1)
cv.fill(clerk, C('0e0618')); cv.fill(rim(clerk, 1, 0), C('c090ff'))
cv.fill(ellipse(cx - 24, 230, 3, 2), C('d0c0a0')); cv.fill(ellipse(cx - 22, 230, 1, 1), C('c02020'))
ground = YY >= 240
cv.grad(ground, (YY - 240) / 32.0, ramp('1e0e30', '120820', '0a0414'))
# ---- enrich: the milky way, brickwork and an armillary sphere on the tower, a reflecting pool holding the comet
mw = np.clip(1 - np.abs((YY - 30) - (XX - ox) * 0.9 + 40) / 26, 0, 1) * fbmd(611, cells=(20, 10, 5, 2))
cv.img = np.clip(cv.img + (np.floor(mw * 5 + BAY) / 5)[:, :, None] * C('8a70c0') * 0.5, 0, 1)
for j in range(500):
    x, y = rng.uniform(ox, ox + PW), rng.uniform(0, 200)
    if mw[min(int(y * HI), H - 1), min(int(x * HI), W - 1)] > 0.2: put_px(cv, x, y, C('f0e8ff'), 0.8)
cv.fill(tower & ((((YY - 70) % 6) < 0.67) | (((XX - cx + 3 * (np.floor((YY - 70) / 6) % 2)) % 8) < 0.67)), C('2a1a40'))
ring = (np.abs(np.hypot(XX - cx, (YY - 18) * 1.0) - 7) < 0.7) | (np.abs(np.hypot((XX - cx) * 2.5, YY - 18) - 7) < 0.7) | (np.abs(np.hypot(XX - cx, (YY - 18) * 3) - 7) < 0.7)

rail = (YY > 76) & (YY < 82) & (np.abs(XX - cx) < 22) & (((XX - cx) % 3) < 0.67)
cv.fill(rail | ((np.abs(YY - 76) < 0.6) & (np.abs(XX - cx) < 22)), C('3a2a50'))
pool = ellipse(cx + 40, 256, 26, 5)
cv.fill(pool, C('1a0e30')); cv.fill(pool & (np.abs(XX - (cx + 40) + (YY - 256) * 0.5) < 3), C('ff5050'))
cv.fill(pool & ~np.roll(pool, 1, 0), C('6a4a9a')); cv.fill(pool & (rng.random(pool.shape) > 0.97), C('ffffff'))
cv.fill(ast, C('5a2a7a')); cv.fill(ast & (YY > 74), C('e8c060')); cv.fill(rim(ast, 1, -1), C('ff9090'))
cv.fill(clerk, C('3a1e5a')); cv.fill(clerk & (np.abs(XX - (cx - 34)) < 1), C('d8b050')); cv.fill(rim(clerk, 1, 0), C('c090ff'))
panel(2, cv)

# ------------------------------------------------------------------ below: the hollow under the old altar
cv = Canvas(); ox = 3 * PW; cx = ox + 80
SURF = 70
cv.grad(YY < SURF, YY / SURF, ramp('3a2a4a', '6a4a5a', 'b0705a', 'e0a060'))
surf = YY >= SURF
n = fbmd(44, cells=(30, 14, 6, 3))
strata = ((YY - SURF) / 12.0 + n * 1.8) % 3
pal = [ramp('6a4a2e', '5a3e26', '4a321e'), ramp('7a5a36', '68482c', '563a22'), ramp('4e3a2a', '40301e', '322416')]
for k in range(3):
    m = surf & (np.floor(strata) == k)
    cv.grad(m, np.clip((YY - SURF) / 200.0, 0, 1), pal[k])
# the great hollow
cav = ellipse(cx, 196, 74, 52) | ellipse(cx - 30, 220, 50, 34) | ellipse(cx + 34, 180, 40, 30)
cav &= ~(n > 0.72) | (YY > 230)
cv.fill(cav, C('060408'))
cv.fill(outline(cav) & surf, C('2a1c14'))
cv.fill(rim(cav, 0, 1) & ((XX + YY) % 2 < 0.67), C('1a120e'))
# stalactites
for k in range(16):
    sx = cx - 70 + k * 9 + rng.integers(-3, 3)
    top_y = np.nonzero(cav[:, int(sx * HI)])[0]
    if len(top_y):
        ty = top_y[0] / HI; L = rng.integers(4, 16)
        cv.fill(poly([(sx - 2, ty - 1), (sx + 2, ty - 1), (sx, ty + L)]), C('2a1c14'))
# crack from the altar down into the hollow
cr = np.zeros((H, W), bool); px, py = cx + 2, SURF
while py < 150:
    nx, ny = px + rng.integers(-3, 4), py + rng.integers(4, 9)
    cr |= line((px, py), (nx, ny), 2); px, py = nx, ny
cv.fill(cr, C('080406')); cv.fill(np.roll(cr, 1, 1) & ~cr & surf, C('ffb060') * 0.6)
# altar with its fire, on the surface
alt = poly([(cx - 16, SURF), (cx + 16, SURF), (cx + 12, SURF - 8), (cx - 12, SURF - 8)])
cv.fill(alt, C('3a2a2a')); cv.fill(rim(alt, 0, -1), C('e0b080'))
cv.glow(cx, SURF - 12, 22, C('ffa040'), 0.6)
cv.fill(poly([(cx - 5, SURF - 8), (cx - 2, SURF - 18), (cx, SURF - 13), (cx + 3, SURF - 22), (cx + 5, SURF - 8)]), C('ffe080'))
pr = figure(cx + 28, SURF, 20, pose='stand', robe=True, arms_up=True, facing=-1)
cv.fill(pr, C('1e1018')); cv.fill(rim(pr, -1, 0), C('ffc080'))
# a single miner, tiny, holding up a lantern at the edge of the dark
mx, my = cx - 52, 236
cv.glow(mx + 8, my - 22, 30, C('ffb050'), 0.55)
mn = figure(mx, my, 24, pose='walk', facing=1, helmet=True)
cv.fill(mn, C('140c08')); cv.fill(rim(mn, 1, 0), C('ffc070'))
cv.fill(ellipse(mx + 8, my - 22, 1.6, 2), C('fff0b0'))
cv.fill(line((mx + 6, my - 12), (mx + 8, my - 20), 1), C('140c08'))
cv.fill(ellipse(mx - 4, my - 21, 3.5, 4), C('6a5a3a'))           # pick over the shoulder
# a pale glow far down, something under there
cv.glow(cx + 30, 238, 22, C('a0b0c0'), 0.25)
cv.fill(ellipse(cx + 30, 240, 2, 1), C('d8e0f0'))
# ---- enrich: roots and bones in the strata, broken columns of an older temple in the hollow, glowing glyphs, a still pool
for i in range(9):
    rx_ = ox + 10 + i * 17 + rng.uniform(-4, 4); py_ = SURF
    rt = np.zeros((H, W), bool); px_ = rx_
    for k in range(6):
        nx_ = px_ + rng.uniform(-4, 4); ny_ = py_ + rng.uniform(3, 7)
        rt |= line((px_, py_), (nx_, ny_), 1); px_, py_ = nx_, ny_
    cv.fill(rt & ~cav, C('3a2414'))
for i in range(6):
    bx_, by_ = rng.uniform(ox + 6, ox + PW - 6), rng.uniform(96, 140)
    bone = capsule((bx_, by_), (bx_ + 6, by_ + 1), 0.8) | ellipse(bx_, by_, 1.3, 1.3) | ellipse(bx_ + 6, by_ + 1, 1.3, 1.3)
    cv.fill(bone & ~cav, C('d8c8a8'))
cv.fill(ellipse(ox + 30, 120, 4, 3) & ~cav & ~ellipse(ox + 30, 120, 2, 1.5), C('c8b890'))     # an old skull-shaped fossil
for (colx, colh, broken) in ((cx - 20, 44, False), (cx + 8, 30, True), (cx + 36, 52, False)):
    colm = poly([(colx - 4, 236), (colx + 4, 236), (colx + 3.5, 236 - colh), (colx - 3.5, 236 - colh)])
    if broken: colm &= ~poly([(colx - 6, 236 - colh), (colx + 6, 236 - colh + 8), (colx + 6, 236 - colh - 4)])
    cv.grad(colm, np.clip((XX - colx + 4) / 8, 0, 1), ramp('8a8070', '5a5248', '3a342e', '242018'))
    cv.fill(colm & (((XX - colx) % 2.5) < 0.67), C('2a2620'))
    cv.fill(poly([(colx - 6, 236 - colh), (colx + 6, 236 - colh), (colx + 5, 236 - colh - 3), (colx - 5, 236 - colh - 3)]) & (not broken), C('6a6258'))
    cv.fill(ellipse(colx, 236 - colh * 0.55, 1.6, 2.4), C('80ffd8')); cv.glow(colx, 236 - colh * 0.55, 10, C('40d0b0'), 0.3)
lake = cav & (YY > 240)
cv.fill(lake, C('0c1418')); cv.fill(lake & ((YY % 3) < 0.67) & (rng.random(lake.shape) > 0.6), C('2a4048'))
for (colx, colh) in ((cx - 20, 44), (cx + 36, 52)):
    cv.fill(lake & (np.abs(XX - colx) < 3) & (YY < 240 + colh * 0.4) & ((YY % 2) < 1), C('3a3a36'))
cv.fill(mn, C('5a3a22')); cv.fill(mn & (YY < my - 20), C('8a7a5a')); cv.fill(rim(mn, 1, 0), C('ffc070'))
panel(3, cv)

# frames between panels
for i in range(1, 4):
    xr = int(i * PW * HI)
    final[:, xr - 2:xr + 2] = C('1a1410')
    final[:, xr - 1] = C('8a6a3a')
img = Image.fromarray((np.clip(final, 0, 1) * 255).astype(np.uint8))
img.save('h3_pic.png')
labels = [(int(80 * HI), int(10 * HI), '北 · 霜湾', (210, 228, 255)), (int(240 * HI), int(10 * HI), '西 · 荆冠', (200, 240, 180)), (int(400 * HI), int(10 * HI), '东 · 暮紫', (236, 206, 255)), (int(560 * HI), int(10 * HI), '古祭坛之下', (255, 220, 170))]
present_slide(img, 2, 5, '北方说帝国夺走了先祖的号角。西方的森林被砍去建祭坛和军营。东方掌管历法，却不肯公开今年的凶兆。而矿工说，古祭坛底下的地是空的。', labels=labels).save('h3.png')
