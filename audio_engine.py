#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brasserie Phoenix — moteur audio original (100% synthetise, libre de droits).

Compose un lit musical cinematique + design sonore cale sur la timeline video :
tempo verrouille (100 BPM -> beat 0.6s) pour que les coupes tombent pile sur les
temps. Voix : kick / sub / pad (progression Am-F-C-G) / pluck / shimmer, plus
whooshs de transition, riser vers le climax, impacts, et gresillement (sizzle).

Sortie : output/reel_audio.wav  (44.1kHz, stereo, ~25.2s)
"""
import os, numpy as np
from scipy.signal import butter, lfilter, fftconvolve

SR   = 44100
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, "output", "reel_audio.wav")

# --- timeline verrouillee (identique a la video) -----------------------------
BPM, BEAT, BAR = 100.0, 0.6, 2.4
DUR   = 25.2
CUTS  = [2.4, 4.8, 6.6, 8.4, 10.2, 12.0, 14.4, 18.0, 20.4]   # bornes de plans
CLIMAX, CTA = 14.4, 20.4
N = int(DUR * SR)
buf = np.zeros((N, 2), np.float32)                # bus principal stereo
wet = np.zeros((N, 2), np.float32)                # bus reverb (send)

def n(t):        return int(t * SR)
def dur_n(d):    return int(d * SR)

def note(name):
    """freq equal temperament, A4=440. ex: 'A3','C4','E4'."""
    names = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
    p = names[name[:-1]]; octv = int(name[-1])
    midi = 12 * (octv + 1) + p
    return 440.0 * 2 ** ((midi - 69) / 12.0)

def env(nsamp, a, d, s, r, sus=0.7):
    """ADSR simple."""
    a, d, r = max(1, int(a*SR)), max(1, int(d*SR)), max(1, int(r*SR))
    s_n = max(0, nsamp - a - d - r)
    e = np.concatenate([
        np.linspace(0, 1, a),
        np.linspace(1, sus, d),
        np.full(s_n, sus),
        np.linspace(sus, 0, r)])
    if len(e) < nsamp: e = np.pad(e, (0, nsamp - len(e)))
    return e[:nsamp].astype(np.float32)

def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo/(SR/2), min(hi,SR/2-1)/(SR/2)], btype='band'); return lfilter(b, a, x)
def lp(x, f, order=2):
    b, a = butter(order, min(f,SR/2-1)/(SR/2), btype='low');  return lfilter(b, a, x)
def hp(x, f, order=2):
    b, a = butter(order, f/(SR/2), btype='high'); return lfilter(b, a, x)

def place(dst, mono, t, gain=1.0, pan=0.0):
    """ajoute un signal mono dans un bus stereo a l'instant t (pan -1..1)."""
    i = n(t); L = len(mono)
    if i >= N: return
    L = min(L, N - i)
    gl = gain * np.sqrt((1 - pan) / 2); gr = gain * np.sqrt((1 + pan) / 2)
    dst[i:i+L, 0] += mono[:L] * gl
    dst[i:i+L, 1] += mono[:L] * gr

# ---------------------------------------------------------------------------
# Voix
# ---------------------------------------------------------------------------
def v_kick(vel=1.0):
    d = dur_n(0.20); tt = np.arange(d)/SR
    f = 48 + (95 - 48) * np.exp(-tt*38)           # pitch env
    body = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt*9)
    click = hp(np.random.randn(d)*np.exp(-tt*120), 1500)*0.5
    return ((body + click) * vel).astype(np.float32)

def v_hat(vel=0.5):
    d = dur_n(0.05); tt = np.arange(d)/SR
    return (hp(np.random.randn(d), 7000) * np.exp(-tt*90) * vel).astype(np.float32)

def v_sub(freq, d, vel=1.0):
    nn = dur_n(d); tt = np.arange(nn)/SR
    x = np.sin(2*np.pi*freq*tt) + 0.25*np.sin(2*np.pi*2*freq*tt)
    return (x * env(nn, .01,.05,.9,.12, .85) * vel).astype(np.float32)

def v_pad(freqs, d, vel=1.0):
    nn = dur_n(d); tt = np.arange(nn)/SR; x = np.zeros(nn)
    for f in freqs:
        for det in (0.994, 1.0, 1.006):           # detune -> largeur
            ph = 2*np.pi*f*det*tt
            x += (np.sin(ph) + 0.28*np.sin(2*ph) + 0.12*np.sin(3*ph))
    x = lp(x, 2600) / (len(freqs)*3)
    return (x * env(nn, .35,.2,.75,.6, .8) * vel).astype(np.float32)

def v_pluck(freq, d=0.5, vel=1.0):
    nn = dur_n(d); tt = np.arange(nn)/SR
    x = (np.sin(2*np.pi*freq*tt) + 0.4*np.sin(2*np.pi*2*freq*tt)
         + 0.2*np.sin(2*np.pi*3*freq*tt))
    x *= np.exp(-tt*6.5)
    return (lp(x, 4200) * vel).astype(np.float32)

