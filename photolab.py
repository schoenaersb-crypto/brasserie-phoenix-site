#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
photolab — analyse & separation d'elements par photo (base de la 2.5D).

Pour chaque plat :
  · masque du SUJET (dish) via GrabCut + plus grande composante + feather
  · ARRIERE-PLAN reconstruit (inpainting) -> permet une vraie parallaxe
  · carte de PROFONDEUR (sujet net/clair = proche ; bords sombres/flous = loin)
  · POINTS CHAUDS (bougies / braises) pour le scintillement
  · zones SPECULAIRES (sauces, verre) pour les reflets qui balaient

Sortie __main__ : output/_analysis/_sheet.png (QA visuel des couches).
"""
import os, numpy as np, cv2

W, H = 1080, 1920
ROOT = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(ROOT, "photos")

def cover_fit(img, w=W, h=H):
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih)
    r = cv2.resize(img, (int(np.ceil(iw*s)), int(np.ceil(ih*s))), interpolation=cv2.INTER_CUBIC)
    x0 = (r.shape[1]-w)//2; y0 = (r.shape[0]-h)//2
    return r[y0:y0+h, x0:x0+w].copy()

def load(path):
    return cover_fit(cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB))

def _largest_cc(mask):
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    if n <= 1:
        return mask
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return (lbl == big).astype(np.uint8)

def subject_mask(rgb):
    """GrabCut seede par un rectangle central ; fallback saillance si echec."""
    h, w = rgb.shape[:2]
    rect = (int(w*0.10), int(h*0.14), int(w*0.80), int(h*0.72))
    mask = np.zeros((h, w), np.uint8)
    bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(rgb.astype(np.uint8), mask, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
        m = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype(np.uint8)
        m = _largest_cc(m)
    except Exception:
        m = np.zeros((h, w), np.uint8)
    frac = m.mean()
    if frac < 0.06 or frac > 0.93:                     # fallback : saillance + luminosite
        g = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        sal = cv2.GaussianBlur(np.abs(cv2.Laplacian(g, cv2.CV_32F, 3)), (0, 0), 25)
        lum = cv2.GaussianBlur(g.astype(np.float32), (0, 0), 25)
        score = sal/ (sal.max()+1e-6)*0.6 + lum/255.0*0.4
        m = (score > np.percentile(score, 62)).astype(np.uint8)
        m = _largest_cc(m)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), 6)   # feather 0..1

def depth_map(rgb, fg):
    """Profondeur pseudo-3D 0(loin)..1(proche)."""
    g = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    sal = cv2.GaussianBlur(np.abs(cv2.Laplacian(g, cv2.CV_32F, 3)), (0, 0), 35)
    sal /= (sal.max()+1e-6)
    lum = cv2.GaussianBlur(g, (0, 0), 35)/255.0
    yy = np.linspace(0, 1, rgb.shape[0])[:, None]      # bas = plus proche (assiette)
    vert = np.repeat(yy, rgb.shape[1], 1)
    d = 0.50*fg + 0.20*sal + 0.18*lum + 0.12*vert
    d = cv2.GaussianBlur(d, (0, 0), 25)
    return (d - d.min())/(d.max()-d.min()+1e-6)

def hotspots(rgb):
    """Bougies/braises : petits blobs chauds & brillants."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = 0.299*r+0.587*g+0.114*b
    warm = (r > 165) & (r.astype(int)-b.astype(int) > 35) & (lum > 155)
    warm = cv2.morphologyEx(warm.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lbl, stats, cent = cv2.connectedComponentsWithStats(warm, 8)
    spots = []
    for i in range(1, n):
        a = stats[i, cv2.CC_STAT_AREA]
        if 12 <= a <= 6000:
            cx, cy = cent[i]
            rad = max(6, (stats[i, cv2.CC_STAT_WIDTH]+stats[i, cv2.CC_STAT_HEIGHT])/3)
            spots.append((float(cx), float(cy), float(rad)))
    spots.sort(key=lambda s: -s[2])
    return spots[:8]

def specular(rgb):
    """Reflets (sauce/verre) : tres brillant, faible saturation locale."""
    hsv = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2HSV)
    v = hsv[..., 2].astype(np.float32)/255.0
    spec = np.clip((v-0.80)/0.20, 0, 1)
    return cv2.GaussianBlur(spec, (0, 0), 4)

def steam_origin(fg):
    """Point d'emission de la vapeur = haut-centre du sujet."""
    ys, xs = np.where(fg > 0.5)
    if len(xs) == 0:
        return W/2, H*0.45
    cx = float(np.median(xs))
    cy = float(np.percentile(ys, 18))                  # haut du plat
    return cx, cy

