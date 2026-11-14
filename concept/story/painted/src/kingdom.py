"""Kingdom-style side-view scene toolkit: layered haze forests, lush lit trees, a thin grass strip,
and the river reflection along the bottom of the frame."""
from illus import *
import sys
sys.path.insert(0, '/home/claude/renders/hand')


def mix(a, b, t):
    return np.asarray(a) * (1 - t) + np.asarray(b) * t


def sky(cv, stops, top=0, bottom=None, sun=None, sun_col=None, sun_r=14, glow=1.0):
    bottom = bottom or H
    t = np.clip((YY - top) / max(1, bottom - top), 0, 1)
    if sun is not None:
        t = np.clip(t + np.clip(1 - np.hypot((XX - sun[0]) / 2.0, YY - sun[1]) / 220, 0, 1) * 0.25 * glow, 0, 1)
    cv.grad(YY < bottom, t, ramp(*stops), amt=0.9)
    if sun is not None:
        cv.glow(sun[0], sun[1], 110, sun_col * 0.9, 0.5 * glow, sx=1.7)
        cv.glow(sun[0], sun[1], 40, sun_col, 0.6 * glow)
        cv.fill(ellipse(sun[0], sun[1], sun_r, sun_r), mix(sun_col, C('ffffff'), 0.6))


def sun(cv, x, y, col, r=12, k=1.0):
    cv.glow(x, y, 120, col * 0.9, 0.45 * k, sx=1.8)
    cv.glow(x, y, 42, col, 0.6 * k)
    cv.fill(ellipse(x, y, r, r), mix(col, C('ffffff'), 0.6))


def cloudbanks(cv, seed, rows, cols, lit, lit_dir=-1):
    """Kingdom-like soft horizontal cloud banks: thin stretched noise, two shades and a lit edge"""
    n = fbm(W, H * 4, seed, cells=(160, 70, 24, 8))[::4]
    for i, (cy_, th) in enumerate(rows):
        dens = np.clip(1 - np.abs(YY - cy_ - (n - 0.5) * th * 1.5) / th, 0, 1) ** 0.7 * (n * 2.6 - 1.15)
        m1 = dens > 0.05; m2 = dens > 0.3
        cv.fill(m1 & ((BAY > 0.5) | (dens > 0.12)), cols[0])
        cv.fill(m2, cols[1])
        cv.fill(m1 & ~np.roll(m1, lit_dir, 0), lit)


def clouds(cv, seed, rows, col, lit, lit_dir=1, alpha=1.0):
    n = fbm(W, H, seed, cells=(110, 50, 18, 6))
    for (cy_, th, sc) in rows:
        m = (np.abs(YY - cy_ - (n - 0.5) * 18) < th * (n * 2.2 - 0.75)) & (n > 0.42)
        cv.fill(m, col, alpha)
        edge = m & ~np.roll(m, lit_dir, 0)
        cv.fill(edge, lit, alpha)


def treeline(cv, base, height, seed, col, top_col=None, density=1.0, bumps=7):
    """a far forest band: rounded crowns along the top"""
    rng = np.random.default_rng(seed)
    m = YY >= base
    x = -10
    while x < W + 10:
        r = rng.uniform(bumps * 0.6, bumps * 1.3)
        h = height * rng.uniform(0.55, 1.0)
        m |= ellipse(x, base - h + r, r, r * 1.1) | ((np.abs(XX - x) < r) & (YY > base - h + r))
        x += r * rng.uniform(1.0, 1.6) / density
    cv.fill(m & (YY < 999), col)
    if top_col is not None:
        cv.fill(m & ~np.roll(m, 1, 0), top_col)
    return m


def hills(cv, y0, amp, seed, col, edge=None):
    m, top = ridge(y0, amp, seed, (120, 50, 16))
    cv.fill(m, col)
    if edge is not None:
        cv.fill(m & ~np.roll(m, 1, 0), edge)
    return m


