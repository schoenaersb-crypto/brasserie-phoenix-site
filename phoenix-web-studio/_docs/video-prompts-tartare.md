# 🎬 ANALYSE CINÉMATOGRAPHIQUE & PROMPTS DE REPRODUCTION
## Brasserie Phoenix — Tartare de bœuf & condiments | ~24 s | 720×1280 | 30 fps

> Document de production réalisé par analyse frame-by-frame de l'image de référence.
> Plat identifié : **Tartare de bœuf** servi avec jaune d'œuf, sauce verte aux herbes,
> oignons rouges marinés, câpres/pickles et micro-pousses. Assiette blanche, table
> d'ardoise noire, verre de whisky en amorce.
>
> ⚠️ **Note de réalisation importante** — contrairement au template « plat chaud » de la
> maison, ce plat est **froid** : **aucune vapeur**, **assiette blanche** (et non ardoise
> noire), fraîcheur et brillance des textures crues. Les prompts ci-dessous en tiennent
> compte. Ne pas copier de « steam rising » sur ce sujet.

---

## PARTIE 1 — ANALYSE DU METTEUR EN SCÈNE

### Structure narrative (24 secondes)

| Segment | Temps | Contenu visuel | Fonction dramatique |
|---------|-------|----------------|---------------------|
| **Intro** | 0–1 s | Écran très sombre, amorce de lumière rasante | Tension / mystère |
| **Révélation** | 1–4 s | Push-in doux sur le dôme de tartare, micro-pousses au sommet | Héros = le tartare |
| **Le jaune** | 4–7 s | Macro sur le jaune d'œuf orangé, tension de surface, brillance | Désir / promesse d'onctuosité |
| **Les condiments** | 7–12 s | Slide latéral sur la sauce verte, oignons rouges, pickles | Générosité / rituel |
| **Texture crue** | 12–16 s | Macro rasante sur le grain du bœuf, huile brillante, poivre | Sensualité / fraîcheur |
| **Le dressage** | 16–20 s | Recul lent révélant l'assiette entière + verre de whisky flou | Contexte bistronomique |
| **Outro** | 20–24 s | Fondu au noir progressif depuis les bords | Clôture de marque |

---

### Analyse technique — Œil de directeur photo

