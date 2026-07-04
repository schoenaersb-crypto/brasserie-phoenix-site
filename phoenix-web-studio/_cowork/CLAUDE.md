# CLAUDE.md — Reprise du studio Phoenix Web Studio

Ce fichier explique comment reprendre et opérer le studio. Lis-le en entier avant toute
action. Objectif du studio : **produire et déployer des sites vitrines pour PME de façon
automatisée**, via un pipeline de 4 agents.

## Ce qu'est le studio
Phoenix Web Studio est une chaîne de production : un client remplit un formulaire, et une
suite d'agents génère puis met en ligne son site vitrine sur GitHub Pages. Trois packs
commerciaux : **Starter** (490€ + 29€/mois), **Business** (990€ + 59€/mois),
**Premium** (1900€ + 99€/mois).

## Structure des dossiers
```
phoenix-web-studio/
├── _base/          Design system partagé (CSS, JS, images). NE PAS dupliquer les styles ailleurs.
├── _templates/     Templates par secteur (ex. restaurant/style-B-moderne/index.html) avec [CROCHETS].
├── _agents/        Spécifications des 4 agents (01 brief-parser → 04 deployer).
├── _core/          orchestrateur.md (pipeline) + database.json (source de vérité clients).
├── _cowork/        Ce fichier + backlog de tâches (taches.md).
├── _docs/          Formulaire d'intake + business plan.
├── _deploy/        deploy.sh (déploiement GitHub Pages).
└── clients/        Un dossier par client : brief-client.md, site/, livraison/, rapports/.
```

## Conventions
- **slug** : minuscules-avec-tirets, sans accents (ex. `bar-la-playa`). Préfixe `test-` tant que le client n'est pas confirmé payant.
- **Repo déployé** : `pws-<slug>`. **URL** : `https://<github-user>.github.io/pws-<slug>/`.
- **Langue** : tout le contenu client est en français.
- **Placeholders** : dans les templates, toujours au format `[MAJUSCULES_AVEC_UNDERSCORES]`.
- **Source de vérité** : `_core/database.json`. Toute création/livraison doit y être reflétée (statut, url, mrr, stats).

## Ajouter un client (procédure)
1. Le client remplit `_docs/formulaire-client.md`.
2. **01 brief-parser** → génère `clients/<slug>/brief-client.md` et crée `clients/<slug>/{site,livraison,rapports}/`.
3. **02 personalizer** → copie le template, remplace **tous** les `[CROCHETS]`, met à jour
   `:root {}` (couleurs + polices), corrige `../../../_base/` → `_base/`, copie `_base/` dans `site/_base/`.
4. **03 qa** → vérifie **0 crochet**, chemins, HTML, liens `tel:`/`mailto:`. **Bloquant.**
5. Ajouter l'entrée du client dans `_core/database.json` (statut `en_cours`) et recalculer `stats`.

## Déployer un site
```bash
bash _deploy/deploy.sh "<slug>" "<github-user>"
```
- Requiert `git` + `gh` (GitHub CLI authentifié).
- Crée `pws-<slug>`, pousse `clients/<slug>/site/`, active GitHub Pages.
- Après vérif `200`, mettre à jour `_core/database.json` : `statut: livré`, `url`, et `stats.sites_deployes`.

## Règles (impératives)
- ⛔ **Toujours vérifier 0 crochet restant avant tout déploiement.**
  `grep -n '\[' clients/<slug>/site/index.html` doit être vide.
- ⛔ **Jamais de déploiement sans verdict PASS de l'agent 03-qa.**
- ✅ Ne jamais modifier un template pour un seul client : personnaliser via le brief, pas via le template.
- ✅ Ne pas laisser de chemin `../../../` dans un site déployé (il embarque son propre `_base/`).
- ✅ Garder `_core/database.json` cohérent : `mrr_total` = somme des `mrr`, `sites_deployes` = nombre de clients `statut: livré`.
- ✅ Écrire un rapport dans `clients/<slug>/rapports/` à chaque étape (qa.md, deploiement.md).

## En cas de doute
- Le pipeline complet et les points de contrôle : `_core/orchestrateur.md`.
- Le détail de chaque agent : `_agents/0X-*.md`.
- Le backlog en cours : `_cowork/taches.md`.