def v_shimmer(freq, d, vel=1.0):
    nn = dur_n(d); tt = np.arange(nn)/SR
    x = (np.sin(2*np.pi*freq*tt) + np.sin(2*np.pi*freq*1.5*tt)
         + np.sin(2*np.pi*freq*2*tt)) * (0.6+0.4*np.sin(2*np.pi*0.7*tt))
    return (x * env(nn, .4,.3,.7,.8, .7) * vel).astype(np.float32)

def v_riser(d=2.4, vel=1.0):
    nn = dur_n(d); tt = np.linspace(0,1,nn)
    noise = np.random.randn(nn)
    sweep = np.zeros(nn)
    for k in range(0, nn, 512):                   # bandpass montant par blocs
        f = 300 + 6000*(k/nn)
        seg = bp(noise[k:k+1024], f, f*1.6)[:min(512,nn-k)]
        sweep[k:k+len(seg)] += seg
    swp_sine = np.sin(2*np.pi*np.cumsum(200+2200*tt)/SR)*0.3
    x = (sweep*0.7 + swp_sine) * (tt**2)          # swell
    return (x * vel).astype(np.float32)

def v_impact(vel=1.0, dark=False):
    d = dur_n(0.9); tt = np.arange(d)/SR
    boom = np.sin(2*np.pi*(52 if dark else 60)*tt) * np.exp(-tt*4.5)
    boom += 0.5*np.sin(2*np.pi*(80)*tt) * np.exp(-tt*7)
    crack = hp(np.random.randn(d)*np.exp(-tt*30), 900)*0.35
    return ((boom + crack) * vel).astype(np.float32)

def v_whoosh(d=0.5, direction=1, vel=1.0):
    nn = dur_n(d); tt = np.linspace(0,1,nn)
    noise = np.random.randn(nn)
    out = np.zeros(nn)
    for k in range(0, nn, 256):                   # bandpass en cloche (bas->haut->bas)
        prog = k/nn; f = 400 + 5000*np.sin(np.pi*prog)
        seg = bp(noise[k:k+512], f, f*1.5)[:min(256,nn-k)]
        out[k:k+len(seg)] += seg
    amp = np.sin(np.pi*tt)                         # enveloppe hann
    return (out * amp * vel).astype(np.float32), direction

def v_sizzle(d, vel=1.0):
    nn = dur_n(d)
    x = bp(np.random.randn(nn), 2500, 6500)
    am = 0.55 + 0.45*np.random.RandomState(7).rand(nn)          # crepitement
    am = lp(am, 40)
    return (x * am * vel).astype(np.float32)

# ---------------------------------------------------------------------------
# Arrangement
# ---------------------------------------------------------------------------
# progression d'accords par mesure (2.4s)
CHORDS = {
    'Am': ['A3','C4','E4'], 'F': ['F3','A3','C4'],
    'C':  ['C4','E4','G4'], 'G': ['G3','B3','D4'],
}
BAR_PLAN = ['Am','Am','F','C','G','F','Am','F','C','Am','Am']   # 11 mesures
PENTA = {'Am':['A4','C5','E4','A4'], 'F':['F4','A4','C5','A4'],
         'C':['C5','E4','G4','E4'], 'G':['G4','B4','D5','B4']}

