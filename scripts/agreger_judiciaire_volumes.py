#!/usr/bin/env python3
"""Volumes et nature des affaires de la justice judiciaire (Judilibre).

Lit `judilibre.duckdb` (couche de travail, hors dépôt, lecture seule) et écrit
`site/agregats/judiciaire_volumes.json`. Agrégats seulement : chaque cellule
publiée compte au moins SEUIL décisions ; les groupes plus petits sont fondus
dans une ligne « autres », elle-même portée au-dessus du seuil. Aucune
ventilation par magistrat, greffier ou personne ; pas de statistique par
chambre de juridiction du fond (seules les chambres de la Cour de cassation,
qui correspondent à des matières, sont comptées).

Deux référentiels publics sont lus en ligne, en mémoire, sans rien écrire :
- la nomenclature des affaires civiles (NAC) du ministère de la Justice,
  publiée sur data.gouv.fr (fichier historique arrêté en juillet 2022) ;
- les libellés des juridictions de Judilibre (dépôt public de la Cour de
  cassation `judilibre-search`, version figée par son commit).

    ~/data/open-justice/work/.venv/bin/python scripts/agreger_judiciaire_volumes.py
"""
import datetime
import io
import json
import re
import sys
import tomllib
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import duckdb

SEUIL = 300
RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "site" / "agregats" / "judiciaire_volumes.json"

NAC_URL = ("https://static.data.gouv.fr/resources/nomenclature-des-affaires-civiles-historiques/"
           "20221012-101711/copie-de-nac-historique-jusquen-juillet-2022.csv")  # en réalité un .xlsx
NAC_PAGE = "https://www.data.gouv.fr/datasets/634677f37b8614146f4090ff"
NAC_DOC = ("https://static.data.gouv.fr/resources/nomenclature-des-affaires-civiles-historiques/"
           "20221012-101743/presentation-generale-nac-et-pp-dacs.pdf")
TAXON_COMMIT = "6cdd7e69917940d3aa43043f9b9992245d292a52"
TAXON_URL = ("https://raw.githubusercontent.com/Cour-de-cassation/judilibre-search/"
             + TAXON_COMMIT + "/src/taxons/{j}/location.js")

JURIDICTIONS = {"cc": "Cour de cassation", "ca": "Cours d'appel",
                "tj": "Tribunaux judiciaires", "tcom": "Tribunaux de commerce"}

# Chambres de la Cour de cassation (valeurs de `chamber`). Les chambres sont des
# matières, chacune composée de nombreux magistrats. Les ordonnances (`ordo`,
# rendues par un seul magistrat) et les petites formations sont regroupées.
CHAMBRES_CC = {"civ1": "Première chambre civile", "civ2": "Deuxième chambre civile",
               "civ3": "Troisième chambre civile", "comm": "Chambre commerciale",
               "soc": "Chambre sociale", "cr": "Chambre criminelle"}

# Regroupements Open Justice, faits à partir des intitulés officiels de la NAC.
# Ce ne sont pas des catégories du ministère.
REGROUPEMENTS = {
    "Baux (habitation, professionnels, ruraux, commerciaux)":
        "left(nac, 2) in ('51', '52', '5A', '5B', '30')",
    "Étrangers : rétention et zone d'attente":
        "left(nac, 2) = '14' and regexp_matches(lower(intitule), 'tranger|zone d''attente|rétention')",
    "Soins psychiatriques sans consentement, isolement, contention":
        "left(nac, 2) = '14' and regexp_matches(lower(intitule), 'hospitalisation|isolement|contention|internement')",
    "Divorce et séparation de corps": "left(nac, 2) in ('20', '21')",
    "Surendettement des particuliers": "left(nac, 2) = '48'",
    "Entreprises en difficulté (hors surendettement)": "left(nac, 1) = '4' and left(nac, 2) <> '48'",
    "Relations individuelles de travail": "left(nac, 2) = '80'",
    "Protection sociale et risques professionnels": "left(nac, 2) in ('88', '89')",
}

# Libellés de chambre des tribunaux de commerce : texte libre, saisi localement.
# Classement par mots-clés, borne basse : une chambre de procédures collectives
# peut porter un libellé neutre (« Chambre 04 »).
TCOM_LIBELLE = """case
    when chamber is null or trim(chamber) in ('', '.') then 'Sans libellé de chambre'
    when regexp_matches(lower(chamber), 'proc[ée]dures? collectives?|redressement|liquidation|sauvegarde|difficult')
        then 'Libellé mentionnant les procédures collectives'
    when regexp_matches(lower(chamber), 'r[ée]f[ée]r[ée]') then 'Libellé mentionnant les référés'
    else 'Autre libellé' end"""


