#!/usr/bin/env python3
"""Charge les lots Judilibre de la couche froide dans une base DuckDB de travail.

    ~/data/open-justice/work/.venv/bin/python scripts/charger_judilibre.py
    ~/data/open-justice/work/.venv/bin/python scripts/charger_judilibre.py --echantillon 3   # essai

Lit cold_dir/judilibre/{cc,ca,tj,tcom}/*.json (réponses /scan, champ `results`).
Étape 1, en parallèle : chaque lot est réduit à une ligne JSON par décision
(work_dir/judilibre_plat/<juridiction>/<lot>.ndjson). Étape 2 : DuckDB lit ces
fichiers plats et écrit work_dir/judilibre.duckdb, table `jud`.

`jud` garde les métadonnées, la longueur du texte, l'introduction (3 000 premiers
caractères) et le dispositif. Le texte intégral reste dans la couche froide.
La base de travail est hors du dépôt et reconstructible. Rien n'est publié d'ici.
"""
import json
import sys
import time
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import duckdb

RACINE = Path(__file__).resolve().parent.parent
JURIDICTIONS = ("cc", "ca", "tj", "tcom")


def chemins():
    config = RACINE / "config.toml"
    c = tomllib.loads(config.read_text(encoding="utf-8")) if config.exists() else {}
    froid = Path(c.get("cold_dir", "~/data/open-justice/cold")).expanduser()
    travail = Path(c.get("work_dir", "~/data/open-justice/work")).expanduser()
    return froid / "judilibre", travail


def zone(texte, zones, nom, limite=None):
    morceaux = (zones or {}).get(nom) or []
    if not morceaux:
        return None
    debut, fin = morceaux[0]["start"], morceaux[-1]["end"]
    if limite:
        fin = min(fin, debut + limite)
    return texte[debut:fin]


def aplatir(args):
    lot, sortie = args
    sortie = Path(sortie)
    if sortie.exists():
        return sortie.name, -1
    with open(lot, encoding="utf-8") as f:
        resultats = json.load(f).get("results") or []
    tmp = sortie.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in resultats:
            texte = r.get("text") or ""
            contested = r.get("contested") or {}
            f.write(json.dumps({
                "id": r.get("id"), "jurisdiction": r.get("jurisdiction"), "location": r.get("location"),
                "chamber": r.get("chamber"), "formation": r.get("formation"), "type": r.get("type"),
                "decision_date": r.get("decision_date"), "update_date": r.get("update_date"),
                "solution": r.get("solution"), "solution_alt": (r.get("solution_alt") or "").strip() or None,
                "nac": r.get("nac"), "themes": r.get("themes") or [], "publication": r.get("publication") or [],
                "interet_particulier": r.get("particularInterest"), "source": r.get("source"), "ecli": r.get("ecli"),
                "attaquee_date": contested.get("date"), "attaquee_titre": contested.get("title"),
                "attaquee_juridiction": contested.get("jurisdiction"),
                "longueur_texte": len(texte), "a_zones": bool(r.get("zones")),
                "introduction": zone(texte, r.get("zones"), "introduction", 3000),
                "dispositif": zone(texte, r.get("zones"), "dispositif"),
            }, ensure_ascii=False) + "\n")
    tmp.replace(sortie)
    return sortie.name, len(resultats)


COLONNES = {
    "id": "VARCHAR", "jurisdiction": "VARCHAR", "location": "VARCHAR", "chamber": "VARCHAR",
    "formation": "VARCHAR", "type": "VARCHAR", "decision_date": "VARCHAR", "update_date": "VARCHAR",
    "solution": "VARCHAR", "solution_alt": "VARCHAR", "nac": "VARCHAR", "themes": "VARCHAR[]",
    "publication": "VARCHAR[]", "interet_particulier": "BOOLEAN", "source": "VARCHAR", "ecli": "VARCHAR",
    "attaquee_date": "VARCHAR", "attaquee_titre": "VARCHAR", "attaquee_juridiction": "VARCHAR",
    "longueur_texte": "BIGINT", "a_zones": "BOOLEAN", "introduction": "VARCHAR", "dispositif": "VARCHAR",
}


def main():
    source, travail = chemins()
    echantillon = int(sys.argv[sys.argv.index("--echantillon") + 1]) if "--echantillon" in sys.argv else 0
    plat = travail / ("judilibre_plat_echantillon" if echantillon else "judilibre_plat")
    cible = travail / ("judilibre-echantillon.duckdb" if echantillon else "judilibre.duckdb")
    taches = []
    for j in JURIDICTIONS:
        (plat / j).mkdir(parents=True, exist_ok=True)
        lots = sorted((source / j).glob("*.json"))
        for lot in lots[:echantillon] if echantillon else lots:
            taches.append((str(lot), str(plat / j / (lot.stem + ".ndjson"))))
    debut, faits, n = time.time(), 0, 0
    with ProcessPoolExecutor() as pool:
        for nom, k in pool.map(aplatir, taches, chunksize=4):
            faits += 1
            n += max(k, 0)
            if faits % 100 == 0 or faits == len(taches):
                print(f"aplati {faits}/{len(taches)} lots ({time.time() - debut:.0f} s)", flush=True)
    tmp = cible.with_suffix(".tmp.duckdb")
    tmp.unlink(missing_ok=True)
    con = duckdb.connect(str(tmp))
    con.execute("SET memory_limit='8GB'; SET preserve_insertion_order=false")
    colonnes = ", ".join(f"'{k}': '{v}'" for k, v in COLONNES.items())
    con.execute(f"""CREATE TABLE jud AS SELECT * FROM read_json('{plat}/*/*.ndjson',
                    format='newline_delimited', columns={{{colonnes}}})""")
    for j, k in con.execute("SELECT jurisdiction, count(*) FROM jud GROUP BY 1 ORDER BY 1").fetchall():
        print(f"{j}: {k} décisions")
    con.close()
    tmp.replace(cible)
    print(f"écrit : {cible} ({time.time() - debut:.0f} s)")


if __name__ == "__main__":
    sys.exit(main())
