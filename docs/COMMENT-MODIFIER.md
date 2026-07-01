# Comment modifier le site — Brasserie Phoenix

Ce site est fait pour être **modifié facilement**, sans toucher au code compliqué.
Tout le contenu vit dans le dossier **`docs/data/`** (des fichiers `.json`).

👉 **Le plus simple : demande-moi la modification en français**, par exemple :
> « Mets à jour le menu de la semaine avec un tartare de thon à 17,90 € »
> « Change le prix de l'entrecôte galicienne à 37,90 € »
> « Ajoute une annonce : fermé le 15 août »

Je m'occupe du fichier. Ci-dessous, les repères si tu veux comprendre où ça se passe.

---

## 1. Modifier un prix ou un plat de la carte
Fichier : **`docs/data/carte.json`**

Chaque plat ressemble à ça :
```json
{
  "id": "entrecote-galicien",
  "prix": "35,90 €",
  "coup_de_coeur": false,
  "nom": { "fr": "Entrecôte de bœuf Galicien", "nl": "…", "es": "…", "en": "…" },
  "desc": { "fr": "…", "nl": "…", "es": "…", "en": "…" }
}
```
- **Changer un prix** : modifier la valeur de `"prix"`.
- **Mettre un plat en avant** : passer `"coup_de_coeur"` à `true` (badge ❤ + surbrillance).
- **Corriger un nom / une description** : les 4 langues sont **au même endroit** (`fr`, `nl`, `es`, `en`).
- **Enlever un plat** : supprimer son bloc `{ … }`.

> ⚠️ Les plats marqués `"verifier_prix": true` sont des prix que j'ai lus dans le PDF
> et qui restent **à confirmer** par toi. Voir la liste dans le message de livraison.

## 2. Changer le menu de la semaine
Fichier : **`docs/data/menu-semaine.json`**
```json
{
  "actif": true,
  "semaine_du": "2026-06-29",
  "plats": [
    { "prix": "18,90 €", "nom": { "fr": "…", "nl": "…", "es": "…", "en": "…" },
      "desc": { "fr": "…", "nl": "…", "es": "…", "en": "…" } }
  ]
}
```
- Remplacer les plats de la liste, mettre à jour `"semaine_du"`.
- Pour **cacher** la section quand il n'y a pas de menu spécial : `"actif": false`.

## 3. Publier / retirer une annonce
Fichier : **`docs/data/annonces.json`**
- `"actif": true` affiche le bandeau, `false` le cache.
- `"ton"` : `"info"` (cuivre), `"fete"` (dégradé feu), `"alerte"` (marine).

## 4. Modifier les infos pratiques
Fichier : **`docs/data/infos.json`** — adresse, téléphone, email, horaires, liens Instagram / Facebook / TikTok.

## 5. Textes des boutons et menus
Fichier : **`docs/data/ui.json`** — libellés de navigation, du formulaire, du hero, etc. (4 langues).

## 6. Le récit « L'esprit Phoenix »
Fichier : **`docs/data/esprit.json`** — sur-titre, titre, paragraphes du récit, image d'ambiance et les 3 « repères ». `"actif": false` masque la section.

## 7. Les plats signature (accueil)
Fichier : **`docs/data/signature.json`** — les plats mis en avant (image, prix, étiquette, 4 langues). Réordonner ou ajouter des blocs dans `"plats"`.

## 8. La galerie photo
Fichier : **`docs/data/galerie.json`** — liste d'images avec légende (4 langues). Un clic ouvre la visionneuse (lightbox). Pour ajouter une photo, copier un bloc et changer `"src"`.

## 9. Les avis clients
Fichier : **`docs/data/avis.json`** — auteur, note sur 5, provenance et texte de l'avis. `"actif": false` masque la section.

## 10. La réservation (WhatsApp / email ou futur moteur)
Fichier : **`docs/assets/js/reservation.js`** — tout en haut, un bloc **`RESERVATION`** isole la cible :
- `mode: "whatsapp_email"` (par défaut) : les 2 boutons ouvrent WhatsApp / email pré-remplis (aucun serveur, aucune donnée stockée).
- `mode: "url"` + `url: "…"` : pour brancher plus tard un vrai moteur de réservation (widget, TheFork, Zenchef…). Un seul endroit à changer.

## 11. Les images (hero, galerie, signature, ambiance)
Dossiers : **`docs/assets/img/`** → `hero/`, `galerie/`, `signature/`, `ambiance/`.

- **Hero** : image de fond définie dans `index.html` (`.hero-kenburns`, `background-image`).
  Photo actuelle : `hero/hero-facade-coucher-soleil.jpg`. Une 2ᵉ photo est prête
  (`hero/hero-enseigne-mer.jpeg`) pour une future section ou un changement.
- **Récit / ambiance** : `data/esprit.json` → `"image"` (photo `ambiance/terrasse-coucher-soleil-mer.jpg`).
- **Plats signature** : `data/signature.json` → `"image"` de chaque plat.
- **Galerie** : `data/galerie.json` → liste `"src"` (17 photos, légendes 4 langues).

> Pour **remplacer** une photo : déposez le nouveau fichier dans le bon dossier et mettez à
> jour le chemin dans le `.json` correspondant — ou gardez le même nom de fichier pour ne
> rien changer d'autre. Les photos de galerie se chargent en `lazy-loading` et leur légende
> sert aussi de texte alternatif (accessibilité + SEO).

---

## Où va le site en ligne
Le site est publié via **GitHub Pages** depuis le dossier `docs/` de la branche `main`.
Après chaque modification poussée sur `main`, le site en ligne se met à jour tout seul en 1-2 minutes.

## Une remarque de sécurité
Ce site n'a **aucun serveur** et **ne stocke aucune donnée client**. Les réservations
ouvrent simplement WhatsApp ou l'email avec un message déjà écrit — rien n'est enregistré.
