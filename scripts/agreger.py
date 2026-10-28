#!/usr/bin/env python3
"""Calcule les agrégats publiables du site à partir de la couche de travail.

Lit `corpus.duckdb` (hors dépôt, lecture seule) et écrit des JSON agrégés dans
`site/agregats/`. Rien de ce qui sort ne descend sous une ligne de décision :
chaque ligne est un groupe d'au moins SEUIL décisions, sans magistrat ni
greffier (article 33 de la loi de 2019). Les groupes plus petits sont écartés.

    python3 scripts/agreger.py
"""
import datetime
import json
import sys
import tomllib
from pathlib import Path

import duckdb

SEUIL = 300
ISSUES = ("gagne", "partiel", "perd", "neutre")
RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "site" / "agregats"

# Nature du premier requérant : « physique » et « etat » tels quels, le reste
# (société, association, collectivité, établissement public) en « morale ».
NATURE = """case json_extract_string(requerants_natures, '$[0]')
    when 'physique' then 'physique' when 'etat' then 'etat' when 'inconnue' then null
    when null then null else 'morale' end"""

# Date de requête retenue : postérieure à 2000 et pas après la lecture.
DUREE = """date_diff('day', try_cast(date_requete as date), try_cast(date_lecture as date))"""
DUREE_OK = f"""try_cast(date_requete as date) >= date '2000-01-01'
    and {DUREE} >= 0"""


def ouvrir():
    cfg = tomllib.loads((RACINE / "config.toml").read_text())
    travail = (RACINE / Path(cfg["work_dir"]).expanduser()).resolve()
    return duckdb.connect(str(travail / "corpus.duckdb"), read_only=True)


def lignes(c, sql):
    cur = c.execute(sql)
    cles = [d[0] for d in cur.description]
    return [dict(zip(cles, r)) for r in cur.fetchall()]


def ecrire(nom, contenu, c):
    SORTIE.mkdir(parents=True, exist_ok=True)
    total = c.execute("select count(*) from d").fetchone()[0]
    enveloppe = {
        "calcule_le": datetime.date.today().isoformat(),
        "base": f"{total} décisions publiées (justice administrative)",
        "seuil": SEUIL,
        **contenu,
    }
    (SORTIE / nom).write_text(json.dumps(enveloppe, ensure_ascii=False, indent=1), encoding="utf-8")
    print(nom, len(contenu["lignes"]), "lignes")


def parts(rows):
    """Passe des comptes par issue à des parts en %, et écarte les petits groupes."""
    sortie = []
    for r in rows:
        n = r["n"]
        if n < SEUIL:
            continue
        sortie.append({**{k: v for k, v in r.items() if k not in ISSUES},
                       **{i: round(100 * r[i] / n, 1) for i in ISSUES}})
    return sortie


def comptes_issue(cle, filtre="true"):
    return f"""select {cle}, count(*) n,
        {', '.join(f"count(*) filter (where issue_requerant = '{i}') as {i}" for i in ISSUES)}
        from d where {filtre} and issue_requerant is not null group by all"""


def main():
    c = ouvrir()

    ecrire("volumes.json", {"lignes": lignes(c, """
        select source as ordre, year(try_cast(date_lecture as date)) as annee,
               type_decision, count(*) n
        from d group by all having count(*) >= %d order by all""" % SEUIL)}, c)

    ecrire("issue_domaine.json", {
        "note": "Part de chaque issue, vue du côté de celui qui saisit le juge. Ordonnances incluses.",
        "lignes": parts(lignes(c, comptes_issue("source as ordre, coalesce(domaine, 'sans_domaine') as domaine")
                               + " order by ordre, n desc"))}, c)

    ecrire("issue_saisissant.json", {
        "note": "Décisions au sens strict (hors ordonnances). Nature du premier requérant cité.",
        "lignes": parts(lignes(c, comptes_issue(f"source as ordre, {NATURE} as saisissant",
                                                f"type_decision = 'Décision' and {NATURE} is not null")
                               + " order by ordre, saisissant"))}, c)

    quantiles = """count(*) n, median(delai) as mediane,
        quantile_cont(delai, 0.25) as q1, quantile_cont(delai, 0.75) as q3, quantile_cont(delai, 0.9) as p90"""
    base = f"(select *, {DUREE} as delai from d where {DUREE_OK})"
    arrondi = lambda rows: [{k: (round(v) if isinstance(v, float) else v) for k, v in r.items()} for r in rows]
    ecrire("duree.json", {
        "note": "Jours entre l'enregistrement de la requête (visas) et la lecture. Pas la durée totale du litige.",
        "par_type": arrondi(lignes(c, f"select source as ordre, type_decision, {quantiles} from {base} group by all having count(*) >= {SEUIL} order by all")),
        "par_procedure": arrondi(lignes(c, f"select source as ordre, type_procedure as procedure, {quantiles} from {base} where type_procedure is not null group by all having count(*) >= {SEUIL} order by all")),
        "par_domaine": arrondi(lignes(c, f"select source as ordre, domaine, {quantiles} from {base} where type_decision = 'Décision' and domaine is not null group by all having count(*) >= {SEUIL} order by all")),
        "lignes": [],
    }, c)

    sorts = ("confirme", "infirme_partiellement", "infirme")
    rows = lignes(c, f"""select ordre, case when grouping(nat) = 1 then 'tous' else coalesce(nat, 'inconnue') end as saisissant, count(*) n,
        count(*) filter (where confirmation_premiere_instance = 'confirme') as confirme,
        count(*) filter (where confirmation_premiere_instance = 'infirme_partiellement') as infirme_partiellement,
        count(*) filter (where confirmation_premiere_instance in ('infirme_totalement', 'annule_et_renvoie')) as infirme
        from (select source as ordre, {NATURE} as nat, confirmation_premiere_instance from d
              where source in ('CAA', 'CE') and type_decision = 'Décision') t
        where confirmation_premiere_instance in ('confirme', 'infirme_partiellement', 'infirme_totalement', 'annule_et_renvoie')
        group by grouping sets ((ordre, nat), (ordre)) order by all""")
    ecrire("appel.json", {
        "note": "Sort du jugement attaqué ; décisions au sens strict ; sans objet exclu. « infirmé » inclut la cassation avec renvoi. « tous » = toutes natures, y compris inconnue.",
        "lignes": [{**{k: v for k, v in r.items() if k not in sorts},
                    **{s: round(100 * r[s] / r["n"], 1) for s in sorts}} for r in rows if r["n"] >= SEUIL],
    }, c)


if __name__ == "__main__":
    sys.exit(main())
