import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  cancelRender,
  continueRender,
  delayRender,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { KenBurns } from "./KenBurns";
import { FPS, SHOTS, SHOT_STARTS, TOTAL } from "./config";

// Load branding fonts and hold the render until they are ready.
const useBrandFonts = () => {
  const [handle] = useState(() => delayRender("loading-fonts"));
  useEffect(() => {
    Promise.all([
      new FontFace(
        "Instrument Serif",
        `url(${staticFile("fonts/InstrumentSerif-Regular.ttf")})`,
      ).load(),
      new FontFace(
        "IBM Plex Serif",
        `url(${staticFile("fonts/IBMPlexSerif-Italic.ttf")})`,
        { style: "italic" },
      ).load(),
    ])
      .then((fonts) => {
        fonts.forEach((f) => document.fonts.add(f));
        continueRender(handle);
      })
      .catch((err) => cancelRender(err));
  }, [handle]);
};

const smooth = (t: number) => t * t * (3 - 2 * t);
const clamp = (v: number, lo: number, hi: number) =>
  Math.max(lo, Math.min(hi, v));

// Fine film grain as an inline SVG turbulence tile.
const GRAIN =
  "url(\"data:image/svg+xml;utf8," +
  encodeURIComponent(
    "<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'>" +
      "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/>" +
      "<feColorMatrix type='saturate' values='0'/></filter>" +
      "<rect width='100%' height='100%' filter='url(#n)'/></svg>",
  ) +
  "\")";

const Overlays: React.FC = () => (
  <>
    {/* split-tone: cool navy shadows */}
    <AbsoluteFill
      style={{
        backgroundColor: "#16364A",
        mixBlendMode: "soft-light",
        opacity: 0.22,
      }}
    />
    {/* split-tone: warm copper highlights */}
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse at 42% 45%, #B98D55 0%, rgba(185,141,85,0) 70%)",
        mixBlendMode: "soft-light",
        opacity: 0.35,
      }}
    />
    {/* vignette */}
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse at center, rgba(0,0,0,0) 42%, rgba(0,0,0,0.58) 118%)",
      }}
    />
    {/* film grain */}
    <AbsoluteFill
      style={{
        backgroundImage: GRAIN,
        backgroundRepeat: "repeat",
        mixBlendMode: "overlay",
        opacity: 0.07,
      }}
    />
  </>
);

const OutroTitle: React.FC = () => {
  const frame = useCurrentFrame();
  const dur = SHOTS[SHOTS.length - 1].f;
  const local = frame / dur;
  const fadeIn = clamp((local - 0.42) / 0.3, 0, 1);
  const fadeOut = clamp((1 - local) / 0.18, 0, 1);
  const op = smooth(fadeIn) * fadeOut;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 300,
        opacity: op,
      }}
    >
      <div
        style={{
          fontFamily: "Instrument Serif",
          fontSize: 78,
          letterSpacing: 6,
          color: "#B98D55",
          textShadow: "0 2px 18px rgba(0,0,0,0.55)",
          whiteSpace: "nowrap",
        }}
      >
        BRASSERIE PHOENIX
      </div>
      <div
        style={{
          width: 120,
          height: 2,
          backgroundColor: "#B98D55",
          opacity: 0.7,
          margin: "18px 0",
        }}
      />
      <div
        style={{
          fontFamily: "IBM Plex Serif",
          fontStyle: "italic",
          fontSize: 34,
          letterSpacing: 3,
          color: "rgba(246,240,228,0.9)",
        }}
      >
        Tartare de bœuf
      </div>
    </AbsoluteFill>
  );
};

const Fades: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeIn = Math.round(0.6 * FPS);
  const fadeOut = Math.round(1.3 * FPS);
  const opacity = interpolate(
    frame,
    [0, fadeIn, TOTAL - fadeOut, TOTAL],
    [1, 0, 0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", opacity, pointerEvents: "none" }} />
  );
};

export const PhoenixTartare: React.FC = () => {
  useBrandFonts();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Shots (hard cuts, one visible at a time) */}
      {SHOTS.map((shot, i) => (
        <Sequence key={shot.name} from={SHOT_STARTS[i]} durationInFrames={shot.f}>
          <KenBurns shot={shot} />
        </Sequence>
      ))}

      {/* Grade + texture above all shots */}
      <Overlays />

      {/* Outro branding on the last shot */}
      <Sequence
        from={SHOT_STARTS[SHOTS.length - 1]}
        durationInFrames={SHOTS[SHOTS.length - 1].f}
      >
        <OutroTitle />
      </Sequence>

      {/* Global fade from / to black */}
      <Fades />
    </AbsoluteFill>
  );
};
