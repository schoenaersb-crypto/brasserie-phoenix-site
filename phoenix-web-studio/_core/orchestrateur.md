# Orchestrateur — Pipeline Phoenix Web Studio

L'orchestrateur pilote la chaîne complète, du formulaire client au site en ligne, en
enchaînant les 4 agents et les étapes commerciales (livraison, facture, rapport).

## Diagramme de bout en bout

```
 ┌─────────────────────┐
 │  FORMULAIRE CLIENT  │  _docs/formulaire-client.md (rempli)
 └──────────┬──────────┘
            │
            ▼
 ┌─────────────────────┐   ⛳ Point de contrôle A
 │  01 brief-parser    │   → brief-client.md complet ? champs obligatoires OK ?
 └──────────┬──────────┘
            │ clients/<slug>/brief-client.md
            ▼
 ┌─────────────────────┐
 │  02 personalizer    │   → template copié, [CROCHETS] remplacés,
 └──────────┬──────────┘      :root {} + chemins _base/ corrigés
            │ clients/<slug>/site/
            ▼
 ┌─────────────────────┐   ⛳ Point de contrôle B (BLOQUANT)
 │  03 qa              │   → 0 crochet ? chemins OK ? HTML valide ? tel/mailto OK ?
 └──────────┬──────────┘
       PASS │ ╲ FAIL → retour à 02 personalizer
            ▼
 ┌─────────────────────┐   ⛳ Point de contrôle C
 │  LIVRAISON          │   → email de livraison + facture (pack)
 │  (email + facture)  │      clients/<slug>/livraison/
 └──────────┬──────────┘
            │
            ▼
 ┌─────────────────────┐   ⛳ Point de contrôle D
 │  04 deployer        │   → deploy.sh, vérif 200, URL GitHub Pages
 └──────────┬──────────┘
            │ url publique
            ▼
 ┌─────────────────────┐
 │  RAPPORT + DB       │   → database.json (statut: livré, url, mrr)
 └─────────────────────┘      clients/<slug>/rapports/
```

## Ordre d'exécution

1. **Formulaire** — le client remplit `_docs/formulaire-client.md`.
2. **01 brief-parser** — génère `clients/<slug>/brief-client.md` + crée l'arborescence client.
3. **02 personalizer** — produit `clients/<slug>/site/` (template personnalisé + `_base/` embarqué).
4. **03 qa** — contrôle qualité ; **bloque** si un défaut est trouvé.
5. **Livraison** — génération de l'email de livraison et de la facture selon le pack.
6. **04 deployer** — déploiement GitHub Pages + récupération de l'URL.
7. **Rapport + DB** — mise à jour de `_core/database.json` et écriture du rapport final.

> Note d'ordonnancement : la **livraison commerciale** (email + facture) est préparée dès
> que la QA est PASS, mais l'**email final** contenant l'URL n'est envoyé qu'après l'étape
> 6 (déploiement réussi). On facture un livrable qui existe.

## Points de contrôle

| ⛳ | Étape | Condition de passage | Si échec |
|----|-------|----------------------|----------|
| **A** | après 01 | Tous les champs obligatoires présents, slug valide/unique | Redemander les infos manquantes au client |
| **B** | après 03 | **0 crochet restant** + chemins + HTML + tel/mailto OK | Retour à 02-personalizer (boucle) |
| **C** | livraison | Pack identifié, montant setup + MRR calculés | Bloquer, alerter le studio |
| **D** | après 04 | URL GitHub Pages répond `200` | Relancer deploy / activer Pages manuellement |

## Règles de l'orchestrateur
- **Jamais de déploiement sans PASS QA** (point B est bloquant).
- **Fail fast** : au premier défaut critique, on s'arrête et on remonte l'erreur.
- **Idempotence** : relancer le pipeline sur un `slug` existant écrase proprement `site/`.
- **Traçabilité** : chaque étape écrit dans `clients/<slug>/rapports/`.
- **Source de vérité** : `_core/database.json` reflète l'état réel (statut, URL, MRR).

## Artefacts produits par client
```
clients/<slug>/
├── brief-client.md          (01)
├── site/                     (02) → déployé (04)
│   ├── index.html
│   └── _base/...
├── livraison/
│   ├── email-livraison.md    (livraison)
│   └── facture.md            (livraison)
└── rapports/
    ├── qa.md                 (03)
    └── deploiement.md        (04)
```
