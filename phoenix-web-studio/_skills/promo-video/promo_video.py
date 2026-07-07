#!/usr/bin/env python3
"""
promo_video.py — génère une vidéo promo (mp4 H.264) pour un commerce/restaurant,
dans un ou plusieurs formats (9:16 Reels, 1:1 feed, 16:9 web), à partir de photos
et d'infos de marque. Pipeline « façon Remotion » : frames composées en Pillow
(Ken Burns + fondus enchaînés + typographie de marque + étalonnage chaud + carte
de fin), puis encodage mp4 via ffmpeg (imageio-ffmpeg).

Usage :
  pip install Pillow imageio-ffmpeg
  python3 promo_video.py config.json

Le config.json décrit la marque, les couleurs, les polices, les photos et les
formats de sortie (voir example-config.json).
"""
import os, math, sys, json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops

CFG = json.load(open(sys.argv[1], encoding="utf-8"))
FONT_DIR = CFG["font_dir"]
FPS = CFG.get("fps", 30); D = CFG.get("scene_dur", 3.4); X = CFG.get("xfade", 0.5)
COL = {k: tuple(v) for k, v in CFG["colors"].items()}   # creme/accent/dark/grey
OUT = CFG["out_dir"]; os.makedirs(OUT, exist_ok=True)
ZMAX = 1.20

def smooth(p): return p*p*(3-2*p)
def rise(lt, st=0.0, du=0.7): return smooth(max(0.0, min(1.0, (lt-st)/du)))


