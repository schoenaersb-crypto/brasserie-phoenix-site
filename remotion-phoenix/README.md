# 🎬 Remotion — Brasserie Phoenix · Tartare de bœuf (Reel 9:16)

Studio vidéo programmatique ([Remotion](https://www.remotion.dev/), React + TypeScript)
qui monte un Reel cinématographique **24 s · 720×1280 · 30 fps** à partir d'une seule
photo de plat. Mouvements de caméra virtuels (Ken Burns / travelling), étalonnage
dark-luxury, split-toning navy/cuivre (charte Phoenix), vignette, grain, fondus et
titre d'outro serif.

## Prérequis
- Node.js ≥ 18
- Un Chromium/Chrome (téléchargé automatiquement par Remotion, ou fourni via
  `--browser-executable`).

## Installation
```bash
npm install
```

## Prévisualiser (studio interactif)
```bash
npm run dev
# ouvre http://localhost:3000 — scrub, ajuste, recharge à chaud
```

## Rendre la vidéo
```bash
npm run render
# -> out/phoenix-tartare.mp4
```
Si Remotion ne peut pas télécharger Chrome (environnement hors-ligne), pointe vers un
binaire existant :
```bash
npx remotion render PhoenixTartare out/phoenix-tartare.mp4 \
  --browser-executable=/chemin/vers/chrome
```

## Structure
| Fichier | Rôle |
|---------|------|
| `src/config.ts` | Constantes + **liste des plans** (durée, zoom, centre) — source unique de vérité |
| `src/KenBurns.tsx` | Mappe un crop normalisé (centre + zoom) vers un transform `<Img>` plein cadre |
| `src/PhoenixTartare.tsx` | Composition : séquences, étalonnage/vignette/grain, titre d'outro, fondus |
| `src/Root.tsx` | Déclaration de la composition (720×1280, 30 fps, 720 frames) |
| `public/tartare.jpeg` | Image source |
| `public/fonts/` | Polices d'outro (Instrument Serif, IBM Plex Serif) |

## Découpage (5 plans, cuts nets, easing ease-in-out)
1. **Push-in plat** (0–4 s) — dolly avant, ouverture au noir
2. **Macro jaune** (4–7 s) — descente serrée sur le jaune d'œuf
3. **Travelling condiments** (7–12 s) — slide latéral sauce verte → oignons → câpres
4. **Macro grain bœuf** (12–16 s) — plongée rasante sur la texture
5. **Pull-back signature** (16–24 s) — recul + titre d'outro, fondu au noir

## Personnaliser
- **Autre plat** : remplace `public/tartare.jpeg`, ajuste `SRC_W`/`SRC_H` et les
  centres de plans dans `src/config.ts`.
- **Autre rythme / durée** : édite `f` (frames) de chaque plan dans `SHOTS`.
- **Étalonnage** : `GRADE_FILTER` dans `config.ts` + overlays dans `PhoenixTartare.tsx`.
- **Format Story 1080×1920** : change `OUT_W`/`OUT_H` dans `config.ts`.

Palette de marque : Navy `#16364A` · Cuivre `#B98D55` · Crème `#F6F0E4`.
