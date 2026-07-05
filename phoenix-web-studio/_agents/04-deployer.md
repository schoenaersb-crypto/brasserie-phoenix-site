# Agent 04 — deployer

## Rôle
Mettre le site validé en ligne sur **GitHub Pages** et renseigner l'URL publique.
Dernier maillon du pipeline ; ne s'exécute **que si la QA a rendu un verdict PASS**.

## Pré-requis (bloquants)
- Verdict **PASS** de l'agent 03-qa (0 crochet restant).
- `git` + `gh` (GitHub CLI authentifié) disponibles dans l'environnement.
- `clients/<slug>/site/index.html` présent.

## Entrée
- `clients/<slug>/site/` validé.
- Le `slug` et le compte GitHub cible `<github-user>`.

## Sortie
- Site en ligne : `https://<github-user>.github.io/pws-<slug>/`.
- URL renseignée dans `_core/database.json` (champ `url`) et dans le rapport client.
- Statut client mis à jour → `livré`.

## Étapes

1. **Vérifier le feu vert QA**
   ```bash
   grep -q 'VERDICT : ✅ PASS' clients/<slug>/rapports/qa.md || { echo "❌ QA non validée"; exit 1; }
   ```

2. **Lancer le déploiement**
   ```bash
   bash _deploy/deploy.sh "<slug>" "<github-user>"
   ```
   Le script :
   - crée le repo `pws-<slug>` (idempotent) ;
   - pousse le contenu de `clients/<slug>/site/` sur la branche `main` ;
   - ajoute `.nojekyll` ;
   - active GitHub Pages (branche `main`, dossier `/`).

3. **Vérifier la mise en ligne**
   ```bash
   URL="https://<github-user>.github.io/pws-<slug>/"
   curl -sS -o /dev/null -w "%{http_code}" "$URL"   # attendu : 200 (peut prendre 1–2 min)
   ```
   GitHub Pages peut mettre 1 à 2 minutes à publier ; réessayer si `404`.

4. **Renseigner l'URL**
   - Mettre à jour `_core/database.json` : `url` = l'URL publique, `statut` = `livré`.
   - Écrire `clients/<slug>/rapports/deploiement.md` (URL, date, code HTTP).

## Format du rapport `deploiement.md`

```markdown
# Déploiement — test-bar-la-playa
- Date : 2026-07-04
- Repo : github.com/<github-user>/pws-test-bar-la-playa
- URL  : https://<github-user>.github.io/pws-test-bar-la-playa/
- Statut HTTP : 200 OK
- Résultat : ✅ En ligne
```

## Fallback (si `gh` absent)
Le script `deploy.sh` sort en code 3 et affiche les étapes manuelles :
créer le repo, pousser `site/`, activer Pages (branche `main`, dossier `/`).

## Critères de succès
- Le repo `pws-<slug>` existe et contient le site.
- L'URL GitHub Pages répond `200`.
- `_core/database.json` reflète `statut: livré` + `url` renseignée.

## Passage de relais
→ Fin du pipeline. L'orchestrateur clôture le dossier et déclenche l'email de livraison
   + la facture (voir `_core/orchestrateur.md`).
