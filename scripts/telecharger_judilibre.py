#!/usr/bin/env python3
"""Télécharge les décisions de Judilibre vers la couche froide.

Par défaut, le script établit seulement un plan : il interroge /stats et affiche
le nombre de décisions par type de juridiction, sans rien télécharger. Le
téléchargement exige --telecharger.

La clé d'API PISTE se lit dans la variable PISTE_KEY_ID, sinon dans le fichier
désigné par `piste_env` de config.toml (hors du dépôt, ligne PISTE_KEY_ID=...).
Elle n'est jamais affichée, ni écrite dans le manifeste.

Chaque lot reçu est conservé tel quel (JSON brut) avec sa somme de contrôle dans
cold/judilibre/manifest.jsonl (ajout seulement). Le téléchargement reprend après
le lot enregistré si le script est relancé. Le curseur est le `next_batch` renvoyé par
l'API (dont `searchAfter`, qui combine score, date et identifiant) : `search_after`
seul, avec un identifiant, est ignoré et renvoie toujours le même lot.
"""
import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode
from urllib.request import Request, urlopen

BASE = "https://api.piste.gouv.fr/cassation/judilibre/v1.0"
BASE_BAC_A_SABLE = "https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0"
JURIDICTIONS = ("cc", "ca", "tj", "tcom")
USER_AGENT = "open-justice (+https://github.com/alanbouo/open-justice)"
MARGE_DISQUE = 200_000_000
FICHIER_CLE = "~/data/open-justice/piste.env"


def lire_config(chemin):
    chemin = Path(chemin).resolve()
    with open(chemin, "rb") as f:
        cfg = tomllib.load(f)
    return chemin.parent, cfg


def lire_cle(cfg, env=os.environ):
    cle = env.get("PISTE_KEY_ID")
    if not cle:
        fichier = Path(cfg.get("piste_env", FICHIER_CLE)).expanduser()
        if fichier.exists():
            if fichier.stat().st_mode & 0o077:
                print(f"Attention : {fichier} est lisible par d'autres comptes (chmod 600).", file=sys.stderr)
            for ligne in fichier.read_text(encoding="utf-8").splitlines():
                nom, _, valeur = ligne.partition("=")
                if nom.strip() == "PISTE_KEY_ID":
                    cle = valeur.strip().strip("\"'")
    if not cle:
        raise SystemExit("Clé PISTE introuvable : définir PISTE_KEY_ID ou créer le fichier "
                         f"{FICHIER_CLE} (ligne PISTE_KEY_ID=...), hors du dépôt.")
    return cle


def requete(base, chemin, params, cle, tentatives=4):
    url = f"{base}{chemin}?{urlencode(params, doseq=True)}"
    for essai in range(tentatives):
        try:
            req = Request(url, headers={"KeyId": cle, "Accept": "application/json", "User-Agent": USER_AGENT})
            with urlopen(req, timeout=120) as r:
                return r.read()
        except HTTPError as e:
            if e.code == 423:
                raise SystemExit("Accès bloqué par le service (423, activité suspecte) : arrêt. Ne pas insister.")
            if e.code in (401, 403):
                raise SystemExit(f"Accès refusé ({e.code}) : clé invalide ou droits insuffisants.")
            if (e.code == 429 or e.code >= 500) and essai < tentatives - 1:
                time.sleep(float(e.headers.get("Retry-After") or 5 * 2**essai))
                continue
            raise
        except URLError:
            if essai == tentatives - 1:
                raise
            time.sleep(2**essai)


def totaux(base, cle):
    """Renvoie {type de juridiction: nombre de décisions} d'après /stats."""
    corps = json.loads(requete(base, "/stats", {"keys": "jurisdiction"}, cle))
    res = corps.get("results", corps)
    # La documentation écrit « aggregated_data » ; son exemple écrit « aggregated_date ».
    seaux = res.get("aggregated_data") or res.get("aggregated_date") or []
    return {s["key"]["jurisdiction"]: s["decisions_count"] for s in seaux}


def lire_manifeste(chemin):
    entrees = []
    if chemin.exists():
        for ligne in chemin.read_text(encoding="utf-8").splitlines():
            if ligne.strip():
                entrees.append(json.loads(ligne))
    return entrees


