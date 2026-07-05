import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import {
  GRADE_FILTER,
  OUT_W,
  SRC_H,
  SRC_W,
  Shot,
  TARGET_AR,
} from "./config";

const smooth = (t: number) => t * t * (3 - 2 * t); // ease-in-out
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const clamp = (v: number, lo: number, hi: number) =>
  Math.max(lo, Math.min(hi, v));

// Maps a normalized crop (center + zoom) to an <Img> transform that fills the
// 9:16 frame, replicating a slider/dolly move from a single still.
export const KenBurns: React.FC<{ shot: Shot }> = ({ shot }) => {
  const frame = useCurrentFrame(); // local frame within the Sequence
  const t = smooth(clamp(frame / Math.max(shot.f - 1, 1), 0, 1));

  const z = lerp(shot.z[0], shot.z[1], t);
  const cx = lerp(shot.c0[0], shot.c1[0], t);
  const cy = lerp(shot.c0[1], shot.c1[1], t);

  let ch = SRC_H / z;
  let cw = ch * TARGET_AR;
  if (cw > SRC_W) {
    cw = SRC_W;
    ch = cw / TARGET_AR;
  }
  const x0 = clamp(cx * SRC_W - cw / 2, 0, SRC_W - cw);
  const y0 = clamp(cy * SRC_H - ch / 2, 0, SRC_H - ch);
  const s = OUT_W / cw;

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <Img
        src={staticFile("tartare.jpeg")}
        style={{
          position: "absolute",
          width: SRC_W * s,
          height: SRC_H * s,
          left: -x0 * s,
          top: -y0 * s,
          filter: GRADE_FILTER,
          willChange: "transform",
        }}
      />
    </AbsoluteFill>
  );
};
