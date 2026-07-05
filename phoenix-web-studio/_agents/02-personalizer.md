# Agent 02 — personalizer

## Rôle
Transformer un template générique en un site personnalisé pour le client, à partir de
`clients/<slug>/brief-client.md`. C'est l'agent qui « habille » le squelette.

## Entrée
- `clients/<slug>/brief-client.md` (produit par 01-brief-parser).
- Le template du secteur : `_templates/<template>/` (ex. `restaurant/style-B-moderne/`).
- Le design system : `_base/`.

## Sortie
- `clients/<slug>/site/index.html` : template personnalisé, 0 crochet restant.
- `clients/<slug>/site/_base/` : copie autonome du design system.

## Étapes (dans l'ordre)

1. **Copier le template** `_templates/<template>/index.html` → `clients/<slug>/site/index.html`.
2. **Remplacer TOUS les `[CROCHETS]`** par les valeurs du brief (voir table ci-dessous).
3. **Mettre à jour le `:root {}`** : injecter `--color-primary`, `--color-accent`,
   `--font-heading`, `--font-body` avec les couleurs et polices du brief.
   Mettre à jour l'URL Google Fonts (`family=<POLICE_TITRES>&family=<POLICE_CORPS>`).
4. **Corriger les chemins** : `../../../_base/` → `_base/` (le site déployé embarque son
   propre `_base/` à la racine, il n'y a plus de remontée de 3 niveaux).
   Concerne notamment :
   - `<link rel="stylesheet" href="../../../_base/assets/css/base.css">` → `_base/assets/css/base.css`
   - `<script src="../../../_base/assets/js/main.js">` → `_base/assets/js/main.js`
5. **Copier `_base/`** → `clients/<slug>/site/_base/` (CSS, JS, images du design system),
   afin que le site soit **autonome** et déployable tel quel.

## Table de correspondance : placeholder → champ du brief

| Placeholder | Champ du brief | Note |
|-------------|----------------|------|
| `[ENTREPRISE]` | entreprise | Utilisé aussi dans `@[ENTREPRISE]` (Instagram) et titres |
| `[SLOGAN]` | slogan | |
| `[DESCRIPTION_COURTE]` | description_courte | Meta description + OG + hero |
| `[DESCRIPTION_LONGUE]` | description_longue | Section « À propos » |
| `[ANNEE_CREATION]` | annee_creation | « depuis [ANNEE_CREATION] » |
| `[SLOGAN]` | slogan | Bloc citation |
| `[TELEPHONE]` | telephone | Liens `tel:` **sans espaces** + texte affiché |
| `[EMAIL]` | email | Liens `mailto:` + texte affiché |
| `[INSTAGRAM]` | instagram | URL du profil (attribut `href`) |
| `[ADRESSE]` | adresse | Rue |
| `[CP]` | cp | Code postal |
| `[VILLE]` | ville | |
| `[PAYS]` | pays | |
| `[HORAIRES]` | horaires | |
| `[SERVICES]` | services | Liste des prestations/spécialités |
| `[NOTE]` | note | Ex. `4,8` |
| `[NB_AVIS]` | nb_avis | Ex. `214` |
| `[AVIS_1_TEXTE]` | avis_1.texte | Verbatim 1 |
| `[AVIS_1_AUTEUR]` | avis_1.auteur | |
| `[AVIS_1_SOURCE]` | avis_1.source | Ex. `Google` |
| `[AVIS_2_TEXTE]` | avis_2.texte | |
| `[AVIS_2_AUTEUR]` | avis_2.auteur | |
| `[AVIS_2_SOURCE]` | avis_2.source | |
| `[AVIS_3_TEXTE]` | avis_3.texte | |
| `[AVIS_3_AUTEUR]` | avis_3.auteur | |
| `[AVIS_3_SOURCE]` | avis_3.source | |
| `[DOMAINE]` | domaine | OG url + footer |
| `[COULEUR_PRINCIPALE]` | couleur_principale | Bloc `:root {}` |
| `[COULEUR_ACCENT]` | couleur_accent | Bloc `:root {}` |
| `[POLICE_TITRES]` | police_titres | `:root {}` + URL Google Fonts |
| `[POLICE_CORPS]` | police_corps | `:root {}` + URL Google Fonts |

## Points de vigilance
- **Téléphone dans `tel:`** : retirer les espaces (`tel:+3221112233`) tout en gardant
  l'affichage lisible (`+32 2 111 22 33`).
- **Polices avec espaces** : dans l'URL Google Fonts, remplacer les espaces par `+`
  (`Playfair+Display`) ; dans le CSS `:root`, garder les guillemets (`"Playfair Display"`).
- **Aucun crochet ne doit subsister** — l'agent 03-qa le vérifiera et bloquera sinon.
- Ne jamais laisser de chemin `../../../` : le site déployé est à plat.

## Critères de succès
- 0 occurrence de `[` (hors code/contenu légitime) dans `site/index.html`.
- `site/_base/assets/css/base.css` et `site/_base/assets/js/main.js` présents.
- `:root {}` contient les vraies couleurs et polices.

## Passage de relais
→ Transmet `clients/<slug>/site/` à l'agent **03-qa**.
