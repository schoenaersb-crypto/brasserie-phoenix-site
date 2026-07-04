# Backlog — Phoenix Web Studio

Suivi des tâches du studio. `[x]` = fait, `[ ]` = à faire.

## Socle & infrastructure
- [x] Mettre en place `_base/` (design system : CSS, JS, images partagées)
- [x] Créer le template restaurant `restaurant/style-B-moderne`
- [x] Écrire le script de déploiement `_deploy/deploy.sh` (GitHub Pages)
- [x] Définir les 4 agents (`_agents/01` → `04`)
- [x] Mettre en place la base clients `_core/database.json`
- [x] Rédiger le formulaire d'intake `_docs/formulaire-client.md`
- [ ] Ajouter un script de bootstrap `new-client.sh` (crée l'arborescence `clients/<slug>/`)
- [ ] Automatiser le calcul des `stats` dans `database.json` (script)

## Templates & design
- [x] Template restaurant style B (moderne)
- [ ] Ajouter le template `restaurant/style-C` (élégant / gastronomique)
- [ ] Ajouter le secteur `coiffure-beaute` (1 template)
- [ ] Ajouter le secteur `artisan-btp` (1 template)
- [ ] Créer une galerie d'images par défaut (banque libre de droits) pour les briefs incomplets

## Commercial & facturation
- [ ] Ajouter le paiement récurrent **Stripe** (setup + abonnement mensuel par pack)
- [ ] Générer automatiquement la facture PDF depuis le pack (`livraison/facture.md` → PDF)
- [ ] Modèle d'email de livraison automatisé (avec URL du site)
- [ ] Page tarifs publique du studio

## Déploiement & domaines
- [ ] **Automatiser la configuration DNS** (domaine client → GitHub Pages, CNAME)
- [ ] Ajouter le HTTPS custom domain automatique
- [ ] Monitoring uptime des sites livrés (ping + alerte)

## Qualité
- [x] Contrôle anti-crochets dans l'agent QA
- [ ] Ajouter un check Lighthouse (perf/SEO/accessibilité) à l'agent 03-qa
- [ ] Vérifier automatiquement les liens externes (Instagram, Google Maps)

## Idées / plus tard
- [ ] Multilingue automatique (FR/NL/EN) pour le pack Premium
- [ ] Espace client (édition de contenu en libre-service)
- [ ] Tableau de bord MRR du studio
