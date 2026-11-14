"""Bake every sprite for the scene into sprites3d/*.png (pixel art, outlined)."""
import os, sys
import numpy as np
from sdf import render, pixelise, save
import props3d as PR
import legionary3d as LG
import cassius3d as CS

OUT = '/home/claude/renders/sprites3d'
os.makedirs(OUT, exist_ok=True)


def bake(name, model, size, scale, yaw, pitch=16, origin=(0, 0), ss=5, outline=True):
    mi, ti, dims = render(model, size, scale=scale, ss=ss, yaw=yaw, pitch=pitch, origin=origin)
    px = pixelise(mi, ti, dims, outline=outline)
    ys, xs = np.nonzero(px[:, :, 3] > 0)
    px = px[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    save(px, f'{OUT}/{name}.png')
    print(name, px.shape[1], 'x', px.shape[0])


if __name__ == '__main__':
    which = sys.argv[1:] or ['all']
    def want(n):
        return 'all' in which or n in which
    if want('legionary'):
        for i, st in enumerate((-1.3, 0.0, 1.3, 0.6)):
            bake(f'legionary{i}', LG.legionary_model(st), (40, 60), 1.25, 32, origin=(0.5, -1.0))
    if want('cassius'):
        bake('cassius', CS.horse_rider(), (64, 86), 1.62, -50, pitch=14, origin=(1.0, -1.5))
    if want('ox'):
        bake('ox', PR.ox_model(0.8), (70, 46), 1.85, -40, origin=(1.5, -1.0))
    if want('cart'):
        bake('cart', PR.cart_model(0.3), (80, 54), 1.9, -40, origin=(3.0, -1.0))
    if want('tent'):
        bake('tent_big', PR.tent_model(10.0, 11.0, 9.0), (110, 74), 3.3, 28, pitch=22, origin=(0, -1.0), ss=4)
        bake('tent_small', PR.tent_model(8.0, 9.0, 7.0), (88, 62), 3.3, 18, pitch=22, origin=(0, -1.0), ss=4)
    if want('vexillum'):
        bake('vexillum', PR.vexillum_model(0.4), (24, 70), 1.45, 12, origin=(0, -1.0))
    if want('column'):
        bake('column', PR.column_model(20.0, True), (20, 40), 2.2, 10, origin=(0, -1.0))
    if want('rock'):
        for i, s in enumerate((4.0, 3.0, 5.0)):
            bake(f'rock{i}', PR.rock_model(i + 3, s), (30, 22), 2.2, 20 * i, pitch=30, origin=(0, -1.0))
    if want('crate'):
        bake('crate', PR.crate_model(3.0), (20, 20), 2.2, 30, pitch=24, origin=(0, -1.0))
    if want('amphora'):
        bake('amphora', PR.amphora_model(), (12, 24), 2.0, 0, origin=(0, -1.0))
    if want('aqueduct'):
        bake('aqueduct', PR.aqueduct_model(), (300, 90), 2.6, 12, pitch=10, origin=(49.0, -1.0), ss=3, outline=False)
    if want('fire'):
        bake('campfire', PR.campfire_model(), (40, 20), 2.4, 0, pitch=34, origin=(0, -2.0))
