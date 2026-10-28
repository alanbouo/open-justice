"""Tests du téléchargement Judilibre, contre un faux serveur local (aucune vraie donnée, aucun accès externe)."""
import io
import json
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import telecharger_judilibre as tj  # noqa: E402

CLE = "cle-de-test"
DECISIONS = {"cc": 5, "ca": 7, "tj": 0, "tcom": 0}   # nombre de décisions inventées par type de juridiction


def inventer(juridiction, i):
    return {"id": f"{juridiction}{i:04d}", "jurisdiction": juridiction, "text": f"texte inventé {i}"}


class Faux(BaseHTTPRequestHandler):
    appels = []

    def log_message(self, *a):
        pass

    def _json(self, code, corps):
        octets = json.dumps(corps).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(octets)))
        self.end_headers()
        self.wfile.write(octets)

    def do_GET(self):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        Faux.appels.append((url.path, q))
        if self.headers.get("KeyId") != CLE:
            return self._json(401, {})
        if url.path == "/stats":
            return self._json(200, {"query": q, "results": {"total_decisions": sum(DECISIONS.values()),
                "aggregated_data": [{"key": {"jurisdiction": j}, "decisions_count": n} for j, n in DECISIONS.items()]}})
        if url.path == "/scan":
            j, taille = q["jurisdiction"], int(q["batch_size"])
            toutes = [inventer(j, i) for i in range(DECISIONS[j])]
            debut = 0
            # Comme l'API réelle : seul `searchAfter` fait avancer, `search_after` seul est ignoré.
            if "searchAfter" in q:
                debut = int(q["searchAfter"].split("&")[-1]) + 1
            lot = toutes[debut:debut + taille]
            suite = debut + taille < len(toutes)
            prochain = urlencode({**{k: v for k, v in q.items() if k != "searchAfter"},
                                  "search_after": lot[-1]["id"] if lot else "",
                                  "searchAfter": f"0&-1&{debut + len(lot) - 1}"})
            return self._json(200, {"results": lot, "total": len(toutes), "batch_size": taille,
                                    "next_batch": prochain if suite else None})
        self._json(404, {})


class TestJudilibre(unittest.TestCase):
    def setUp(self):
        Faux.appels = []
        self.tmp = tempfile.TemporaryDirectory()
        racine = Path(self.tmp.name)
        self.config = racine / "config.toml"
        self.config.write_text('cold_dir = "froid"\n')
        self.froid = racine / "froid"
        self.http = HTTPServer(("127.0.0.1", 0), Faux)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.http.server_port}"
        self.env = {"PISTE_KEY_ID": CLE}
        self._ancien = tj.os.environ.get("PISTE_KEY_ID")
        tj.os.environ["PISTE_KEY_ID"] = CLE

    def tearDown(self):
        if self._ancien is None:
            tj.os.environ.pop("PISTE_KEY_ID", None)
        else:
            tj.os.environ["PISTE_KEY_ID"] = self._ancien
        self.http.shutdown()
        self.http.server_close()
        self.tmp.cleanup()

    def lancer(self, *args):
        sortie = io.StringIO()
        with redirect_stdout(sortie):
            code = tj.main(["--config", str(self.config), "--base-url", self.base, "--pause", "0", *args])
        return code, sortie.getvalue()

    def manifeste(self):
        chemin = self.froid / "judilibre" / "manifest.jsonl"
        return [json.loads(l) for l in chemin.read_text().splitlines()] if chemin.exists() else []

    def test_plan_seul_ne_telecharge_rien(self):
        code, sortie = self.lancer()
        self.assertEqual(code, 0)
        self.assertIn("cc", sortie)
        self.assertNotIn("/scan", [p for p, _ in Faux.appels])
        self.assertFalse(self.froid.exists())

    def test_telechargement_en_plusieurs_lots_et_fin(self):
        self.lancer("--telecharger", "--juridictions", "ca", "--taille", "3")
        lots = [e for e in self.manifeste() if e["kind"] == "scan"]
        self.assertEqual([e["n"] for e in lots], [3, 3, 1])
        self.assertEqual(lots[0]["first_id"], "ca0000")
        self.assertEqual(lots[-1]["last_id"], "ca0006")
        self.assertEqual(self.manifeste()[-1]["kind"], "fin")
        for e in lots:
            self.assertTrue((self.froid / e["path"]).exists())

    def test_reprise_apres_interruption(self):
        self.lancer("--telecharger", "--juridictions", "ca", "--taille", "3", "--max-lots", "1")
        self.assertEqual(len([e for e in self.manifeste() if e["kind"] == "scan"]), 1)
        self.lancer("--telecharger", "--juridictions", "ca", "--taille", "3")
        lots = [e for e in self.manifeste() if e["kind"] == "scan"]
        self.assertEqual([e["first_id"] for e in lots], ["ca0000", "ca0003", "ca0006"])

    def test_deja_termine_ne_retelecharge_pas(self):
        self.lancer("--telecharger", "--juridictions", "cc", "--taille", "10")
        avant = len([p for p, _ in Faux.appels if p == "/scan"])
        _, sortie = self.lancer("--telecharger", "--juridictions", "cc", "--taille", "10")
        self.assertEqual(len([p for p, _ in Faux.appels if p == "/scan"]), avant)
        self.assertIn("déjà téléchargé", sortie)

    def test_juridiction_vide_se_termine(self):
        _, sortie = self.lancer("--telecharger", "--juridictions", "tj")
        self.assertIn("terminé", sortie)
        self.assertEqual(self.manifeste()[-1]["kind"], "fin")

    def test_mauvaise_cle_refusee(self):
        tj.os.environ["PISTE_KEY_ID"] = "mauvaise"
        with self.assertRaises(SystemExit) as e:
            self.lancer()
        self.assertIn("refusé", str(e.exception))

    def test_la_cle_n_est_ni_dans_le_manifeste_ni_dans_la_sortie(self):
        _, sortie = self.lancer("--telecharger", "--juridictions", "cc")
        self.assertNotIn(CLE, sortie)
        self.assertNotIn(CLE, (self.froid / "judilibre" / "manifest.jsonl").read_text())

    def test_cle_introuvable(self):
        tj.os.environ.pop("PISTE_KEY_ID")
        with self.assertRaises(SystemExit) as e:
            tj.lire_cle({"piste_env": str(Path(self.tmp.name) / "absent.env")}, env={})
        self.assertIn("introuvable", str(e.exception))

    def test_cle_lue_dans_le_fichier(self):
        fichier = Path(self.tmp.name) / "piste.env"
        fichier.write_text('PISTE_KEY_ID="abc"\n')
        fichier.chmod(0o600)
        self.assertEqual(tj.lire_cle({"piste_env": str(fichier)}, env={}), "abc")


if __name__ == "__main__":
    unittest.main()