def ajouter_manifeste(chemin, entree):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(entree, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def etat(entrees, juridiction):
    """Renvoie (curseur de reprise, terminé, lots déjà stockés) pour une juridiction."""
    propres = [e for e in entrees if e["jurisdiction"] == juridiction]
    lots = [e for e in propres if e["kind"] == "scan"]
    termine = any(e["kind"] == "fin" for e in propres)
    return (lots[-1].get("next_batch") if lots else None), termine, len(lots)


def telecharger_juridiction(base, cle, juridiction, froid, manifeste, taille, pause, max_lots):
    entrees = lire_manifeste(manifeste)
    curseur, termine, deja = etat(entrees, juridiction)
    if termine:
        print(f"{juridiction}: déjà téléchargé en entier ({deja} lots). Mises à jour : à traiter par /transactionalhistory.")
        return 0
    dossier = froid / "judilibre" / juridiction
    dossier.mkdir(parents=True, exist_ok=True)
    fait = 0
    while max_lots is None or fait < max_lots:
        if shutil.disk_usage(dossier).free < MARGE_DISQUE:
            raise SystemExit("Disque presque plein : arrêt.")
        if curseur:
            params = dict(parse_qsl(curseur))
        else:
            params = {"jurisdiction": juridiction, "batch_size": taille, "order": "asc", "date_type": "creation"}
        corps = requete(base, "/scan", params, cle)
        lot = json.loads(corps)
        resultats = lot.get("results") or []
        if not resultats:
            ajouter_manifeste(manifeste, {"kind": "fin", "jurisdiction": juridiction, "lots": deja + fait,
                                          "total": lot.get("total"),
                                          "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
            print(f"{juridiction}: terminé ({deja + fait} lots).")
            return fait
        sha = hashlib.sha256(corps).hexdigest()
        horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        final = dossier / f"{deja + fait:06d}_{horodatage}_{sha[:12]}.json"
        partiel = dossier / f".part-{os.getpid()}"
        partiel.write_bytes(corps)
        partiel.rename(final)
        curseur = lot.get("next_batch")
        ajouter_manifeste(manifeste, {
            "kind": "scan", "jurisdiction": juridiction, "lot": deja + fait, "n": len(resultats),
            "first_id": resultats[0]["id"], "last_id": resultats[-1]["id"], "next_batch": curseur, "total": lot.get("total"),
            "size": len(corps), "sha256": sha, "path": str(final.relative_to(froid)),
            "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "params": {k: v for k, v in params.items() if k not in ("search_after", "searchAfter")}})
        fait += 1
        print(f"stocké    {juridiction} lot {deja + fait - 1} ({len(resultats)} décisions, {len(corps) / 1e6:.1f} Mo)")
        if not curseur or len(resultats) < taille:
            ajouter_manifeste(manifeste, {"kind": "fin", "jurisdiction": juridiction, "lots": deja + fait,
                                          "total": lot.get("total"),
                                          "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
            print(f"{juridiction}: terminé ({deja + fait} lots).")
            return fait
        time.sleep(pause)
    return fait


def main(argv=None):
    racine = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=racine / "config.toml")
    p.add_argument("--base-url", help="adresse de l'API (défaut : production PISTE)")
    p.add_argument("--bac-a-sable", action="store_true", help="utiliser le bac à sable PISTE")
    p.add_argument("--juridictions", default=",".join(JURIDICTIONS), help="cc,ca,tj,tcom (défaut : toutes)")
    p.add_argument("--taille", type=int, default=1000, help="décisions par lot (1 000 au maximum)")
    p.add_argument("--max-lots", type=int, help="nombre maximal de lots pendant cette exécution")
    p.add_argument("--pause", type=float, default=1.0, help="secondes entre deux lots")
    p.add_argument("--telecharger", action="store_true", help="exécuter le téléchargement (sinon : plan seul)")
    a = p.parse_args(argv)

    juridictions = [j.strip() for j in a.juridictions.split(",") if j.strip()]
    inconnues = set(juridictions) - set(JURIDICTIONS)
    if inconnues:
        p.error(f"juridictions inconnues : {', '.join(sorted(inconnues))}")
    base = (a.base_url or (BASE_BAC_A_SABLE if a.bac_a_sable else BASE)).rstrip("/")
    dossier_config, cfg = lire_config(a.config)
    froid = dossier_config / Path(cfg["cold_dir"]).expanduser()
    manifeste = froid / "judilibre" / "manifest.jsonl"
    cle = lire_cle(cfg)

    par_type = totaux(base, cle)
    entrees = lire_manifeste(manifeste)
    print(f"Plan : Judilibre ({base})")
    for j in juridictions:
        n = par_type.get(j)
        curseur, termine, lots = etat(entrees, j)
        lots_prevus = f"{math.ceil(n / a.taille)} lots de {a.taille}" if n else "total inconnu"
        statut = "terminé" if termine else (f"{lots} lots déjà stockés" if lots else "à faire")
        print(f"  {j:5} {n if n is not None else '?':>10} décisions — {lots_prevus} — {statut}")
    if not a.telecharger:
        print("Aucun téléchargement (plan seul). Relancer avec --telecharger pour exécuter.")
        return 0

    for j in juridictions:
        telecharger_juridiction(base, cle, j, froid, manifeste, min(a.taille, 1000), a.pause, a.max_lots)
    return 0


if __name__ == "__main__":
    sys.exit(main())
