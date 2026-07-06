---
name: promo-video
description: >-
  Génère une vidéo promo (mp4 H.264) pour un restaurant/commerce à partir de photos
  et d'infos de marque, en 9:16 (Reels/TikTok), 1:1 (feed) et 16:9 (web). Pipeline
  Pillow (Ken Burns + fondus enchaînés + typographie de marque + étalonnage chaud +
  carte de fin avec réservation) encodé via ffmpeg. Aucune dépendance à Remotion.
  À utiliser quand on demande « une vidéo promo », « un Reel », « une story » ou
  « mettre les photos en mouvement » pour un client Phoenix Web Studio.
---

# promo-video — vidéo promo de commerce, multi-format

## Ce que ça produit
Une à trois vidéos verticale/carrée/horizontale, montage cohérent : carte titre
(nom + slogan sur la plus belle photo), 4–6 photos en **Ken Burns** enchaînées par
**fondus**, textes animés, **étalonnage chaud** + vignette, et **carte de fin**
(logo + « Réservez » + téléphone + adresse + réseau). Piste audio silencieuse
(la musique s'ajoute dans l'app Instagram/TikTok, meilleur pour l'algorithme).

## Pré-requis
```bash
pip install Pillow imageio-ffmpeg
```
`imageio-ffmpeg` fournit un ffmpeg complet (H.264) — pas besoin d'installer ffmpeg.
Polices : par défaut celles de `canvas-fonts` (CrimsonPro serif + Bricolage sans) ;
remplaçables par les polices de marque du client.

## Utilisation
```bash
python3 promo_video.py config.json
```
Sort `promo-<tag>.mp4` pour chaque format déclaré, dans `out_dir`.

## Format du config.json
Voir `example-config.json`. Champs clés :
- `brand` : `line1`, `line2` (titre sur 2 lignes), `place` (sur-titre capitales),
  `slogan` (1–2 lignes italiques).
- `colors` : `creme`, `accent`, `dark`, `grey` (RGB) — **la charte du client**.
- `fonts` + `font_dir` : familles titres/corps (serif_bold, serif_italic, sans_bold, sans_reg).
- `logo`, `hero` (photo de la carte titre), `photos` : liste `[chemin, "légende", "in"|"out"]`
  (`in`/`out` = sens du zoom Ken Burns).
- `outro` : `title`, `cta`, `phone`, `address`, `social`.
- `formats` : liste `[largeur, hauteur, "tag"]` — ex. `[1080,1920,"reels"]`, `[1080,1080,"square"]`, `[1920,1080,"wide"]`.
- `fps` (30), `scene_dur` (3.4), `xfade` (0.5), `out_dir`.

## Notes
- Les textes se placent proportionnellement à la hauteur → rendu propre dans les 3 formats.
- Pour un autre secteur, changez `colors`, `fonts`, `photos` et les légendes.
- La musique n'est pas intégrée (droits) : à ajouter dans l'app, ou fournir un fichier
  audio et l'ajouter à l'appel ffmpeg (`-i musique.mp3` au lieu de `anullsrc`).
