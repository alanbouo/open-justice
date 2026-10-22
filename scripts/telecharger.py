#!/usr/bin/env python3
"""Télécharge les archives de la justice administrative vers la couche froide.

Par défaut, le script établit seulement un plan : il lit les trois index et
envoie une requête HEAD par archive (quelques Ko en tout), sans rien
télécharger. Le téléchargement exige --telecharger.

Chaque version téléchargée est conservée avec sa date, sa taille et sa somme de
contrôle dans manifest.jsonl (ajout seulement). Une archive déjà connue n'est
retéléchargée que si ses en-têtes ont changé ; si son contenu est identique à
la dernière version, aucun doublon n'est stocké.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import tomllib
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

BASE = "https://opendata.justice-administrative.fr"
SOURCES = {"CE": "DCE", "CAA": "DCA", "TA": "DTA"}
USER_AGENT = "open-justice (+https://github.com/alanbouo/open-justice)"
MARGE_DISQUE = 1.1


def requete(url, methode="GET", tentatives=3):
    for essai in range(tentatives):
        try:
            req = Request(url, method=methode, headers={"User-Agent": USER_AGENT})
            return urlopen(req, timeout=60)
        except HTTPError as e:
            if e.code < 500 or essai == tentatives - 1:
                raise
        except URLError:
            if essai == tentatives - 1:
                raise
        time.sleep(2**essai)


def lire_config(chemin):
    chemin = Path(chemin).resolve()
    with open(chemin, "rb") as f:
        cfg = tomllib.load(f)
    return chemin.parent / Path(cfg["cold_dir"]).expanduser()


def lister(base, sources):
    """Renvoie les éléments distants : archives mensuelles et fichiers CSV."""
    elements = []
    for src in sources:
        rep = SOURCES[src]
        index = f"{base}/{rep}/"
        with requete(index) as r:
            html = r.read().decode("utf-8", "replace")
        for href, periode in re.findall(rf'href="([^"]*/{src}_(\d{{6}})\.zip)"', html):
            elements.append({"kind": "archive", "source": src, "period": periode,
                             "name": f"{src}_{periode}.zip", "url": urljoin(index, href)})
        nom = f"{src}_documents_reverses.csv"
        elements.append({"kind": "reverses", "source": src, "period": "",
                         "name": nom, "url": urljoin(index, nom)})
    return sorted(elements, key=lambda e: (e["kind"] != "archive", e["period"], e["source"]))


def entetes(url):
    with requete(url, "HEAD") as r:
        taille = r.headers.get("Content-Length")
        return {"size": int(taille) if taille else None,
                "last_modified": r.headers.get("Last-Modified"),
                "etag": r.headers.get("ETag")}


def lire_manifeste(chemin):
    derniers = {}
    if chemin.exists():
        for ligne in chemin.read_text(encoding="utf-8").splitlines():
            if ligne.strip():
                entree = json.loads(ligne)
                derniers[entree["name"]] = entree
    return derniers


def ajouter_manifeste(chemin, entree):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(entree, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def statut(info, dernier):
    if dernier is None:
        return "nouveau"
    for cle in ("size", "last_modified", "etag"):
        if info[cle] is not None and dernier.get(cle) is not None and info[cle] != dernier[cle]:
            return "modifié"
    return "à jour"


def telecharger(url, info, dossier, limite_debit):
    """Télécharge vers un fichier partiel et le vérifie. Renvoie (chemin, sha256, taille)."""
    dossier.mkdir(parents=True, exist_ok=True)
    partiel = dossier / f".part-{os.getpid()}"
    h = hashlib.sha256()
    n = 0
    debut = time.monotonic()
    try:
        with requete(url) as r, open(partiel, "wb") as f:
            while bloc := r.read(1 << 20):
                f.write(bloc)
                h.update(bloc)
                n += len(bloc)
                if limite_debit:
                    attendu = n / (limite_debit * 1e6)
                    ecoule = time.monotonic() - debut
                    if attendu > ecoule:
                        time.sleep(attendu - ecoule)
        if info["size"] is not None and n != info["size"]:
            raise OSError(f"taille reçue {n} différente de la taille annoncée {info['size']}")
        if url.endswith(".zip"):
            with zipfile.ZipFile(partiel) as z:
                if z.testzip() is not None:
                    raise OSError("archive zip corrompue")
    except BaseException:
        partiel.unlink(missing_ok=True)
        raise
    return partiel, h.hexdigest(), n


def go(octets):
    return f"{octets / 1e9:.2f} Go"


def main(argv=None):
    racine = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=racine / "config.toml")
    p.add_argument("--base-url", default=BASE)
    p.add_argument("--sources", default=",".join(SOURCES), help="CE,CAA,TA (défaut : toutes)")
    p.add_argument("--depuis", help="première période AAAAMM")
    p.add_argument("--jusqua", help="dernière période AAAAMM")
    p.add_argument("--archive", action="append", help="nom exact (répétable), ex. TA_202609.zip")
    p.add_argument("--telecharger", action="store_true", help="exécuter le téléchargement (sinon : plan seul)")
    p.add_argument("--max-go", type=float, help="plafond de données téléchargées pendant cette exécution")
    p.add_argument("--limite-debit", type=float, help="débit maximal en Mo/s")
    p.add_argument("--pause", type=float, default=1.0, help="secondes entre deux téléchargements")
    p.add_argument("--detail", action="store_true", help="afficher chaque élément du plan")
    a = p.parse_args(argv)

    sources = [s.strip().upper() for s in a.sources.split(",") if s.strip()]
    inconnues = set(sources) - set(SOURCES)
    if inconnues:
        p.error(f"sources inconnues : {', '.join(sorted(inconnues))}")
    froid = lire_config(a.config)
    manifeste = froid / "manifest.jsonl"
    derniers = lire_manifeste(manifeste)

    elements = lister(a.base_url.rstrip("/"), sources)
    if a.archive:
        elements = [e for e in elements if e["name"] in a.archive]
    else:
        elements = [e for e in elements if e["kind"] == "reverses"
                    or ((not a.depuis or e["period"] >= a.depuis) and (not a.jusqua or e["period"] <= a.jusqua))]

    plan = []
    for e in elements:
        info = entetes(e["url"])
        plan.append((e, info, statut(info, derniers.get(e["name"]))))

    a_faire = [x for x in plan if x[2] != "à jour"]
    compte = {s: sum(1 for x in plan if x[2] == s) for s in ("nouveau", "modifié", "à jour")}
    volume = sum(x[1]["size"] or 0 for x in a_faire)
    print(f"Plan : {len(plan)} éléments — {compte['nouveau']} nouveaux, {compte['modifié']} modifiés, "
          f"{compte['à jour']} à jour — {go(volume)} à télécharger")
    if a.detail:
        for e, info, s in plan:
            print(f"  {s:8} {e['name']:32} {go(info['size'] or 0)}")
    if not a.telecharger:
        print("Aucun téléchargement (plan seul). Relancer avec --telecharger pour exécuter.")
        return 0

    reste = a.max_go * 1e9 if a.max_go is not None else None
    froid.mkdir(parents=True, exist_ok=True)
    fait = 0
    for e, info, s in a_faire:
        taille = info["size"] or 0
        if reste is not None and taille > reste:
            print(f"Plafond atteint : arrêt avant {e['name']} ({go(taille)} > {go(reste)} restants).")
            break
        if taille * MARGE_DISQUE > shutil.disk_usage(froid).free:
            print(f"Disque insuffisant pour {e['name']} : arrêt.", file=sys.stderr)
            return 1
        sous = "archives" if e["kind"] == "archive" else "reverses"
        dossier = froid / sous / e["source"] / e["name"].removesuffix(".zip").removesuffix(".csv")
        try:
            partiel, sha, n = telecharger(e["url"], info, dossier, a.limite_debit)
        except (OSError, URLError, zipfile.BadZipFile) as err:
            print(f"Échec {e['name']} : {err}", file=sys.stderr)
            continue
        dernier = derniers.get(e["name"])
        if dernier and dernier["sha256"] == sha:
            partiel.unlink()
            chemin, doublon = dernier["path"], True
        else:
            horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            final = dossier / f"{horodatage}_{sha[:12]}{Path(e['name']).suffix}"
            partiel.rename(final)
            chemin, doublon = str(final.relative_to(froid)), False
        entree = {"kind": e["kind"], "source": e["source"], "name": e["name"], "period": e["period"],
                  "url": e["url"], "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "size": info["size"] if info["size"] is not None else n, "last_modified": info["last_modified"],
                  "etag": info["etag"], "sha256": sha, "path": chemin, "identique_a_la_precedente": doublon}
        ajouter_manifeste(manifeste, entree)
        derniers[e["name"]] = entree
        fait += 1
        if reste is not None:
            reste -= n
        print(f"{'identique' if doublon else 'stocké':9} {e['name']} ({go(n)})")
        time.sleep(a.pause)
    print(f"Terminé : {fait}/{len(a_faire)} éléments traités.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
