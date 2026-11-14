"""Shared helpers for the story slides: bake 3D models on demand, present with cinematic bars + subtitles."""
import os, sys, hashlib, pickle
os.environ['WIDE'] = '1'
sys.path.insert(0, '/home/claude/renders/hand')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sdf import render, pixelise

CACHE = '/home/claude/renders/bakecache'
os.makedirs(CACHE, exist_ok=True)
SP = '/home/claude/renders/sprites3d'


def bake(key, model_fn, size, scale, yaw, pitch=16, origin=(0, -1.0), ss=4, outline=True, flip=False):
    path = f'{CACHE}/{key}.png'
    if not os.path.exists(path):
        mi, ti, dims = render(model_fn(), size, scale=scale, ss=ss, yaw=yaw, pitch=pitch, origin=origin)
        px = pixelise(mi, ti, dims, outline=outline)
        ys, xs = np.nonzero(px[:, :, 3] > 0)
        px = px[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        Image.fromarray((np.clip(px, 0, 1) * 255).astype(np.uint8), 'RGBA').save(path)
    a = np.asarray(Image.open(path).convert('RGBA'), dtype=float) / 255.0
    return a[:, ::-1].copy() if flip else a


def sprite(name, flip=False):
    a = np.asarray(Image.open(f'{SP}/{name}.png').convert('RGBA'), dtype=float) / 255.0
    return a[:, ::-1].copy() if flip else a


SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Medium.ttc'
SERIF_L = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Light.ttc'


def wrap(d, text, font, width):
    lines, cur = [], ''
    no_start = '，。、：；！？）」』——…'
    for ch in text:
        if d.textlength(cur + ch, font=font) > width and ch not in no_start:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def present_slide(pic, index, total, subtitle, labels=(), sw=1920, sh=1080):
    pw, ph = pic.size
    k = sw // pw
    big = pic.resize((pw * k, ph * k), Image.NEAREST)
    canvas = Image.new('RGB', (sw, sh), (0, 0, 0))
    y0 = (sh - big.height) // 2
    canvas.paste(big, ((sw - big.width) // 2, y0))
    d = ImageDraw.Draw(canvas)
    s = sh / 1080.0
    # labels inside the picture
    fl = ImageFont.truetype(SERIF, int(26 * s))
    for (px, py, text, col) in labels:
        X, Y = (sw - big.width) // 2 + px * k, y0 + py * k
        tw = d.textlength(text, font=fl)
        for ox, oy in ((2, 2), (-1, 1), (1, -1)):
            d.text((X - tw / 2 + ox, Y + oy), text, font=fl, fill=(0, 0, 0))
        d.text((X - tw / 2, Y), text, font=fl, fill=col)
    # progress marks in the top bar
    for i in range(total):
        cx = sw / 2 + (i - (total - 1) / 2) * 34 * s
        r = 5 * s if i == index else 3 * s
        col = (226, 196, 140) if i == index else (90, 80, 70)
        d.ellipse((cx - r, y0 / 2 - r, cx + r, y0 / 2 + r), fill=col)
    # subtitle in the bottom bar, centred, serif
    fs = ImageFont.truetype(SERIF_L, int(30 * s))
    lines = wrap(d, subtitle, fs, sw * 0.72)
    lh = 44 * s
    y1 = y0 + big.height
    ty = y1 + ((sh - y1) - lh * len(lines)) / 2
    for i, line in enumerate(lines):
        tw = d.textlength(line, font=fs)
        d.text(((sw - tw) / 2, ty + i * lh), line, font=fs, fill=(232, 220, 196))
    hint = ImageFont.truetype(SERIF_L, int(18 * s))
    t = '任意键继续    Esc 跳过'
    d.text((sw - d.textlength(t, font=hint) - 40 * s, sh - 34 * s), t, font=hint, fill=(110, 100, 90))
    return canvas
