#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE PHOENIX — Ethereal Dish Showcase (5s / 9:16 / 1080x1920 / 30fps).
Inspire du template CapCut "Ethereal Product Showcase" : braises lumineuses,
revelation mysterieuse du plat (Entrecote Black Angus a la piedra), logo & texte.

Sortie : output/phoenix_entrecote_showcase.mp4
"""
import os, sys, math, glob
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, NF = 1080, 1920, 30, 150
ROOT = os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(ROOT, "assets", "fonts")
OUTDIR = os.path.join(ROOT, "output"); FRAMES = os.path.join(OUTDIR, "_sc_frames")

BLACK  = np.array([10, 10, 10], np.float32)
NAVY   = np.array([22, 54, 74], np.float32)
COPPER = np.array([185, 141, 85], np.float32)
GOLD   = np.array([212, 168, 67], np.float32)
CREAM  = np.array([246, 240, 228], np.float32)
WARM   = np.array([255, 245, 224], np.float32)
EMBER  = np.array([255, 140, 58], np.float32)
WHITE  = np.array([255, 255, 255], np.float32)
PALETTE = [COPPER, GOLD, WARM, EMBER]

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_cx, _cy = W/2.0, H*0.44
_rad = np.sqrt((xx-_cx)**2 + (yy-_cy)**2)

def font(name, s): return ImageFont.truetype(os.path.join(FT, name), s)
CB = lambda s: font("Cormorant-Bold.ttf", s)
CI = lambda s: font("Cormorant-BoldItalic.ttf", s)
JR = lambda s: font("Jost-Regular.ttf", s)
JL = lambda s: font("Jost-Light.ttf", s)

def ease(p): p = min(1, max(0, p)); return p*p*(3-2*p)
def eout(p): p = min(1, max(0, p)); return 1-(1-p)**3
def elastic(p):
    p = min(1, max(0, p))
    if p >= 1: return 1.0
    return 1 - pow(2, -9*p)*math.cos(p*math.pi*3.0)*0.55 - (1-1)  # ease-out leger rebond

def load(path):
    return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB).astype(np.float32)

def cover_fit(img, w, h):
    ih, iw = img.shape[:2]; s = max(w/iw, h/ih)
    r = cv2.resize(img, (int(math.ceil(iw*s)), int(math.ceil(ih*s))), interpolation=cv2.INTER_CUBIC)
    y0 = (r.shape[0]-h)//2; x0 = (r.shape[1]-w)//2
    return r[y0:y0+h, x0:x0+w]

# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------
DISH = cover_fit(load(os.path.join(ROOT, "assets_sc", "dish_crop.png")), int(W*1.02), int(H*0.66))
DISH_H, DISH_W = DISH.shape[:2]

def logo_gold(scale_w):
    """Phenix detoure + recolorise cuivre->or (garde le modele du dessin)."""
    im = load(os.path.join(ROOT, "photos", "logo.png"))
    mx = im.max(2); mn = im.min(2)
    bg = (mx/255.0 > .80) & ((mx-mn)/(mx+1e-6) < .14)
    fgm = np.where(bg, 0, 255).astype(np.uint8)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(fgm, 8)
    keep = np.zeros_like(fgm)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 45: keep[lbl == i] = 255
    al = cv2.GaussianBlur(keep.astype(np.float32)/255.0, (0, 0), 1.0)
    # luminance du dessin -> module la brillance de l'or
    lum = (im*np.array([.299,.587,.114],np.float32)).sum(2)
    lum = (lum-lum.min())/(lum.max()-lum.min()+1e-6)
    ih, iw = im.shape[:2]
    grad = np.linspace(0, 1, ih)[:, None]                    # haut=or, bas=cuivre
    tint = GOLD[None, None, :]*grad[..., None] + COPPER[None, None, :]*(1-grad[..., None])
    rgb = tint[:, 0, :][:, None, :]*0 + tint                 # (ih,iw,3)
    rgb = rgb * (0.45 + 0.75*lum[..., None])
    nw = scale_w; nh = int(ih*scale_w/iw)
    rgb = cv2.resize(np.clip(rgb, 0, 255), (nw, nh), interpolation=cv2.INTER_CUBIC)
    a = cv2.resize(al, (nw, nh))[..., None]
    return rgb, a
LOGO_RGB, LOGO_A = logo_gold(int(W*0.30))

# ---------------------------------------------------------------------------
# Particules (braises montantes)
# ---------------------------------------------------------------------------
class Embers:
    def __init__(self, n=220, seed=7):
        r = np.random.RandomState(seed)
        self.x = r.uniform(0, W, n)
        self.y = r.uniform(H*0.4, H*1.05, n)
        self.vx = r.uniform(-0.35, 0.35, n)
        self.vy = r.uniform(-2.0, -0.5, n)
        self.size = r.uniform(1.2, 4.2, n)
        self.tw = r.uniform(0.12, 0.42, n)
        self.ph = r.uniform(0, 6.28, n)
        self.op = r.uniform(0.3, 0.95, n)
        self.col = np.array([PALETTE[i][:] for i in r.randint(0, len(PALETTE), n)], np.float32)
        self.turb = r.uniform(0.4, 1.4, n)
        self.n = n; self.r = r

    def step(self):
        self.y += self.vy
        self.x += self.vx + np.sin((self.y*0.02) + self.ph)*0.5*self.turb
        dead = self.y < -10
        k = dead.sum()
        if k:
            self.y[dead] = H*self.r.uniform(0.85, 1.05, k)
            self.x[dead] = self.r.uniform(0, W, k)

    def render(self, frame_idx, intensity):
        lay = np.zeros((H, W, 3), np.float32)
        opn = self.op*(0.45+0.55*np.sin(frame_idx*self.tw + self.ph))
        for i in range(self.n):
            o = opn[i]*intensity
            if o <= 0.02: continue
            cv2.circle(lay, (int(self.x[i]), int(self.y[i])), int(self.size[i]),
                       (self.col[i]*o).tolist(), -1, cv2.LINE_AA)
        glow = cv2.GaussianBlur(lay, (0, 0), 6)
        return lay + glow*0.9                                # noyau + halo

EMB = Embers()

# ---------------------------------------------------------------------------
# Texte
# ---------------------------------------------------------------------------
def _tw(f, s, tr): return sum((f.getbbox(c)[2]-f.getbbox(c)[0])+tr for c in s)-tr
def text(canvas, s, f, tr, color, y, cx=W/2, alpha=1.0, rise=0):
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    x = cx - _tw(f, s, tr)/2
    for ch in s:
        d.text((x, y-rise), ch, font=f, fill=255); bb = f.getbbox(ch); x += (bb[2]-bb[0])+tr
    m = (np.asarray(im, np.float32)/255.0*alpha)[..., None]
    return canvas*(1-m) + np.array(color, np.float32)*m

def paste(canvas, rgb, a, cx, cy, scale=1.0, alpha=1.0):
    nh, nw = rgb.shape[:2]
    if scale != 1.0:
        nw, nh = max(1, int(nw*scale)), max(1, int(nh*scale))
        rgb = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_CUBIC)
        a = cv2.resize(a, (nw, nh))[..., None] if a.ndim == 3 else cv2.resize(a, (nw, nh))[..., None]
    ox, oy = int(cx-nw/2), int(cy-nh/2)
    x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox+nw), min(H, oy+nh)
    if x1 <= x0 or y1 <= y0: return canvas
    aa = a[y0-oy:y1-oy, x0-ox:x1-ox]*alpha; cc = rgb[y0-oy:y1-oy, x0-ox:x1-ox]
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1]*(1-aa)+cc*aa
    return canvas

# ---------------------------------------------------------------------------
# Grading luxe
# ---------------------------------------------------------------------------
def grade(f):
    n = f/255.0
    lum = (n*np.array([.299,.587,.114],np.float32)).sum(2, keepdims=True)
    n = n + (1-lum)*(NAVY/255.0-0.0)*0.10 + lum*(GOLD/255.0)*0.06   # ombres navy, hautes or
    g = n.mean(2, keepdims=True)
    n = g + (n-g)*0.90                                              # -10% saturation
    n = np.clip((n-0.5)*1.15+0.5, 0, 1)                            # +15% contraste
    return np.clip(n, 0, 1)*255.0

# ---------------------------------------------------------------------------
# Rendu frame
# ---------------------------------------------------------------------------
# vignette forte (radial)
VIG = np.clip((_rad/(W*0.95)), 0, 1)[..., None]**1.7
HALO = np.exp(-(_rad/(W*0.42))**2)[..., None]                       # lueur centrale

def render(fi):
    f = np.ones((H, W, 3), np.float32)*BLACK
    # enveloppe d'intensite des braises
    if fi < 36:   emb_i = 0.40*ease(fi/36)
    elif fi < 90: emb_i = 0.40 + 0.25*ease((fi-36)/54)
    elif fi < 126: emb_i = 0.65 + 0.20*ease((fi-90)/36)
    else:         emb_i = 0.85 + 0.15*ease((fi-126)/24)
    EMB.step()
    emb_layer = EMB.render(fi, emb_i)

    # halo cuivre (des phase 2)
    if fi >= 30:
        hi = ease((fi-30)/40)
        f = f + HALO*COPPER*0.22*hi

    # --- plat (phase 2) ---
    if fi >= 34:
        p2 = ease((fi-34)/(90-34))
        scale = 1.15 - 0.15*p2
        op = p2
        sigma = 20*(1-p2)
        dish = DISH
        if sigma > 0.6:
            dish = cv2.GaussianBlur(dish, (0, 0), sigma)
        dw, dh = int(DISH_W*scale), int(DISH_H*scale)
        dish = cv2.resize(dish, (dw, dh), interpolation=cv2.INTER_CUBIC)
        # bord doux + reveal radial depuis le centre
        canvasd = np.zeros((H, W, 3), np.float32)
        ox, oy = (W-dw)//2, int(_cy-dh/2)
        x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox+dw), min(H, oy+dh)
        canvasd[y0:y1, x0:x1] = dish[y0-oy:y1-oy, x0-ox:x1-ox]
        soft = np.clip(1.0-(_rad/(W*0.58)), 0, 1)[..., None]**1.3      # bord fondu au noir
        reveal_r = (0.15+1.1*p2)*W*0.6
        rmask = np.clip((reveal_r-_rad)/120.0, 0, 1)[..., None]
        a = op*soft*rmask
        f = f*(1-a) + canvasd*a

    # brillance +10% phase 4
    if fi >= 126:
        f = f*(1.0+0.10*ease((fi-126)/24))

    # braises (screen additif)
    f = 1-(1-np.clip(f, 0, 255)/255.0)*(1-np.clip(emb_layer, 0, 255)/255.0)
    f = f*255.0

    # vignette
    f = f*(1-VIG*0.9) + BLACK*(VIG*0.9)

    # --- logo + marque (phase 3) ---
    if fi >= 90:
        p3 = (fi-90)/12.0
        sc = 0.2 + 0.8*eout(min(1, p3))
        al = eout(min(1, (fi-90)/12.0))
        f = paste(f, LOGO_RGB, LOGO_A, W*0.5, H*0.145, scale=sc, alpha=al*0.98)
        f = text(f, "LE PHOENIX", CB(60), 4, GOLD, H*0.205, alpha=eout((fi-96)/12.0), rise=int(12*(1-eout((fi-96)/12.0))))
        f = text(f, "RESTAURANT · BRASSERIE", JR(21), 6, COPPER, H*0.245,
                 alpha=eout((fi-100)/12.0)*0.9, rise=int(8*(1-eout((fi-100)/12.0))))

    # --- texte plat (phase 4) ---
    if fi >= 124:
        a1 = eout((fi-124)/10.0)
        f = text(f, "ENTRECÔTE BLACK ANGUS", CB(50), 2, WHITE, H*0.775, alpha=a1, rise=int(14*(1-a1)))
        f = text(f, "a la piedra", CI(46), 1, GOLD, H*0.815, alpha=eout((fi-128)/10.0), rise=int(10*(1-eout((fi-128)/10.0))))
        p = (fi-132)/10.0
        if p > 0:
            xw = int(70*ease(min(1, p)))
            cv2.line(f, (W//2-xw, int(H*0.862)), (W//2+xw, int(H*0.862)), (COPPER*0.9).tolist(), 1, cv2.LINE_AA)
        f = text(f, "COCINADA A LA PIEDRA  ·  SALSAS CASERAS", JL(19), 3,
                 np.array([204, 187, 170], np.float32), H*0.878, alpha=eout((fi-134)/10.0)*0.85)

    # grade final + leger fondu d'entree
    f = grade(f)
    if fi < 6: f = f*(fi/6.0)
    return np.clip(f, 0, 255)

def main():
    test = "--test" in sys.argv
    os.makedirs(FRAMES, exist_ok=True)
    for old in glob.glob(os.path.join(FRAMES, "*.png")): os.remove(old)
    idxs = [0, 20, 40, 60, 80, 100, 120, 140, 149] if test else range(NF)
    # deterministe : rejouer les particules depuis 0 a chaque frame demandee en test
    global EMB
    if test:
        for n in idxs:
            EMB = Embers()
            for _ in range(n): EMB.step()
            fr = render(n).astype(np.uint8)
            Image.fromarray(fr).save(os.path.join(OUTDIR, "_sc_frames", "test_%03d.png" % n))
            print("test", n)
        return
    for n in range(NF):
        fr = render(n).astype(np.uint8)
        cv2.imwrite(os.path.join(FRAMES, "f_%03d.png" % n), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR),
                    [cv2.IMWRITE_PNG_COMPRESSION, 1])
        if n % 15 == 0: print("frame %d/%d" % (n, NF), flush=True)
    print("done", NF)

if __name__ == "__main__":
    main()
