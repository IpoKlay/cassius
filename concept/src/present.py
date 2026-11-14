"""Puts a 640x272 picture on a real screen: integer scale, cinematic bars, hi-res UI in the bars."""
from PIL import Image, ImageDraw, ImageFont

SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Medium.ttc'
SANS = '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc'
COIN = Image.open('/home/claude/cassius/assets/ui/coin_big.png').convert('RGBA')
ITEMS = Image.open('/home/claude/cassius/assets/ui/items.png').convert('RGBA')


def present(pic, sw, sh, top_items, right, chapter, hints, prompt=None, notch=False):
    pw, ph = pic.size
    k = sw // pw
    cols = sw // k                                  # flexible width: extra columns fill the screen
    if cols > pw:                                   # (concept: pad by stretching the edge columns' content)
        wide = Image.new('RGB', (cols, ph))
        wide.paste(pic, ((cols - pw) // 2, 0))
        pic = wide
    big = pic.resize((pic.width * k, ph * k), Image.NEAREST)
    canvas = Image.new('RGB', (sw, sh), (0, 0, 0))
    y0 = (sh - big.height) // 2
    canvas.paste(big, ((sw - big.width) // 2, y0))
    d = ImageDraw.Draw(canvas)
    s = sh / 1080.0                                # UI scales with the screen, text stays crisp
    fs = ImageFont.truetype(SANS, int(25 * s))
    ft = ImageFont.truetype(SERIF, int(40 * s))
    fsmall = ImageFont.truetype(SANS, int(21 * s))
    bar_mid = y0 // 2
    # chapter title, centred in the top bar, letter-spaced
    title = '  '.join(chapter)
    tw = d.textlength(title, font=ft)
    d.text(((sw - tw) / 2, bar_mid - 30 * s), title, font=ft, fill=(236, 214, 170))
    # resources along the bottom edge of the top bar
    x = int(60 * s)
    yi = y0 - int(54 * s)
    for kind, text, col in top_items:
        if kind == 'coin':
            ic = COIN.resize((int(34 * s), int(34 * s)), Image.NEAREST)
            canvas.paste(ic, (x, yi - int(3 * s)), ic); x += int(44 * s)
        elif kind == 'grain':
            g = ITEMS.crop((80, 0, 96, 16)).resize((int(32 * s), int(32 * s)), Image.NEAREST)
            canvas.paste(g, (x, yi - int(2 * s)), g); x += int(40 * s)
        d.text((x, yi), text, font=fs, fill=col)
        x += int(d.textlength(text, font=fs)) + int(46 * s)
    rw = d.textlength(right, font=fs)
    d.text((sw - rw - 60 * s, yi), right, font=fs, fill=(150, 138, 124))
    # key hints centred in the bottom bar
    y1 = y0 + big.height
    hw = d.textlength(hints, font=fsmall)
    d.text(((sw - hw) / 2, y1 + (sh - y1) / 2 - 14 * s), hints, font=fsmall, fill=(120, 110, 100))
    if prompt:
        (px, py), text = prompt
        X = (sw - big.width) // 2 + px * k
        Y = y0 + py * k
        tw = d.textlength(text, font=fs)
        d.text((X - tw / 2 + 2, Y + 2), text, font=fs, fill=(0, 0, 0))
        d.text((X - tw / 2, Y), text, font=fs, fill=(255, 244, 214))
    if notch:                                       # MacBook camera housing, for reference
        nw, nh = int(sw * 0.075), int(sh * 0.02)
        d.rounded_rectangle(((sw - nw) // 2, -10, (sw + nw) // 2, nh), radius=nh // 2, fill=(20, 20, 22))
    return canvas, k