def foliage_tree(cv, x, gy, h, pal, trunk_pal, seed, light=(-1, -1), spread=1.0, kind='oak'):
    """a lush Kingdom-like tree: bark-shaded trunk, a crown of clumps lit from one side, leaf speckle"""
    rng = np.random.default_rng(seed)
    tw = max(2, h * 0.06)
    trunk = poly([(x - tw, gy), (x + tw, gy), (x + tw * 0.6, gy - h * 0.62), (x - tw * 0.6, gy - h * 0.62)])
    for k in range(3):                                          # branches
        a = rng.uniform(-1, 1)
        trunk |= capsule((x, gy - h * (0.45 + k * 0.1)), (x + a * h * 0.22, gy - h * (0.62 + k * 0.08)), max(1, tw * 0.45))
    tt = np.clip((XX - x + tw) / (2 * tw), 0, 1)
    cv.grad(trunk, tt if light[0] < 0 else 1 - tt, trunk_pal)
    cv.fill(trunk & ((YY * 3 + XX * 7) % 11 == 0), trunk_pal[-1])
    if kind == 'pine':
        crown = np.zeros((H, W), bool)
        for k in range(7):
            yk = gy - h * (0.25 + k * 0.11); w = h * 0.32 * (1 - k / 8)
            crown |= poly([(x - w, yk), (x + w, yk), (x, yk - h * 0.22)])
        cx_, cy_, R = x, gy - h * 0.6, h * 0.4
    else:
        cx_, cy_, R = x, gy - h * 0.72, h * 0.32 * spread
        n = fbm(W, H, seed + 3, cells=(10, 5, 3, 2))
        clumps = []
        for k in range(16):
            a = rng.uniform(0, 2 * math.pi); d = rng.uniform(0, 1) ** 0.6 * R * 0.8
            r = R * rng.uniform(0.32, 0.5)
            clumps.append((cx_ + math.cos(a) * d * 1.3, cy_ + math.sin(a) * d * 0.75, r))
        lx, ly = light
        clumps.sort(key=lambda c: (c[0] - cx_) * lx + (c[1] - cy_) * ly)      # lit clumps drawn last
        crown = np.zeros((H, W), bool)
        for (px, py, r) in clumps:
            m = ellipse(px, py, r * 1.15, r * 0.85)
            m &= ~((n < 0.36) & ~ellipse(px, py, r * 0.8, r * 0.6))
            t = ((XX - px) * -lx + (YY - py) * -ly) / (r * 2.0) + 0.5
            gl = ((XX - cx_) * -lx + (YY - cy_) * -ly) / (R * 3.0)          # whole-crown light falloff
            cv.grad(m, np.clip(t * 0.6 + gl + 0.2 + (n - 0.5) * 0.4, 0, 1), pal)
            cv.fill(m & ~np.roll(np.roll(m, -ly, 0), -lx, 1) & (t < 0.5), pal[0])
            crown |= m
        spk = crown & (BAY > 0.9) & (n > 0.55)
        cv.fill(spk, pal[1])
        return crown | trunk
    n = fbm(W, H, seed + 3, cells=(14, 7, 3, 2))
    lx, ly = light
    t = ((XX - cx_) * -lx + (YY - cy_) * -ly) / (R * 1.6) * 0.5 + 0.5 + (n - 0.5) * 0.5
    cv.grad(crown, np.clip(t, 0, 1), pal)
    cv.fill(crown & ~np.roll(np.roll(crown, -ly, 0), -lx, 1), pal[0])
    return crown | trunk