def telecharger(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def lire_nac():
    """Feuille unique du classeur NAC → liste de lignes (code, n1, n2, niveau1, niveau2, intitulé, création, suppression)."""
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    z = zipfile.ZipFile(io.BytesIO(telecharger(NAC_URL)))
    chaines = ["".join(t.text or "" for t in si.iter(ns + "t"))
               for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(ns + "si")]
    lignes = []
    for row in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter(ns + "row"):
        cellules = {}
        for c in row.findall(ns + "c"):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            v = c.find(ns + "v")
            val = "" if v is None else (chaines[int(v.text)] if c.get("t") == "s" else v.text)
            cellules[col] = (val or "").strip()
        lignes.append([cellules.get(k, "") for k in "ABCDEFGH"])
    entete, corps = lignes[0], lignes[1:]
    assert entete[0] == "Code NAC" and entete[5].startswith("Intitul"), entete
    return [l for l in corps if l[0]]


def lire_lieux(j):
    texte = telecharger(TAXON_URL.format(j=j)).decode("utf-8")
    return {m[1]: m[3] for m in re.findall(r"""(['"]?)([\w-]+)\1\s*:\s*(['"])(.*?)\3\s*,""", texte)}


def ouvrir():
    cfg = tomllib.loads((RACINE / "config.toml").read_text())
    travail = (RACINE / Path(cfg["work_dir"]).expanduser()).resolve()
    return duckdb.connect(str(travail / "judilibre.duckdb"), read_only=True)


def lignes(c, sql):
    cur = c.execute(sql)
    cles = [d[0] for d in cur.description]
    return [dict(zip(cles, r)) for r in cur.fetchall()]


def seuiller(rows, groupe, cle, autre="autres (groupes sous le seuil)"):
    """Fond les lignes sous SEUIL dans une ligne « autres » par groupe ; si cette
    ligne reste sous le seuil, y fond aussi les plus petites lignes publiées,
    pour qu'aucune cellule ne soit déductible par différence."""
    par_groupe = {}
    for r in rows:
        par_groupe.setdefault(tuple(r[g] for g in groupe), []).append(r)
    sortie = []
    for g, rs in par_groupe.items():
        gardees = sorted([r for r in rs if r["n"] >= SEUIL], key=lambda r: -r["n"])
        petites = [r for r in rs if r["n"] < SEUIL]
        reste = sum(r["n"] for r in petites)
        nb = len(petites)
        while petites and 0 < reste < SEUIL and gardees:
            r = gardees.pop()
            reste += r["n"]
            nb += 1
        if reste >= SEUIL:
            gardees.append({**dict(zip(groupe, g)), cle: autre, "n": reste, "groupes_fondus": nb})
        elif reste:
            raise RuntimeError(f"groupe {g} : {reste} décisions sous le seuil impossibles à fondre")
        sortie.extend(gardees)
    return sortie


def avec_parts(rows, groupe):
    totaux = {}
    for r in rows:
        k = tuple(r[g] for g in groupe)
        totaux[k] = totaux.get(k, 0) + r["n"]
    return [{**r, "part": round(100 * r["n"] / totaux[tuple(r[g] for g in groupe)], 1)} for r in rows]


def main():
    c = ouvrir()
    nac = lire_nac()
    c.execute("create temp table ref (code varchar, n1 varchar, n2 varchar, niveau1 varchar, niveau2 varchar,"
              " intitule varchar, creation varchar, suppression varchar)")
    c.executemany("insert into ref values (?, ?, ?, ?, ?, ?, ?, ?)", nac)
    lieux = {j: lire_lieux(j) for j in ("ca", "tj", "tcom")}
    libelle_n1 = {l[0]: l[5] for l in nac if len(l[0]) == 1}
    libelle_n2 = {l[0]: l[5] for l in nac if len(l[0]) == 2}

    # Vue de travail : année lisible, NAC nettoyé (« null » en toutes lettres = absent).
    c.execute("""create temp view v as select jurisdiction j, source, location, chamber,
        try_cast(decision_date as date) d, year(try_cast(decision_date as date)) annee,
        case when nac is null or nac = 'null' or trim(nac) = '' then null else upper(trim(nac)) end nac
        from jud""")

    total = c.execute("select count(*) from v").fetchone()[0]
    par_juridiction = lignes(c, """select j as juridiction, count(*) n, min(d)::varchar premiere_date,
        max(d)::varchar derniere_date, count(*) filter (where nac is not null) avec_nac,
        count(distinct location) lieux from v group by 1 order by n desc""")
    for r in par_juridiction:
        r["libelle"] = JURIDICTIONS[r["juridiction"]]
        if r["avec_nac"] == 0:
            r["avec_nac"] = None  # champ absent pour cette juridiction

    # 1. Volumes par année de décision et par source d'alimentation.
    annees = lignes(c, """select j as juridiction, source,
        case when annee < 1800 then 'date aberrante'
             -- quelques décisions de tribunaux de commerce datées du 31/12/2024, flux ouvert en 2025
             when j = 'tcom' and annee <= 2025 then '2024-2025'
             else annee::varchar end as annee, count(*) n
        from v group by all order by all""")
    annees = seuiller(annees, ("juridiction", "source"), "annee", "autres années (sous le seuil chacune)")

    # 2. Volumes mensuels depuis le début du flux régulier.
    mois = lignes(c, """select j as juridiction, strftime(d, '%Y-%m') mois, count(*) n from v
        where (j = 'ca' and source = 'jurica' and d >= date '2022-04-01')
           or (j = 'tj') or (j = 'tcom' and d >= date '2025-01-01')
        group by all order by all""")
    mois = seuiller(mois, ("juridiction",), "mois")

    # 3. Nombre de juridictions présentes par trimestre (entrée progressive dans Judilibre).
    trimestres = lignes(c, """select j as juridiction, year(d) || '-T' || quarter(d) trimestre,
        count(distinct location) juridictions_presentes, count(*) n from v
        where j in ('ca', 'tj', 'tcom') and d >= date '2022-01-01' group by all order by all""")
    trimestres = [r for r in trimestres if r["n"] >= SEUIL]

    # 4. Volumes par cour ou tribunal, toutes années puis année 2025 seule.
    def par_lieu(filtre):
        rows = lignes(c, f"""select j as juridiction, location as lieu, count(*) n from v
            where j in ('ca', 'tj', 'tcom') and {filtre} group by all""")
        for r in rows:
            r["libelle"] = lieux[r["juridiction"]].get(r["lieu"], r["lieu"])
        rows = seuiller(rows, ("juridiction",), "lieu")
        for r in rows:
            r.setdefault("libelle", "Autres (sous le seuil)")
        return sorted(rows, key=lambda r: (r["juridiction"], -r["n"]))

    lieux_tout = par_lieu("true")
    lieux_2025 = par_lieu("annee = 2025")
    libelles_manquants = {j: sorted({r["lieu"] for r in lignes(c, f"select distinct location lieu from v where j = '{j}'")}
                                    - set(lieux[j])) for j in lieux}

    # 5. Cour de cassation : chambre (matière), toutes années et depuis 2020.
    cas = "case " + " ".join(f"when chamber = '{k}' then '{v}'" for k, v in CHAMBRES_CC.items()) \
          + " else 'Ordonnances, assemblée plénière, chambre mixte et autres' end"
    cc_chambres = avec_parts(lignes(c, f"""select periode, {cas} as chambre, count(*) n from
        (select *, 'toutes années' periode from v where j = 'cc'
         union all select *, '2020 et après' from v where j = 'cc' and annee >= 2020)
        group by all order by periode, n desc"""), ("periode",))
    assert all(r["n"] >= SEUIL for r in cc_chambres)

    # 6. Tribunaux de commerce : classement du libellé de chambre par mots-clés.
    tcom = avec_parts(lignes(c, f"select {TCOM_LIBELLE} as categorie_libelle, count(*) n from v "
                                f"where j = 'tcom' group by 1 order by n desc"), ())
    assert all(r["n"] >= SEUIL for r in tcom)

    # 7. Nature des affaires (NAC), cours d'appel et tribunaux judiciaires.
    couverture_nac = lignes(c, """select j as juridiction, count(*) n,
        count(*) filter (where v.nac is not null) avec_nac,
        count(*) filter (where v.nac is not null and r.code is not null) nac_dans_table,
        count(*) filter (where r.suppression <> '') nac_supprime_avant_2022,
        count(distinct v.nac) codes_distincts from v left join ref r on r.code = v.nac
        where j in ('ca', 'tj') group by 1 order by 1""")
    periodes = """(select *, 'toutes années' periode from v where j in ('ca', 'tj')
        union all select *, annee::varchar from v where j in ('ca', 'tj') and annee in (2024, 2025))"""
    n1 = lignes(c, f"""select j as juridiction, periode, coalesce(left(nac, 1), 'non renseigné') niveau1, count(*) n
        from {periodes} group by all order by all""")
    for r in n1:
        r["libelle"] = libelle_n1.get(r["niveau1"], "Code de nature d'affaire absent")
    n1 = avec_parts(seuiller(n1, ("juridiction", "periode"), "niveau1"), ("juridiction", "periode"))
    for r in n1:
        r.setdefault("libelle", "Autres (sous le seuil)")

    n2 = lignes(c, """select j as juridiction, coalesce(left(nac, 2), 'non renseigné') niveau2, count(*) n
        from v where j in ('ca', 'tj') group by all""")
    for r in n2:
        r["libelle"] = libelle_n2.get(r["niveau2"], "Code de nature d'affaire absent"
                                      if r["niveau2"] == "non renseigné" else "Hors table NAC 2022")
    n2 = avec_parts(seuiller(n2, ("juridiction",), "niveau2"), ("juridiction",))
    n2.sort(key=lambda r: (r["juridiction"], -r["n"]))

    codes = lignes(c, """select j as juridiction, v.nac as code, coalesce(r.intitule, 'Hors table NAC 2022') intitule,
        count(*) n from v left join ref r on r.code = v.nac
        where j in ('ca', 'tj') and v.nac is not null group by all""")
    codes = avec_parts(seuiller(codes, ("juridiction",), "code"), ("juridiction",))
    for r in codes:
        r.setdefault("intitule", "Autres codes (sous le seuil chacun)")
    codes.sort(key=lambda r: (r["juridiction"], -r["n"]))

    base_regr = """(select v.j, v.nac, r.intitule from v left join ref r on r.code = v.nac
        where v.j in ('ca', 'tj') and v.nac is not null)"""
    regroupements = []
    for nom, cond in REGROUPEMENTS.items():
        for r in lignes(c, f"select j as juridiction, count(*) filter (where {cond}) n, count(*) total "
                           f"from {base_regr} group by 1 order by 1"):
            if r["n"] >= SEUIL:
                regroupements.append({"regroupement": nom, "juridiction": r["juridiction"], "n": r["n"],
                                      "part": round(100 * r["n"] / r["total"], 1)})

    contenu = {
        "calcule_le": datetime.date.today().isoformat(),
        "base": f"{total} décisions publiées dans Judilibre (justice judiciaire), photographie du 28/10/2026",
        "seuil": SEUIL,
        "note": ("Décisions publiées en open data, pas décisions rendues. Les volumes suivent l'entrée "
                 "progressive des juridictions dans Judilibre autant que leur activité. Groupes de moins de "
                 f"{SEUIL} décisions fondus dans « autres »."),
        "sources": {
            "decisions": "API Judilibre (Cour de cassation), téléchargement complet du 28/10/2026",
            "nac": {"titre": "Ministère de la Justice, Nomenclature des affaires civiles – Modifications "
                             "effectuées entre 2002 et 2022 [archive], data.gouv.fr, licence ouverte 2.0",
                    "page": NAC_PAGE, "fichier": NAC_URL, "presentation": NAC_DOC},
            "libelles_juridictions": f"https://github.com/Cour-de-cassation/judilibre-search/tree/{TAXON_COMMIT}/src/taxons",
        },
        "par_juridiction": par_juridiction,
        "par_annee": annees,
        "par_mois": mois,
        "juridictions_par_trimestre": trimestres,
        "par_lieu": lieux_tout,
        "par_lieu_2025": lieux_2025,
        "lieux_sans_libelle": libelles_manquants,
        "cc_par_chambre": cc_chambres,
        "tcom_par_libelle_de_chambre": tcom,
        "nac_couverture": couverture_nac,
        "nac_niveau1": n1,
        "nac_niveau2": n2,
        "nac_codes": codes,
        "nac_regroupements": regroupements,
        "lignes": [],
    }
    verifier(contenu)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(contenu, ensure_ascii=False, indent=1), encoding="utf-8")
    print(SORTIE.relative_to(RACINE), {k: len(v) for k, v in contenu.items() if isinstance(v, list)})


def verifier(contenu):
    """Aucun compte de décisions sous le seuil, nulle part dans le JSON. Les champs
    exclus ne comptent pas des décisions (juridictions, codes, groupes fondus)."""
    hors_compte = {"seuil", "groupes_fondus", "juridictions_presentes", "codes_distincts", "lieux"}

    def parcourir(x, chemin):
        if isinstance(x, dict):
            for k, v in x.items():
                if (k not in hors_compte and isinstance(v, int) and not isinstance(v, bool)
                        and v < SEUIL):
                    raise RuntimeError(f"cellule sous le seuil : {chemin} {x}")
                parcourir(v, chemin + "/" + k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                parcourir(v, f"{chemin}[{i}]")
    parcourir(contenu, "")


if __name__ == "__main__":
    sys.exit(main())
