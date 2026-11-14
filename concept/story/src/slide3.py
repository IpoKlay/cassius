"""Slide 3: four vignettes of a world under strain - north, west, east, and beneath the altar."""
from slidekit import *
import math, random
from kit import *
import sprites as S
import figures3d as F
import buildings3d as B
import props3d as PR
from fx import flame, torch_on

X0, Y0, PW, PH = 160, 68, 319, 135          # each vignette is composed in the middle of a full frame, then cropped
yy, xx = np.mgrid[0:H, 0:W]


def finish(sc, img, lift, sat=1.0, contrast=1.12):
    img = grade(img, lift, gamma=1.03, sat=sat, vignette=0.0, contrast=contrast)
    return img[Y0:Y0 + PH, X0:X0 + PW]


# ---------------------------------------------------------------- north: the empty plinth by the fjord
def north():
    sc = Scene(seed=31); rng = random.Random(31)
    sc.sun = (0.6, 0.4)
    SN = [C('6a7a9a'), C('8292b4'), C('9cacca'), C('b8c6de'), C('d6e0ee')]
    n = fbm(W, H, 31, cells=(32, 16, 8, 4))
    g = band(np.clip(0.5 + (n - 0.5) * 0.8, 0, 0.999), len(SN), dither=False)
    sc.alb[:] = np.array(SN)[(g * len(SN)).astype(int)]
    for i in range(500):
        x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
        sc.alb[y, x] = C('ffffff')
    shore = lambda x: 106 + 6 * np.sin(x / 23.0) + 3 * np.sin(x / 7.0)
    sc.add(bake('longship', B.longship, (110, 46), 1.7, -25, pitch=18), 330, 112, depth=40)
    for x in (200, 236, 440, 468):
        sc.add(S.snow_pine(rng.randint(0, 999), h=rng.randint(50, 64)), x, 96 + rng.randint(-2, 6))
    sc.add(bake('plinth_empty', lambda: B.plinth(True), (30, 30), 1.9, 25, pitch=22), 318, 150)
    nm = bake('northman', lambda: F.human(body='blue', legs='fur', cloak='fur', beard='brown', head='helmet', arms=('down', 'forward'), shield='round', spear=True, scale=1.1), (44, 66), 1.15, 30)
    nm2 = bake('northman_point', lambda: F.human(body='blue', legs='fur', cloak='fur', beard='linen', head='bare', hair='brown', arms=('out', 'down'), scale=1.1), (44, 66), 1.15, 60)
    nm3 = bake('northman_back', lambda: F.human(body='fur', legs='fur', cloak='blue', beard='brown', head='helmet', arms=('down', 'down'), shield='round', spear=True, scale=1.1), (44, 66), 1.15, 200)
    sc.add(nm2, 280, 164); sc.add(nm[:, ::-1].copy(), 372, 168); sc.add(nm3, 330, 196); sc.add(nm, 236, 190)
    rs, rse = S.runestone(True)
    sc.add(rs, 430, 150, emissive=rse)
    sc.light(430, 132, 40, (0.35, 0.65, 1.0), 0.5)
    for x in (262, 392):
        sc.add(rgba(2, 1), x, 150)
        torch_on(sc, x, 128, 151, seed=x, light=0.8, radius=50)
        pole = rgba(2, 24); pole[:, :, :3] = C('4a3020'); pole[:, :, 3] = 1
        sc.add(pole, x, 152, depth=150)
    sc.compose_items()
    img = sc.lit(C('3a4a80') * 0.8, C('aabce0') * 0.5, shadow_strength=0.7)
    sky = lambda x, y: C('3a4a78') + C('8aa0d0') * 0.2 * (0.5 + 0.5 * math.sin(x * 0.05))
    img = reflect(img, lambda x: shore(np.array(x)) * 0 + 300, C('2a3a60'))    # (no river)
    water = yy < shore(xx)
    wm = water & ~sc.obj
    img[wm] = img[wm] * 0.35 + C('22305a') * 0.65
    rip = wm & (np.sin(xx * 0.21 + yy * 1.7) > 0.85)
    img[rip] = img[rip] * 0.6 + C('8aa0d0') * 0.4
    edge = np.abs(yy - shore(xx)) < 1
    img[edge] = C('dce6f4')
    r = random.Random(4)
    for i in range(300):
        x, y = r.randint(X0, X0 + PW - 1), r.randint(Y0, Y0 + PH - 1)
        img[y, x] = img[y, x] * 0.2 + C('ffffff') * 0.85
    for (x, y, rr, c, s) in sc.lights:
        img = sc.glow(img, x, y, 9, tuple(c), 0.25, bands=3)
    return finish(sc, img, C('0e1430'))


