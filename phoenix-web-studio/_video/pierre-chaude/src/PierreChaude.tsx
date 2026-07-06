import React from 'react';
import {
  AbsoluteFill,
  Img,
  staticFile,
  interpolate,
  useCurrentFrame,
  Easing,
  Sequence,
} from 'remotion';

/* ─────────── Charte Brasserie Phoenix ─────────── */
const NAVY = '#16364A';
const COPPER = '#B98D55';
const COPPER_LIGHT = '#D4A96A';
const CREAM = '#F6F0E4';

const easeInOut = Easing.inOut(Easing.cubic);

/* Keyframes de la "caméra virtuelle" sur la photo (scale + translation %) */
type Cam = {f: number; scale: number; x: number; y: number};
const CAM: Cam[] = [
  {f: 0, scale: 1.06, x: 0, y: -2}, // intro
  {f: 120, scale: 1.18, x: 0, y: -7}, // 4s  — la pierre
  {f: 240, scale: 1.52, x: -9, y: -12}, // 8s  — macro saisie
  {f: 390, scale: 1.46, x: 22, y: -7}, // 13s — les sauces (gauche)
  {f: 480, scale: 1.4, x: 1, y: 30}, // 16s — la salade (haut)
  {f: 660, scale: 1.09, x: 0, y: 0}, // 22s — dressage complet
  {f: 720, scale: 1.13, x: 0, y: 1}, // outro
];

