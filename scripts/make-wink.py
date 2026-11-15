# Draws a closed right-hand eye on the hero photo (used for assets/img/hero-wink.png).
# Usage: python scripts/make-wink.py <hero.png> <out.png>; the page uses only the eye area with transparency.
import sys, numpy as np, random
from PIL import Image, ImageDraw, ImageFilter
SRC, OUT = sys.argv[1], sys.argv[2]
im = Image.open(SRC).convert('RGB'); A = np.asarray(im).astype(float); H, W, _ = A.shape
EYES = [
  # (T points above lash tips / crease), (B points: lower lid edge), outer side ('left' or 'right')
  dict(T=[(1036,110),(1050,98),(1080,89),(1110,85),(1140,86),(1160,94),(1176,110),(1190,146)],
       B=[(1036,110),(1050,126),(1080,138),(1110,144),(1140,146),(1170,148),(1190,150)], outer='left'),
  dict(T=[(1320,186),(1330,172),(1350,160),(1380,152),(1410,152),(1440,160),(1460,174),(1472,196),(1476,210)],
       B=[(1320,190),(1340,196),(1360,202),(1390,209),(1420,211),(1440,210),(1460,210),(1476,210)], outer='right'),
]
def smooth(v, k=7):
    p = np.pad(v, ((k, k), (0, 0)), mode='edge'); c = np.cumsum(p, 0); c = np.vstack([np.zeros((1, 3)), c])
    return (c[2*k+1:] - c[:-2*k-1]) / (2*k+1)
out = A.copy(); mask = np.zeros((H, W)); lid_lines = []
rng = np.random.default_rng(1)
for e in EYES[1:]:  # wink: only the lower (right-hand) eye
    T = np.array(e['T'], float); B = np.array(e['B'], float)
    x0, x1 = int(T[0,0]), int(T[-1,0]); xs = np.arange(x0, x1+1)
    t = np.interp(xs, T[:,0], T[:,1]); b = np.interp(xs, B[:,0], B[:,1])
    top = np.array([np.median(A[int(ty)-7:int(ty)-2, x-2:x+3].reshape(-1,3), 0) for x, ty in zip(xs, t)])
    bot = np.array([np.median(A[int(by)+2:int(by)+5, x], 0) for x, by in zip(xs, b)])
    top, bot = smooth(top, 18), smooth(bot, 12)
    top = top*0.85 + np.median(top,0)*0.15
    c = b - 2  # closure line
    pts = []
    for i, x in enumerate(xs):
        y0, y1 = int(np.floor(t[i])) - 2, int(np.ceil(b[i])) + 1
        for y in range(y0, y1+1):
            f = np.clip((y - t[i]) / max(c[i] - t[i], 1), 0, 1)
            g = f**2.2
            col = (top[i] * (1 - 0.25*g)) if y <= c[i] else bot[i]
            # convex lid: slight highlight in the middle, shadow at the closure
            col = col * (1.05 + 0.04*np.sin(np.pi*f))
            shade = 1 - 0.18 * np.clip(1 - (c[i] - y) / 5, 0, 1)
            out[y, x] = np.clip(col * shade + rng.normal(0, 4.5, 1), 0, 255)
            mask[y, x] = 1
        pts.append((x, c[i]))
    lid_lines.append((pts, e['outer']))
# feather the mask
m = Image.fromarray((mask*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2))
m = np.asarray(m).astype(float)[..., None] / 255
res = Image.fromarray((A * (1 - m) + out * m).astype(np.uint8))
# lashes and lash line, supersampled
SS = 4; ov = Image.new('RGBA', (W*SS, H*SS), (0,0,0,0)); d = ImageDraw.Draw(ov)
lash = (45, 25, 35)
for pts, outer in lid_lines:
    n = len(pts)
    for j in range(n-1):
        pos = j/(n-1); w = 0.6 + 1.3*np.sin(np.pi*pos)**0.6
        d.line([(pts[j][0]*SS, pts[j][1]*SS), (pts[j+1][0]*SS, pts[j+1][1]*SS)], fill=lash+(int(150+80*np.sin(np.pi*pos)),), width=max(1,int(w*SS)))
    n = len(pts); sgn = -1 if outer == 'left' else 1
    for j in range(3, n-3, 2):
        x, y = pts[j]; pos = j / n if outer == 'right' else 1 - j / n   # 0 inner -> 1 outer
        L = 3 + 7 * np.sin(np.pi * min(pos*1.1, 1)) ** 0.7 + rng.uniform(-1, 1)
        ang = np.deg2rad(70 - 35 * pos + rng.uniform(-6, 6))  # from horizontal, pointing down/outward
        dx, dy = sgn * np.cos(ang) * L, np.sin(ang) * L
        mx, my = x + dx*0.5 + sgn*0.8, y + dy*0.45
        d.line([(x*SS, y*SS), (mx*SS, my*SS), ((x+dx)*SS, (y+dy)*SS)], fill=lash+(int(170 - 60*rng.random()),), width=int(1.1*SS))
ov = ov.resize((W, H), Image.LANCZOS)
res = res.convert('RGBA'); res.alpha_composite(ov); res = res.convert('RGB')
res.save(OUT)
