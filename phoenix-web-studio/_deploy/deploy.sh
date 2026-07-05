#!/usr/bin/env bash
# =============================================================================
# Phoenix Web Studio — Déploiement d'un site client sur GitHub Pages
#
# Usage : bash _deploy/deploy.sh "<slug>" "<github-user>"
# Exemple : bash _deploy/deploy.sh "test-bar-la-playa" "schoenaersb-crypto"
#
# Prérequis : git + gh (GitHub CLI authentifié).
# Le script crée le repo pws-<slug>, pousse le contenu de
# clients/<slug>/site/ et active GitHub Pages sur la branche main.
# =============================================================================
set -euo pipefail

SLUG="${1:-}"
GH_USER="${2:-}"

if [[ -z "$SLUG" || -z "$GH_USER" ]]; then
  echo "❌ Usage : bash _deploy/deploy.sh \"<slug>\" \"<github-user>\"" >&2
  exit 2
fi

# Racine du studio (dossier parent de _deploy)
STUDIO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SITE_DIR="$STUDIO_ROOT/clients/$SLUG/site"
REPO="pws-$SLUG"
REMOTE="https://github.com/$GH_USER/$REPO.git"

echo "▶ Déploiement de '$SLUG' vers $GH_USER/$REPO"

if [[ ! -d "$SITE_DIR" ]]; then
  echo "❌ Introuvable : $SITE_DIR" >&2
  exit 1
fi
if [[ ! -f "$SITE_DIR/index.html" ]]; then
  echo "❌ index.html manquant dans $SITE_DIR" >&2
  exit 1
fi

# gh est requis pour créer le repo et activer Pages automatiquement.
if ! command -v gh >/dev/null 2>&1; then
  echo "⚠  GitHub CLI 'gh' introuvable dans cet environnement." >&2
  echo "   → Fallback manuel requis (voir README). Étapes :" >&2
  echo "     1. Créer le repo $GH_USER/$REPO" >&2
  echo "     2. Pousser le contenu de $SITE_DIR" >&2
  echo "     3. Activer GitHub Pages (branche main, dossier /)" >&2
  exit 3
fi

# --- 1. Créer le repo (idempotent) -------------------------------------------
if gh repo view "$GH_USER/$REPO" >/dev/null 2>&1; then
  echo "ℹ  Repo déjà existant, réutilisation."
else
  gh repo create "$GH_USER/$REPO" --public --disable-wiki \
    --description "Site $SLUG — déployé par Phoenix Web Studio"
fi

# --- 2. Pousser le contenu du site -------------------------------------------
WORK="$(mktemp -d)"
cp -R "$SITE_DIR/." "$WORK/"
touch "$WORK/.nojekyll"   # désactive Jekyll sur GitHub Pages
(
  cd "$WORK"
  git init -q
  git checkout -q -B main
  git add -A
  git -c user.name="Phoenix Web Studio" -c user.email="studio@phoenix.local" \
      commit -q -m "Déploiement initial de $SLUG"
  git remote add origin "$REMOTE"
  git push -u origin main --force
)
rm -rf "$WORK"

# --- 3. Activer GitHub Pages --------------------------------------------------
gh api -X POST "repos/$GH_USER/$REPO/pages" \
  -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 || \
  echo "ℹ  Pages déjà activé ou activation manuelle nécessaire."

echo "✅ Déployé : https://$GH_USER.github.io/$REPO/"
