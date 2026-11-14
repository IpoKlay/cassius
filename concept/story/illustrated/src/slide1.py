"""Slide 1: the four realms around the inner sea - an illustrated pixel map."""
from slidekit import *
import math, random
from kit import *
import sprites as S
import figures3d as F
import buildings3d as B
import props3d as PR

rng = random.Random(11)
yy, xx = np.mgrid[0:H, 0:W]
cx, cy = 320, 138
dx, dy = (xx - cx) / 292.0, (yy - cy) / 120.0
d = np.hypot(dx, dy)
ang = np.degrees(np.arctan2(dy, dx))
n1 = fbm(W, H, 101, cells=(64, 32, 16, 8)); n2 = fbm(W, H, 102, cells=(24, 12, 6, 3))
inner = 0.30 + (n1 - 0.5) * 0.22
outer = 0.93 + (n2 - 0.5) * 0.22 + (n1 - 0.5) * 0.12
# fjords: deep inlets cut into the northern coast
fj = (ang < -50) & (ang > -130) & (np.sin(xx * 0.11 + n1 * 6) > 0.86) & (d > 0.7)
land = (d > inner) & (d < outer) & ~fj
island = np.hypot((xx - cx) / 26.0, (yy - cy) / 13.0) < 1 + (n2 - 0.5) * 0.5
land |= island
angw = ang + (n2 - 0.5) * 70 + np.sin(d * 9) * 6
region = np.where((angw >= -135) & (angw < -45), 0, np.where((angw >= -45) & (angw < 45), 2, np.where((angw >= 45) & (angw < 135), 3, 1)))  # 0 N,1 W,2 E,3 S
elev = np.clip((n1 * 0.7 + n2 * 0.5) * (0.6 + 0.8 * np.clip((d - inner) / 0.6, 0, 1)), 0, 1)
PAL = {
    0: [C('5a6a7e'), C('7a8ca2'), C('9cb0c6'), C('c4d4e4'), C('f0f6ff')],
    1: [C('1e3a1e'), C('2c5026'), C('3e6a2e'), C('5a8a3a'), C('86aa50')],
    2: [C('3a2050'), C('542e6c'), C('70408a'), C('9058a8'), C('c290d0')],
    3: [C('7a5a2a'), C('9a7a36'), C('b89a46'), C('d4b65e'), C('ecd48a')],
}
img = np.zeros((H, W, 3))
# sea: deep outside, lighter inner sea, shallows by the coast
dist_land = np.zeros((H, W))
from scipy import ndimage
dist_land = ndimage.distance_transform_edt(~land)
sea = np.where((d < 0.6)[:, :, None], C('2a5a7a')[None, None, :] * np.ones((H, W, 1)), C('163050')[None, None, :] * np.ones((H, W, 1)))
sea = sea * (1 + 0.08 * np.sin(xx * 0.05 + yy * 0.09)[:, :, None])
shallow = np.clip(1 - dist_land / 7.0, 0, 1)
sea = sea * (1 - band(shallow, 3, dither=False)[:, :, None] * 0.0) + C('5a9ab0') * band(shallow, 3, dither=False)[:, :, None] * 0.45
img[:] = sea
# wave glyphs
for i in range(900):
    x, y = rng.randint(2, W - 6), rng.randint(2, H - 3)
    if not land[y, x] and dist_land[y, x] > 4:
        img[y, x:x + 2] = img[y, x:x + 2] * 0.6 + 0.35
        img[y - 1, x + 2:x + 4] = img[y - 1, x + 2:x + 4] * 0.6 + 0.35
# land colour by region and elevation with hill shading from the north-west
gy, gx = np.gradient(elev * 30)
shade = np.clip(0.5 - (gx * 0.6 + gy * 0.8) * 0.5, 0, 1)
for r, pal in PAL.items():
    m = land & (region == r)
    t = np.clip(elev * 0.7 + shade * 0.45 - 0.08, 0, 0.999)
    t = band(t, len(pal), dither=False)
    img[m] = np.array(pal)[(t[m] * len(pal)).astype(int)]