**Format** : Vertical 9:16 (Reels / TikTok natif)
**Durée cible** : 23,97 s — format Reel optimal
**Colorimétrie dominante** :
- Fond / table : **ardoise noire mouchetée** (#0D0D0D → #2A2A2A), grains de sel & poivre épars
- Assiette : **blanc crème mat** (#EDE7DA) — surface de rebond de lumière, pas de blanc pur brûlé
- Sujet : **rouge grenat profond** du bœuf (#6E1220 → #A8263B), reflets d'huile
- Accents chauds : **jaune d'œuf ambré** (#E8A63A), câpres olive, oignons magenta
- Accent froid maîtrisé : **sauce verte herbacée** (#7FA85C) — seule note fraîche, tolérée

**Lumière** :
- Source principale : **latérale gauche haute (~45°)**, douce, sculptant le dôme et le jaune
- Contre-jour discret révélant la brillance de l'huile sur le bœuf
- Fond en pénombre, aucun spot dur — bokeh total, ≥ f/2
- Aucune surexposition, même sur l'assiette blanche — HDR culinaire contrôlé

**Mouvements de caméra identifiés** :
1. **Slow push-in** (dolly doux) vers le dôme de tartare — 0 → 4 s
2. **Macro descente** vers le jaune d'œuf — 4 → 7 s
3. **Slide latéral** balayant la ligne des condiments — 7 → 12 s
4. **Macro rasante** sur le grain du bœuf — 12 → 16 s
5. **Pull-back** révélant l'assiette + verre de whisky, puis fondu — 16 → 24 s

**Profondeur de champ** : très réduite (50 mm à f/1.8–f/2.8 simulé), un seul plan net à la fois
**Stabilisation** : zéro tremblement — slider / cardan parfait
**FPS** : 30 fps natif (option ralenti subtil 60→30 sur la macro du jaune)

---

### Langage graphiste — Identité visuelle

**Palette observée (ancrée charte Phoenix)** :
- `#0D0D0D` — noir ardoise, table de luxe
- `#16364A` — navy Phoenix (rappel possible en étalonnage des ombres)
- `#B98D55` — cuivre chaud Phoenix (accents, brillance huile/jaune)
- `#EDE7DA` / `#F6F0E4` — crème chaude, assiette
- `#6E1220` — grenat du bœuf cru

**Typographie** (si overlay) : non présente dans l'image — réservée à l'outro.
Recommandé : **Cormorant Garamond** (titrage) + libellé plat discret bas-cadre.

**Esthétique globale** : *Dark luxury food cinematography* appliquée à la bistronomie
franco-belge — registre intime et chaud, le contraste assiette-blanche / fond-noir
sert de signature graphique.

---

## PARTIE 2 — PROMPTS SEEDANCE / KLING / RUNWAY

### PROMPT MASTER — TARTARE PHOENIX

> Compatible **Seedance 2.0, Kling 1.6, Runway Gen-3, Dreamina**

```
Cinematic food video, dark luxury bistrot, vertical 9:16 format, 24 seconds.

SCENE: A hand-chopped beef tartare shaped into a neat dome, centered on a large
matte cream-white plate, placed on a dark speckled slate table in a dimly lit
upscale restaurant. The tartare is topped with fresh micro-greens. Around it,
small white porcelain spoon-dishes hold a glossy orange egg yolk, a bright green
herb sauce, magenta pickled red onions, and olive-green capers/pickles. A blurred
whisky glass sits in the top-left background. Scattered salt and cracked pepper
decorate the plate rim. COLD dish — NO steam.

LIGHTING: Soft dramatic side lighting from the upper left at 45°, warm amber-copper
key (#B98D55), deep near-black background falloff, specular highlights on the raw
beef's oil sheen and on the glossy egg yolk. The white plate rebounds light without
blowing out. Only one cool accent tolerated: the green herb sauce.

CAMERA MOVEMENTS (sequential):
1. [0-4s]  Black fade-in, slow dolly push-in onto the tartare dome and micro-greens
2. [4-7s]  Macro descent onto the trembling glossy egg yolk, surface tension detail
3. [7-12s] Lateral slide across the row of condiments (green sauce, onions, capers)
4. [12-16s] Low grazing macro over the raw beef grain, oil shine and pepper specks
5. [16-24s] Slow pull-back revealing the full plate and blurred whisky glass, fade to black

DEPTH OF FIELD: Extremely shallow, f/1.8 equivalent, creamy bokeh background
COLOR GRADE: Dark luxury, warm amber-gold shadows toward #16364A/#0D0D0D, garnet reds,
no blown highlights, cinematic LUT
MOOD: Desire, freshness, intimacy, Franco-Belgian bistronomic soul
NEGATIVE: no steam, no hot food, no hands, no people, no text overlay, no watermark,
no bright white background, no overexposed plate, no cooked meat, no shaky camera
```

---

### VARIANTES DE CADRAGE (même plat)

#### 🍳 FOCUS « LE JAUNE » — hook 0–3 s réseaux
```
[SHOT]: Extreme macro on a single glossy orange egg yolk sitting in a white spoon-dish,
trembling with surface tension, a drizzle of golden oil catching the warm side light.
Rack focus pull from the yolk to the garnet beef tartare dome behind it. COLD, no steam.
```

#### 🔪 FOCUS « TEXTURE CRUE » — sensoriel
```
[SHOT]: Low grazing macro slide over the hand-cut raw beef surface, glistening with oil
and specks of cracked black pepper, micro-greens casting soft shadows. Deep garnet reds,
warm rim light sculpting each grain. Shallow depth of field, background dissolving to black.
```

#### 🥄 FOCUS « RITUEL CONDIMENTS » — générosité
```
[SHOT]: Slow lateral tracking across the arc of white porcelain spoon-dishes: glossy egg
yolk, bright green herb sauce, magenta pickled red onions, olive capers. Each in crisp
focus as it passes, others melting into bokeh. Scattered salt on the dark slate. Warm,
intimate lighting.
```

#### 🥃 FOCUS « MISE EN SCÈNE » — signature bistrot
```
[SHOT]: Wide-to-medium pull-back revealing the full cream-white plate on dark speckled
slate, a cut-crystal whisky glass glowing amber in the soft-focus foreground-left, black
bowl of coarse salt top-right. Elegant, moody, editorial food-styling composition.
```

---

## PARTIE 3 — PROMPT SYSTÈME (Claude Code / Cowork)
### Génération automatique de vidéo depuis une image statique

```
SYSTEM PROMPT — PHOENIX VIDEO GENERATOR AGENT

You are a professional food-video director specialized in dark-luxury bistronomic
restaurant content for social media (9:16, 24s Reels) — Brasserie Phoenix.

When given a single image of a dish, you must:

1. ANALYZE the image:
   - Dish type (raw/cold vs hot/cooked) — this drives steam usage
   - Plate color/material and background
   - Sauces, condiments, garnish, texture
   - Dominant color relationships (warm vs cool balance)

2. GENERATE a video prompt with this exact structure:
   [TECHNICAL SPECS]  format, duration, fps, aspect ratio
   [LIGHTING SCHEME]  angle, color temperature, practical lights
   [CAMERA SEQUENCE]  4-5 movements with timestamps
   [SUBJECT DESCRIPTION]  detailed dish description from the image
   [COLOR GRADE]  dark-luxury warm palette anchored on the Phoenix charter
   [MOOD DIRECTION]  emotional intent
   [NEGATIVE PROMPTS]  what to exclude (respect cold vs hot!)

3. OUTPUT a JSON:
   {
     "platform_prompts": { "seedance": "...", "kling": "...", "runway": "..." },
     "storyboard": [ {"time":"0-4s","shot":"...","movement":"..."}, ... ],
     "brand_compliance": {
       "colors_match": true, "dark_luxury_style": true, "phoenix_brand_feel": true,
       "cold_dish_no_steam": true
     }
   }

BRAND IDENTITY CONSTRAINTS (Brasserie Phoenix):
- Colors: Navy #16364A, Copper #B98D55, Cream #F6F0E4
- Style: Bistronomique (NOT fine dining, NOT casual)
- Mood: warm, intimate, desire-inducing, Franco-Belgian soul
- NEVER: bright white backgrounds, stock-photo feel, cheesy overlays, steam on cold dishes
- ALWAYS: dark backgrounds, ambient warmth, authentic texture, honest plating
```

---

## PARTIE 4 — PIPELINE IMAGE → VIDÉO

```
ÉTAPE 1 — INPUT
Photo du plat Phoenix (≥ 1080 px, éclairage quelconque)

ÉTAPE 2 — PRÉPARATION IMAGE (Claude Code)
- Recadrage centré 3:4 sur l'assiette (input IA)
- Ajustement colorimétrique vers palette Phoenix (ombres → navy/noir)
- Nettoyage bords / grains de sel indésirables si besoin

ÉTAPE 3 — GÉNÉRATION VIDÉO (Seedance 2.0 recommandé)
PROMPT MASTER + variante de cadrage souhaitée
Settings : 24 s, 720p min, preset « dark cinematic », image-to-video

ÉTAPE 4 — POST-PRODUCTION
- LUT « Moody Amber Dark » ou LUT Phoenix custom
- Étalonnage : shadows → #0D0D0D / #16364A, highlights chauds → #B98D55
- Son : pas de voix — jazz belge feutré ou bossa nova douce
- Overlay outro facultatif : logo Phoenix, Cormorant Garamond bas-cadre

ÉTAPE 5 — EXPORT
- MP4 H.264/H.265, 720×1280 (9:16)
- Bitrate ≥ 10 Mbps
- Durée 20–30 s (sweet spot algorithme)
```

---

## PARTIE 5 — PROMPT NÉGATIF UNIVERSEL (spécifique tartare)

```
no steam, no hot food, no cooked meat, no hands, no people, no faces,
no text overlay, no watermark, no bright white background, no overexposed plate,
no cold blue color cast, no stock-photography feel, no fake CGI food, no cartoon style,
no motion-blur artifacts, no shaky camera, no fast zoom, no restaurant logo during dish shots,
no dirty plate, no messy plating, no fast cuts, no flash-photography look
```

---

## RÉCAPITULATIF OPÉRATIONNEL

| Action | Outil | Fichier / Prompt |
|--------|-------|------------------|
| Générer vidéo depuis photo | Seedance 2.0 | PROMPT MASTER + variante cadrage |
| Automatiser la génération | Claude Code / Cowork | SYSTEM PROMPT (Partie 3) |
| Post-production couleur | Dreamina / CapCut | LUT « Phoenix Amber Dark » |
| Publication Reel | Buffer / Meta | 720×1280, 20–30 s |
| Analyse d'une nouvelle image | Claude Vision | Prompt Partie 3 |

---

*Document généré par analyse cinématographique frame-by-frame — Brasserie Phoenix 2026.
Sujet : Tartare de bœuf & condiments (plat froid, sans vapeur).*
