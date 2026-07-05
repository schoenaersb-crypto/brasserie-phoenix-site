#!/usr/bin/env python3
"""
Phoenix Web Studio — moteur de pipeline (CLI).

Incarne de façon DÉTERMINISTE la partie mécanique des 4 agents définis dans _agents/ :
  01 brief-parser  ->  pws.py parse     (brief-client.md -> dict normalisé)
  02 personalizer  ->  pws.py build     (template -> site/ personnalisé + _base)
  03 qa            ->  pws.py qa        (5 contrôles, verdict PASS/FAIL, rapport)
  -- livraison --  ->  pws.py deliver   (email + facture selon le pack)
  04 deployer      ->  pws.py deploy    (garde-fou QA, appelle deploy.sh)
  orchestrateur    ->  pws.py run       (enchaîne build -> qa -> deliver -> deploy)

Les sous-agents Claude Code (.claude/agents/pws-*.md) appellent ce moteur pour tout
ce qui est déterministe, et gardent le jugement IA pour le flou (lire un formulaire
en texte libre, ajuster le ton d'un email).

Usage :
  python _core/pws.py new     <slug>
  python _core/pws.py parse   <slug>
  python _core/pws.py build   <slug>
  python _core/pws.py qa      <slug>
  python _core/pws.py deliver <slug>
  python _core/pws.py deploy  <slug> <github-user>
  python _core/pws.py run     <slug> [github-user]     # pipeline complet
"""
from __future__ import annotations
import json, re, shutil, subprocess, sys, urllib.parse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # phoenix-web-studio/
TEMPLATES = ROOT / "_templates"
BASE = ROOT / "_base"
CLIENTS = ROOT / "clients"
DB = ROOT / "_core" / "database.json"

REQUIRED = ["entreprise", "client", "slug", "secteur", "template", "pack",
            "telephone", "email", "couleur_principale", "couleur_accent",
            "police_titres", "police_corps", "description_courte"]


# --------------------------------------------------------------------------- #
#  Utilitaires
# --------------------------------------------------------------------------- #
def die(msg: str, code: int = 1):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)


def load_db() -> dict:
    return json.loads(DB.read_text(encoding="utf-8"))


def save_db(data: dict):
    DB.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def font_url_name(name: str) -> str:
    """Nom de police -> segment d'URL Google Fonts (espaces -> +)."""
    return name.strip().replace(" ", "+")


def tel_uri(phone: str) -> str:
    """+34 612 345 678 -> +34612345678 (garde le + de tête)."""
    return re.sub(r"[^\d+]", "", phone)


# --------------------------------------------------------------------------- #
#  01 — brief-parser
# --------------------------------------------------------------------------- #
def parse_brief(slug: str) -> dict:
    """Lit clients/<slug>/brief-client.md (format '- clef : valeur') -> dict."""
    path = CLIENTS / slug / "brief-client.md"
    if not path.exists():
        die(f"brief introuvable : {path}")
    data: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*[-*]\s*([a-z0-9_]+)\s*:\s*(.+?)\s*$", line)
        if m:
            data[m.group(1)] = m.group(2).strip()
    missing = [k for k in REQUIRED if not data.get(k)]
    if missing:
        die(f"champs obligatoires manquants dans le brief : {', '.join(missing)}")
    return data


# --------------------------------------------------------------------------- #
#  02 — personalizer
# --------------------------------------------------------------------------- #
def placeholder_map(d: dict) -> dict:
    """dict du brief -> table {placeholder: valeur} pour le remplacement simple."""
    return {
        "[ENTREPRISE]": d["entreprise"],
        "[CLIENT_NOM]": d.get("client", ""),
        "[SLOGAN]": d.get("slogan", ""),
        "[DESCRIPTION_COURTE]": d.get("description_courte", ""),
        "[DESCRIPTION_LONGUE]": d.get("description_longue", ""),
        "[TELEPHONE]": d["telephone"],
        "[EMAIL]": d["email"],
        "[ADRESSE]": d.get("adresse", ""),
        "[CP]": d.get("cp", ""),
        "[VILLE]": d.get("ville", ""),
        "[PAYS]": d.get("pays", ""),
        "[DOMAINE]": d.get("domaine", ""),
        "[INSTAGRAM]": d.get("instagram", ""),
        "[COULEUR_PRINCIPALE]": d["couleur_principale"],
        "[COULEUR_ACCENT]": d["couleur_accent"],
        "[POLICE_TITRES]": d["police_titres"],
        "[POLICE_CORPS]": d["police_corps"],
        "[HORAIRES]": d.get("horaires", ""),
        "[SERVICES]": d.get("services", ""),
        "[NOTE]": d.get("note", ""),
        "[NB_AVIS]": d.get("nb_avis", ""),
        "[ANNEE_CREATION]": d.get("annee_creation", ""),
        "[AVIS_1_TEXTE]": d.get("avis_1_texte", ""),
        "[AVIS_1_AUTEUR]": d.get("avis_1_auteur", ""),
        "[AVIS_1_SOURCE]": d.get("avis_1_source", ""),
        "[AVIS_2_TEXTE]": d.get("avis_2_texte", ""),
        "[AVIS_2_AUTEUR]": d.get("avis_2_auteur", ""),
        "[AVIS_2_SOURCE]": d.get("avis_2_source", ""),
        "[AVIS_3_TEXTE]": d.get("avis_3_texte", ""),
        "[AVIS_3_AUTEUR]": d.get("avis_3_auteur", ""),
        "[AVIS_3_SOURCE]": d.get("avis_3_source", ""),
    }