img[island] = np.array(PAL[3])[2] * 1.05
rb = land & ((region != np.roll(region, 1, 0)) | (region != np.roll(region, 1, 1))) & ~island & (d > inner + 0.04)
img[rb] = C('2a1a14')
coast = land & (ndimage.binary_dilation(~land) & land)
img[coast] = img[coast] * 0.55 + C('f0e2b0') * 0.45
foam = (~land) & (dist_land < 1.5)
img[foam] = img[foam] * 0.4 + C('e8f0f4') * 0.6


def stamp(a, x, y, mult=1.0):
    h, w = a.shape[:2]
    x0, y0 = int(x - w / 2), int(y - h)
    for j in range(h):
        for i in range(w):
            if a[j, i, 3] > 0.5 and 0 <= x0 + i < W and 0 <= y0 + j < H:
                img[y0 + j, x0 + i] = a[j, i, :3] * mult


# west: dense forest canopy, smoke from tribal fires, totems
pts = [(x, y) for x, y in zip(rng.choices(range(W), k=5000), rng.choices(range(H), k=5000)) if land[y, x] and region[y, x] == 1]
for (x, y) in sorted(pts, key=lambda p: p[1])[:1400]:
    for (ox, oy, c) in ((0, 0, C('16301a')), (1, 0, C('2a4a24')), (-1, 0, C('22401e')), (0, -1, C('5a8a3a')), (1, -1, C('3e6a2e')), (0, 1, C('0e1e10'))):
        if 0 <= x + ox < W and 0 <= y + oy < H and land[y + oy, x + ox]:
            img[y + oy, x + ox] = c
# north: peaks with snow, little pines, the longship in the fjord
pk = [(x, y) for x, y in zip(rng.choices(range(8, W - 8), k=3000), rng.choices(range(10, H - 4), k=3000)) if land[y, x] and region[y, x] == 0 and elev[y, x] > 0.45]
for (x, y) in sorted(pk[:70], key=lambda p: p[1]):
    hgt = rng.randint(6, 10)
    for k in range(hgt):
        hw = (hgt - k) * 0.8
        for i in range(int(-hw), int(hw) + 1):
            c = C('f4f8ff') if k > hgt * 0.55 else (C('8a9cb4') if i < 0 else C('4e5c72'))
            img[y - k, x + i] = c
for i in range(500):
    x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
    if land[y, x] and region[y, x] == 0 and elev[y, x] <= 0.5:
        img[y, x] = C('1e3a3a'); img[y - 1, x] = C('2c4e48'); img[y + 1, x - 1:x + 2] = C('16302e')
ship = bake('longship_map', B.longship, (60, 30), 0.85, -25, pitch=22)
stamp(ship, 238, 30); stamp(ship[:, ::-1], 470, 26)
# east: violet towers, crystal outcrops
tw = bake('tower_map', B.watchtower, (20, 50), 0.55, 10, pitch=12)
ept = [(x, y) for x, y in zip(rng.choices(range(W), k=4000), rng.choices(range(H), k=4000)) if land[y, x] and region[y, x] == 2 and 0.55 < d[y, x] < 0.8 and land[min(y + 3, H - 1), x]]
placed = []
for (x, y) in ept:
    if all(abs(x - a) > 24 or abs(y - b) > 30 for a, b in placed):
        placed.append((x, y))
    if len(placed) == 4: break
for (x, y) in sorted(placed, key=lambda p: p[1]):
    stamp(tw, x, y + 2)
for i in range(160):
    x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
    if land[y, x] and region[y, x] == 2:
        for k in range(4):
            img[y - k, x] = C('e8c8ff') if k > 1 else C('8a50c0')
