// Shared composition constants + shot list (single source of truth).
export const FPS = 30;
export const OUT_W = 720;
export const OUT_H = 1280;
export const TARGET_AR = OUT_W / OUT_H; // 0.5625 (9:16)

// Natural size of public/tartare.jpeg
export const SRC_W = 1086;
export const SRC_H = 1448;

export type Shot = {
  name: string;
  f: number; // duration in frames
  z: [number, number]; // zoom start -> end (1 = full height visible)
  c0: [number, number]; // center start (normalized on source)
  c1: [number, number]; // center end
};

// Same choreography as the reference edit, expressed declaratively.
export const SHOTS: Shot[] = [
  { name: "push-in plat", f: 120, z: [1.0, 1.12], c0: [0.5, 0.55], c1: [0.46, 0.57] },
  { name: "macro jaune", f: 90, z: [1.58, 1.72], c0: [0.37, 0.28], c1: [0.39, 0.3] },
  { name: "travelling condiments", f: 150, z: [1.5, 1.5], c0: [0.6, 0.31], c1: [0.75, 0.66] },
  { name: "macro grain boeuf", f: 120, z: [1.66, 1.84], c0: [0.42, 0.6], c1: [0.4, 0.62] },
  { name: "pull-back signature", f: 240, z: [1.3, 1.0], c0: [0.48, 0.56], c1: [0.5, 0.55] },
];

export const TOTAL = SHOTS.reduce((a, s) => a + s.f, 0); // 720 frames = 24s
export const SHOT_STARTS = SHOTS.reduce<number[]>((acc, s, i) => {
  acc.push(i === 0 ? 0 : acc[i - 1] + SHOTS[i - 1].f);
  return acc;
}, []);

// Dark-luxury grade applied to every frame (CSS filter on the image).
export const GRADE_FILTER =
  "contrast(1.13) saturate(1.16) brightness(0.99) sepia(0.10) hue-rotate(-6deg)";
