# Route B — Image-to-Video : prompts plan par plan

But : transformer nos 8 photos fixes en **vrai mouvement** (vapeur, sear, versé,
travelling) via un outil IA image-to-vidéo, puis me renvoyer les clips pour que
je les **assemble sur la piste audio existante** (montage rythmé + grade + typo).

**Outils recommandés** (par ordre de contrôle) : **Runway Gen-4** (motion brush
sur la vapeur + contrôle caméra), **Kling 2.x** (mouvement physique
photoréaliste), **Luma Dream Machine** (travelling depuis une keyframe).

## Réglages globaux (à appliquer à chaque plan)
- **Format** : 9:16, 1080×1920, **3–4 s**, 24–30 fps.
- **Caméra** : *push-in lent* OU *parallaxe subtile* uniquement — pas de mouvement brusque.
- **Image de départ = notre photo** (image-to-video, jamais text-to-video : garde le plat, la couleur, le dressage).
- **Motion strength** : faible à moyen (le plat ne doit pas se déformer).
- **Prompt négatif commun** : `no text, no people, no hands, morphing, warping food, extra objects, deformed, plastic look, oversaturated`
- **Directive commune** : `photorealistic food, locked plating, preserve original colors, cinematic shallow depth of field, subtle motion`

## Prompts par plan

| # | Photo | Prompt (positif) | Mouvement clé |
|---|-------|------------------|----------------|
| 1 | `01_spread.jpg` | slow cinematic push-in across a hot-stone steak board, faint steam rising off the seared meat, candle flame flickering, gentle heat shimmer | vapeur + flamme + push-in |
| 2 | `02_burrata_pasta.jpg` | soft steam rising from fresh spaghetti, light breeze on microgreens, slow 20° camera orbit, glistening olive oil | vapeur + micro-breeze + orbit |
| 3 | `03_squid.jpg` | thin smoke rising off grilled calamari, slow dolly-in, sauce glistening, embers glow | fumée + dolly-in |
| 4 | `04_burger.jpg` | slow push-in on a burger with burrata, pesto slowly dripping, faint steam, melty highlight | drip + vapeur + push |
| 5 | `05_bread.jpg` | warm steam off toasted bread, subtle push-in, aioli surface glistening, a few crumbs settling | vapeur pain + push |
| 6 | `06_tartare.jpg` | gentle breeze on microgreens over beef tartare, egg yolk glistening, slow parallax, no deformation | micro-breeze + parallaxe |
| 7 | `07_steak.jpg` | **hero** : sizzling seared steak on a 900°C hot stone, strong steam and smoke rising, ember glow, slow push-in to the crust | sizzle + fumée forte (climax) |
| 8 | `08_martini.jpg` | espresso martini foam settling, coffee swirling under the crema, condensation on glass, bokeh Christmas lights twinkling behind, slow push-in | mousse + bokeh + push |

## Ce que je fais ensuite
1. Tu me renvoies les **8 clips** (3–4 s, 9:16), nommés `01…08`.
2. Je les **coupe sur le beat** de `output/reel_audio.wav` (100 BPM, grille déjà calée).
3. Je réapplique le **grade unifié + halation + grain** et la **typo cinétique** (kickers, filets, reveals).
4. Je garde **logo en ouverture / adresse en clôture** + le design sonore (whooshs, riser, impacts, sizzle).
5. Export **1080×1920 · 30fps · H.264** + version web légère.

> Astuce : génère 2–3 variantes par plan et garde la plus **stable** (le plat qui ne se déforme pas gagne toujours sur le mouvement le plus spectaculaire).
