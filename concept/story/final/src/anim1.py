"""Slide 1 animated: seamless 6 s loop of per-realm particles over the map."""
import sys, subprocess, math, random
import numpy as np
from PIL import Image
from slidekit import present_slide

T = 180
base = np.asarray(Image.open('slide1_base.png').convert('RGB')).astype(float) / 255
S = np.load('slide1_state.npz')
land, region, d, island, dist_land, route = S['land'], S['region'], S['d'], S['island'], S['dist_land'], S['route']
H, W = land.shape
rng = np.random.default_rng(7)
TAU = 2 * math.pi
def C(h): return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0

def sample(mask, n, box=None):
    ys, xs = np.nonzero(mask)
    i = rng.integers(0, len(xs), n)
    return xs[i].astype(float), ys[i].astype(float)

class Emitter:
    """n particles, each born at a fixed point with a fixed phase; age = (t + phase) % life loops seamlessly."""
    def __init__(s, n, life, x, y, **kw):
        s.n, s.life, s.x, s.y = n, life, x, y
        s.ph = rng.integers(0, life, n); s.r = rng.random(n); s.kw = kw
    def ages(s, t):
        a = (t + s.ph) % s.life
        return a, a / s.life

def put(img, x, y, c, a=1.0, add=False):
    xi, yi = int(round(x)), int(round(y))
    if 0 <= xi < W and 0 <= yi < H:
        if add: img[yi, xi] = np.minimum(1, img[yi, xi] + c * a)
        else: img[yi, xi] = img[yi, xi] * (1 - a) + c * a

def glow(img, x, y, c, a):
    put(img, x, y, c, a, True)
    for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        put(img, x + ox, y + oy, c, a * 0.35, True)

def fade(u, k=0.15):
    return np.clip(np.minimum(u / k, (1 - u) / k), 0, 1)

north_zone = (region == 0) & (d > 0.5)
yy, xx = np.mgrid[0:H, 0:W]
north_zone &= yy < 150
nz = np.zeros((H + 40, W)); nz[40:] = north_zone; nz[:40] = north_zone[0]   # allow spawning above the frame
snow = Emitter(700, 180, *sample(north_zone, 700))
snow.y -= 60 * snow.r                                       # spread births upward
west_zone = land & (region == 1)
leaves = Emitter(110, 120, *sample(west_zone, 110))
flies = Emitter(90, 90, *sample(west_zone, 90))
east_zone = land & (region == 2)
motes = Emitter(150, 150, *sample(east_zone, 150))
south_zone = land & (region == 3) & ~island
dust = Emitter(140, 150, *sample(south_zone, 140))
sea_pts = sample((~land) & (dist_land > 3), 220)
sea_ph = rng.random(220); sea_k = rng.integers(1, 4, 220)
smoke = Emitter(16, 90, np.full(16, 166.0), np.full(16, 202.0))
embers = Emitter(28, 60, 320 + rng.uniform(-9, 9, 28), np.full(28, 124.0))
SNOW = [C('ffffff'), C('dce8f8'), C('b8cce4')]
LEAF = [C('d08a2a'), C('b85a1e'), C('8aa040'), C('e0b040')]
VIO = [C('e8b8ff'), C('ff9ce0'), C('b890ff')]