# ---------------------------------------------------------------- west: the forest cut down for altars
def west():
    sc = Scene(seed=32); rng = random.Random(32)
    sc.sun = (1.2, 0.35)
    GR = [C('1a2a16'), C('263c1c'), C('344e22'), C('46642a'), C('5e7e34')]
    n = fbm(W, H, 32, cells=(32, 16, 8, 4))
    g = band(np.clip(0.5 + (n - 0.5) * 0.8, 0, 0.999), len(GR), dither=False)
    sc.alb[:] = np.array(GR)[(g * len(GR)).astype(int)]
    for i in range(1200):                     # sawdust and chips
        x, y = rng.randint(200, 440), rng.randint(110, 200)
        sc.alb[y, x] = rng.choice([C('b89a6a'), C('8a6a46'), C('d8c090')])
    P = [C('0c1e14'), C('16301c'), C('224424'), C('345e2c'), C('5a8838')]
    BARK = [C('1c1612'), C('34281e'), C('54402e')]
    for x in range(140, 500, 26):
        sc.add(S.oak(rng.randint(0, 999), P, BARK, R=rng.randint(16, 22), fine=0.7), x, 104 + rng.randint(-4, 4))
    stump = bake('stump', B.stump, (20, 14), 1.8, 10, pitch=30)
    for (x, y) in ((222, 128), (300, 122), (380, 132), (250, 176), (424, 170), (196, 196)):
        sc.add(stump, x, y)
    sc.add(bake('logpile', B.logpile, (40, 24), 2.0, -35, pitch=24), 334, 160)
    wc = bake('woodcutter', lambda: F.human(body='red', legs='skin', head='helmet', arms=('axe', 'axe'), axe=True), (40, 62), 1.2, 40)
    sc.add(wc, 282, 150); sc.add(wc[:, ::-1].copy(), 404, 156)
    sc.add(sprite('legionary1'), 230, 154)
    sc.add(sprite('cart'), 360, 200)
    gob = bake('goblin', lambda: F.human(body='fur', legs='goblin', skin='goblin', scale=0.72, mask=True, arms=('down', 'forward'), spear=True, head='none', belt='leather'), (34, 52), 1.25, -40)
    sc.add(gob, 466, 128); sc.add(gob[:, ::-1].copy(), 184, 120)
    sc.add(S.totem(), 448, 120)
    for (x, y) in ((176, 104), (486, 110), (458, 100)):
        e, ee = S.goblin_eyes()
        sc.add(e, x, y, emissive=ee, cast=False, depth=999)
    sc.compose_items()
    img = sc.lit(C('3a5a78') * 0.62, C('ffe0b0') * 0.66, shadow_strength=0.75)
    ray = np.sin((xx * 0.7 + yy) * 0.07) * 0.5 + 0.5
    img = img + C('fff0c8')[None, None, :] * band(np.clip((ray - 0.7) * 3, 0, 1) * 0.1, 3, dither=False)[:, :, None]
    img = fog(img, C('b8ccd8'), 0.25, 80, 210, seed=33)
    return finish(sc, img, C('10243a'))


