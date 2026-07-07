#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONCEPT — nouvelle direction "film editorial".
On joue avec les FORMES (ronds des assiettes/verre), le VIDE et la TYPO.
Aucun effet gadget : composition, cercles, match-cut, grade sobre, grain fin.
Rend 4 images-concept dans output/_concept/.
"""
import os, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
ROOT = os.path.dirname(os.path.abspath(__file__))
PH = os.path.join(ROOT, "photos"); FT = os.path.join(ROOT, "assets", "fonts")
NAVY = np.array([16, 32, 44], np.float32)
NAVY2 = np.array([26, 52, 70], np.float32)
COPPER = np.array([185, 141, 85], np.float32)
COPPER_HI = np.array([206, 165, 106], np.float32)
CREAM = np.array([243, 237, 226], np.float32)

def font(name, sz): return ImageFont.truetype(os.path.join(FT, name), sz)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def cover_square(img, size):
    ih, iw = img.shape[:2]; s = size/min(ih, iw)
    r = cv2.resize(img, (int(math.ceil(iw*s)), int(math.ceil(ih*s))), interpolation=cv2.INTER_CUBIC)
    y0 = (r.shape[0]-size)//2; x0 = (r.shape[1]-size)//2
    return r[y0:y0+size, x0:x0+size]

def cover_fit(img, w, h):
    ih, iw = img.shape[:2]; s = max(w/iw, h/ih)
    r = cv2.resize(img, (int(math.ceil(iw*s)), int(math.ceil(ih*s))), interpolation=cv2.INTER_CUBIC)
    y0 = (r.shape[0]-h)//2; x0 = (r.shape[1]-w)//2
    return r[y0:y0+h, x0:x0+w]

def load(name): return cv2.cvtColor(cv2.imread(os.path.join(PH, name)), cv2.COLOR_BGR2RGB).astype(np.float32)

def grade(f):
    """Grade cinema sobre : split-tone doux + courbe S + leger halo. Pas de gadget."""
    n = f/255.0
    lum = (n*np.array([.299,.587,.114],np.float32)).sum(2,keepdims=True)
    n = n + (1-lum)*np.array([-.02,.008,.035],np.float32) + lum*np.array([.035,.014,-.02],np.float32)
    n = np.clip(n,0,1); n = np.clip((n-0.5)*1.08+0.5,0,1)
    return n*255.0

def grain(f, s=4.0):
    return f + np.random.RandomState(7).normal(0, s, (H, W, 1)).astype(np.float32)

def bg_field():
    g = np.clip(1.0 - np.sqrt(((xx-W/2)/(W*0.75))**2 + ((yy-H*0.42)/(H*0.7))**2), 0, 1)[..., None]
    return NAVY + (NAVY2-NAVY)*g

def disc(canvas, img_sq, cx, cy, R, ring=True, feather=2.5):
    """Depose une image circulaire (rond d'assiette) avec anneau copper fin."""
    d = np.sqrt((xx-cx)**2 + (yy-cy)**2)
    a = np.clip((R - d)/feather, 0, 1)[..., None]
    size = 2*R
    big = np.zeros((H, W, 3), np.float32)
    y0, x0 = int(cy-R), int(cx-R)
    sq = cv2.resize(img_sq, (size, size), interpolation=cv2.INTER_CUBIC)
    yy0, xx0 = max(0,y0), max(0,x0); yy1, xx1 = min(H,y0+size), min(W,x0+size)
    big[yy0:yy1, xx0:xx1] = sq[yy0-y0:yy1-y0, xx0-x0:xx1-x0]
    out = canvas*(1-a) + big*a
    if ring:
        rr = np.clip(1-np.abs(d-R)/1.6, 0, 1)[..., None]
        out = out*(1-rr) + COPPER*rr
    return out

def tracked(draw, xy, text, fnt, tr, fill):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        bb = fnt.getbbox(ch); x += (bb[2]-bb[0]) + tr
    return x

def text_w(fnt, text, tr):
    return sum((fnt.getbbox(c)[2]-fnt.getbbox(c)[0])+tr for c in text) - tr

def draw_text(canvas, text, fnt, tr, color, cx=None, x=None, y=0, alpha=1.0):
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    w = text_w(fnt, text, tr)
    sx = (W-w)/2 if cx is None else (cx - w/2 if x is None else x)
    tracked(d, (sx, y), text, fnt, tr, 255)
    m = (np.asarray(im, np.float32)/255.0*alpha)[..., None]
    return canvas*(1-m) + np.array(color, np.float32)*m

def logo_rgba(scale_w):
    im = load("logo.png"); mx = im.max(2); mn = im.min(2)
    bg = (mx/255.0 > 0.80) & ((mx-mn)/(mx+1e-6) < 0.14)
    fgm = np.where(bg, 0, 255).astype(np.uint8)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(fgm, 8)
    keep = np.zeros_like(fgm)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 45: keep[lbl == i] = 255
    al = cv2.GaussianBlur(keep.astype(np.float32)/255.0, (0, 0), 1.2)
    ih, iw = im.shape[:2]; nw = scale_w; nh = int(ih*scale_w/iw)
    return cv2.resize(im, (nw, nh), interpolation=cv2.INTER_CUBIC), cv2.resize(al, (nw, nh))[..., None]

def paste(canvas, rgb, a, cx, cy):
    nh, nw = rgb.shape[:2]; ox = int(cx-nw/2); oy = int(cy-nh/2)
    x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox+nw), min(H, oy+nh)
    aa = a[y0-oy:y1-oy, x0-ox:x1-ox]; cc = rgb[y0-oy:y1-oy, x0-ox:x1-ox]
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1]*(1-aa) + cc*aa