def frame(t):
    img = base.copy()
    ph = t / T
    # sea glints
    for i in range(220):
        b = max(0.0, math.sin(TAU * (ph * sea_k[i] + sea_ph[i]))) ** 10
        if b > 0.05: put(img, sea_pts[0][i], sea_pts[1][i], C('d8f4ff'), b * 0.9)
    # altar: breathing halo and embers
    pulse = 0.5 + 0.5 * math.sin(TAU * ph * 2)
    r = np.hypot((xx - 320) / 1.6, yy - 128)
    halo = np.clip(1 - r / 22, 0, 1) ** 2 * (0.10 + 0.10 * pulse)
    img = np.minimum(1, img + halo[:, :, None] * C('ffb050'))
    a, u = embers.ages(t)
    for i in range(embers.n):
        x = embers.x[i] + math.sin(u[i] * 7 + embers.r[i] * 6) * 2
        y = embers.y[i] - a[i] * 0.42
        col = C('ffe080') if u[i] < 0.4 else (C('ff8030') if u[i] < 0.75 else C('a02818'))
        put(img, x, y, col, (1 - u[i]) * 0.95, True)
    # route: crawling dashes and a pulse marching from the fort to the altar
    n = len(route); head = ph * (n + 40) - 20
    for i, (x, y) in enumerate(route):
        on = ((i + int(t * 0.2)) // 3) % 2 == 0
        near = max(0.0, 1 - abs(i - head) / 14)
        if on or near > 0.3:
            c = C('c8281c') * (1 - near) + C('ffd080') * near
            put(img, x, y, c); put(img, x, y + 1, C('6a1010') * (1 - near) + C('a05020') * near)
    # fort chimney smoke
    a, u = smoke.ages(t)
    for i in range(smoke.n):
        x = smoke.x[i] + a[i] * 0.07 + math.sin(u[i] * 5 + smoke.r[i] * 6) * 1.2
        y = smoke.y[i] - a[i] * 0.2
        s = 1 + int(u[i] * 2.5)
        for ox in range(s):
            for oy in range(s):
                put(img, x + ox, y + oy, C('b0a8a0'), 0.45 * (1 - u[i]))
    # south: drifting chaff and dust
    a, u = dust.ages(t)
    for i in range(dust.n):
        x = dust.x[i] + a[i] * 0.3; y = dust.y[i] - a[i] * 0.03 + math.sin(u[i] * 9 + dust.r[i] * 6)
        put(img, x, y, C('fff0b8'), 0.8 * fade(u[i]))
    # east: rising violet motes that twinkle
    a, u = motes.ages(t)
    for i in range(motes.n):
        x = motes.x[i] + math.sin(u[i] * 6 + motes.r[i] * 9) * 1.5; y = motes.y[i] - a[i] * 0.12
        tw = 0.6 + 0.4 * math.sin(TAU * (u[i] * 3 + motes.r[i]))
        glow(img, x, y, VIO[i % 3], 1.0 * tw * fade(u[i]))
    # west: tumbling leaves and blinking fireflies
    a, u = leaves.ages(t)
    for i in range(leaves.n):
        x = leaves.x[i] + a[i] * 0.22 + math.sin(u[i] * 8 + leaves.r[i] * 6) * 2
        y = leaves.y[i] + a[i] * 0.16
        c = LEAF[i % 4] * (1.0 if (int(a[i]) // 5) % 2 == 0 else 0.7)
        put(img, x, y, c, fade(u[i])); 
        if (int(a[i]) // 5) % 2 == 0: put(img, x + 1, y, c * 0.8, fade(u[i]))
    a, u = flies.ages(t)
    for i in range(flies.n):
        x = flies.x[i] + math.sin(u[i] * TAU + flies.r[i] * 6) * 3; y = flies.y[i] + math.cos(u[i] * TAU * 2 + flies.r[i]) * 2
        b = max(0.0, math.sin(TAU * u[i] * 2)) ** 3
        glow(img, x, y, C('e8ff80'), 0.9 * b)
    # north: snow, swaying, two sizes, only over the north realm and its sea
    a, u = snow.ages(t)
    for i in range(snow.n):
        x = snow.x[i] + a[i] * 0.18 + math.sin(u[i] * 10 + snow.r[i] * 6) * 2.5
        y = snow.y[i] + a[i] * 0.42
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < W and 0 <= yi < H and north_zone[yi, xi]:
            c = SNOW[i % 3]; al = fade(u[i], 0.08)
            put(img, x, y, c, al)
            if snow.r[i] > 0.6: put(img, x + 1, y, c, al); put(img, x, y + 1, c, al); put(img, x + 1, y + 1, c * 0.9, al)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))

exec(open('slide1.py').read().split('labels = [')[1].join(['labels = [', '']).split('\n')[0]) if False else None
LABELS = [(320, 18, '霜湾氏族', (210, 228, 255)), (70, 124, '荆冠诸部', (190, 240, 180)), (574, 124, '暮紫巫庭', (236, 206, 255)),
          (300, 248, '赤旌帝国', (255, 226, 170)), (250, 132, '内 海', (190, 220, 240)), (320, 144, '大祭场', (255, 236, 200)), (168, 228, '边境要塞', (255, 200, 170))]
SUB = '内海四周环伺着四股势力。每一方都相信神明在索要不同的东西——也都认为，别人献错了。'

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        for t in (0, 70):
            present_slide(frame(t), 0, 5, SUB, labels=LABELS).save(f'anim1_t{t}.png')
            frame(t).resize((1280, 544), Image.NEAREST).save(f'anim1_n{t}.png')
    else:
        out = sys.argv[2]
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '30', '-i', '-',
                              '-c:v', 'libx264', '-crf', '16', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-tune', 'animation', out + '.tmp.mp4'], stdin=subprocess.PIPE)
        for loop in range(int(sys.argv[3])):
            for t in range(T):
                p.stdin.write(present_slide(frame(t), 0, 5, SUB, labels=LABELS).tobytes())
        p.stdin.close(); assert p.wait() == 0
        import os; os.rename(out + '.tmp.mp4', out)
