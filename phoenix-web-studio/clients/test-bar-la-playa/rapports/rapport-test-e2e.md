# Rapport de test end-to-end — test-bar-la-playa

**Date :** 4 juillet 2026
**Client fictif :** Bar La Playa (Carlos Martinez) · Torrevieja, ES
**Template :** restaurant/style-B-moderne · **Pack :** Business

## Résultats par étape

| Étape | Description | Statut |
|---|---|:--:|
| 1 | Structure du studio (_base, _templates×7, _agents, _core, _cowork, _deploy, _docs) | ✅ |
| 2 | Dossier client (brief-client.md, site/, livraison/, rapports/) + copie du template | ✅ |
| 3 | Personnalisation : placeholders remplacés, :root couleurs/polices, chemins _base corrigés, _base copié | ✅ |
| 4 | Anti-balises : **0 crochet `[...]` restant** | ✅ |
| 5 | Documents : email-bienvenue.md + facture-setup.md (990 € setup + 59 €/mois) | ✅ |
| 6 | Déploiement GitHub Pages | ⚠️ bloqué (permissions d'intégration) |
| 7 | Rendu visuel du site (screenshot headless) | ✅ |

## Détails Étape 4 — anti-balises
`grep -noE '\[[A-Z0-9_]+\]'` sur `site/index.html` → **aucun résultat**. Aucun `[` résiduel. Chemins `../../../_base/` → `_base/` corrigés (2 occurrences : CSS ligne 21, JS ligne 176).

## Détails Étape 6 — déploiement
- `deploy.sh` s'exécute correctement et détecte proprement l'absence de `gh` (code de sortie 3, instructions de fallback affichées).
- Fallback via API GitHub : **échec** — `403 Resource not accessible by integration`. L'intégration GitHub de cette session cloud ne peut ni créer le repo `pws-test-bar-la-playa`, ni pousser hors du seul repo autorisé (`brasserie-phoenix-site`).
- **Cause :** limite d'environnement (token de session à portée restreinte), pas un bug du pipeline.
- **Pour déployer réellement :** exécuter `bash _deploy/deploy.sh "test-bar-la-playa" "schoenaersb-crypto"` en local avec `gh` authentifié → URL cible : `https://schoenaersb-crypto.github.io/pws-test-bar-la-playa/`.

## Vérification de rendu
Le site généré a été rendu en headless (Chromium) : couleurs client appliquées (hero `#0A2540`, accents `#FF6B35`), contenus injectés, 3 avis, sections complètes. Polices Google en fallback local uniquement (proxy bloque fonts.googleapis.com) — se chargeront en production.

## Verdict
Pipeline **fonctionnel de bout en bout** jusqu'à la génération du site prêt à déployer. Seule la publication GitHub Pages nécessite un environnement avec droits de création de repo (local + `gh`, ou élargissement de la portée GitHub de la session).
