import numpy as np
from PIL import Image, ImageDraw, ImageFont
from kit import W, H

FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 8)
COIN = Image.open('/home/claude/cassius/assets/ui/coin.png').convert('RGBA')
ITEMS = Image.open('/home/claude/cassius/assets/ui/items.png').convert('RGBA')


def hud(im, top, bottom, right='', bars=20):
    im = im.copy()
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.rectangle([0, 0, W, bars - 1], fill=(0, 0, 0))
    d.rectangle([0, H - bars, W, H], fill=(0, 0, 0))
    x = 8
    for kind, text, col in top:
        if kind == 'coin':
            im.paste(COIN, (x, 2), COIN); x += 18
        elif kind == 'grain':
            g = ITEMS.crop((5 * 16, 0, 6 * 16, 16)); im.paste(g, (x, 2), g); x += 18
        d.text((x, 5), text, font=FONT, fill=col)
        x += int(d.textlength(text, font=FONT)) + 12
    if right:
        d.text((W - 8 - d.textlength(right, font=FONT), 5), right, font=FONT, fill=(150, 140, 128))
    d.text((8, H - bars + 6), bottom, font=FONT, fill=(150, 140, 128))
    return im


def text(im, xy, s, col=(250, 236, 200), shadow=True, center=False, scale=1):
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    if scale != 1:
        tmp = Image.new('RGBA', (int(d.textlength(s, font=FONT)) + 4, 12), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp); td.fontmode = '1'
        td.text((1, 1), s, font=FONT, fill=(0, 0, 0, 220)); td.text((0, 0), s, font=FONT, fill=col + (255,))
        tmp = tmp.resize((tmp.width * scale, tmp.height * scale), Image.NEAREST)
        x = xy[0] - tmp.width // 2 if center else xy[0]
        im.paste(tmp, (x, xy[1]), tmp)
        return
    x = xy[0] - int(d.textlength(s, font=FONT)) // 2 if center else xy[0]
    if shadow:
        d.text((x + 1, xy[1] + 1), s, font=FONT, fill=(0, 0, 0))
    d.text((x, xy[1]), s, font=FONT, fill=col)