# ---------------------------------------------------------------- east: the tower that keeps the calendar
def east():
    sc = Scene(seed=33); rng = random.Random(33)
    sc.sun = (0.4, 0.5)
    VG = [C('2a1a3e'), C('3a2450'), C('4a2e62'), C('5e3a76'), C('76488c')]
    n = fbm(W, H, 33, cells=(32, 16, 8, 4))
    g = band(np.clip(0.5 + (n - 0.5) * 0.8, 0, 0.999), len(VG), dither=False)
    sc.alb[:] = np.array(VG)[(g * len(VG)).astype(int)]
    # paved terrace
    # reflecting pool: shows the night sky - stars and the forbidden comet
    pool = ((xx - 352) / 44.0) ** 2 + ((yy - 162) / 16.0) ** 2 < 1
    sc.alb[pool] = C('0e0a1e')
    rr = random.Random(5)
    for i in range(70):
        x, y = rr.randint(310, 396), rr.randint(148, 176)
        if pool[y, x]:
            sc.emi[y, x] = C('fff4e0') * rr.uniform(0.5, 1.0)
    for k in range(26):                          # the comet, red, streaking
        x, y = 372 - k, 156 + k * 0.35
        for w in range(max(1, 3 - k // 9)):
            if pool[int(y) + w, int(x)]:
                sc.emi[int(y) + w, int(x)] = C('ff6a50') * (1.2 - k * 0.04)
    rim = pool & ~np.roll(pool, 1, axis=0)
    sc.alb[rim] = C('b8a4d0')
    tower = bake('tower', B.watchtower, (40, 90), 1.25, 10, pitch=10)
    sc.add(tower, 250, 186)
    sc.light(250, 140, 44, (1.0, 0.75, 0.35), 0.7)
    sc.add(bake('tower_far', B.watchtower, (40, 90), 0.9, -15, pitch=10), 456, 128, depth=60)
    sc.light(456, 100, 30, (1.0, 0.75, 0.35), 0.5)
    for (x, y) in ((200, 132), (300, 118), (420, 196), (196, 200)):
        ob = bake('obelisk', lambda: PR.column_model(16.0, False), (20, 40), 1.6, 20)
        sc.add(ob * np.array([0.8, 0.7, 1.0, 1.0]), x, y)
    ast = bake('astrologer', lambda: F.human(body='violet', robe=True, cloak='purple', head='hood', arms=('up', 'forward'), belt='gold'), (40, 62), 1.2, 30)
    sc.add(ast, 310, 158)
    clerk = bake('clerk', lambda: F.human(body='purple', robe=True, cloak='violet', head='hood', arms=('chest', 'chest'), scroll=True), (40, 62), 1.1, -20)
    sc.add(clerk, 404, 142)
    for (x, y) in ((210, 166), (430, 190), (232, 196)):
        cr = rgba(8, 14)
        for yy2 in range(14):
            for xx2 in range(8):
                if abs(xx2 - 3.5) < yy2 * 0.3:
                    put(cr, xx2, yy2, C('c8a0f0') if xx2 < 4 else C('7a4ab0'))
        sc.add(cr, x, y, emissive=cr * np.array([0.5, 0.4, 0.7, 1]), cast=False)
        sc.light(x, y - 6, 26, (0.7, 0.45, 1.0), 0.5)
    sc.compose_items()
    img = sc.lit(C('3a2a6a') * 0.7, C('a090d0') * 0.4, shadow_strength=0.7)
    img = sc.glow(img, 250, 146, 14, (1.0, 0.8, 0.4), 0.3, bands=3)
    r = random.Random(7)
    for i in range(60):
        x, y = r.randint(X0, X0 + PW - 1), r.randint(Y0, Y0 + PH - 1)
        img[y, x] = img[y, x] * 0.4 + C('e8d0ff') * 0.6
    return finish(sc, img, C('140a28'), sat=1.08)


# ---------------------------------------------------------------- beneath: the hollow under the old altar
def below():
    sc = Scene(seed=34); rng = random.Random(34)
    sc.sun = (1.0, 0.3)
    surf = 132                                   # ground level in this cut-away
    EA = [C('2a1c16'), C('3a281e'), C('4c3626'), C('5e4430'), C('70523a')]
    n = fbm(W, H, 34, cells=(24, 12, 6, 3))
    strata = np.floor((yy - surf) / 9 + np.sin(xx / 30.0) * 0.6).astype(int)
    tone = np.clip((n * 3 + strata % 3) / 5.0, 0, 0.999)
    sc.alb[:] = np.array(EA)[(tone * len(EA)).astype(int)]
    grass = yy < surf
    sc.alb[grass] = np.array([C('3e5222'), C('4e6428'), C('62782e')])[((n[grass] * 3).astype(int)) % 3]
    sc.alb[(yy >= surf) & (yy < surf + 2)] = C('243014')
    for i in range(160):                          # embedded stones and bones
        x, y = rng.randint(X0, X0 + PW), rng.randint(surf + 4, Y0 + PH)
        sc.alb[y:y + 2, x:x + 3] = rng.choice([C('6a6266'), C('8a8284'), C('c8bea8')])
    # the hollow: an irregular dark cavern directly below the altar
    cav = (((xx - 316) / 96.0) ** 2 + ((yy - 184) / 20.0) ** 2) < (1 + 0.12 * np.sin(xx / 9.0) + 0.08 * np.sin(yy / 5.0))
    cav &= yy > surf + 14
    depth = np.clip((yy - 150) / 40.0, 0, 1)
    sc.alb[cav] = (C('0c0808')[None, :] * (1 - depth[cav][:, None]) + C('180c10')[None, :] * depth[cav][:, None])
    ceil = cav & ~np.roll(cav, 1, axis=0)
    sc.alb[ceil] = C('4a3628')
    for i in range(40):                           # roots and drips hanging from the ceiling
        x = rng.randint(240, 400)
        ys = np.nonzero(cav[:, x])[0]
        if len(ys):
            for k in range(rng.randint(3, 10)):
                if ys[0] + k < H:
                    sc.alb[ys[0] + k, x] = C('5a3e28') if k % 3 else C('3a2618')
    # a crack from the altar down into the void
    x = 316
    for y in range(surf + 2, surf + 22):
        x += rng.choice([-1, 0, 1])
        sc.alb[y, x] = C('060404'); sc.alb[y, x + 1] = C('140c0a')
    # something below glows faintly
    glow_pts = [(300, 192), (338, 196)]
    alt = bake('altar_small', B.altar_stone, (60, 40), 1.4, 20, pitch=24)
    sc.add(alt, 316, surf + 2)
    fl, fe = flame(12, 14, 9, 26)
    sc.add(fl, 316, surf + 2 - alt.shape[0] + 8, emissive=fe, cast=False, depth=surf + 3)
    sc.light(316, surf - alt.shape[0], 40, (1.0, 0.55, 0.25), 0.6)
    sc.add(bake('priest_up', None, (40, 62), 1.2, 20), 362, surf + 4)
    miner = bake('miner', lambda: F.human(body='brown', legs='brown', head='cap', arms=('down', 'forward'), lantern=True, beard='mane'), (40, 62), 1.1, 30)
    miner2 = bake('miner2', lambda: F.human(body='grey', legs='brown', head='cap', arms=('axe', 'down'), axe=True), (40, 62), 1.1, -30)
    sc.add(miner, 270, 200, cast=False); sc.add(miner2, 364, 202, cast=False)
    sc.compose_items()
    img = sc.lit(C('3a3448') * 0.55, C('ffd8a8') * 0.55, shadow_strength=0.6)
    img[cav & ~sc.obj] *= 0.6
    img = sc.glow(img, 278, 176, 30, (1.0, 0.7, 0.3), 0.35, bands=4)        # the miner's lantern
    img = sc.glow(img, 318, 204, 46, (0.5, 0.9, 0.7), 0.18, bands=4)        # a pale glow from deeper down
    return finish(sc, img, C('140c10'))


panels = [north(), west(), east(), below()]
pic_arr = np.zeros((H, W, 3))
for i, p in enumerate(panels):
    ox, oy = (i % 2) * (PW + 2), (i // 2) * (PH + 2)
    pic_arr[oy:oy + PH, ox:ox + PW] = p
pic = to_image(pic_arr, colors=0)
pic.save('slide3_pic.png')
labels = [(60, 6, '北 · 霜湾', (210, 226, 255)), (380, 6, '西 · 荆冠', (200, 236, 190)), (60, 143, '东 · 暮紫', (232, 210, 255)), (380, 143, '古祭坛之下', (240, 214, 180))]
out = present_slide(pic, 2, 5, '北方说帝国夺走了先祖的号角。西方的森林被砍去建祭坛和军营。东方掌管历法，却不肯公开今年的凶兆。而矿工说，古祭坛底下的地是空的。', labels=labels)
out.save('slide3.png')
