#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brasserie Phoenix — Reel 3D cinematique (1080x1920 / 30fps / ~25s / H.264).

Pipeline de rendu programmatique pseudo-3D :
  E1 Depth Warp (parallax via cv2.remap)      E5 Motion Blur transitions
  E2 Ken Burns IA-aware (Laplacian saliency)  E6 Vignette navy respirante
  E3 Tilt-Shift cinematique                   E7 Grain cinematique
  E4 Light Leak copper (screen blend)         E8 Text reveal "Forge"

Assets reels : logo phoenix + 3 photos plats (pierre bruante / tartare / salade
gambas) + carte adresse. Le storyboard 8-temps est adapte a ces assets
(reutilisation avec cadrages/effets distincts), logo en ouverture, adresse en
cloture.
"""
import os, sys, math, glob
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------------------
# Constantes / identite visuelle verrouillee
# ----------------------------------------------------------------------------
W, H   = 1080, 1920
FPS    = 30
ROOT   = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(ROOT, "photos")
FONTS  = os.path.join(ROOT, "assets", "fonts")
OUTDIR = os.path.join(ROOT, "output")
FRAMES = os.path.join(OUTDIR, "_frames")

NAVY   = np.array([22, 54, 74],   np.float32)   # #16364A
COPPER = np.array([185, 141, 85], np.float32)   # #B98D55
CREAM  = np.array([246, 240, 228],np.float32)   # #F6F0E4
WARM   = np.array([255, 245, 224],np.float32)   # #FFF5E0 (forge start)
BLACK  = np.array([0, 0, 0],      np.float32)

def F(name):
    return os.path.join(FONTS, name)

FONT = {
    "cormorant_bold": F("Cormorant-Bold.ttf"),
    "cormorant_semi": F("Cormorant-SemiBold.ttf"),
    "cormorant_med":  F("Cormorant-Medium.ttf"),
    "jost_light":     F("Jost-Light.ttf"),
    "jost_reg":       F("Jost-Regular.ttf"),
    "jost_med":       F("Jost-Medium.ttf"),
    "jost_light_it":  F("Jost-LightItalic.ttf"),
}

# ----------------------------------------------------------------------------
# Utilitaires generaux
# ----------------------------------------------------------------------------
def ease(p):                      # ease-in-out (smoothstep)
    p = min(1.0, max(0.0, p))
    return p * p * (3 - 2 * p)

def ease_out_expo(p):
    p = min(1.0, max(0.0, p))
    return 1.0 if p >= 1 else 1 - pow(2, -10 * p)

def cover_fit(img, w, h):
    """Redimensionne + recadre pour remplir (w,h) sans deformation."""
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih)
    nw, nh = int(math.ceil(iw * s)), int(math.ceil(ih * s))
    r = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_CUBIC)
    x0 = (nw - w) // 2
    y0 = (nh - h) // 2
    return r[y0:y0 + h, x0:x0 + w].copy()

def load_photo(path):
    im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB).astype(np.float32)
    return im

# ----------------------------------------------------------------------------
# E2 — detection du sujet (carte de nettete Laplacienne)
# ----------------------------------------------------------------------------
def detect_subject(img):
    g = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    lap = np.abs(cv2.Laplacian(g, cv2.CV_32F, ksize=3))
    sal = cv2.GaussianBlur(lap, (0, 0), 45)
    # combine nettete + luminosite (le sujet des plats est eclaire)
    sal = sal / (sal.max() + 1e-6)
    lum = cv2.GaussianBlur(g.astype(np.float32) / 255.0, (0, 0), 45)
    score = 0.7 * sal + 0.3 * lum
    _, _, _, mx = cv2.minMaxLoc(score)
    cx, cy = mx[0] / img.shape[1], mx[1] / img.shape[0]
    # borne pour eviter des recadrages trop excentres
    cx = min(0.68, max(0.32, cx))
    cy = min(0.66, max(0.34, cy))
    return cx, cy

# ----------------------------------------------------------------------------
# Champs statiques precalcules (vignette, depth, masque tilt-shift)
# ----------------------------------------------------------------------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_nx = (xx - W / 2) / (W / 2)
_ny = (yy - H / 2) / (H / 2)
_r_oval = np.sqrt((_nx * 1.0) ** 2 + (_ny * 0.62) ** 2)      # distance ovale

# E6 vignette navy : 0 au centre -> 1 aux bords
VIGN = np.clip((_r_oval - 0.35) / (1.15 - 0.35), 0, 1) ** 1.35
VIGN = VIGN[..., None]

# E1 depth : 1 au centre (avant-plan) -> 0 aux bords (arriere-plan)
DEPTH = np.clip(1.0 - _r_oval / 1.25, 0, 1)
DEPTH = cv2.GaussianBlur(DEPTH, (0, 0), 60)

# grille de base pour remap depth-warp
MAPX_BASE = xx.copy()
MAPY_BASE = yy.copy()

# E3 masque tilt-shift : bande centrale nette (40% h), flou haut/bas
def _tilt_mask():
    band = 0.40
    top = 0.5 - band / 2
    bot = 0.5 + band / 2
    yn = yy / H
    m = np.ones((H, W), np.float32)
    up = yn < top
    m[up] = np.clip((yn[up] / top), 0, 1) ** 1.3          # 0 en haut -> 1
    dn = yn > bot
    m[dn] = np.clip((1 - yn[dn]) / (1 - bot), 0, 1) ** 1.3  # 1 -> 0 en bas
    m = cv2.GaussianBlur(m, (0, 0), 30)
    return m[..., None]
TILT_SHARP = _tilt_mask()          # 1 = net, 0 = floute

# ----------------------------------------------------------------------------
# Effets frame-par-frame
# ----------------------------------------------------------------------------
def ken_burns(base, zoom, cx, cy):
    """Recadre une fenetre (zoom>=1) centree pres de (cx,cy) puis upscale."""
    bw = W / zoom
    bh = H / zoom
    cxp = cx * W
    cyp = cy * H
    x0 = cxp - bw / 2
    y0 = cyp - bh / 2
    x0 = min(max(0.0, x0), W - bw)
    y0 = min(max(0.0, y0), H - bh)
    x0i, y0i = int(round(x0)), int(round(y0))
    bwi, bhi = int(round(bw)), int(round(bh))
    bwi = min(bwi, W - x0i); bhi = min(bhi, H - y0i)
    crop = base[y0i:y0i + bhi, x0i:x0i + bwi]
    return cv2.resize(crop, (W, H), interpolation=cv2.INTER_CUBIC)

def depth_warp(frame, shift):
    """E1 : avant-plan +shift, arriere-plan -shift/2 (parallax pseudo-3D)."""
    if abs(shift) < 0.05:
        return frame
    disp = shift * (2 * DEPTH - 1.0)          # +shift centre, -shift bords
    mapx = (MAPX_BASE - disp).astype(np.float32)
    return cv2.remap(frame, mapx, MAPY_BASE, interpolation=cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT)

def tilt_shift(frame, smax=13, boost=True):
    """E3 : mise au point selective + saturation/contraste sur bande nette."""
    blurred = cv2.GaussianBlur(frame, (0, 0), smax)
    out = frame * TILT_SHARP + blurred * (1 - TILT_SHARP)
    if boost:
        lum = (out * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
        sat = lum + (out - lum) * 1.15                 # +15% saturation
        con = (sat - 128) * 1.10 + 128                 # +10% contraste
        out = out * (1 - TILT_SHARP) + con * TILT_SHARP
    return out

def make_light_leak(seed, hi=True):
    """E4 : ellipse copper diffuse (blur 80), position pseudo-aleatoire seedee."""
    rng = np.random.RandomState(seed)
    layer = np.zeros((H, W, 3), np.float32)
    cxp = rng.randint(int(W * 0.15), int(W * 0.85))
    cyp = rng.randint(int(H * 0.08), int(H * 0.28)) if hi else \
          rng.randint(int(H * 0.72), int(H * 0.92))
    ax = rng.randint(int(W * 0.30), int(W * 0.55))
    ay = rng.randint(int(H * 0.14), int(H * 0.26))
    ang = rng.randint(0, 180)
    mask = np.zeros((H, W), np.float32)
    cv2.ellipse(mask, (cxp, cyp), (ax, ay), ang, 0, 360, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), 80)
    mask /= (mask.max() + 1e-6)
    for c in range(3):
        layer[..., c] = mask * COPPER[c]
    return layer

def screen_blend(frame, leak, opacity):
    """E4 : blend screen  out = 1-(1-a)(1-b)."""
    if opacity <= 0.001:
        return frame
    a = frame / 255.0
    b = (leak / 255.0) * opacity
    return (1 - (1 - a) * (1 - b)) * 255.0

def vignette(frame, intensity):
    """E6 : vignette navy, intensite passee (respiration geree par l'appelant)."""
    return frame * (1 - VIGN * intensity) + NAVY * (VIGN * intensity)

def add_grain(frame, std, seed):
    """E7 : bruit gaussien organique, std variable +/-2 par frame."""
    rng = np.random.RandomState(seed & 0x7fffffff)
    s = std + rng.uniform(-2, 2)
    noise = rng.normal(0, s, (H, W, 1)).astype(np.float32)
    return frame + noise

def motion_blur(frame, k, horizontal=True):
    """E5 : flou directionnel (kernel 1xk)."""
    k = max(1, int(k))
    if k <= 1:
        return frame
    ker = np.zeros((k, k), np.float32)
    if horizontal:
        ker[k // 2, :] = 1.0 / k
    else:
        ker[:, k // 2] = 1.0 / k
    return cv2.filter2D(frame, -1, ker)

# ----------------------------------------------------------------------------
# E8 — texte "forge" (PIL, tracking, glow copper, reveal color-shift)
# ----------------------------------------------------------------------------
_FONT_CACHE = {}
def get_font(path, size):
    key = (path, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]

def _tracked_size(font, text, tracking):
    if not text:
        return 0, 0
    total = 0
    h = 0
    for ch in text:
        bb = font.getbbox(ch)
        total += (bb[2] - bb[0]) + tracking
        h = max(h, bb[3] - bb[1])
    total -= tracking
    asc, desc = font.getmetrics()
    return total, asc + desc

def render_text_mask(text, font_path, size, tracking):
    """Retourne (mask float 0..1 HxW plein cadre, y_top, y_bottom) centre X."""
    font = get_font(font_path, size)
    tw, th = _tracked_size(font, text, tracking)
    asc, desc = font.getmetrics()
    pad = size
    img = Image.new("L", (tw + 2 * pad, asc + desc + 2 * pad), 0)
    d = ImageDraw.Draw(img)
    x = pad
    for ch in text:
        d.text((x, pad), ch, font=font, fill=255)
        bb = font.getbbox(ch)
        x += (bb[2] - bb[0]) + tracking
    return np.asarray(img, np.float32) / 255.0, tw, (asc + desc)

class TextEl:
    """Element de texte anime facon forge."""
    def __init__(self, text, font_path, size, color, cx=0.5, cy=0.5,
                 tracking=0, start=0.0, dur=0.6, glow=True, max_alpha=1.0,
                 shift_color=True, scrim=False, scrim_k=0.55):
        self.color = np.array(color, np.float32)
        self.start = start
        self.dur = dur
        self.glow = glow
        self.max_alpha = max_alpha
        self.shift_color = shift_color
        self.scrim_k = scrim_k
        mask, tw, thh = render_text_mask(text, font_path, size, tracking)
        self.mh, self.mw = mask.shape
        # position du coin haut-gauche dans le cadre plein
        self.ox = int(round(cx * W - self.mw / 2))
        self.oy = int(round(cy * H - self.mh / 2))
        self.mask = mask
        self.glow_mask = cv2.GaussianBlur(mask, (0, 0), 8) if glow else None
        # scrim : halo sombre navy sous le texte (lisibilite sur photo chargee)
        if scrim:
            k = max(9, size // 3)
            dil = cv2.dilate(mask, np.ones((k, k), np.float32))
            sc = cv2.GaussianBlur(dil, (0, 0), max(14, size * 0.6))
            self.scrim = sc / (sc.max() + 1e-6)
        else:
            self.scrim = None

    def _paste(self, canvas, layer_rgb, alpha):
        x0 = max(0, self.ox); y0 = max(0, self.oy)
        x1 = min(W, self.ox + self.mw); y1 = min(H, self.oy + self.mh)
        if x1 <= x0 or y1 <= y0:
            return
        sx0, sy0 = x0 - self.ox, y0 - self.oy
        a = alpha[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
        rgb = layer_rgb[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
        canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - a) + rgb * a

    def draw(self, canvas, t):
        p = (t - self.start) / self.dur
        if p <= 0:
            return
        e = ease_out_expo(p)
        col = (WARM * (1 - e) + self.color * e) if self.shift_color else self.color
        base_a = min(1.0, e) * self.max_alpha
        H0, W0 = self.mh, self.mw
        if self.scrim is not None:
            sa = (self.scrim * base_a * self.scrim_k)[..., None]
            navy_rgb = np.ones((H0, W0, 3), np.float32) * NAVY
            self._paste(canvas, navy_rgb, sa)
        if self.glow:
            g = (self.glow_mask * base_a * 0.6)[..., None]
            glow_rgb = np.ones((H0, W0, 3), np.float32) * COPPER
            self._paste(canvas, glow_rgb, g)
        a = (self.mask * base_a)[..., None]
        rgb = np.ones((H0, W0, 3), np.float32) * col
        self._paste(canvas, rgb, a)

# ----------------------------------------------------------------------------
# Logo phoenix detoure (fond creme -> transparent)
# ----------------------------------------------------------------------------
def load_logo_rgba(scale_w):
    im = load_photo(os.path.join(PHOTOS, "logo.png"))
    mx = im.max(2); mn = im.min(2)
    val = mx / 255.0
    sat = (mx - mn) / (mx + 1e-6)
    bg = (val > 0.80) & (sat < 0.14)              # creme = clair + peu sature
    fg = np.where(bg, 0, 255).astype(np.uint8)
    # retirer les petites composantes parasites (marques en bord d'image)
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(fg, 8)
    keep = np.zeros_like(fg)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 45:
            keep[lbl == i] = 255
    alpha = (keep.astype(np.float32) / 255.0)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.2)
    ih, iw = im.shape[:2]
    nw = scale_w; nh = int(round(ih * scale_w / iw))
    rgb = cv2.resize(im, (nw, nh), interpolation=cv2.INTER_CUBIC)
    al = cv2.resize(alpha, (nw, nh), interpolation=cv2.INTER_CUBIC)[..., None]
    return rgb, al

def paste_rgba(canvas, rgb, alpha, cx, cy):
    nh, nw = rgb.shape[:2]
    ox = int(round(cx * W - nw / 2)); oy = int(round(cy * H - nh / 2))
    x0 = max(0, ox); y0 = max(0, oy)
    x1 = min(W, ox + nw); y1 = min(H, oy + nh)
    if x1 <= x0 or y1 <= y0:
        return
    sx0, sy0 = x0 - ox, y0 - oy
    a = alpha[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    c = rgb[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - a) + c * a

# ----------------------------------------------------------------------------
# Scenes
# ----------------------------------------------------------------------------
class PhotoScene:
    """Scene basee sur une photo, avec pile d'effets configurable."""
    def __init__(self, img_path, dur, texts=None, *,
                 zoom=(1.0, 1.15), kb_dir=(0, 0), warp_amp=0.0,
                 tilt=False, leak_seed=None, leak_hi=True, leak_max=0.22,
                 grain=6.0, vign=(0.55, 0.75), breathe=True, subject=None):
        base = load_photo(img_path)
        self.base = cover_fit(base, W, H)
        self.dur = dur
        self.texts = texts or []
        self.zoom = zoom
        self.kb_dir = kb_dir
        self.warp_amp = warp_amp
        self.tilt = tilt
        self.leak = make_light_leak(leak_seed, leak_hi) if leak_seed is not None else None
        self.leak_max = leak_max
        self.grain = grain
        self.vign = vign
        self.breathe = breathe
        if subject is None:
            subject = detect_subject(self.base)
        self.cx0, self.cy0 = subject

    def render(self, t):
        p = min(1.0, max(0.0, t / self.dur))
        e = ease(p)
        # E2 Ken Burns IA-aware
        z = self.zoom[0] + (self.zoom[1] - self.zoom[0]) * e
        cx = self.cx0 + self.kb_dir[0] * (e - 0.5)
        cy = self.cy0 + self.kb_dir[1] * (e - 0.5)
        cx = min(0.72, max(0.28, cx)); cy = min(0.72, max(0.28, cy))
        f = ken_burns(self.base, z, cx, cy)
        # E1 Depth warp
        if self.warp_amp:
            f = depth_warp(f, self.warp_amp * math.sin(p * math.pi))
        # E3 Tilt-shift
        if self.tilt:
            f = tilt_shift(f)
        # E4 Light leak (fenetre 1.5s au tiers du clip)
        if self.leak is not None:
            lt = t - self.dur * 0.28
            if 0 <= lt <= 1.5:
                op = math.sin(lt / 1.5 * math.pi) * self.leak_max
                f = screen_blend(f, self.leak, op)
        # E6 Vignette navy respirante (0.8Hz)
        vmin, vmax = self.vign
        vi = (vmin + vmax) / 2
        if self.breathe:
            vi += (vmax - vmin) / 2 * math.sin(2 * math.pi * 0.8 * t)
        f = vignette(f, vi)
        # E7 Grain
        f = add_grain(f, self.grain, int(t * 1000) ^ 0x9e3779b9)
        # E8 Texte
        for te in self.texts:
            te.draw(f, t)
        return np.clip(f, 0, 255)


class LogoScene:
    """Ouverture : logo phoenix sur degrade navy + light leak + titre forge."""
    def __init__(self, dur, texts):
        self.dur = dur
        self.texts = texts
        # fond degrade radial navy
        g = np.clip(1.0 - _r_oval / 1.3, 0, 1)[..., None]
        self.bg = NAVY * (0.55 + 0.45 * g)
        self.logo_rgb, self.logo_a = load_logo_rgba(int(W * 0.42))
        self.leak = make_light_leak(101, hi=True)

    def render(self, t):
        p = min(1.0, max(0.0, t / self.dur))
        f = self.bg.copy()
        # leak copper doux permanent (respiration)
        op = 0.10 + 0.06 * math.sin(2 * math.pi * 0.5 * t)
        f = screen_blend(f, self.leak, op)
        # logo : leger float vertical + fade/scale d'entree
        e = ease(min(1.0, t / 1.0))
        cy = 0.40 + 0.010 * math.sin(2 * math.pi * 0.25 * t)
        rgb = self.logo_rgb
        al = self.logo_a * e
        paste_rgba(f, rgb, al, 0.5, cy)
        f = vignette(f, 0.45)
        f = add_grain(f, 5.0, int(t * 1000) ^ 0x51 )
        for te in self.texts:
            te.draw(f, t)
        return np.clip(f, 0, 255)


class CTAScene:
    """Cloture : cadre navy + bordure copper animee + bloc reservation."""
    def __init__(self, dur, texts):
        self.dur = dur
        self.texts = texts
        self.bg = np.ones((H, W, 3), np.float32) * NAVY
        self.logo_rgb, self.logo_a = load_logo_rgba(int(W * 0.20))
        # rectangle de bordure copper
        self.rx0, self.ry0 = int(W * 0.12), int(H * 0.22)
        self.rx1, self.ry1 = int(W * 0.88), int(H * 0.80)

    def _border(self, f, prog):
        """Trace progressif d'un rectangle copper 2px (sens horaire)."""
        e = ease(prog)
        x0, y0, x1, y1 = self.rx0, self.ry0, self.rx1, self.ry1
        peri = 2 * ((x1 - x0) + (y1 - y0))
        drawn = peri * e
        th = 2
        segs = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
        acc = 0
        for (ax, ay), (bx, by) in segs:
            L = abs(bx - ax) + abs(by - ay)
            if drawn <= acc:
                break
            frac = min(1.0, (drawn - acc) / L)
            ex = int(ax + (bx - ax) * frac); ey = int(ay + (by - ay) * frac)
            cv2.line(f, (ax, ay), (ex, ey), tuple(COPPER.tolist()), th, cv2.LINE_AA)
            acc += L

    def render(self, t):
        f = self.bg.copy()
        # leger halo copper central
        halo = np.clip(1.0 - _r_oval / 0.9, 0, 1)[..., None]
        f = f + halo * COPPER * 0.06
        self._border(f, min(1.0, t / 0.8))
        paste_rgba(f, self.logo_rgb, self.logo_a, 0.5, 0.30)
        f = add_grain(f, 4.0, int(t * 1000) ^ 0x1234)
        for te in self.texts:
            te.draw(f, t)
        # fondu final vers noir (1.2s a partir de dur-1.2)
        fo = (t - (self.dur - 1.2)) / 1.2
        if fo > 0:
            f = f * (1 - min(1.0, fo))
        return np.clip(f, 0, 255)

# ----------------------------------------------------------------------------
# Transitions (straddle : moitie sortante / moitie entrante autour du bord)
# ----------------------------------------------------------------------------
def trans_glide(a, b, q, direction=1):
    """TYPE A — glide cut : motion blur directionnel, switch net a q=0.5."""
    amt = (1 - abs(2 * q - 1)) * 34
    if q < 0.5:
        return motion_blur(a, amt, horizontal=True)
    return motion_blur(b, amt, horizontal=True)

def trans_flash(a, b, q, direction=1):
    """TYPE B — light flash creme (braise)."""
    if q < 0.42:
        k = q / 0.42
        return a + (WARM - a) * (k * 0.85)
    if q > 0.58:
        k = (1 - q) / 0.42
        return b + (WARM - b) * (k * 0.85)
    return np.ones((H, W, 3), np.float32) * WARM

def trans_iris(a, b, q, direction=1):
    """TYPE C — iris navy : disque net de b qui s'ouvre depuis le centre."""
    rmax = math.hypot(W / 2, H / 2)
    r = rmax * ease(q)
    d = np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2)
    m = np.clip((r - d) / 40.0, 0, 1)[..., None]
    # anneau copper sur le front de l'iris
    ring = np.clip(1 - np.abs(d - r) / 6.0, 0, 1)[..., None]
    out = a * (1 - m) + b * m
    out = out + ring * COPPER * 0.5 * (1 - q)
    return out

# ----------------------------------------------------------------------------
# Construction du storyboard
# ----------------------------------------------------------------------------
def cap(text, font, size, color, cy=0.88, cx=0.5, start=0.4, tracking=2,
        glow=False, max_alpha=0.92, shift=False, scrim=True):
    """Raccourci micro-caption."""
    return TextEl(text, FONT[font], size, color, cx=cx, cy=cy, tracking=tracking,
                  start=start, dur=0.6, glow=glow, max_alpha=max_alpha,
                  shift_color=shift, scrim=scrim)

def build_timeline():
    P = lambda n: os.path.join(PHOTOS, n)

    # --- LOGO / HOOK ---
    logo = LogoScene(2.8, [
        TextEl("Brasserie Phoenix", FONT["cormorant_bold"], 88, COPPER,
               cx=0.5, cy=0.66, tracking=10, start=0.7, dur=0.7),
        TextEl("Pierres brûlantes  ·  Pâtes maison  ·  Âme belge",
               FONT["jost_light"], 27, CREAM, cx=0.5, cy=0.74, tracking=2,
               start=1.3, dur=0.6, glow=False, max_alpha=0.92, shift_color=False),
    ])

    # --- 1. PLATEAU PIERRE CHAUDE (plan large) / DESIR ---
    s1 = PhotoScene(P("01_spread.jpg"), 2.8, [
        cap("Torrevieja  ·  Orihuela Costa", "jost_light", 30, CREAM,
            cy=0.90, start=0.5, tracking=1)],
        zoom=(1.0, 1.10), kb_dir=(0.04, 0.03), warp_amp=6.0, tilt=False,
        leak_seed=1, leak_hi=True, leak_max=0.22, grain=6)

    # --- 2. SPAGHETTI BURRATA / PATES MAISON ---
    s2 = PhotoScene(P("02_burrata_pasta.jpg"), 2.5, [
        cap("Pâtes maison", "cormorant_semi", 46, COPPER, cy=0.89, start=0.35)],
        zoom=(1.02, 1.16), kb_dir=(-0.04, 0.03), warp_amp=0.0, tilt=True,
        leak_seed=None, grain=6)

    # --- 3. CALAMAR GRILLE / MER ---
    s3 = PhotoScene(P("03_squid.jpg"), 2.5, [
        cap("Produits de la mer", "jost_light", 30, CREAM, cy=0.90, start=0.3)],
        zoom=(1.16, 1.02), kb_dir=(0.05, -0.03), warp_amp=5.0, tilt=False,
        leak_seed=3, leak_hi=True, leak_max=0.2, grain=7)

    # --- 4. BURGER BURRATA / SIGNATURE ---
    s4 = PhotoScene(P("04_burger.jpg"), 2.5, [
        cap("Fait maison", "jost_med", 30, COPPER, cy=0.90, start=0.3)],
        zoom=(1.0, 1.14), kb_dir=(-0.05, 0.02), warp_amp=6.0, tilt=False,
        leak_seed=None, grain=7)

    # --- 5. PAIN / SALSA / AIOLI — A PARTAGER ---
    s5 = PhotoScene(P("05_bread.jpg"), 2.5, [
        cap("À partager", "jost_light_it", 32, CREAM, cy=0.90, start=0.3)],
        zoom=(1.14, 1.02), kb_dir=(0.04, 0.03), warp_amp=0.0, tilt=True,
        leak_seed=5, leak_hi=False, leak_max=0.2, grain=8)

    # --- 6. TARTARE / L'ART DU CRU ---
    s6 = PhotoScene(P("06_tartare.jpg"), 2.6, [
        cap("L'art du cru", "cormorant_med", 46, CREAM, cy=0.89, start=0.35)],
        zoom=(1.02, 1.15), kb_dir=(0.04, -0.03), warp_amp=4.0, tilt=False,
        leak_seed=None, grain=6)

    # --- 7. STEAK PIERRE 900°C (gros plan) / CLIMAX ---
    s7 = PhotoScene(P("07_steak.jpg"), 3.4, [
        TextEl("Pierres brûlantes.", FONT["cormorant_semi"], 62, COPPER,
               cx=0.5, cy=0.40, tracking=4, start=0.3, dur=0.6, scrim=True),
        TextEl("Pâtes maison.", FONT["cormorant_semi"], 62, COPPER,
               cx=0.5, cy=0.50, tracking=4, start=0.7, dur=0.6, scrim=True),
        TextEl("Âme belge.", FONT["cormorant_semi"], 62, CREAM,
               cx=0.5, cy=0.60, tracking=4, start=1.1, dur=0.6, scrim=True),
    ], zoom=(1.0, 1.20), kb_dir=(-0.03, 0.04), warp_amp=9.0, tilt=False,
        leak_seed=7, leak_hi=True, leak_max=0.35, grain=7,
        subject=(0.60, 0.66), vign=(0.6, 0.8))

    # --- 8. ESPRESSO MARTINI / DOUCEUR ---
    s8 = PhotoScene(P("08_martini.jpg"), 2.8, [
        TextEl("Une table vous attend.", FONT["cormorant_med"], 60, CREAM,
               cx=0.5, cy=0.85, tracking=3, start=0.4, dur=0.7, glow=True, scrim=True),
    ], zoom=(1.12, 1.02), kb_dir=(0.02, -0.03), warp_amp=4.0, tilt=False,
        leak_seed=None, grain=7, vign=(0.58, 0.8))

    # --- CTA ---
    cta = CTAScene(4.8, [
        TextEl("Réservez votre table", FONT["cormorant_bold"], 70, COPPER,
               cx=0.5, cy=0.45, tracking=6, start=0.5, dur=0.7),
        TextEl("Jeudi  ›  Lundi  ·  Midi & Soir", FONT["jost_reg"], 30, CREAM,
               cx=0.5, cy=0.545, tracking=2, start=0.9, dur=0.6,
               glow=False, shift_color=False),
        TextEl("Av. Desiderio Rodríguez 37  ·  Torrevieja", FONT["jost_light"], 25,
               CREAM, cx=0.5, cy=0.62, tracking=1, start=1.2, dur=0.6,
               glow=False, max_alpha=0.78, shift_color=False),
        TextEl("(+34) 744 622 975", FONT["jost_light"], 25, COPPER,
               cx=0.5, cy=0.675, tracking=2, start=1.45, dur=0.6,
               glow=False, max_alpha=0.9, shift_color=False),
    ])

    scenes = [logo, s1, s2, s3, s4, s5, s6, s7, s8, cta]
    # 9 transitions (type, duree, direction) : glide/flash alternes, iris aux bornes
    trans = [
        (trans_iris,  0.5,  1),   # logo -> 1
        (trans_glide, 0.4,  1),   # 1 -> 2
        (trans_flash, 0.3,  1),   # 2 -> 3
        (trans_glide, 0.4, -1),   # 3 -> 4
        (trans_flash, 0.3,  1),   # 4 -> 5
        (trans_glide, 0.4,  1),   # 5 -> 6
        (trans_flash, 0.3,  1),   # 6 -> 7
        (trans_iris,  0.5,  1),   # 7 -> 8
        (trans_iris,  0.5,  1),   # 8 -> CTA
    ]
    return scenes, trans

# ----------------------------------------------------------------------------
# Rendu du timeline -> frame(t global)
# ----------------------------------------------------------------------------
class Timeline:
    def __init__(self, scenes, trans):
        self.scenes = scenes
        self.trans = trans
        self.starts = []
        acc = 0.0
        for s in scenes:
            self.starts.append(acc)
            acc += s.dur
        self.total = acc

    def frame(self, t):
        # detecter fenetre de transition
        for i in range(len(self.scenes) - 1):
            fn, td, dirn = self.trans[i]
            tb = self.starts[i + 1]        # bord = debut scene i+1
            if tb - td / 2 <= t < tb + td / 2:
                a = self.scenes[i].render(t - self.starts[i])
                b = self.scenes[i + 1].render(t - self.starts[i + 1])
                q = (t - (tb - td / 2)) / td
                return np.clip(fn(a, b, q, dirn), 0, 255)
        # sinon scene courante
        idx = 0
        for i, st in enumerate(self.starts):
            if t >= st:
                idx = i
        return self.scenes[idx].render(t - self.starts[idx])

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    preview = "--preview" in sys.argv
    scenes, trans = build_timeline()
    tl = Timeline(scenes, trans)
    print("Duree timeline : %.2fs  (%d frames @ %dfps)" %
          (tl.total, int(round(tl.total * FPS)), FPS))

    if preview:
        os.makedirs(os.path.join(OUTDIR, "_preview"), exist_ok=True)
        # instants representatifs (incluant transitions)
        times = [1.2, 4.2, 6.8, 9.3, 11.8, 14.3, 16.8, 20.0, 22.8, 26.5]
        for k, t in enumerate(times):
            t = min(t, tl.total - 0.01)
            fr = tl.frame(t).astype(np.uint8)
            Image.fromarray(fr).save(
                os.path.join(OUTDIR, "_preview", "t_%05.2f.png" % t))
            print("  preview t=%.2fs" % t)
        print("Preview ecrit dans output/_preview/")
        return

    # rendu complet -> PNG frames
    os.makedirs(FRAMES, exist_ok=True)
    for old in glob.glob(os.path.join(FRAMES, "*.png")):
        os.remove(old)
    nframes = int(round(tl.total * FPS))
    for n in range(nframes):
        t = n / FPS
        fr = tl.frame(t).astype(np.uint8)
        cv2.imwrite(os.path.join(FRAMES, "f_%05d.png" % n),
                    cv2.cvtColor(fr, cv2.COLOR_RGB2BGR),
                    [cv2.IMWRITE_PNG_COMPRESSION, 1])
        if n % 30 == 0:
            print("  frame %d/%d (t=%.1fs)" % (n, nframes, t), flush=True)
    print("Frames rendues : %d" % nframes)

if __name__ == "__main__":
    main()