def build():
    nb_bars = int(np.ceil(DUR / BAR))
    for bi in range(nb_bars):
        tb = bi * BAR
        if tb >= DUR: break
        ch = BAR_PLAN[min(bi, len(BAR_PLAN)-1)]
        freqs = [note(x) for x in CHORDS[ch]]
        strong = tb >= CLIMAX - 0.01 and tb < 18.0     # mesures climax
        build_phase = tb >= 2.4                         # apres l'intro
        # -- pad (send reverb) --
        pv = 0.5 if not strong else 0.62
        if tb < 2.4: pv = 0.32
        place(wet, v_pad(freqs, BAR*0.98, pv), tb, gain=0.9)
        place(buf, v_pad(freqs, BAR*0.98, pv*0.7), tb, gain=0.5)
        # -- sub (racine) --
        root = note(CHORDS[ch][0]) / 2
        if build_phase:
            place(buf, v_sub(root, BAR*0.95, 0.7 if not strong else 0.85), tb, gain=0.8)
        else:
            place(buf, v_sub(root, BAR*0.95, 0.45), tb, gain=0.6)
        # -- shimmer (send) --
        place(wet, v_shimmer(note('A5'), BAR, 0.10 + (0.06 if strong else 0)), tb, gain=0.5)
        # -- drums --
        for bt in range(4):
            t = tb + bt*BEAT
            if t >= DUR: break
            if build_phase:
                if strong:                              # 4-on-floor au climax
                    place(buf, v_kick(0.95), t, gain=0.9)
                elif bt in (0, 2):                       # kick doux 1 & 3
                    place(buf, v_kick(0.7), t, gain=0.8)
                if bt in (1, 3):                         # hats contretemps
                    place(buf, v_hat(0.4), t+BEAT/2, gain=0.5, pan=0.2)
        # -- pluck motif (build + resolve, pas a l'intro) --
        if build_phase and tb < 12.0 or (tb >= 18.0):
            motif = PENTA[ch]
            for bt, nm in enumerate(motif):
                t = tb + bt*BEAT
                if t < DUR:
                    place(buf, v_pluck(note(nm), 0.55, 0.28), t, gain=0.7, pan=(-0.25 if bt%2 else 0.25))

    # -- riser vers le climax (mesure avant 14.4) --
    place(buf, v_riser(2.2, 0.5), CLIMAX-2.2, gain=0.7)
    place(wet, v_riser(2.2, 0.3), CLIMAX-2.2, gain=0.5)

    # -- impacts sur transitions cles --
    place(buf, v_impact(0.5), 0.0, gain=0.7)                 # hook logo
    place(wet, v_impact(0.4), 0.0, gain=0.6)
    place(buf, v_impact(0.7), 10.2, gain=0.7)               # flash braise (s4->s5)
    place(buf, v_impact(1.0, dark=True), CLIMAX, gain=0.95) # IMPACT climax
    place(wet, v_impact(0.7, dark=True), CLIMAX, gain=0.8)
    place(buf, v_impact(0.55), CTA, gain=0.7)               # ouverture CTA
    place(wet, v_impact(0.45), CTA, gain=0.6)

    # -- whooshs de transition (~0.18s avant chaque cut) --
    for k, ct in enumerate(CUTS):
        if abs(ct-10.2) < .01 or abs(ct-14.4) < .01:        # ces cuts ont deja un impact
            continue
        w, d = v_whoosh(0.5, direction=(1 if k%2 else -1), vel=0.45)
        place(buf, w, ct-0.32, gain=0.6, pan=0.5*d)

    # -- sizzle (ASMR) sur les plans steak : s1 large 2.4-4.8 et climax 14.4-18 --
    place(buf, v_sizzle(2.2, 0.05), 2.5, gain=0.5)
    place(buf, v_sizzle(3.4, 0.07), 14.5, gain=0.6)

    # -- fin : accord tenu + queue de reverb --
    place(wet, v_pad([note('A3'),note('C4'),note('E4'),note('A4')], 4.0, 0.5), 21.0, gain=0.9)

# ---------------------------------------------------------------------------
# Reverb (convolution IR synthetique) + mix bus
# ---------------------------------------------------------------------------
def reverb(stereo, decay=0.85, wetlvl=0.9):
    ir_len = int(decay * SR)
    tt = np.arange(ir_len)/SR
    out = np.zeros_like(stereo)
    for c in range(2):
        ir = np.random.RandomState(11+c).randn(ir_len) * np.exp(-tt/(decay*0.5))
        ir[:80] *= np.linspace(0,1,80)                      # pre-delay doux
        rev = fftconvolve(stereo[:, c], ir)[:len(stereo)]
        out[:, c] = rev
    m = np.max(np.abs(out)) + 1e-9
    return out / m * wetlvl

def main():
    np.random.seed(42)
    build()
    mix = buf.copy()
    mix += reverb(wet, decay=1.1, wetlvl=0.28)              # send reverb
    # sidechain global doux sur les downbeats (pompage)
    duck = np.ones(N, np.float32)
    for bi in range(int(DUR/BEAT)):
        i = n(bi*BEAT); L = dur_n(0.18)
        if i < N:
            L = min(L, N-i)
            duck[i:i+L] = np.minimum(duck[i:i+L], np.linspace(0.62, 1.0, L))
    mix *= duck[:, None]
    # bus glue : saturation douce (tanh) + highpass 28Hz + limiteur
    mix = hp(mix, 28, order=2)
    mix = np.tanh(mix * 1.15) * 0.92
    peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / peak * 0.95                                  # normalisation -0.5 dBFS
    # fondu d'ent ree/sortie propre
    fi, fo = dur_n(0.05), dur_n(0.6)
    mix[:fi] *= np.linspace(0,1,fi)[:,None]
    mix[-fo:] *= np.linspace(1,0,fo)[:,None]
    data = np.clip(mix, -1, 1)
    from scipy.io.wavfile import write
    write(OUT, SR, (data*32767).astype(np.int16))
    rms = np.sqrt(np.mean(data**2))
    print("OK %s  %.2fs  peak=%.3f rms=%.3f (%.1f dBFS)" %
          (OUT, DUR, np.max(np.abs(data)), rms, 20*np.log10(rms+1e-9)))

if __name__ == "__main__":
    main()
