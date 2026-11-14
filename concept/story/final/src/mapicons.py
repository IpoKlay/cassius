"""Hand-pixelled map icons (no 3D): ship, tower, temple, aqueduct, fort gate. Returns float RGBA arrays."""
import numpy as np
from PIL import Image, ImageDraw

def _hex(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
OUT = _hex('2a1a14')

def _finish(im):
    a = np.asarray(im).astype(float) / 255
    m = a[..., 3] > 0.5
    o = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        o |= np.roll(np.roll(m, dy, 0), dx, 1)
    o &= ~m
    a[o] = np.array(OUT) / 255
    return a

def ship():
    im = Image.new('RGBA', (34, 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(3, 16), (30, 16), (32, 12), (28, 19), (6, 19), (1, 12)], fill=_hex('7a4a2a'))
    d.line([(4, 17), (29, 17)], fill=_hex('a06a3a'))
    for x in range(6, 28, 4): d.ellipse((x, 15, x + 2, 17), fill=_hex('e8c060') if x % 8 else _hex('c03a2a'))
    d.line([(17, 15), (17, 3)], fill=_hex('4a2a1a'))
    for i, y in enumerate(range(4, 14, 2)): d.rectangle((11, y, 23, y + 1), fill=_hex('c02a20') if i % 2 else _hex('f0e8d8'))
    d.line([(32, 12), (33, 9)], fill=_hex('7a4a2a')); d.point((33, 8), fill=_hex('e8c060'))
    return _finish(im)

def tower():
    im = Image.new('RGBA', (12, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((2, 10, 9, 29), fill=_hex('5a3a7a')); d.rectangle((2, 10, 4, 29), fill=_hex('8a60a8')); d.rectangle((8, 10, 9, 29), fill=_hex('3a2250'))
    d.polygon([(1, 10), (10, 10), (5, 1)], fill=_hex('a050c0')); d.line([(5, 1), (2, 9)], fill=_hex('d090e8'))
    d.rectangle((5, 14, 6, 16), fill=_hex('ffc060')); d.rectangle((5, 21, 6, 23), fill=_hex('ffc060'))
    for y in range(12, 29, 3): d.line([(3, y), (8, y)], fill=_hex('4a2e66'))
    return _finish(im)

def temple():
    im = Image.new('RGBA', (32, 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(2, 7), (29, 7), (16, 1)], fill=_hex('e8dcc0')); d.line([(16, 1), (29, 7)], fill=_hex('a89878'))
    d.rectangle((2, 7, 29, 8), fill=_hex('c8b898'))
    for x in range(4, 29, 5): d.rectangle((x, 9, x + 2, 16), fill=_hex('f0e8d0')); d.line([(x + 2, 9), (x + 2, 16)], fill=_hex('a89878'))
    d.rectangle((1, 17, 30, 18), fill=_hex('d8ccb0')); d.rectangle((0, 19, 31, 19), fill=_hex('b0a080'))
    d.rectangle((7, 10, 24, 16), fill=None)
    return _finish(im)

def aqueduct():
    im = Image.new('RGBA', (52, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 1, 51, 4), fill=_hex('d8c8a0')); d.line([(0, 4), (51, 4)], fill=_hex('a89870'))
    for x in range(0, 52, 9):
        d.rectangle((x, 4, x + 2, 15), fill=_hex('c8b890')); d.line([(x + 2, 4), (x + 2, 15)], fill=_hex('988860'))
        d.arc((x + 2, 4, x + 9, 11), 180, 360, fill=_hex('a89870'))
    return _finish(im)

def gate():
    im = Image.new('RGBA', (26, 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in range(0, 26, 3): d.polygon([(x, 19), (x + 2, 19), (x + 2, 9), (x + 1, 7), (x, 9)], fill=_hex('8a6a4a'))
    for tx in (3, 19):
        d.rectangle((tx, 4, tx + 4, 19), fill=_hex('7a5a3a')); d.polygon([(tx - 1, 4), (tx + 5, 4), (tx + 2, 0)], fill=_hex('a03a2a'))
    d.rectangle((10, 11, 15, 19), fill=_hex('ffc070')); d.line([(10, 10), (15, 10)], fill=_hex('5a3a2a'))
    d.line([(12, 9), (12, 2)], fill=_hex('4a2a1a')); d.rectangle((13, 2, 16, 5), fill=_hex('c02a20'))
    return _finish(im)
