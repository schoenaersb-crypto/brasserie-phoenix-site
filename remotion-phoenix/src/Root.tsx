import React from "react";
import { Composition } from "remotion";
import { PhoenixTartare } from "./PhoenixTartare";
import { FPS, OUT_H, OUT_W, TOTAL } from "./config";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="PhoenixTartare"
      component={PhoenixTartare}
      durationInFrames={TOTAL}
      fps={FPS}
      width={OUT_W}
      height={OUT_H}
    />
  );
};