def analyze(path):
    rgb = load(path).astype(np.float32)
    fg = subject_mask(rgb)
    depth = depth_map(rgb, fg)
    fgd = cv2.dilate((fg > 0.4).astype(np.uint8), np.ones((15, 15), np.uint8))
    bg_plate = cv2.inpaint(rgb.astype(np.uint8), fgd, 9, cv2.INPAINT_TELEA).astype(np.float32)
    bg_plate = cv2.GaussianBlur(bg_plate, (0, 0), 2.0)     # attenue les stries d'inpaint
    return dict(rgb=rgb, fg=fg, depth=depth, bg=bg_plate,
                hot=hotspots(rgb), spec=specular(rgb),
                steam=np.array(steam_origin(fg), np.float32))

_CACHE = {}
def analyze_cached(path):
    """Analyse mise en cache disque (.npz) — GrabCut ne tourne qu'une fois."""
    if path in _CACHE:
        return _CACHE[path]
    cdir = os.path.join(ROOT, "output", "_analysis"); os.makedirs(cdir, exist_ok=True)
    cf = os.path.join(cdir, os.path.basename(path) + ".npz")
    if os.path.exists(cf):
        z = np.load(cf, allow_pickle=True)
        a = dict(rgb=z["rgb"], fg=z["fg"], depth=z["depth"], bg=z["bg"],
                 hot=[tuple(x) for x in z["hot"]], spec=z["spec"], steam=z["steam"])
    else:
        a = analyze(path)
        np.savez_compressed(cf, rgb=a["rgb"], fg=a["fg"], depth=a["depth"], bg=a["bg"],
                            hot=np.array(a["hot"], np.float32) if a["hot"] else np.zeros((0, 3), np.float32),
                            spec=a["spec"], steam=a["steam"])
    _CACHE[path] = a
    return a

# ---------------------------------------------------------------------------
PHOTO_FILES = ["01_spread.jpg", "02_burrata_pasta.jpg", "03_squid.jpg",
               "04_burger.jpg", "05_bread.jpg", "06_tartare.jpg",
               "07_steak.jpg", "08_martini.jpg"]

def _viz(a):
    """4 vignettes : original+hotspots / masque sujet / profondeur / bg reconstruit."""
    rgb = a["rgb"].astype(np.uint8).copy()
    for cx, cy, rad in a["hot"]:
        cv2.circle(rgb, (int(cx), int(cy)), int(rad)+6, (255, 90, 40), 3)
    cx, cy = a["steam"]; cv2.circle(rgb, (int(cx), int(cy)), 14, (120, 220, 255), 3)
    fg = cv2.cvtColor((a["fg"]*255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
    dh = cv2.applyColorMap((a["depth"]*255).astype(np.uint8), cv2.COLORMAP_INFERNO)
    dh = cv2.cvtColor(dh, cv2.COLOR_BGR2RGB)
    bg = a["bg"].astype(np.uint8)
    tiles = [rgb, fg, dh, bg]
    th = 300; tw = int(th*W/H)
    return [cv2.resize(t, (tw, th)) for t in tiles]

def main():
    from PIL import Image, ImageDraw
    outdir = os.path.join(ROOT, "output", "_analysis"); os.makedirs(outdir, exist_ok=True)
    rows = []
    labels = ["original + points chauds", "sujet (GrabCut)", "profondeur", "arriere-plan reconstruit"]
    for f in PHOTO_FILES:
        a = analyze(os.path.join(PHOTOS, f))
        tiles = _viz(a)
        print("%-22s fg=%.0f%% hotspots=%d steam@(%.0f,%.0f)" %
              (f, a["fg"].mean()*100, len(a["hot"]), a["steam"][0], a["steam"][1]))
        rows.append((f, tiles))
    tw, th = rows[0][1][0].shape[1], rows[0][1][0].shape[0]
    pad = 30; lblh = 26
    sheet = Image.new("RGB", (tw*4 + pad*5, (th+lblh)*len(rows) + pad + 30), (14, 20, 26))
    d = ImageDraw.Draw(sheet)
    for c, lab in enumerate(labels):
        d.text((pad + c*(tw+pad), 8), lab, fill=(210, 170, 110))
    for r, (name, tiles) in enumerate(rows):
        y = 30 + r*(th+lblh) + pad
        d.text((pad, y-2), name, fill=(200, 200, 190))
        for c, t in enumerate(tiles):
            sheet.paste(Image.fromarray(t), (pad + c*(tw+pad), y+lblh-8))
    p = os.path.join(outdir, "_sheet.png"); sheet.save(p)
    print("QA ->", p)

if __name__ == "__main__":
    main()