# south: patchwork fields, roads, the capital and the border fort
for i in range(220):
    x, y = rng.randint(0, W - 12), rng.randint(0, H - 8)
    if land[y, x] and region[y, x] == 3 and land[y + 6, x + 10]:
        c = rng.choice([C('d4b65e'), C('b8a040'), C('8a9a3a'), C('a6743a'), C('c8c070')])
        img[y:y + rng.randint(3, 6), x:x + rng.randint(6, 11)] = c
        img[y, x:x + 10] = img[y, x:x + 10] * 0.8
temple = bake('temple_map', lambda: B.temple_front(6, 9.0, 30.0, 10.0), (60, 34), 0.55, 0, pitch=20)
stamp(temple, 352, 236)
aq = sprite('aqueduct')
aqs = aq[::4, ::4]
stamp(aqs, 410, 226)
fort = bake('gate_map', B.gatehouse, (40, 26), 0.55, 0, pitch=18)
stamp(fort, 168, 222)
stamp(temple, 320, 142)                                         # the Great Altar on its island
# the route: from the border fort up the north road, round to the Great Altar
route = [(168, 216), (130, 190), (96, 150), (108, 108), (160, 74), (230, 60), (300, 76), (316, 112), (320, 132)]
pts = []
for (a, b) in zip(route, route[1:]):
    for t in np.linspace(0, 1, 30, endpoint=False):
        pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
import os
np.savez('slide1_state.npz', land=land, region=region, d=d, island=island, dist_land=dist_land, elev=elev, route=np.array(pts))
for i, (x, y) in enumerate(pts):
    if (i // 3) % 2 == 0 and not os.environ.get('NOROUTE'):
        img[int(y), int(x)] = C('c8281c'); img[int(y) + 1, int(x)] = C('6a1010')
# sea serpent in the western ocean, compass rose in the south-east
for k in range(4):
    x0 = 20 + k * 9
    for t in np.linspace(0, math.pi, 10):
        img[int(250 - math.sin(t) * 5), int(x0 + t * 2)] = C('2e6a4a')
img[244:247, 56:59] = C('2e6a4a')
cr_x, cr_y = 596, 236
for a in range(0, 360, 45):
    L = 14 if a % 90 == 0 else 8
    for r in range(L):
        img[int(cr_y + math.sin(math.radians(a)) * r), int(cr_x + math.cos(math.radians(a)) * r)] = C('e0c070') if a % 90 == 0 else C('a08040')
img[cr_y - 15:cr_y - 13, cr_x] = C('f0e0b0')
# parchment frame and soft vignette
img = grade(img, C('1a1020'), gamma=1.0, sat=1.08, vignette=0.75, contrast=1.06)
img[:2, :] = C('8a6a3a'); img[-2:, :] = C('8a6a3a'); img[:, :2] = C('8a6a3a'); img[:, -2:] = C('8a6a3a')
img[3, 3:-3] = C('c8a050'); img[-4, 3:-3] = C('c8a050'); img[3:-3, 3] = C('c8a050'); img[3:-3, -4] = C('c8a050')
pic = to_image(img, colors=0)
pic.save('slide1_base.png' if os.environ.get('NOROUTE') else 'slide1_pic.png')
labels = [(320, 18, '霜湾氏族', (210, 228, 255)), (70, 124, '荆冠诸部', (190, 240, 180)), (574, 124, '暮紫巫庭', (236, 206, 255)),
          (300, 248, '赤旌帝国', (255, 226, 170)), (250, 132, '内 海', (190, 220, 240)), (320, 144, '大祭场', (255, 236, 200)), (168, 228, '边境要塞', (255, 200, 170))]
LABELS = labels
if os.environ.get('NOROUTE'): raise SystemExit
out = present_slide(pic, 0, 5, '内海四周环伺着四股势力。每一方都相信神明在索要不同的东西——也都认为，别人献错了。', labels=labels)
out.save('slide1.png')
