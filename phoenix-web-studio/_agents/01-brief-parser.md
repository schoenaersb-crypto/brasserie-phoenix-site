# Agent 01 — brief-parser

## Rôle
Lire le **formulaire d'intake** rempli par le client (voir `_docs/formulaire-client.md`)
et produire un fichier **`clients/<slug>/brief-client.md`** structuré, normalisé et
directement exploitable par l'agent `02-personalizer`.

C'est le point d'entrée de tout le pipeline : la qualité du brief conditionne la qualité
du site final.

## Entrée
- Formulaire client rempli (texte libre, email, ou document collé).

## Sortie
- `clients/<slug>/brief-client.md` : brief structuré.
- Création du dossier client `clients/<slug>/` avec ses sous-dossiers :
  `site/`, `livraison/`, `rapports/`.

## Champs extraits

| Champ | Description | Exemple |
|-------|-------------|---------|
| **entreprise** | Nom commercial affiché | Bar La Playa |
| **client** | Nom du contact / gérant | Carlos Martinez |
| **slug** | Identifiant technique (minuscules-tirets) | test-bar-la-playa |
| **secteur** | Secteur d'activité | restaurant |
| **template** | Chemin du template choisi | restaurant/style-B-moderne |
| **pack** | Pack commercial souscrit | Business |
| **contacts** | Téléphone + email | +32 2 111 22 33 / contact@barlaplaya.be |
| **adresse** | Rue, code postal, ville, pays | Digue de Mer 12, 8400 Ostende (Belgique) |
| **couleurs** | Couleur principale + accent (hex) | #C0392B / #F1C40F |
| **polices** | Police titres + police corps (Google Fonts) | Playfair Display / Inter |
| **descriptions** | Description courte + description longue | « Cocktails & tapas les pieds dans le sable » / … |
| **slogan** | Accroche principale | Le goût des vacances toute l'année |
| **horaires** | Jours et heures d'ouverture | Mar–Dim 11h–23h · Fermé lundi |
| **services** | Liste des prestations / spécialités | Tapas, cocktails, terrasse, brunch |
| **note / avis** | Note Google + nombre d'avis + 3 avis clients | 4,8 · 214 avis + 3 verbatims |
| **réseaux sociaux** | Instagram (URL) | https://instagram.com/barlaplaya |
| **année** | Année de création | 2015 |

## Traitements de normalisation
- **slug** : si absent, le générer depuis `entreprise` (minuscules, accents retirés, espaces → tirets), préfixé `test-` tant que le client n'est pas confirmé payant.
- **couleurs** : garantir le format hexadécimal `#RRGGBB`.
- **polices** : ne retenir que des familles disponibles sur Google Fonts.
- **téléphone** : conserver un format international propre pour le lien `tel:` (sans espaces : `tel:+3221112233`).
- **avis** : exactement 3 verbatims (auteur, source, texte) ; compléter avec des avis réels du client si moins de 3 sont fournis.

## Format de sortie `brief-client.md`

```markdown
# Brief client — Bar La Playa

## Identité
- entreprise : Bar La Playa
- client : Carlos Martinez
- slug : test-bar-la-playa
- secteur : restaurant
- template : restaurant/style-B-moderne
- pack : Business

## Contacts
- telephone : +32 2 111 22 33
- email : contact@barlaplaya.be
- instagram : https://instagram.com/barlaplaya

## Adresse
- adresse : Digue de Mer 12
- cp : 8400
- ville : Ostende
- pays : Belgique

## Identité visuelle
- couleur_principale : #C0392B
- couleur_accent : #F1C40F
- police_titres : Playfair Display
- police_corps : Inter

## Contenu
- slogan : Le goût des vacances toute l'année
- description_courte : Cocktails & tapas les pieds dans le sable.
- description_longue : Depuis 2015, Bar La Playa réunit ...
- annee_creation : 2015
- horaires : Mar–Dim 11h–23h · Fermé lundi
- services : Tapas maison, cocktails signature, terrasse vue mer, brunch du week-end
- domaine : barlaplaya.be

## Réputation
- note : 4,8
- nb_avis : 214
- avis_1 : { auteur, source, texte }
- avis_2 : { auteur, source, texte }
- avis_3 : { auteur, source, texte }
```

## Critères de succès
- Tous les champs obligatoires sont renseignés (aucun champ vide critique).
- Le `slug` est valide et unique dans `_core/database.json`.
- Le dossier `clients/<slug>/` est créé avec `site/`, `livraison/`, `rapports/`.

## Passage de relais
→ Transmet `clients/<slug>/brief-client.md` à l'agent **02-personalizer**.