const sampleCam = (frame: number, key: 'scale' | 'x' | 'y') => {
  const frames = CAM.map((c) => c.f);
  const vals = CAM.map((c) => c[key]);
  return interpolate(frame, frames, vals, {
    easing: easeInOut,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
};

/* ─────────── Vapeur qui monte ─────────── */
const Steam: React.FC = () => {
  const frame = useCurrentFrame();
  // Présente pendant la saisie (60→300) puis la révélation finale (450→720)
  const env =
    interpolate(frame, [50, 110, 300, 340], [0, 1, 1, 0], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }) +
    interpolate(frame, [450, 520, 690, 720], [0, 1, 1, 0], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  const wisps = [
    {x: 42, delay: 0, sway: 22, w: 240, h: 520},
    {x: 55, delay: 40, sway: -18, w: 200, h: 460},
    {x: 63, delay: 80, sway: 26, w: 180, h: 420},
    {x: 48, delay: 120, sway: -24, w: 160, h: 400},
  ];
  return (
    <AbsoluteFill style={{opacity: Math.min(env, 1)}}>
      {wisps.map((wsp, i) => {
        const t = (frame + wsp.delay) / 90;
        const rise = ((t % 3) / 3) * 900; // remonte en boucle
        const fade = Math.sin((t % 3) / 3 * Math.PI); // apparaît/disparaît
        const sway = Math.sin(t * 1.6 + i) * wsp.sway;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${wsp.x}%`,
              top: '64%',
              width: wsp.w,
              height: wsp.h,
              transform: `translate(${sway - wsp.w / 2}px, ${-rise}px)`,
              background:
                'radial-gradient(ellipse at 50% 80%, rgba(255,246,232,0.5), rgba(255,246,232,0.12) 45%, transparent 70%)',
              filter: 'blur(24px)',
              opacity: 0.5 * fade,
              mixBlendMode: 'screen',
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/* ─────────── Particules cuivre magiques ─────────── */
const Particles: React.FC = () => {
  const frame = useCurrentFrame();
  const env = interpolate(frame, [70, 130, 470, 520], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const N = 34;
  return (
    <AbsoluteFill style={{opacity: env, mixBlendMode: 'screen'}}>
      {Array.from({length: N}).map((_, i) => {
        const seed = (i * 97.13) % 100;
        const baseX = (seed / 100) * 100;
        const speed = 0.4 + ((i * 53) % 40) / 100;
        const t = (frame * speed) / 30 + i;
        const y = 100 - ((t * 9) % 120);
        const x = baseX + Math.sin(t * 0.8 + i) * 4;
        const size = 3 + ((i * 31) % 5);
        const tw = 0.4 + 0.6 * Math.abs(Math.sin(t * 2 + i));
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${x}%`,
              top: `${y}%`,
              width: size,
              height: size,
              borderRadius: '50%',
              background: COPPER_LIGHT,
              boxShadow: `0 0 ${size * 2}px ${COPPER}`,
              opacity: tw * 0.7,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/* ─────────── Bandeau texte (acte) ─────────── */
const Lower: React.FC<{eyebrow: string; title: string}> = ({eyebrow, title}) => {
  const frame = useCurrentFrame();
  const appear = interpolate(frame, [8, 28], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const y = interpolate(frame, [8, 28], [24, 0], {
    easing: easeInOut,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill
      style={{
        justifyContent: 'flex-end',
        padding: '0 90px 220px',
        opacity: appear,
      }}
    >
      <div style={{transform: `translateY(${y}px)`}}>
        <div
          style={{
            color: COPPER,
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontSize: 26,
            letterSpacing: 10,
            textTransform: 'uppercase',
            fontWeight: 300,
            marginBottom: 14,
          }}
        >
          {eyebrow}
        </div>
        <div
          style={{
            color: CREAM,
            fontFamily: 'Georgia, "Times New Roman", serif',
            fontSize: 76,
            lineHeight: 1.05,
            fontWeight: 400,
            textShadow: '0 4px 30px rgba(0,0,0,0.8)',
          }}
        >
          {title}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ─────────── Composition principale ─────────── */
export const PierreChaude: React.FC = () => {
  const frame = useCurrentFrame();

  const scale = sampleCam(frame, 'scale');
  const tx = sampleCam(frame, 'x');
  const ty = sampleCam(frame, 'y');

  // Respiration légère continue
  const breath = Math.sin(frame / 42) * 0.006;

  // Fondu d'ouverture (0→1s) et de fermeture (23→24s)
  const openFade = interpolate(frame, [0, 30], [1, 0], {extrapolateRight: 'clamp'});
  const closeFade = interpolate(frame, [690, 720], [0, 1], {extrapolateLeft: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#060608'}}>
      {/* Image héro + caméra virtuelle */}
      <AbsoluteFill
        style={{
          transform: `scale(${scale + breath}) translate(${tx}%, ${ty}%)`,
        }}
      >
        <Img
          src={staticFile('pierre-boeuf.png')}
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
        />
      </AbsoluteFill>

      {/* Étalonnage chaud (dark luxury) */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(120% 90% at 42% 55%, rgba(185,141,85,0.16), transparent 55%)`,
          mixBlendMode: 'soft-light',
        }}
      />
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, rgba(22,54,74,0.28) 0%, transparent 30%, transparent 62%, rgba(6,6,8,0.55) 100%)`,
        }}
      />

      <Particles />
      <Steam />

      {/* Vignette */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse at center, transparent 38%, rgba(0,0,0,0.82) 100%)',
        }}
      />

      {/* ─── Bandeaux narratifs synchronisés au storyboard ─── */}
      <Sequence from={40} durationInFrames={90}>
        <Lower eyebrow="Acte I — Le feu" title="La pierre brûlante" />
      </Sequence>
      <Sequence from={135} durationInFrames={95}>
        <Lower eyebrow="Acte II — La saisie" title="Bœuf saisi, croûte caramel" />
      </Sequence>
      <Sequence from={250} durationInFrames={125}>
        <Lower eyebrow="Acte III — Le rituel" title="Nos trois sauces maison" />
      </Sequence>
      <Sequence from={390} durationInFrames={80}>
        <Lower eyebrow="Acte IV — La fraîcheur" title="Salade, oignon rouge & pousses" />
      </Sequence>

      {/* ─── Signature de marque (outro) ─── */}
      <Sequence from={545} durationInFrames={175}>
        <Outro />
      </Sequence>

      {/* Fondus */}
      <AbsoluteFill style={{backgroundColor: '#000', opacity: Math.max(openFade, closeFade)}} />
    </AbsoluteFill>
  );
};

const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const appear = interpolate(frame, [10, 40], [0, 1], {
    easing: easeInOut,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const line = interpolate(frame, [30, 70], [0, 220], {
    easing: easeInOut,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        opacity: appear,
      }}
    >
      <div style={{textAlign: 'center'}}>
        <div
          style={{
            color: COPPER,
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontSize: 24,
            letterSpacing: 8,
            textTransform: 'uppercase',
            marginBottom: 26,
          }}
        >
          Brasserie
        </div>
        <div
          style={{
            color: CREAM,
            fontFamily: 'Georgia, "Times New Roman", serif',
            fontSize: 120,
            letterSpacing: 4,
            textShadow: `0 0 40px rgba(185,141,85,0.35)`,
          }}
        >
          PHŒNIX
        </div>
        <div
          style={{
            width: line,
            height: 2,
            background: `linear-gradient(90deg, transparent, ${COPPER}, transparent)`,
            margin: '30px auto',
          }}
        />
        <div
          style={{
            color: COPPER_LIGHT,
            fontFamily: 'Georgia, "Times New Roman", serif',
            fontSize: 40,
            fontStyle: 'italic',
          }}
        >
          Bœuf sur pierre chaude
        </div>
      </div>
    </AbsoluteFill>
  );
};
