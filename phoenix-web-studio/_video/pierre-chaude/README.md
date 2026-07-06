# 🎬 Reel Remotion — Bœuf sur pierre chaude (Brasserie Phoenix)

Projet [Remotion](https://remotion.dev) qui transforme la **photo réelle** d'un plat
(`public/pierre-boeuf.png`) en un reel cinématique vertical, dans la direction artistique
« dark luxury » de la Brasserie Phoenix.

- **Format** : 1080×1920 (9:16), 30 fps
- **Durée** : 24 s (720 frames)
- **Codec** : H.264 / yuv420p (lecture universelle Reels / TikTok / QuickTime)
- **Storyboard** : voir `../../_docs/video-prompts-pierre-chaude.md`

## Découpage narratif

| Temps | Plan | Mouvement |
|-------|------|-----------|
| 0–4 s | La pierre brûlante | fondu au noir → push-in, premières volutes de vapeur |
| 4–8 s | La saisie | macro rasante sur la croûte caramel, jus brillant |
| 8–13 s | Le rituel des sauces | slide latéral sur les trois ramequins |
| 13–16 s | La fraîcheur | bascule vers la salade, oignon rouge & pousses |
| 16–24 s | Le dressage + signature | pull-back, vapeur, logo Phœnix, fondu |

## Rendu

```bash
npm install
npm run render      # → out/pierre-chaude.mp4
```

> ⚠️ Environnement sans Chromium « full » : ce dépôt a été rendu avec le binaire
> `headless_shell`. Si `remotion render` échoue au lancement du navigateur, préciser :
>
> ```bash
> npx remotion render PierreChaude out/pierre-chaude.mp4 \
>   --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
>   --chrome-mode=chrome-for-testing
> ```

## Aperçu interactif (studio)

```bash
npm run dev         # ouvre Remotion Studio pour scrubber / ajuster
```

## Personnaliser

- **Changer le plat** : remplacer `public/pierre-boeuf.png` (garder un cadrage portrait).
- **Recadrer la caméra virtuelle** : ajuster le tableau `CAM` dans `src/PierreChaude.tsx`.
- **Textes / actes** : les `<Sequence>` + `<Lower>` dans `src/PierreChaude.tsx`.

> `out/` et `node_modules/` sont ignorés par git : le MP4 est un artefact reproductible
> via `npm run render`.