def build(slug: str) -> Path:
    d = parse_brief(slug)
    tpl_dir = TEMPLATES / d["template"]
    tpl = tpl_dir / "index.html"
    if not tpl.exists():
        die(f"template introuvable : {tpl}")

    site = CLIENTS / slug / "site"
    site.mkdir(parents=True, exist_ok=True)
    html = tpl.read_text(encoding="utf-8")

    # 1) URL Google Fonts : espaces -> + AVANT le remplacement générique
    html = html.replace("family=[POLICE_TITRES]", f"family={font_url_name(d['police_titres'])}")
    html = html.replace("family=[POLICE_CORPS]",  f"family={font_url_name(d['police_corps'])}")

    # 2) URL Google Maps : adresse encodée
    addr = urllib.parse.quote_plus(
        " ".join(x for x in [d.get("adresse"), d.get("cp"), d.get("ville"), d.get("pays")] if x))
    html = html.replace("q=[ADRESSE]+[CP]+[VILLE]+[PAYS]", f"q={addr}")

    # 3) Liens tel: sans espaces (avant remplacement générique de [TELEPHONE])
    html = html.replace("tel:[TELEPHONE]", f"tel:{tel_uri(d['telephone'])}")

    # 4) Remplacement générique de tous les autres placeholders
    for ph, val in placeholder_map(d).items():
        html = html.replace(ph, val)

    # 5) Chemins _base/ à plat pour le déploiement
    html = html.replace("../../../_base/", "_base/")

    (site / "index.html").write_text(html, encoding="utf-8")

    # 6) _base autonome
    dst = site / "_base"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(BASE, dst)

    print(f"✅ build : {site/'index.html'} (+ _base/)")
    return site