class Renderer:
    def __init__(self, W, H):
        self.W, self.H, self.K = W, H, H/1920.0
        self.VIGN = self._vignette()
        self.SCRIM = self._scrim(int(H*0.4))
        sz = (int(W*ZMAX), int(H*ZMAX))
        self.hero = self._cover(CFG["hero"], sz)
        self.photos = [(self._cover(p[0], sz), p[1], p[2] == "in") for p in CFG["photos"]]

    def _f(self, key, s):
        return ImageFont.truetype(os.path.join(FONT_DIR, CFG["fonts"][key]), max(10, int(s*self.K)))

    def _vignette(self):
        W, H = self.W, self.H
        m = Image.new("L", (W, H), 0); px = m.load(); cx, cy = W/2, H/2; md = math.hypot(cx, cy)
        for y in range(H):
            for x in range(W):
                d = math.hypot(x-cx, y-cy)/md
                px[x, y] = max(0, min(255, 255-int(150*max(0.0, (d-0.45)/0.55)**1.6)))
        return Image.merge("RGB", (m, m, m))

    def _scrim(self, hgt, amax=170):
        W, H = self.W, self.H
        g = Image.new("L", (1, hgt))
        for y in range(hgt): g.putpixel((0, y), int(amax*(y/hgt)**1.4))
        g = g.resize((W, hgt)); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        blk = Image.new("RGBA", (W, hgt), (8, 20, 28, 255)); blk.putalpha(g)
        lay.paste(blk, (0, H-hgt), blk); return lay

    def _cover(self, path, size):
        im = Image.open(path).convert("RGB"); tw, th = size; iw, ih = im.size
        s = max(tw/iw, th/ih); im = im.resize((int(iw*s+1), int(ih*s+1)), Image.LANCZOS)
        iw, ih = im.size
        return im.crop(((iw-tw)//2, (ih-th)//2, (iw-tw)//2+tw, (ih-th)//2+th))

    def grade(self, im):
        im = ImageEnhance.Color(im).enhance(1.14); im = ImageEnhance.Contrast(im).enhance(1.07)
        im = ImageEnhance.Brightness(im).enhance(1.02)
        warm = Image.new("RGB", im.size, (255, 232, 200))
        im = Image.blend(im, ImageChops.multiply(im, warm), 0.12)
        return ImageChops.multiply(im, self.VIGN)

    def kenburns(self, cov, p, zin):
        W, H = self.W, self.H; cw, ch = cov.size; q = smooth(p if zin else 1-p)
        ww = int(cw-(cw-W)*q); hh = int(ch-(ch-H)*q); drift = int((cw-W)*0.15)
        dx = int((p-0.5)*drift); dy = int((p-0.5)*drift*0.4)
        cx = max(0, min(cw-ww, (cw-ww)//2+dx)); cy = max(0, min(ch-hh, (ch-hh)//2+dy))
        return cov.crop((cx, cy, cx+ww, cy+hh)).resize((W, H), Image.LANCZOS)

    def text(self, base, s, fnt, yf, fill, alpha=255, track=0):
        if track: s = (" "*track).join(list(s))
        W, H = self.W, self.H
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        bb = d.textbbox((0, 0), s, font=fnt); tw = bb[2]-bb[0]
        xx = (W-tw)//2-bb[0]; y = int(yf*H)
        d.text((xx+2, y+3), s, font=fnt, fill=(0, 0, 0, int(0.55*alpha)))
        d.text((xx, y), s, font=fnt, fill=fill+(alpha,)); base.alpha_composite(lay)

    # ---- scènes ----
    def scene_title(self, lt):
        b = CFG["brand"]
        base = self.grade(self.kenburns(self.hero, lt/D, True)).convert("RGBA")
        base.alpha_composite(Image.new("RGBA", (self.W, self.H), (8, 18, 26, 90)))
        a = rise(lt, 0.15, 0.9); A = int(255*a); dy = (1-a)*0.012
        if b.get("place"): self.text(base, b["place"], self._f("sans_reg", 30), 0.292-dy, COL["accent"], A, track=1)
        self.text(base, b["line1"], self._f("serif_bold", 150), 0.330-dy, COL["creme"], A)
        if b.get("line2"): self.text(base, b["line2"], self._f("serif_bold", 150), 0.415-dy, COL["creme"], A)
        a2 = rise(lt, 0.5, 0.9); A2 = int(255*a2); dy2 = (1-a2)*0.01
        sl = b.get("slogan", [])
        for i, line in enumerate(sl):
            self.text(base, line, self._f("serif_italic", 56), 0.540+0.035*i-dy2, COL["accent"], A2)
        return base.convert("RGB")

    def scene_photo(self, cov, label, lt, zin):
        base = self.grade(self.kenburns(cov, lt/D, zin)).convert("RGBA"); base.alpha_composite(self.SCRIM)
        a = rise(lt, 0.12, 0.7); A = int(255*a); dy = (1-a)*0.014
        self.text(base, label, self._f("serif_bold", 72), 0.79-dy, COL["creme"], A)
        return base.convert("RGB")

    def scene_outro(self, lt):
        o = CFG["outro"]
        base = ImageChops.multiply(Image.new("RGB", (self.W, self.H), COL["dark"]), self.VIGN).convert("RGBA")
        a = rise(lt, 0.1, 0.8); A = int(255*a); dy = int((1-a)*0.012*self.H)
        if CFG.get("logo"):
            lw = int(300*self.K); lg = Image.open(CFG["logo"]).convert("RGBA")
            lg = lg.resize((lw, int(lg.size[1]*lw/lg.size[0])), Image.LANCZOS)
            ll = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0)); ll.paste(lg, ((self.W-lw)//2, int(0.23*self.H)-dy), lg)
            ll.putalpha(ll.getchannel("A").point(lambda v: int(v*a))); base.alpha_composite(ll)
        self.text(base, o["title"], self._f("serif_bold", 88), 0.42-dy/self.H, COL["creme"], A)
        a2 = rise(lt, 0.45, 0.8); A2 = int(255*a2)
        self.text(base, o["cta"],   self._f("serif_italic", 60), 0.50, COL["accent"], A2)
        self.text(base, o["phone"], self._f("sans_bold", 56), 0.585, COL["creme"], A2)
        if o.get("address"): self.text(base, o["address"], self._f("sans_reg", 34), 0.645, COL["grey"], A2)
        if o.get("social"):  self.text(base, o["social"],  self._f("sans_reg", 38), 0.678, COL["accent"], A2)
        return base.convert("RGB")

    def scene(self, i, lt):
        if i == 0: return self.scene_title(lt)
        if i == len(self.photos)+1: return self.scene_outro(lt)
        cov, label, zin = self.photos[i-1]; return self.scene_photo(cov, label, lt, zin)

    def render(self, frames_dir):
        os.makedirs(frames_dir, exist_ok=True)
        nsc = len(self.photos)+2; step = D-X; total = D+(nsc-1)*step; nf = int(total*FPS)
        for gf in range(nf):
            tg = gf/FPS
            act = [(i, tg-i*step) for i in range(nsc) if i*step-1e-6 <= tg < i*step+D+1e-6]
            if not act: act = [(nsc-1, D)]
            if len(act) == 1:
                fr = self.scene(*act[0])
            else:
                (i1, l1), (i2, l2) = act[0], act[1]; al = max(0.0, min(1.0, (tg-i2*step)/X))
                fr = Image.blend(self.scene(i1, l1), self.scene(i2, l2), smooth(al))
            fr.save(os.path.join(frames_dir, f"{gf:04d}.png"))
        return nf


def encode(frames_dir, nf, out_mp4):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe(); dur = nf/FPS
    subprocess.run([ff, "-y", "-framerate", str(FPS), "-i", os.path.join(frames_dir, "%04d.png"),
                    "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out_mp4],
                   check=True)


if __name__ == "__main__":
    for W, H, tag in CFG["formats"]:
        fdir = os.path.join(OUT, "frames_"+tag)
        print(f"→ rendu {tag} {W}x{H} …")
        nf = Renderer(W, H).render(fdir)
        out = os.path.join(OUT, f"promo-{tag}.mp4")
        encode(fdir, nf, out)
        print(f"✅ {out}")
