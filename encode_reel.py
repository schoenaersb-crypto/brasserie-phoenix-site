#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Encodage final H.264 via moviepy (frames PNG -> phoenix_reel_3d.mp4)."""
import os, glob
import numpy as np
from moviepy import ImageSequenceClip, AudioArrayClip

ROOT   = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(ROOT, "output", "_frames")
OUT    = os.path.join(ROOT, "output", "phoenix_reel_3d.mp4")
FPS    = 30

frames = sorted(glob.glob(os.path.join(FRAMES, "f_*.png")))
assert frames, "aucune frame rendue"
dur = len(frames) / FPS
print("Frames : %d  |  duree : %.2fs" % (len(frames), dur))

clip = ImageSequenceClip(frames, fps=FPS)

# piste audio silencieuse propre (AAC)
silence = np.zeros((int(dur * 44100), 2), np.float32)
clip = clip.with_audio(AudioArrayClip(silence, fps=44100))

clip.write_videofile(
    OUT,
    codec="libx264",
    audio_codec="aac",
    bitrate="10000k",
    fps=FPS,
    preset="slow",
    ffmpeg_params=["-pix_fmt", "yuv420p",
                   "-profile:v", "high",
                   "-level", "4.0",
                   "-movflags", "+faststart"],
)
sz = os.path.getsize(OUT) / (1024 * 1024)
print("OK -> %s  (%.1f Mo)" % (OUT, sz))
