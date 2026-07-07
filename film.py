#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brasserie Phoenix — LE FILM (1080x1920 / 30fps / 25.2s).

Ligne directrice : un seul CERCLE DE CUIVRE, ne du phenix, devient chaque
assiette, voyage de plat en plat (match-cut sur la forme), grandit en plein
cadre pour le feu, puis se referme sur l'invitation. Menu en 8 temps (I-VIII).

La transition N'EST PAS un effet plaque : c'est le cercle lui-meme qui se
deplace / grandit / retrecit + fondu vertical (tout "monte", le phenix renait).
Grade sobre, grain fin. Zero gadget (pas de vapeur/parallaxe/bokeh).
"""
import os, sys, math, glob
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.abspath(__file__))
PH = os.path.join(ROOT, "photos"); FT = os.path.join(ROOT, "assets", "fonts")
OUTDIR = os.path.join(ROOT, "output"); FRAMES = os.path.join(OUTDIR, "_frames")

NAVY  = np.array([15, 30, 42], np.float32)
NAVY2 = np.array([27, 54, 72], np.float32)
COPPER = np.array([185, 141, 85], np.float32)
CREAM = np.array([243, 237, 226], np.float32)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_DIAG = math.hypot(W/2, H/2)

def fnt(name, s): return ImageFont.truetype(os.path.join(FT, name), s)
FONTS = {}
def F(name, s):
    k = (name, s)
    if k not in FONTS: FONTS[k] = fnt(name, s)
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
    n = np.clip(n, 0, 1); n = np.clip((n-0.5)*1.08+0.5, 0, 1)
    return n*255.0

def cover_square(img, size, bias=(0., 0.)):
    ih, iw = img.shape[:2]; s = size/min(ih, iw)
    r = cv2.resize(img, (int(math.ceil(iw*s)), int(math.ceil(ih*s))), interpolation=cv2.INTER_CUBIC)
    exx, exy = r.shape[1]-size, r.shape[0]-size
    x0 = int(exx*(0.5+bias[0]*0.5)); y0 = int(exy*(0.5+bias[1]*0.5))
    x0 = min(max(0, x0), exx); y0 = min(max(0, y0), exy)
    return r[y0:y0+size, x0:x0+size]

def bg_field():
    g = np.clip(1.0-np.sqrt(((xx-W/2)/(W*0.8))**2+((yy-H*0.42)/(H*0.72))**2), 0, 1)[..., None]
    return (NAVY+(NAVY2-NAVY)*g).copy()

_grain_cache = [np.random.RandomState(i).normal(0, 3.4, (H, W, 1)).astype(np.float32) for i in range(12)]
def grain(f, i): return f + _grain_cache[i % 12]

# ---------------------------------------------------------------------------
# Dishes (carres pre-grades) + donnees de chapitre
# ---------------------------------------------------------------------------
COURSES = [
    dict(file="01_spread.jpg",       num="I",    name="La pierre chaude",   sub="TORREVIEJA · ORIHUELA COSTA",
         mode="bleed",  C=(.50,.44), R=1.16, bias=(0,-.1)),
    dict(file="02_burrata_pasta.jpg",num="II",   name="Pâtes maison",       sub="BURRATA · BASILIC · POIVRE",
         mode="circle", C=(.57,.34), R=.40, bias=(0,0)),
    dict(file="03_squid.jpg",        num="III",  name="Calamar grillé",     sub="GRILLÉ MINUTE · PIMENT",
         mode="circle", C=(.43,.35), R=.40, bias=(0,0)),
    dict(file="04_burger.jpg",       num="IV",   name="Fait maison",        sub="BŒUF · BURRATA · PESTO",
         mode="circle", C=(.50,.35), R=.43, bias=(-.1,0)),
    dict(file="05_bread.jpg",        num="V",    name="À partager",         sub="PAIN · SALSA · AÏOLI",
         mode="circle", C=(.58,.34), R=.40, bias=(0,0)),
    dict(file="06_tartare.jpg",      num="VI",   name="Tartare au couteau", sub="BŒUF · CÂPRES · JAUNE",
         mode="circle", C=(.42,.36), R=.43, bias=(0,0)),
    dict(file="07_steak.jpg",        num="VII",  name="Pierres brûlantes",  sub="900°C · À LA PIERRE",
         mode="bleed",  C=(.50,.50), R=1.22, bias=(.18,.42)),
    dict(file="08_martini.jpg",      num="VIII", name="L'heure douce",      sub="ESPRESSO MARTINI",
         mode="circle", C=(.50,.31), R=.33, bias=(0,-.05)),
]
for c in COURSES:
    sz = int((1.24 if c["mode"] == "bleed" else 2*c["R"]) * W) + 4
    c["sq"] = grade(cover_square(load(c["file"]), max(sz, 300), c["bias"]))

def circle_of(c):
    return (c["C"][0]*W, c["C"][1]*H, c["R"]*W)

# ---------------------------------------------------------------------------
# Rendu d'un disque (assiette) : dish carre -> cercle (C,R), decalage vertical
# ---------------------------------------------------------------------------
def draw_disc(canvas, sq, cx, cy, R, alpha=1.0, rise=0.0, ring=True):
    R = max(6.0, R); size = int(R*2)
    d = np.sqrt((xx-cx)**2+(yy-cy)**2)
    m = np.clip((R-d)/2.5, 0, 1)
    if alpha < 1: m = m*alpha
    if m.max() <= 0: return canvas
    big = cv2.resize(sq, (size, size), interpolation=cv2.INTER_CUBIC)
    canvasbig = np.zeros((H, W, 3), np.float32)
    oy = int(cy-R - rise); ox = int(cx-R)
    y0, x0 = max(0, oy), max(0, ox); y1, x1 = min(H, oy+size), min(W, ox+size)
    if y1 > y0 and x1 > x0:
        canvasbig[y0:y1, x0:x1] = big[y0-oy:y1-oy, x0-ox:x1-ox]
    mm = m[..., None]
    out = canvas*(1-mm)+canvasbig*mm
    if ring:
        ra = np.clip((0.78*W - R)/(0.23*W), 0, 1)          # anneau s'efface en plein cadre
        if ra > 0.01:
            rr = np.clip(1-np.abs(d-R)/1.7, 0, 1)[..., None]*ra
            out = out*(1-rr)+COPPER*rr
    return out

# ---------------------------------------------------------------------------
# Typo (reveal : monte + fondu ; mono-ligne, tracking)
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

def reveal(canvas, s, font, tr, color, y, t, start, dur=0.55, cx=None, xleft=None, amax=1.0):
    p = (t-start)/dur
    if p <= 0: return canvas
    e = eout(p); return text(canvas, s, font, tr, color, y, cx=cx, xleft=xleft,
                             alpha=min(1, e)*amax, rise=int((1-e)*16))

def course_type(canvas, c, t):
    """Bloc chapitre : numero + nom + filet + sous-titre. Position selon mode."""
    if c["mode"] == "bleed":
        base = H*0.79
        canvas = reveal(canvas, c["num"], CS(58), 0, COPPER, base, t, 0.25, cx=W*0.5)
        canvas = reveal(canvas, c["name"]+".", CM(74), 2, CREAM, base+66, t, 0.4, cx=W*0.5)
        canvas = reveal(canvas, c["sub"], JL(23), 5, CREAM, base+150, t, 0.6, cx=W*0.5, amax=0.72)
    else:
        lx = W*0.13; base = H*0.64
        canvas = reveal(canvas, c["num"], CS(86), 0, COPPER, base, t, 0.25, xleft=lx)
        canvas = reveal(canvas, c["name"], CM(72), 2, CREAM, base+120, t, 0.42, xleft=lx)
        p = (t-0.6)/0.5
        if p > 0:
            xw = int(90*ease(min(1, p)))
            cv2.line(canvas, (int(lx)+2, int(base+232)), (int(lx)+2+xw, int(base+232)),
                     COPPER.tolist(), 2, cv2.LINE_AA)
        canvas = reveal(canvas, c["sub"], JL(23), 5, CREAM, base+250, t, 0.7, xleft=lx, amax=0.72)
    return canvas

# ---------------------------------------------------------------------------
# Logo phenix detoure
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
    ih, iw = im.shape[:2]; nw = scale_w; nh = int(ih*scale_w/iw)
    return cv2.resize(im, (nw, nh), interpolation=cv2.INTER_CUBIC), cv2.resize(al, (nw, nh))[..., None]

LOGO_RGB, LOGO_A = logo_rgba(int(W*0.30))
def paste_logo(canvas, cx, cy, alpha):
    rgb, a = LOGO_RGB, LOGO_A*alpha; nh, nw = rgb.shape[:2]
    ox, oy = int(cx-nw/2), int(cy-nh/2)
    x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox+nw), min(H, oy+nh)
    aa = a[y0-oy:y1-oy, x0-ox:x1-ox]; cc = rgb[y0-oy:y1-oy, x0-ox:x1-ox]
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1]*(1-aa)+cc*aa

# ---------------------------------------------------------------------------
# Timeline : le cercle voyageur
# ---------------------------------------------------------------------------
DUR = [2.4, 2.4, 1.8, 1.8, 1.8, 1.8, 2.4, 3.6, 2.4, 4.8]   # titre + 8 + cta
NAMES = ["title"] + [c["name"] for c in COURSES] + ["cta"]
STARTS = np.cumsum([0]+DUR)[:-1]; TOTAL = sum(DUR)
TRANS = 0.55                                               # fenetre de transition

# cercle "cible" de chaque segment (le titre nait autour du phenix ; la cta au meme endroit que le martini qui monte)
TITLE_CIRCLE = (W*0.5, H*0.34, W*0.30)
CTA_CIRCLE   = (W*0.5, H*0.26, W*0.26)
SEG_CIRCLE = [TITLE_CIRCLE] + [circle_of(c) for c in COURSES] + [CTA_CIRCLE]
SEG_DISH   = [None] + list(range(8)) + [7]                  # cta reprend le martini

def seg_at(t):
    i = 0
    for k, s in enumerate(STARTS):
        if t >= s: i = k
    return i

def circle_lerp(a, b, e):
    return (a[0]+(b[0]-a[0])*e, a[1]+(b[1]-a[1])*e, a[2]+(b[2]-a[2])*e)

def render(t):
    f = bg_field()
    i = seg_at(t)
    # position dans le segment + fenetres de transition
    s0 = STARTS[i]; dur = DUR[i]
    # transition entrante (autour de la borne s0) et sortante (borne s0+dur)
    # on gere via le voisinage de chaque borne b = STARTS[i+1]
    in_trans = None
    for b_idx in range(1, len(STARTS)):
        b = STARTS[b_idx]
        if b-TRANS/2 <= t < b+TRANS/2:
            in_trans = b_idx; break
    if in_trans is not None:
        i0, i1 = in_trans-1, in_trans
        b = STARTS[in_trans]; q = (t-(b-TRANS/2))/TRANS; e = ease(q)
        C = circle_lerp(SEG_CIRCLE[i0], SEG_CIRCLE[i1], e)
        # fondu vertical "qui monte" : ancien plat monte et sort, nouveau monte depuis le bas
        d0, d1 = SEG_DISH[i0], SEG_DISH[i1]
        rise0 = e*C[2]*0.5; rise1 = -(1-e)*C[2]*0.5
        if d0 is not None:
            f = draw_disc(f, COURSES[d0]["sq"], C[0], C[1], C[2], alpha=1.0-e, rise=rise0)
        else:
            f = _title_visual(f, C, 1.0-e)
        if d1 is not None:
            f = draw_disc(f, COURSES[d1]["sq"], C[0], C[1], C[2], alpha=e, rise=rise1)
        else:
            f = _cta_visual(f, C, e, t-b)
        f = grain(f, int(t*FPS))
        return np.clip(f, 0, 255)

    # --- HOLD ---
    tl = t-s0
    C = SEG_CIRCLE[i]
    # respiration tres subtile du cercle + leger drift vertical (ca "monte")
    br = 1.0+0.012*math.sin(tl*0.7)
    C = (C[0], C[1]-tl*2.0, C[2]*br)
    d = SEG_DISH[i]; last = len(DUR)-1
    if i == 0:
        f = _title_hold(f, C, tl)
    elif i == last:
        f = _cta_visual(f, C, 1.0, tl); f = _cta_type(f, tl)
    else:
        c = COURSES[d]
        f = draw_disc(f, c["sq"], C[0], C[1], C[2])
        if c["mode"] == "bleed": f = _bleed_finish(f)
        f = course_type(f, c, tl)
    f = grain(f, int(t*FPS))
    return np.clip(f, 0, 255)

def _bleed_finish(f):
    """Vignette + scrim bas pour lisibilite en plein cadre."""
    d = np.sqrt(((xx-W/2)/(W*0.62))**2 + ((yy-H*0.5)/(H*0.62))**2)
    vig = np.clip((d-0.4)/0.8, 0, 1)[..., None]**1.4
    f = f*(1-vig*0.80) + NAVY*(vig*0.80)
    grad = np.clip((yy/H-0.58)/0.42, 0, 1)[..., None]
    f = f*(1-grad*0.66) + NAVY*(grad*0.66)
    return f

def _title_visual(f, C, alpha):
    paste_logo(f, C[0], C[1], alpha*0.95)
    ra = np.clip((0.78*W-C[2])/(0.23*W), 0, 1)*alpha
    d = np.sqrt((xx-C[0])**2+(yy-C[1])**2)
    rr = np.clip(1-np.abs(d-C[2])/1.7, 0, 1)[..., None]*ra*0.9
    return f*(1-rr)+COPPER*rr

def _title_hold(f, C, tl):
    # anneau qui se dessine autour du phenix (il en nait le cercle)
    prog = ease(min(1, tl/0.9))
    d = np.sqrt((xx-C[0])**2+(yy-C[1])**2)
    ang = (np.arctan2(yy-C[1], xx-C[0])+math.pi)/(2*math.pi)      # 0..1 horaire
    ring = np.clip(1-np.abs(d-C[2])/1.8, 0, 1)*(ang < prog).astype(np.float32)
    paste_logo(f, C[0], C[1], eout(min(1, tl/0.8))*0.97)
    f = f*(1-ring[..., None])+COPPER*ring[..., None]
    f = reveal(f, "BRASSERIE", CB(118), 6, CREAM, H*0.52, tl, 0.7, cx=W*0.5)
    f = reveal(f, "PHOENIX", CB(118), 24, COPPER, H*0.585, tl, 0.9, cx=W*0.5)
    p = (tl-1.2)/0.5
    if p > 0:
        xw = int(W*0.12*ease(min(1, p)))
        cv2.line(f, (W//2-xw, int(H*0.66)), (W//2+xw, int(H*0.66)), COPPER.tolist(), 1, cv2.LINE_AA)
    f = reveal(f, "PIERRES BRÛLANTES   ·   PÂTES MAISON   ·   ÂME BELGE", JL(23), 6, CREAM,
               H*0.685, tl, 1.35, cx=W*0.5, amax=0.8)
    return f

def _cta_visual(f, C, alpha, tl):
    f = draw_disc(f, COURSES[7]["sq"], C[0], C[1], C[2], alpha=alpha)
    return f

def _cta_type(f, tl):
    f = reveal(f, "RÉSERVEZ", JM(30), 10, COPPER, H*0.50, tl, 0.35, cx=W*0.5)
    f = reveal(f, "votre table", CM(90), 2, CREAM, H*0.535, tl, 0.5, cx=W*0.5)
    p = (tl-0.8)/0.5
    if p > 0:
        xw = int(W*0.10*ease(min(1, p)))
        cv2.line(f, (W//2-xw, int(H*0.68)), (W//2+xw, int(H*0.68)), COPPER.tolist(), 1, cv2.LINE_AA)
    f = reveal(f, "JEUDI — LUNDI    ·    MIDI & SOIR", JL(24), 5, CREAM, H*0.695, tl, 1.0, cx=W*0.5, amax=0.85)
    f = reveal(f, "Av. Desiderio Rodríguez 37 · Torrevieja", JL(22), 2, CREAM, H*0.735, tl, 1.25, cx=W*0.5, amax=0.62)
    f = reveal(f, "(+34) 744 622 975", JL(22), 3, COPPER, H*0.775, tl, 1.4, cx=W*0.5, amax=0.85)
    # fondu au noir final
    fo = (tl-(DUR[-1]-1.1))/1.1
    if fo > 0: f = f*(1-min(1, fo))
    return f

def main():
    if "--preview" in sys.argv:
        os.makedirs(os.path.join(OUTDIR, "_film"), exist_ok=True)
        for t in [1.4, 2.4, 3.4, 5.6, 7.4, 9.2, 11.0, 13.2, 14.4, 16.2, 18.9, 22.0, 24.4]:
            t = min(t, TOTAL-0.01)
            Image.fromarray(render(t).astype(np.uint8)).save(
                os.path.join(OUTDIR, "_film", "t_%05.2f.png" % t))
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
    print("done", nf, "dur", TOTAL)

if __name__ == "__main__":
    print("film dur %.2fs" % TOTAL)
    main()
