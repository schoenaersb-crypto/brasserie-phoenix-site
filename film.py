#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brasserie Phoenix — LE FILM v2 (1080x1920 / 30fps / 25.2s).

Corrections :
 · PLATS ENTIERS — chaque plat est montre COMPLET (contain largeur), jamais
   recadre. Cadre cuivre fin + bandeaux navy pour la typo.
 · SUJET CLAIR — brasserie belge a Torrevieja, sa CARTE en 8 plats (I-VIII).
   Kicker "BRASSERIE PHOENIX · LA CARTE" sur chaque plan.
 · PATES — "Spaghetti burrata" (pas "maison"), slogan sans revendication fausse.

Ligne directrice : la carte se deroule, chaque plat MONTE a l'ecran (le phenix
renait), relie par un filet de cuivre qui balaie la coupe. Grade sobre, grain fin.
"""
import os, sys, math, glob
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.abspath(__file__))
PH = os.path.join(ROOT, "photos"); FT = os.path.join(ROOT, "assets", "fonts")
OUTDIR = os.path.join(ROOT, "output"); FRAMES = os.path.join(OUTDIR, "_frames")

NAVY  = np.array([14, 28, 39], np.float32)
NAVY2 = np.array([25, 50, 68], np.float32)
COPPER = np.array([185, 141, 85], np.float32)
CREAM = np.array([244, 238, 227], np.float32)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

FONTS = {}
def F(name, s):
    k = (name, s)
    if k not in FONTS: FONTS[k] = ImageFont.truetype(os.path.join(FT, name), s)
    return FONTS[k]
CB = lambda s: F("Cormorant-Bold.ttf", s); CM = lambda s: F("Cormorant-Medium.ttf", s)
CS = lambda s: F("Cormorant-SemiBold.ttf", s)
JL = lambda s: F("Jost-Light.ttf", s); JM = lambda s: F("Jost-Medium.ttf", s)

def ease(p): p = min(1, max(0, p)); return p*p*(3-2*p)
def eout(p): p = min(1, max(0, p)); return 1-(1-p)**3

def load(name):
    return cv2.cvtColor(cv2.imread(os.path.join(PH, name)), cv2.COLOR_BGR2RGB).astype(np.float32)

def grade(f):
    n = f/255.0
    lum = (n*np.array([.299,.587,.114],np.float32)).sum(2, keepdims=True)
    n = n + (1-lum)*np.array([-.020,.008,.035],np.float32) + lum*np.array([.035,.014,-.020],np.float32)
    n = np.clip(n, 0, 1); n = np.clip((n-0.5)*1.07+0.5, 0, 1)
    return n*255.0

def bg_field():
    g = np.clip(1.0-np.sqrt(((xx-W/2)/(W*0.85))**2+((yy-H*0.44)/(H*0.75))**2), 0, 1)[..., None]
    return (NAVY+(NAVY2-NAVY)*g).copy()

_grain = [np.random.RandomState(i).normal(0, 3.2, (H, W, 1)).astype(np.float32) for i in range(12)]
def grain(f, i): return f + _grain[i % 12]

def contain_width(img, wd):
    """Largeur = wd, image ENTIERE visible (aucun recadrage)."""
    ih, iw = img.shape[:2]; s = wd/iw
    return cv2.resize(img, (wd, int(round(ih*s))), interpolation=cv2.INTER_CUBIC)

# ---------------------------------------------------------------------------
# CARTE — 8 plats (noms exacts). Sujet : brasserie belge, Torrevieja.
# ---------------------------------------------------------------------------
IMG_W = int(W*0.90)            # largeur du plat a l'ecran (plat entier)
COURSES = [
    dict(file="01_spread.jpg",        num="I",    name="La piedra caliente",  sub="EL FUEGO · A LA PIEDRA 400°C"),
    dict(file="02_burrata_pasta.jpg", num="II",   name="Spaghetti burrata",   sub="BURRATA · ALBAHACA · PIMIENTA"),
    dict(file="03_squid.jpg",         num="III",  name="Sepia a la parrilla", sub="A LA PARRILLA · PIMIENTO DULCE"),
    dict(file="04_burger.jpg",        num="IV",   name="Hamburguesa burrata", sub="TERNERA · BURRATA · PESTO"),
    dict(file="05_bread.jpg",         num="V",    name="Pan & alioli",        sub="PARA COMPARTIR · SALSA CASERA"),
    dict(file="06_tartare.jpg",       num="VI",   name="Tartar a cuchillo",   sub="TERNERA · ALCAPARRAS · YEMA"),
    dict(file="07_steak.jpg",         num="VII",  name="Piedras calientes",   sub="LA ESPECIALIDAD · 400°C"),
    dict(file="08_martini.jpg",       num="VIII", name="Espresso martini",    sub="LA HORA DULCE"),
]
for c in COURSES:
    c["img"] = grade(contain_width(load(c["file"]), IMG_W))
    c["ih"] = c["img"].shape[0]

IMG_CY = int(H*0.375)          # centre vertical du plat
def dish_box(c):
    ih = c["ih"]; y0 = IMG_CY - ih//2; return y0, y0+ih

# ---------------------------------------------------------------------------
# Depose d'un plat ENTIER + cadre cuivre fin
# ---------------------------------------------------------------------------
def place_dish(canvas, c, alpha=1.0, rise=0):
    img = c["img"]; ih = c["ih"]
    y0 = IMG_CY - ih//2 - int(rise); x0 = (W - IMG_W)//2
    yy0, yy1 = max(0, y0), min(H, y0+ih); xx0, xx1 = x0, x0+IMG_W
    if yy1 <= yy0: return canvas
    sub = img[yy0-y0:yy1-y0]
    canvas[yy0:yy1, xx0:xx1] = canvas[yy0:yy1, xx0:xx1]*(1-alpha) + sub*alpha
    # cadre cuivre fin
    if alpha > 0.5:
        a = (alpha-0.5)*2
        col = (COPPER*a + canvas[0, 0]*0).tolist()
        cv2.rectangle(canvas, (xx0-1, yy0-1), (xx1, yy1), COPPER.tolist(), 1, cv2.LINE_AA)
    return canvas

# ---------------------------------------------------------------------------
# Typo
# ---------------------------------------------------------------------------
def _tw(font, s, tr): return sum((font.getbbox(c)[2]-font.getbbox(c)[0])+tr for c in s)-tr
def text(canvas, s, font, tr, color, y, cx=None, xleft=None, alpha=1.0, rise=0):
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    w = _tw(font, s, tr)
    x = (W-w)/2 if (cx is None and xleft is None) else (xleft if xleft is not None else cx-w/2)
    for ch in s:
        d.text((x, y-rise), ch, font=font, fill=255); bb = font.getbbox(ch); x += (bb[2]-bb[0])+tr
    m = (np.asarray(im, np.float32)/255.0*alpha)[..., None]
    return canvas*(1-m)+np.array(color, np.float32)*m

def reveal(canvas, s, font, tr, color, y, t, start, dur=0.5, cx=None, xleft=None, amax=1.0):
    p = (t-start)/dur
    if p <= 0: return canvas
    e = eout(p); return text(canvas, s, font, tr, color, y, cx=cx, xleft=xleft,
                             alpha=min(1, e)*amax, rise=int((1-e)*14))

def kicker(canvas, alpha=0.6):
    return text(canvas, "BRASSERIE  PHOENIX      ·      LA  CARTA", JM(19), 6, COPPER,
                H*0.052, cx=W*0.5, alpha=alpha)

def course_type(canvas, c, tl):
    by = H*0.72
    canvas = kicker(canvas, 0.55)
    canvas = reveal(canvas, c["num"], CS(64), 0, COPPER, by, tl, 0.15, cx=W*0.5)
    canvas = reveal(canvas, c["name"], CM(80), 2, CREAM, by+70, tl, 0.3, cx=W*0.5)
    p = (tl-0.5)/0.5
    if p > 0:
        xw = int(W*0.11*ease(min(1, p)))
        cv2.line(canvas, (W//2-xw, int(by+172)), (W//2+xw, int(by+172)), COPPER.tolist(), 1, cv2.LINE_AA)
    canvas = reveal(canvas, c["sub"], JL(23), 5, CREAM, by+190, tl, 0.65, cx=W*0.5, amax=0.72)
    return canvas

# ---------------------------------------------------------------------------
# Logo
# ---------------------------------------------------------------------------
def logo_rgba(scale_w):
    im = load("logo.png"); mx = im.max(2); mn = im.min(2)
    bg = (mx/255.0 > .80) & ((mx-mn)/(mx+1e-6) < .14)
    fgm = np.where(bg, 0, 255).astype(np.uint8)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(fgm, 8)
    keep = np.zeros_like(fgm)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 45: keep[lbl == i] = 255
    al = cv2.GaussianBlur(keep.astype(np.float32)/255.0, (0, 0), 1.2)
    ih, iw = im.shape[:2]; nw = scale_w
    return cv2.resize(im, (nw, int(ih*scale_w/iw)), interpolation=cv2.INTER_CUBIC), \
           cv2.resize(al, (nw, int(ih*scale_w/iw)))[..., None]
LOGO_RGB, LOGO_A = logo_rgba(int(W*0.30))
def paste_logo(canvas, cx, cy, alpha):
    rgb, a = LOGO_RGB, LOGO_A*alpha; nh, nw = rgb.shape[:2]
    ox, oy = int(cx-nw/2), int(cy-nh/2)
    x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox+nw), min(H, oy+nh)
    aa = a[y0-oy:y1-oy, x0-ox:x1-ox]; cc = rgb[y0-oy:y1-oy, x0-ox:x1-ox]
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1]*(1-aa)+cc*aa

# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------
DUR = [2.4, 2.4, 1.8, 1.8, 1.8, 1.8, 2.4, 3.6, 2.4, 4.8]   # titre + 8 + cta
STARTS = list(np.cumsum([0]+DUR)[:-1]); TOTAL = sum(DUR)
TRANS = 0.42

def seg_at(t):
    i = 0
    for k, s in enumerate(STARTS):
        if t >= s: i = k
    return i

def title_visual(canvas, alpha, rise):
    paste_logo(canvas, W*0.5, H*0.335 - rise, alpha*0.96)
    return canvas

def title_type(canvas, tl):
    canvas = reveal(canvas, "BRASSERIE", CB(116), 6, CREAM, H*0.50, tl, 0.55, cx=W*0.5)
    canvas = reveal(canvas, "PHOENIX", CB(116), 24, COPPER, H*0.565, tl, 0.72, cx=W*0.5)
    p = (tl-1.0)/0.5
    if p > 0:
        xw = int(W*0.12*ease(min(1, p)))
        cv2.line(canvas, (W//2-xw, int(H*0.645)), (W//2+xw, int(H*0.645)), COPPER.tolist(), 1, cv2.LINE_AA)
    canvas = reveal(canvas, "COCINA BELGA   ·   TORREVIEJA", JM(22), 7, CREAM, H*0.668, tl, 1.1, cx=W*0.5, amax=0.85)
    canvas = reveal(canvas, "Piedra caliente · Cocina de mercado · Alma belga", CM(33), 1, CREAM,
                    H*0.705, tl, 1.35, cx=W*0.5, amax=0.8)
    return canvas

def cta_visual(canvas, alpha, rise):
    c = COURSES[7]; ih = c["ih"]; scale = 0.62
    small = cv2.resize(c["img"], (int(IMG_W*scale), int(ih*scale)), interpolation=cv2.INTER_CUBIC)
    sh, sw = small.shape[:2]; cy = int(H*0.28 - rise); x0 = (W-sw)//2; y0 = cy-sh//2
    yy0, yy1 = max(0, y0), min(H, y0+sh)
    if yy1 > yy0:
        canvas[yy0:yy1, x0:x0+sw] = canvas[yy0:yy1, x0:x0+sw]*(1-alpha)+small[yy0-y0:yy1-y0]*alpha
        if alpha > 0.5:
            cv2.rectangle(canvas, (x0-1, yy0-1), (x0+sw, yy1), COPPER.tolist(), 1, cv2.LINE_AA)
    return canvas

def cta_type(canvas, tl):
    canvas = reveal(canvas, "RESERVA", JM(30), 10, COPPER, H*0.50, tl, 0.3, cx=W*0.5)
    canvas = reveal(canvas, "tu mesa", CM(88), 2, CREAM, H*0.535, tl, 0.45, cx=W*0.5)
    p = (tl-0.75)/0.5
    if p > 0:
        xw = int(W*0.10*ease(min(1, p)))
        cv2.line(canvas, (W//2-xw, int(H*0.675)), (W//2+xw, int(H*0.675)), COPPER.tolist(), 1, cv2.LINE_AA)
    canvas = reveal(canvas, "JUEVES — LUNES     ·     MEDIODÍA Y NOCHE", JL(24), 5, CREAM, H*0.69, tl, 0.95, cx=W*0.5, amax=0.85)
    canvas = reveal(canvas, "Av. Desiderio Rodríguez 37 · Torrevieja", JL(22), 2, CREAM, H*0.73, tl, 1.15, cx=W*0.5, amax=0.62)
    canvas = reveal(canvas, "(+34) 744 622 975", JL(22), 3, COPPER, H*0.77, tl, 1.3, cx=W*0.5, amax=0.85)
    fo = (tl-(DUR[-1]-1.1))/1.1
    if fo > 0: canvas = canvas*(1-min(1, fo))
    return canvas

def seg_visual(canvas, i, alpha, rise):
    last = len(DUR)-1
    if i == 0:   return title_visual(canvas, alpha, rise)
    if i == last: return cta_visual(canvas, alpha, rise)
    return place_dish(canvas, COURSES[i-1], alpha, rise)

def copper_sweep(canvas, e):
    """Filet de cuivre qui balaie horizontalement la coupe (pic a e=0.5)."""
    w = int(W*0.62*(1-abs(2*e-1))); y = int(H*0.5)
    if w > 4:
        cv2.line(canvas, (W//2-w//2, y), (W//2+w//2, y), COPPER.tolist(), 2, cv2.LINE_AA)
    return canvas

def render(t):
    f = bg_field()
    # transition autour d'une borne ?
    for b_idx in range(1, len(STARTS)):
        b = STARTS[b_idx]
        if b-TRANS/2 <= t < b+TRANS/2:
            e = ease((t-(b-TRANS/2))/TRANS); i0, i1 = b_idx-1, b_idx
            f = seg_visual(f, i0, 1.0-e, int(e*130))          # sortant monte
            f = seg_visual(f, i1, e, int(-(1-e)*130))         # entrant monte du bas
            f = kicker(f, 0.5)
            f = copper_sweep(f, e)
            return np.clip(grain(f, int(t*FPS)), 0, 255)
    # hold
    i = seg_at(t); tl = t-STARTS[i]; last = len(DUR)-1
    rise = tl*3.0                                             # leger drift qui monte
    if i == 0:
        f = title_visual(f, eout(min(1, tl/0.8))*0.96, 0); f = title_type(f, tl)
    elif i == last:
        f = cta_visual(f, 1.0, 0); f = cta_type(f, tl)
    else:
        f = place_dish(f, COURSES[i-1], 1.0, int(rise)); f = course_type(f, COURSES[i-1], tl)
    return np.clip(grain(f, int(t*FPS)), 0, 255)

def main():
    if "--preview" in sys.argv:
        d = os.path.join(OUTDIR, "_film"); os.makedirs(d, exist_ok=True)
        for t in [1.4, 3.2, 5.0, 7.0, 9.0, 11.0, 13.0, 15.8, 19.0, 22.5, 24.6]:
            t = min(t, TOTAL-0.01)
            Image.fromarray(render(t).astype(np.uint8)).save(os.path.join(d, "t_%05.2f.png" % t))
            print("prev", round(t, 2))
        return
    os.makedirs(FRAMES, exist_ok=True)
    for old in glob.glob(os.path.join(FRAMES, "*.png")): os.remove(old)
    nf = int(round(TOTAL*FPS))
    for n in range(nf):
        fr = render(n/FPS).astype(np.uint8)
        cv2.imwrite(os.path.join(FRAMES, "f_%05d.png" % n), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR),
                    [cv2.IMWRITE_PNG_COMPRESSION, 1])
        if n % 30 == 0: print("frame %d/%d" % (n, nf), flush=True)
    print("done", nf)

if __name__ == "__main__":
    print("film v2 %.2fs" % TOTAL); main()
