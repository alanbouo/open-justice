"""Tests du script de téléchargement, contre un serveur HTTP local (aucun accès réseau externe)."""
import io
import json
import sys
import tempfile
import threading
import unittest
import zipfile
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import telecharger  # noqa: E402


def faire_zip(contenu):
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as z:
        z.writestr("decision.xml", contenu)
    return tampon.getvalue()


class Serveur(BaseHTTPRequestHandler):
    fichiers = {}   # chemin -> (octets, last_modified)
    pages = {}      # chemin -> html

    def log_message(self, *a):
        pass

    def _repondre(self, avec_corps):
        if self.path in self.pages:
            corps, type_ = self.pages[self.path].encode(), "text/html"
            modif = None
        elif self.path in self.fichiers:
            (corps, modif), type_ = self.fichiers[self.path], "application/octet-stream"
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", type_)
        self.send_header("Content-Length", str(len(corps)))
        if modif:
            self.send_header("Last-Modified", modif)
        self.end_headers()
        if avec_corps:
            self.wfile.write(corps)

    def do_GET(self):
        self._repondre(True)

    def do_HEAD(self):
        self._repondre(False)


class TestTelecharger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        racine = Path(self.tmp.name)
        self.config = racine / "config.toml"
        self.config.write_text('cold_dir = "froid"\n')
        self.froid = racine / "froid"
        Serveur.fichiers = {
            "/DCE/2026/08/CE_202608.zip": (faire_zip("a"), "Mon, 01 Sep 2026 00:00:00 GMT"),
            "/DCE/2026/09/CE_202609.zip": (faire_zip("b"), "Mon, 01 Oct 2026 00:00:00 GMT"),
            "/DCE/CE_documents_reverses.csv": (b"a;b\n", "Mon, 01 Oct 2026 00:00:00 GMT"),
            "/DCA/CAA_documents_reverses.csv": (b"a;b\n", "Mon, 01 Oct 2026 00:00:00 GMT"),
            "/DTA/TA_documents_reverses.csv": (b"a;b\n", "Mon, 01 Oct 2026 00:00:00 GMT"),
        }
        Serveur.pages = {
            "/DCE/": '<a href="/DCE/2026/08/CE_202608.zip">x</a><a href="/DCE/2026/09/CE_202609.zip">y</a>',
            "/DCA/": "", "/DTA/": "",
        }
        self.http = HTTPServer(("127.0.0.1", 0), Serveur)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.http.server_port}"

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.tmp.cleanup()

    def lancer(self, *args):
        sortie = io.StringIO()
        with redirect_stdout(sortie):
            code = telecharger.main(["--config", str(self.config), "--base-url", self.base,
                                     "--pause", "0", *args])
        return code, sortie.getvalue()

    def manifeste(self):
        chemin = self.froid / "manifest.jsonl"
        return [json.loads(l) for l in chemin.read_text().splitlines()] if chemin.exists() else []

    def test_plan_seul_ne_telecharge_rien(self):
        code, sortie = self.lancer()
        self.assertEqual(code, 0)
        self.assertIn("5 éléments — 5 nouveaux", sortie)
        self.assertFalse(self.froid.exists())

    def test_telechargement_puis_a_jour(self):
        self.lancer("--telecharger")
        entrees = self.manifeste()
        self.assertEqual(len(entrees), 5)
        for e in entrees:
            fichier = self.froid / e["path"]
            self.assertTrue(fichier.exists())
            self.assertEqual(fichier.stat().st_size, e["size"])
        _, sortie = self.lancer("--telecharger")
        self.assertIn("5 à jour", sortie)
        self.assertEqual(len(self.manifeste()), 5)

    def test_archive_modifiee_cree_une_nouvelle_version(self):
        self.lancer("--telecharger", "--archive", "CE_202609.zip")
        Serveur.fichiers["/DCE/2026/09/CE_202609.zip"] = (faire_zip("b modifié"), "Tue, 02 Oct 2026 00:00:00 GMT")
        _, sortie = self.lancer("--telecharger", "--archive", "CE_202609.zip")
        self.assertIn("stocké", sortie)
        entrees = self.manifeste()
        self.assertEqual(len(entrees), 2)
        self.assertNotEqual(entrees[0]["sha256"], entrees[1]["sha256"])
        self.assertTrue((self.froid / entrees[0]["path"]).exists())
        self.assertTrue((self.froid / entrees[1]["path"]).exists())

    def test_en_tetes_changes_contenu_identique_sans_doublon(self):
        self.lancer("--telecharger", "--archive", "CE_202609.zip")
        octets, _ = Serveur.fichiers["/DCE/2026/09/CE_202609.zip"]
        Serveur.fichiers["/DCE/2026/09/CE_202609.zip"] = (octets, "Tue, 02 Oct 2026 00:00:00 GMT")
        _, sortie = self.lancer("--telecharger", "--archive", "CE_202609.zip")
        self.assertIn("identique", sortie)
        entrees = self.manifeste()
        self.assertTrue(entrees[1]["identique_a_la_precedente"])
        self.assertEqual(entrees[0]["path"], entrees[1]["path"])
        self.assertEqual(len(list((self.froid / "archives/CE/CE_202609").glob("*.zip"))), 1)

    def test_plafond_arrete_avant_depassement(self):
        _, sortie = self.lancer("--telecharger", "--archive", "CE_202608.zip",
                                "--archive", "CE_202609.zip", "--max-go", "0.0000001")
        self.assertIn("Plafond atteint", sortie)
        self.assertEqual(self.manifeste(), [])

    def test_filtre_par_periode(self):
        _, sortie = self.lancer("--depuis", "202609")
        self.assertIn("4 éléments", sortie)

    def test_taille_incoherente_rejetee(self):
        info = {"size": 999999, "last_modified": None, "etag": None}
        with self.assertRaises(OSError):
            telecharger.telecharger(f"{self.base}/DCE/2026/09/CE_202609.zip", info, self.froid / "x", None)
        self.assertEqual(list((self.froid / "x").glob(".part-*")), [])


if __name__ == "__main__":
    unittest.main()