# --------------------------------------------------------------------------- #
#  03 — qa
# --------------------------------------------------------------------------- #
def qa(slug: str) -> bool:
    site = CLIENTS / slug / "site"
    idx = site / "index.html"
    if not idx.exists():
        die(f"site introuvable, lancez 'build' d'abord : {idx}")
    html = idx.read_text(encoding="utf-8")
    checks: list[tuple[str, bool, str]] = []

    # 1. Anti-crochets (bloquant)
    brackets = re.findall(r"\[[A-Z0-9_]+\]", html)
    checks.append(("Crochets restants", not brackets,
                   "0" if not brackets else ", ".join(sorted(set(brackets)))))

    # 2. Chemins
    no_updots = "../../../" not in html
    base_ok = (site / "_base/assets/css/base.css").exists() and \
              (site / "_base/assets/js/main.js").exists()
    checks.append(("Chemins _base/", no_updots and base_ok,
                   "../../../ absent + _base présent" if no_updots and base_ok else "chemin/_base KO"))

    # 3. Validation HTML (structure)
    html_ok = all(t in html for t in ["<!doctype html", "<html", "<head", "<body", "</html>"])
    title_ok = bool(re.search(r"<title>[^<\[]+</title>", html))
    checks.append(("Validation HTML", html_ok and title_ok,
                   "structure + <title> OK" if html_ok and title_ok else "structure/title KO"))

    # 4. Liens tel:/mailto:
    tels = re.findall(r'tel:([^"]+)', html)
    tel_ok = all(" " not in t and re.fullmatch(r"\+?\d+", t) for t in tels) and bool(tels)
    mails = re.findall(r'mailto:([^"]+)', html)
    mail_ok = all(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", m) for m in mails) and bool(mails)
    checks.append(("Liens tel:/mailto:", tel_ok and mail_ok,
                   f"{len(tels)} tel, {len(mails)} mailto valides" if tel_ok and mail_ok else "lien KO"))

    # 5. Identité visuelle
    root_colors = re.findall(r"--color-(?:primary|accent):\s*(#[0-9A-Fa-f]{3,8})", html)
    visual_ok = len(root_colors) >= 2
    checks.append(("Identité visuelle", visual_ok,
                   " / ".join(root_colors) if visual_ok else "couleurs :root KO"))

    verdict = all(ok for _, ok, _ in checks)

    lines = [f"# Rapport QA — {slug}", f"Date : {date.today().isoformat()}", "",
             "| Contrôle | Résultat | Détail |", "|---|---|---|"]
    for name, ok, detail in checks:
        lines.append(f"| {name} | {'✅ PASS' if ok else '❌ FAIL'} | {detail} |")
    lines += ["", f"VERDICT : {'✅ PASS — déploiement autorisé.' if verdict else '❌ FAIL — retour au personalizer.'}", ""]
    rap = CLIENTS / slug / "rapports"
    rap.mkdir(parents=True, exist_ok=True)
    (rap / "qa.md").write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    return verdict


# --------------------------------------------------------------------------- #
#  Livraison — email + facture
# --------------------------------------------------------------------------- #
def deliver(slug: str):
    d = parse_brief(slug)
    db = load_db()
    pack = d.get("pack", "Business")
    prices = db["packs"].get(pack)
    if not prices:
        die(f"pack inconnu : {pack}")
    liv = CLIENTS / slug / "livraison"
    liv.mkdir(parents=True, exist_ok=True)

    url_hint = f"https://<github-user>.github.io/pws-{slug}/"
    (liv / "email-bienvenue.md").write_text(
        f"""Objet : 🎉 Votre site {d['entreprise']} est prêt !

Bonjour {d.get('client','')},

Merci de votre confiance ! Votre site vitrine **{d['entreprise']}** est en ligne.

- Aperçu : {url_hint}
- Domaine à connecter : {d.get('domaine','—')}
- Pack : {pack} ({prices['setup']} € setup + {prices['mensuel']} €/mois)

Deux séries de retouches sont incluses — répondez simplement à cet email.

À très vite,
L'équipe Phoenix Web Studio
""", encoding="utf-8")

    total_an = prices["setup"] + 12 * prices["mensuel"]
    (liv / "facture-setup.md").write_text(
        f"""# FACTURE — Phoenix Web Studio

**Client :** {d['entreprise']} — {d.get('client','')}
**Date :** {date.today().isoformat()}
**Pack :** {pack}

| Désignation | P.U. | Total |
|---|--:|--:|
| Création du site (setup unique) | {prices['setup']:.2f} € | {prices['setup']:.2f} € |
| Abonnement mensuel (1er mois) | {prices['mensuel']:.2f} € | {prices['mensuel']:.2f} € |
| **Total 1er versement** | | **{prices['setup']+prices['mensuel']:.2f} €** |

- Setup : {prices['setup']} € (unique) · Mensualité : {prices['mensuel']} €/mois
- Coût 1re année : {prices['setup']} € + 12 × {prices['mensuel']} € = **{total_an} €**
""", encoding="utf-8")

    print(f"✅ livraison : email-bienvenue.md + facture-setup.md ({pack})")


# --------------------------------------------------------------------------- #
#  04 — deployer
# --------------------------------------------------------------------------- #
def deploy(slug: str, github_user: str):
    qa_file = CLIENTS / slug / "rapports" / "qa.md"
    if not qa_file.exists() or "VERDICT : ✅ PASS" not in qa_file.read_text(encoding="utf-8"):
        die("QA non validée (verdict PASS requis avant déploiement). Lancez 'qa'.")
    script = ROOT / "_deploy" / "deploy.sh"
    print(f"▶ deploy.sh {slug} {github_user}")
    res = subprocess.run(["bash", str(script), slug, github_user])
    url = f"https://{github_user}.github.io/pws-{slug}/"
    if res.returncode == 0:
        db = load_db()
        for c in db["clients"]:
            if c["slug"] == slug:
                c["url"], c["statut"] = url, "livré"
        db["stats"]["sites_deployes"] = sum(1 for c in db["clients"] if c["statut"] in ("livré", "déployé"))
        save_db(db)
        print(f"✅ déployé : {url}")
    else:
        print(f"⚠ deploy.sh code {res.returncode} — voir sortie ci-dessus (fallback manuel).")
    return res.returncode


# --------------------------------------------------------------------------- #
#  new + run
# --------------------------------------------------------------------------- #
def new_client(slug: str):
    for sub in ("site", "livraison", "rapports"):
        (CLIENTS / slug / sub).mkdir(parents=True, exist_ok=True)
    print(f"✅ dossier client créé : clients/{slug}/ (site, livraison, rapports)")


def run(slug: str, github_user: str | None):
    build(slug)
    if not qa(slug):
        die("Pipeline stoppé : QA FAIL.", 2)
    deliver(slug)
    if github_user:
        deploy(slug, github_user)
    else:
        print("ℹ  Pas de github-user fourni : build + QA + livraison OK, déploiement à lancer séparément.")


# --------------------------------------------------------------------------- #
def main(argv: list[str]):
    if len(argv) < 2:
        print(__doc__); sys.exit(0)
    cmd, rest = argv[1], argv[2:]
    if cmd == "new" and rest:      new_client(rest[0])
    elif cmd == "parse" and rest:  print(json.dumps(parse_brief(rest[0]), ensure_ascii=False, indent=2))
    elif cmd == "build" and rest:  build(rest[0])
    elif cmd == "qa" and rest:     sys.exit(0 if qa(rest[0]) else 2)
    elif cmd == "deliver" and rest: deliver(rest[0])
    elif cmd == "deploy" and len(rest) >= 2: sys.exit(deploy(rest[0], rest[1]))
    elif cmd == "run" and rest:    run(rest[0], rest[1] if len(rest) > 1 else None)
    else:
        print(__doc__); die(f"commande invalide : {' '.join(argv[1:])}")


if __name__ == "__main__":
    main(sys.argv)
