# Guide d'utilisation — Phoenix Web Studio

Une **usine à sites vitrines** : tu remplis les infos d'un client → la chaîne génère,
contrôle et met en ligne un site personnalisé. Deux façons de la piloter :
les **agents IA** (langage naturel) ou le **moteur CLI** (commandes).

---

## 1. Carte du dossier

```
phoenix-web-studio/
├── _base/            design system commun (CSS/JS) — le socle de tous les sites
├── _templates/       7 modèles par secteur (voir §3)
├── _agents/          specs de référence des agents
├── _core/
│   ├── pws.py        ⚙️  LE MOTEUR : parse | build | qa | deliver | deploy | run
│   └── database.json registre clients + tarifs + stats
├── _deploy/deploy.sh mise en ligne GitHub Pages
├── _docs/            formulaire d'intake vierge + business plan
├── GUIDE.md          ce fichier
└── clients/<slug>/
    ├── brief-client.md   les infos (format « - clef : valeur »)
    ├── site/             le site généré + son _base autonome
    ├── livraison/        email + facture
    └── rapports/         qa.md, déploiement…

.claude/agents/  → 5 agents invocables (pws-orchestrator, pws-brief-parser,
                    pws-personalizer, pws-qa, pws-deployer)
```

---

## 2. Les 5 agents

| Agent | Rôle | Entre / Sort |
|-------|------|--------------|
| `pws-brief-parser` | Formulaire brut → brief structuré | infos → `brief-client.md` |
| `pws-personalizer` | Brief → site personnalisé | brief → `site/` |
| `pws-qa` | Garde-fou : 5 contrôles, verdict PASS/FAIL | `site/` → `rapports/qa.md` |
| `pws-deployer` | Mise en ligne GitHub Pages (gate QA PASS) | `site/` → URL |
| `pws-orchestrator` | Chef d'orchestre bout en bout | infos → site en ligne |

> Les agents apparaissent dans une **nouvelle session Claude Code** ouverte sur ce repo
> (ils sont chargés au démarrage de session).

---

## 3. Les 7 templates

`restaurant/style-B-moderne` · `restaurant/style-A-classique` ·
`coiffeur/style-A-elegant` · `artisan/style-A-pro` · `commerce/style-A-boutique` ·
`immobilier/style-A-premium` · `coach/style-A-energie`

---

## 4. Méthode A — par les agents (le plus simple)

Dans une session Claude Code sur ce repo, en langage naturel :

> **« Fais tourner le studio pour ce client : … »** → l'agent `pws-orchestrator`
> enchaîne brief → site → QA → livraison → (déploiement).

Ou une étape précise : invoque `pws-personalizer`, `pws-qa`, etc.

---

## 5. Méthode B — par le moteur CLI

Depuis `phoenix-web-studio/` :

```bash
python3 _core/pws.py new     <slug>                 # crée le dossier client
# → écris clients/<slug>/brief-client.md (voir §6)
python3 _core/pws.py parse   <slug>                 # valide le brief
python3 _core/pws.py build   <slug>                 # génère le site
python3 _core/pws.py qa      <slug>                 # verdict PASS/FAIL (code 0/2)
python3 _core/pws.py deliver <slug>                 # email + facture (selon pack)
python3 _core/pws.py deploy  <slug> <github-user>   # mise en ligne (gh requis)

python3 _core/pws.py run     <slug> [github-user]   # TOUT d'un coup
```

Ce que `build` fait automatiquement : remplace tous les `[CROCHETS]`, met à jour le
`:root {}` (couleurs + polices), encode l'URL Google Fonts, normalise les liens `tel:`,
encode l'adresse Maps, corrige les chemins `../../../_base/` → `_base/`, et copie `_base/`.

---

## 6. Le brief (seul fichier écrit à la main)

`clients/<slug>/brief-client.md`, une clef par ligne :

```markdown
- entreprise : Mon Resto
- client : Prénom Nom
- slug : mon-client
- secteur : restaurant
- template : restaurant/style-B-moderne
- pack : Business
- telephone : +33 6 12 34 56 78
- email : contact@monresto.fr
- instagram : https://instagram.com/monresto
- adresse : 12 rue des Fleurs
- cp : 75001
- ville : Paris
- pays : FR
- domaine : monresto.fr
- couleur_principale : #0A2540
- couleur_accent : #FF6B35
- police_titres : Space Grotesk
- police_corps : Inter
- slogan : …
- description_courte : …
- description_longue : …
- annee_creation : 2019
- horaires : Mar–Dim 12h–23h
- services : … · … · …
- note : 4.8
- nb_avis : 214
- avis_1_texte : …
- avis_1_auteur : …
- avis_1_source : Google
- avis_2_texte : …   (etc. avis_2_*, avis_3_*)
```

**Champs obligatoires** (sinon `parse` échoue) : `entreprise, client, slug, secteur,
template, pack, telephone, email, couleur_principale, couleur_accent, police_titres,
police_corps, description_courte`. Modèle complet dans `_docs/formulaire-client.md`.

---

## 7. Packs & tarifs (`_core/database.json`)

| Pack | Setup | Mensuel |
|------|------:|--------:|
| Starter | 490 € | 29 €/mois |
| Business | 990 € | 59 €/mois |
| Premium | 1900 € | 99 €/mois |

`deliver` génère la facture avec les bons montants selon le `pack` du brief.

---

## 8. Déploiement

`deploy.sh` crée le repo `pws-<slug>`, pousse `clients/<slug>/site/` et active
GitHub Pages. **Pré-requis : `gh` authentifié** (`gh auth login`) avec le droit de créer
un repo. Le déploiement est **bloqué tant que la QA n'a pas rendu PASS**.

```bash
python3 _core/pws.py deploy mon-client schoenaersb-crypto
# → https://schoenaersb-crypto.github.io/pws-mon-client/
```

---

## 9. Règles d'or (câblées dans le moteur)

- **Jamais de déploiement sans QA PASS.**
- **Jamais de `[CROCHET]` dans un site livré** (contrôle bloquant).
- Ne jamais inventer d'avis clients ni simuler un déploiement réussi.
- `_core/database.json` reflète toujours l'état réel (statut, url, stats).
