#!/usr/bin/env python3
"""Extrait les métadonnées de toutes les décisions de la couche froide vers un CSV.

Lit les archives directement (aucune décompression sur disque). Le texte
intégral n'est pas conservé : seule sa longueur l'est. Aucune identité de
magistrat ni de greffier n'est lue.
"""
import csv
import json
import sys
import tomllib
import zipfile
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from pathlib import Path

CHAMPS = ["source", "periode", "fichier", "code_juridiction", "nom_juridiction", "date_lecture",
          "date_mise_a_jour", "type_decision", "type_recours", "code_publication", "solution",
          "date_audience", "formation_jugement", "ecli", "longueur_texte"]


def txt(el, chemin):
    n = el.find(chemin)
    return (n.text or "").strip() if n is not None else ""


def traiter(args):
    chemin, source, periode = args
    lignes, echecs = [], 0
    with zipfile.ZipFile(chemin) as z:
        for nom in z.namelist():
            if not nom.endswith(".xml"):
                continue
            try:
                r = ET.fromstring(z.read(nom))
            except ET.ParseError:
                echecs += 1
                continue
            t = r.find("Decision/Texte_Integral")
            lignes.append([source, periode, nom.rsplit("/", 1)[-1],
                           txt(r, "Dossier/Code_Juridiction"), txt(r, "Dossier/Nom_Juridiction"),
                           txt(r, "Dossier/Date_Lecture"), txt(r, "Donnees_Techniques/Date_Mise_Jour"),
                           txt(r, "Dossier/Type_Decision"), txt(r, "Dossier/Type_Recours"),
                           txt(r, "Dossier/Code_Publication"), txt(r, "Dossier/Solution"),
                           txt(r, "Audience/Date_Audience"), txt(r, "Audience/Formation_Jugement"),
                           txt(r, "Dossier/Numero_ECLI"),
                           len("".join(t.itertext())) if t is not None else 0])
    return source, periode, lignes, echecs


def main():
    racine = Path(__file__).resolve().parent.parent
    cfg = tomllib.loads((racine / "config.toml").read_text())
    froid = (racine / Path(cfg["cold_dir"]).expanduser()).resolve()
    travail = (racine / Path(cfg["work_dir"]).expanduser()).resolve()
    travail.mkdir(parents=True, exist_ok=True)
    derniers = {}
    for l in (froid / "manifest.jsonl").read_text().splitlines():
        if l.strip():
            e = json.loads(l)
            derniers[e["name"]] = e
    taches = [(froid / e["path"], e["source"], e["period"]) for e in derniers.values() if e["kind"] == "archive"]
    sortie = travail / "metadonnees.csv"
    total = echecs = 0
    with open(sortie, "w", newline="", encoding="utf-8") as f, Pool() as p:
        w = csv.writer(f)
        w.writerow(CHAMPS)
        for src, per, lignes, ech in p.imap_unordered(traiter, taches):
            w.writerows(lignes)
            total += len(lignes)
            echecs += ech
            print(f"{src} {per} : {len(lignes)}", file=sys.stderr)
    print(f"{total} décisions, {echecs} échecs d'analyse -> {sortie}")


if __name__ == "__main__":
    main()
