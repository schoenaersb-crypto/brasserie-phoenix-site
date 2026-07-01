#!/usr/bin/env python3
"""Génère docs/data/carte/ depuis docs/data/carte.json (source d'édition).
- index.json : ordre des catégories + noms/notes (4 langues) pour les en-têtes.
- <id>.<lang>.json : contenu d'une catégorie, résolu dans UNE langue (charge léger).
Relancer après chaque modification de carte.json.
"""
import json, os

BASE = "/home/user/brasserie-phoenix-site/docs/data"
LANGS = ["fr", "nl", "es", "en"]
OUT = os.path.join(BASE, "carte")

def res(v, lang):
    """Résout {fr,nl,es,en} -> string de la langue (repli fr puis 1re dispo)."""
    if isinstance(v, dict):
        return v.get(lang) or v.get("fr") or next(iter(v.values()), "")
    return v

def res_item(it, lang):
    o = {}
    for k, val in it.items():
        if k in ("nom", "desc", "origine", "prix_texte"):
            o[k] = res(val, lang)
        else:
            o[k] = val  # id, prix, coup_de_coeur, prix_special, verifier_prix
    return o

def res_souslist(bloc, lang):
    return {"titre": res(bloc["titre"], lang),
            "liste": [res(x, lang) for x in bloc.get("liste", [])]}

def main():
    src = json.load(open(os.path.join(BASE, "carte.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)

    index = {"_commentaire": "Généré depuis carte.json (source). Ordre + en-têtes des catégories. Le détail de chaque catégorie est dans carte/<id>.<langue>.json, chargé à la demande.",
             "categories": []}

    for c in src["categories"]:
        entry = {"id": c["id"], "nom": c["nom"]}
        if "note" in c:
            entry["note"] = c["note"]
        index["categories"].append(entry)

        for lang in LANGS:
            data = {"items": [res_item(it, lang) for it in c.get("items", [])]}
            if "sauces" in c:
                data["sauces"] = res_souslist(c["sauces"], lang)
            if "accompagnements" in c:
                data["accompagnements"] = res_souslist(c["accompagnements"], lang)
            path = os.path.join(OUT, f"{c['id']}.{lang}.json")
            json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    json.dump(index, open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    files = sorted(os.listdir(OUT))
    print(f"{len(files)} fichiers générés dans data/carte/ :")
    for f in files:
        sz = os.path.getsize(os.path.join(OUT, f))
        print(f"  {f:22} {sz:5} o")

if __name__ == "__main__":
    main()
