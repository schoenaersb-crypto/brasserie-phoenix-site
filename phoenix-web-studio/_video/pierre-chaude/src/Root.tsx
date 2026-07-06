import {Composition} from 'remotion';
import {PierreChaude} from './PierreChaude';

// 9:16 vertical — 1080x1920, 30 fps, 24 s (720 frames)
export const FPS = 30;
export const DURATION_IN_FRAMES = 720;
export const WIDTH = 1080;
export const HEIGHT = 1920;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PierreChaude"
        component={PierreChaude}
        durationInFrames={DURATION_IN_FRAMES}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