def grass_strip(cv, gy, top_col, mid_col, soil_col, seed, h=6, flowers=None):
    rng = np.random.default_rng(seed)
    m = (YY >= gy) & (YY < gy + h)
    cv.fill(m, mid_col)
    cv.fill((YY >= gy + h - 2) & (YY < gy + h), soil_col)
    for x in range(W):
        if rng.random() < 0.6:
            L = rng.integers(1, 4)
            for k in range(L):
                y = gy - k
                if 0 <= y < H:
                    cv.img[y, x] = top_col if k == L - 1 else mid_col
    if flowers is not None:
        for i in range(W // 9):
            x = rng.integers(0, W); cv.img[gy - rng.integers(1, 3), x] = flowers[rng.integers(0, len(flowers))]


def reflect(cv, gy, tint, dark=0.55, seed=0, phase=0.0, streak=None):
    """mirror the scene above gy into the water below it, with Kingdom's horizontal ripple break-up"""
    src = cv.img.copy()
    for y in range(gy, H):
        d = y - gy
        sy = gy - 1 - d
        if sy < 0:
            sy = 0
        amp = 0.6 + d * 0.06
        off = int(round(math.sin(d * 0.9 + phase * 2 * math.pi) * amp + math.sin(d * 0.37 + 1.3) * amp * 0.6))
        row = np.roll(src[sy], off, 0)
        k = dark - min(d / (H - gy), 1) * 0.12
        cv.img[y] = row * k + tint * (1 - k)
    rng = np.random.default_rng(seed)
    for i in range(int((H - gy) * 4.5)):                       # ripple highlight dashes
        y = rng.integers(gy + 1, H); x = rng.integers(0, W); L = rng.integers(2, 9)
        cv.img[y, x:x + L] = cv.img[y, x:x + L] * 0.6 + 0.4 * np.clip(src[max(0, 2 * gy - y - 1), x:x + L] * 1.3, 0, 1)
    if streak is not None:                                    # light path on the water (sun or fires)
        sx, w, col = streak
        for y in range(gy + 1, H):
            for k in range(3):
                x = int(sx + rng.normal(0, w * (0.4 + (y - gy) / (H - gy))))
                L = rng.integers(2, 6)
                if 0 <= x < W - L and rng.random() < 0.8:
                    cv.img[y, x:x + L] = cv.img[y, x:x + L] * 0.3 + col * 0.7
    cv.fill((YY == gy), cv.img[gy - 1].mean(axis=0) * 0.6)


def put(cv, a, x, base_y, tint=None, rim_col=None, rim_dir=1, shade=1.0, alpha_cut=0.5):
    """composite an RGBA sprite with its feet at (x, base_y); optional ambient tint and rim light"""
    h, w = a.shape[:2]
    x0, y0 = int(round(x - w / 2)), int(round(base_y - h))
    for j in range(h):
        yy = y0 + j
        if not (0 <= yy < H): continue
        for i in range(w):
            xx = x0 + i
            if not (0 <= xx < W) or a[j, i, 3] < alpha_cut: continue
            c = a[j, i, :3] * shade
            if tint is not None:
                c = c * tint
            if rim_col is not None:
                ni = i + rim_dir
                if not (0 <= ni < w) or a[j, ni, 3] < alpha_cut:
                    c = c * 0.4 + rim_col * 0.6
            cv.img[yy, xx] = np.clip(c, 0, 1)


def pointlight(cv, x, y, r, col, k=1.0):
    """warm pool of light: banded, lights the scene multiplicatively and additively"""
    d = np.hypot(XX - x, (YY - y) * 1.15) / r
    f = np.clip(1 - d, 0, 1) ** 1.6
    f = np.floor(f * 5 + BAY * 0.95) / 5 * k
    cv.img = np.clip(cv.img * (1 + f[:, :, None] * 1.4 * col[None, None, :]) + f[:, :, None] * 0.18 * col[None, None, :], 0, 1)


def ambient(cv, mul, mask=None):
    if mask is None:
        cv.img = cv.img * np.asarray(mul)[None, None, :]
    else:
        cv.img[mask] = cv.img[mask] * np.asarray(mul)


def flame(cv, x, y, s=1.0, seed=0):
    rng = np.random.default_rng(seed)
    f = poly([(x - 3 * s, y), (x - 2 * s, y - 5 * s), (x - 0.5 * s, y - 3 * s), (x, y - 9 * s), (x + 1.5 * s, y - 4 * s), (x + 3 * s, y - 6 * s), (x + 3 * s, y)])
    cv.fill(f, C('ff8a2a')); cv.fill(f & (YY > y - 4 * s) & (np.abs(XX - x) < 2 * s), C('ffe6a0'))