# ---- fonts ----
CORM_B = lambda s: font("Cormorant-Bold.ttf", s)
CORM_M = lambda s: font("Cormorant-Medium.ttf", s)
CORM_S = lambda s: font("Cormorant-SemiBold.ttf", s)
JOST_L = lambda s: font("Jost-Light.ttf", s)
JOST_M = lambda s: font("Jost-Medium.ttf", s)

def frame_title():
    f = bg_field()
    rgb, a = logo_rgba(int(W*0.30))
    paste(f, rgb, a*0.95, W/2, H*0.34)
    f = grade(f)
    f = draw_text(f, "BRASSERIE", CORM_B(120), 6, CREAM, y=H*0.44)
    f = draw_text(f, "PHOENIX", CORM_B(120), 24, COPPER, y=H*0.51)
    # filet + baseline
    cv2.line(f, (int(W*0.38), int(H*0.605)), (int(W*0.62), int(H*0.605)), tuple(COPPER.tolist()), 1, cv2.LINE_AA)
    f = draw_text(f, "PIERRES BRÛLANTES   ·   PÂTES MAISON   ·   ÂME BELGE",
                  JOST_L(24), 6, CREAM, y=H*0.625, alpha=0.8)
    return grain(f)

def frame_course():
    """Layout editorial : grand rond (assiette) + numero + nom + vide."""
    f = bg_field()
    dish = cover_square(load("02_burrata_pasta.jpg"), 760)
    dish = grade(dish)
    R = int(W*0.40)
    f = disc(f, dish, W*0.54, H*0.36, R)
    # bloc typo en bas, aligne a gauche avec du vide
    lx = W*0.12
    f = draw_text(f, "II", CORM_S(96), 0, COPPER, cx=lx+30, x=lx, y=H*0.66)
    f = draw_text(f, "Pâtes maison", CORM_M(78), 2, CREAM, cx=lx+300, x=lx, y=H*0.745)
    cv2.line(f, (int(lx)+2, int(H*0.845)), (int(lx)+90, int(H*0.845)), tuple(COPPER.tolist()), 2, cv2.LINE_AA)
    f = draw_text(f, "BURRATA  ·  BASILIC  ·  POIVRE", JOST_L(24), 5, CREAM, cx=lx+240, x=lx, y=H*0.862, alpha=0.75)
    return grain(f)

def frame_bleed():
    """Plein cadre cinema, vignette, typo minimale bas."""
    f = cover_fit(load("07_steak.jpg"), W, H)
    f = grade(f)
    d = np.sqrt(((xx-W/2)/(W*0.62))**2 + ((yy-H*0.5)/(H*0.62))**2)
    vig = np.clip((d-0.4)/0.75, 0, 1)[..., None]**1.4
    f = f*(1-vig*0.85) + NAVY*(vig*0.85)
    # scrim bas
    grad = np.clip((yy/H-0.62)/0.38, 0, 1)[..., None]
    f = f*(1-grad*0.6) + NAVY*(grad*0.6)
    f = draw_text(f, "VII", CORM_S(60), 0, COPPER, cx=W*0.5, y=H*0.80)
    f = draw_text(f, "Pierres brûlantes.", CORM_M(76), 2, CREAM, cx=W*0.5, y=H*0.845)
    return grain(f)

def frame_cta():
    f = bg_field()
    dish = cover_square(load("08_martini.jpg"), 620)
    dish = grade(dish)
    f = disc(f, dish, W*0.5, H*0.30, int(W*0.30))
    f = grade(f) if False else f
    f = draw_text(f, "RÉSERVEZ", JOST_M(30), 10, COPPER, y=H*0.52)
    f = draw_text(f, "votre table", CORM_M(92), 2, CREAM, y=H*0.555)
    cv2.line(f, (int(W*0.40), int(H*0.70)), (int(W*0.60), int(H*0.70)), tuple(COPPER.tolist()), 1, cv2.LINE_AA)
    f = draw_text(f, "JEUDI — LUNDI   ·   MIDI & SOIR", JOST_L(24), 5, CREAM, y=H*0.715, alpha=0.85)
    f = draw_text(f, "Av. Desiderio Rodríguez 37 · Torrevieja", JOST_L(23), 2, CREAM, y=H*0.755, alpha=0.6)
    return grain(f)

def main():
    out = os.path.join(ROOT, "output", "_concept"); os.makedirs(out, exist_ok=True)
    for name, fn in [("1_title", frame_title), ("2_course", frame_course),
                     ("3_bleed", frame_bleed), ("4_cta", frame_cta)]:
        img = np.clip(fn(), 0, 255).astype(np.uint8)
        Image.fromarray(img).save(os.path.join(out, name+".png"))
        print("wrote", name)

if __name__ == "__main__":
    main()
