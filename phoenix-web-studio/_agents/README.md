# Agents — Phoenix Web Studio

Ce dossier décrit les **4 agents** qui composent la chaîne de production automatisée
du studio. Chaque agent est spécialisé, exécute une seule responsabilité, et passe le
relais au suivant. L'ensemble est piloté par l'orchestrateur (`_core/orchestrateur.md`).

## Vue d'ensemble

```
Formulaire client rempli
        │
        ▼
 ┌──────────────────┐
 │ 01 brief-parser  │  → clients/<slug>/brief-client.md
 └──────────────────┘
        │
        ▼
 ┌──────────────────┐
 │ 02 personalizer  │  → clients/<slug>/site/ (template personnalisé)
 └──────────────────┘
        │
        ▼
 ┌──────────────────┐
 │ 03 qa            │  → rapport QA (0 crochet = feu vert)
 └──────────────────┘
        │
        ▼
 ┌──────────────────┐
 │ 04 deployer      │  → site en ligne (GitHub Pages) + URL
 └──────────────────┘
```

## Les 4 agents

| # | Agent | Rôle | Entrée | Sortie |
|---|-------|------|--------|--------|
| 01 | **brief-parser** | Lit le formulaire d'intake rempli et produit un `brief-client.md` structuré et exploitable par les agents suivants. | Formulaire client | `brief-client.md` |
| 02 | **personalizer** | Copie le template du secteur, remplace tous les `[CROCHETS]`, met à jour le `:root {}` (couleurs + polices), corrige les chemins `_base/` et embarque le design system dans le site. | `brief-client.md` + template | `clients/<slug>/site/` |
| 03 | **qa** | Contrôle qualité : cherche les crochets restants, vérifie les chemins, valide le HTML, teste les liens `tel:`/`mailto:`. Bloque le déploiement si un défaut est trouvé. | `clients/<slug>/site/` | Rapport QA (PASS/FAIL) |
| 04 | **deployer** | Lance `_deploy/deploy.sh`, vérifie la mise en ligne, renseigne l'URL GitHub Pages dans la base et le rapport. | `clients/<slug>/site/` validé | URL publique |

## Principes communs

- **Une seule responsabilité par agent** : pas de chevauchement, chaque étape est vérifiable.
- **Fail fast** : un agent qui détecte une anomalie s'arrête et remonte l'erreur à l'orchestrateur plutôt que de laisser passer un défaut.
- **Idempotence** : relancer un agent sur le même client ne casse rien (écrasement propre).
- **Traçabilité** : chaque agent écrit ce qu'il a fait dans `clients/<slug>/rapports/`.
- **Règle d'or** : **aucun déploiement tant que la QA n'a pas validé 0 crochet restant.**

## Convention de nommage

- `slug` : identifiant technique du client en minuscules-avec-tirets (ex. `test-bar-la-playa`).
- Repo GitHub déployé : `pws-<slug>`.
- URL publique : `https://<github-user>.github.io/pws-<slug>/`.
