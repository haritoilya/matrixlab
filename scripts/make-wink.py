#!/usr/bin/env python3
"""Draws the frames of a wink (upper, left-hand eye) on the home page hero photo.

Usage: python scripts/make-wink.py
Writes assets/img/hero-wink-1.png ... hero-wink-4.png: transparent overlays,
same size as the hero photo, with the eyelid lowered 25/50/75/100 %.
Needs Python 3 with Pillow and NumPy.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets/img/f9b6ef7d-643f-4798-8b78-bb513b794962-3650554.png')
OUT = os.path.join(ROOT, 'assets/img/hero-wink-%d.png')
STEPS = (0.25, 0.5, 0.75, 1.0)

# Eye outline in photo pixels (the upper eye, nearer the centre of the photo).
T = [(1036, 110), (1050, 98), (1080, 89), (1110, 85), (1140, 86), (1160, 94), (1176, 110), (1190, 146)]  # lid crease / above lash tips
U = [(1036, 110), (1050, 104), (1070, 103), (1090, 106), (1120, 108), (1150, 116), (1170, 130), (1190, 148)]  # upper lash line
B = [(1036, 110), (1050, 126), (1080, 138), (1110, 144), (1140, 146), (1170, 148), (1190, 150)]  # lower lid edge
SKIN_DY = 92        # skin texture is borrowed from the cheek this many px below
LASH = (45, 25, 35)
SS = 4              # supersampling for lashes


def smooth(v, k):
    p = np.pad(v, ((k, k), (0, 0)), mode='edge')
    c = np.vstack([np.zeros((1, v.shape[1])), np.cumsum(p, 0)])
    return (c[2 * k + 1:] - c[:-2 * k - 1]) / (2 * k + 1)


def main():
    im = Image.open(SRC).convert('RGB')
    A = np.asarray(im).astype(float)
    H, W, _ = A.shape
    blur = np.asarray(im.filter(ImageFilter.GaussianBlur(2.5))).astype(float)
    blur8 = np.asarray(im.filter(ImageFilter.GaussianBlur(8))).astype(float)
    # skin texture of the photo: fine pores plus soft mottling, clipped so stray dark details do not show
    detail = 1.6 * np.clip(A - blur, -16, 16) + 0.9 * np.clip(blur - blur8, -8, 8)

    xs = np.arange(T[0][0], T[-1][0] + 1)
    t = np.interp(xs, *zip(*T))
    u = np.interp(xs, *zip(*U))
    b = np.interp(xs, *zip(*B))
    c = b - 2                                           # where the closed lid meets the lower lid
    top = np.array([np.median(A[int(ty) - 7:int(ty) - 2, x - 2:x + 3].reshape(-1, 3), 0) for x, ty in zip(xs, t)])
    top = smooth(top, 18) * 0.85 + np.median(top, 0) * 0.15
    rng = np.random.default_rng(7)
    # procedural skin grain (fine pores + soft mottling), luminance only
    def noise(sigma, amp):
        n = Image.fromarray(np.clip(rng.normal(128, 40, (H, W)), 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sigma))
        n = np.asarray(n).astype(float) - 128
        return n / (n.std() + 1e-6) * amp
    grain = noise(0.6, 4.5) + noise(2.5, 3.0)
    lash_seed = [(rng.uniform(-1, 1), rng.uniform(-6, 6), rng.random()) for _ in xs]

    for n, k in enumerate(STEPS, 1):
        out = A.copy()
        mask = np.zeros((H, W))
        edge = u + k * (c - u)                          # current lid edge
        for i, x in enumerate(xs):
            span = max(edge[i] - t[i], 1)
            for y in range(int(np.floor(t[i])) - 2, int(np.ceil(edge[i])) + 1):
                f = np.clip((y - t[i]) / span, 0, 1)
                col = top[i] * (1 - 0.22 * f ** 2.2) * (1.05 + 0.04 * np.sin(np.pi * f))
                col = col * (1 - 0.18 * np.clip(1 - (edge[i] - y) / 5, 0, 1))      # shadow at the lid edge
                crease = np.exp(-((y - (t[i] + 3.5)) / 1.8) ** 2) * 0.05 * k      # soft fold at the crease
                gx = (x - xs[0]) / (xs[-1] - xs[0])
                sheen = 0.07 * np.exp(-((f - 0.35) / 0.25) ** 2) * np.exp(-((gx - 0.5) / 0.3) ** 2)  # light on the convex lid
                col = col * (1 - crease + sheen) + detail[min(y + SKIN_DY, H - 1), x] + grain[y, x]
                out[y, x] = np.clip(col, 0, 255)
                mask[y, x] = 1
        m = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.8))).astype(float)[..., None] / 255
        frame = Image.fromarray((A * (1 - m) + out * m).astype(np.uint8)).convert('RGBA')

        # lash line and lashes: they point up while the lid is high and down when it is closed
        ov = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        pts = list(zip(xs, edge))
        N = len(pts)
        for j in range(N - 1):
            pos = j / (N - 1)
            w = 0.6 + 1.3 * np.sin(np.pi * pos) ** 0.6
            d.line([(pts[j][0] * SS, pts[j][1] * SS), (pts[j + 1][0] * SS, pts[j + 1][1] * SS)],
                   fill=LASH + (int(150 + 80 * np.sin(np.pi * pos)),), width=max(1, int(w * SS)))
        for j in range(3, N - 3, 2):
            x, y = pts[j]
            pos = 1 - j / N                                  # 0 at the inner corner, 1 at the outer (left) corner
            jl, ja, jo = lash_seed[j]
            L = 3 + 8 * np.sin(np.pi * min(pos * 1.1, 1)) ** 0.7 + jl
            down = np.deg2rad(70 - 35 * pos + ja)            # angle below horizontal when closed
            ang = -down + k * 2 * down if k < 1 else down    # lashes swing from up to down as the lid closes
            dx, dy = -np.cos(ang) * L, np.sin(ang) * L
            d.line([(x * SS, y * SS), ((x + dx * 0.5 - 0.8) * SS, (y + dy * 0.45) * SS), ((x + dx) * SS, (y + dy) * SS)],
                   fill=LASH + (int(170 - 60 * jo),), width=int(1.1 * SS))
        frame.alpha_composite(ov.resize((W, H), Image.LANCZOS))

        # keep only the changed area, transparent elsewhere
        diff = np.abs(np.asarray(frame.convert('RGB')).astype(int) - A.astype(int)).sum(2) > 0
        alpha = Image.fromarray((diff * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(2))
        frame.putalpha(alpha)
        a = np.asarray(frame).copy()
        a[a[..., 3] == 0] = 0
        Image.fromarray(a).save(OUT % n, optimize=True)
        print('wrote', OUT % n)


if __name__ == '__main__':
    main()
