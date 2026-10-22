# Open Justice

Plateforme ouverte pour voir comment fonctionne la justice en France : rendre
lisibles, pour les citoyens, les décisions de justice publiées en open data.

Nom de domaine : `open-justice.fr` (enregistré le 22 octobre 2026).

## État du projet

Idée à l'étude. Aucune ligne de code, aucun produit, aucun utilisateur.
La recherche préalable est dans [`recherche.md`](recherche.md).

## Intention

- Informer les citoyens sur l'exécution de la justice en France.
- S'appuyer uniquement sur des données publiques et ouvertes.
- Rester un projet ouvert : code et méthode publics.

## Architecture retenue

Les décisions brutes (archives zip et XML) ne sont pas hébergées par la
plateforme en ligne. Elles sont stockées sur un disque à part, où elles sont
téléchargées et traitées. Seules les **statistiques** qui en sont calculées sont
publiées sur le site (open-justice.fr).

Trois couches :

- **Froide** (`cold_dir`) : archives zip d'origine, jamais modifiées. Chaque
  version téléchargée est conservée avec sa date et sa somme de contrôle, car
  des archives passées peuvent être complétées après coup (voir `mesures.md`).
  Provisoirement sur le Mac (`~/data/open-justice/cold`), à déplacer sur un
  disque externe. Un seul disque pour l'instant, sans copie.
- **De travail** (`work_dir`, `~/data/open-justice/work`) : XML décompressés,
  Parquet, DuckDB.
  Reconstructible depuis la couche froide.
- **Publiée** : statistiques agrégées uniquement, sur le site.

Raison : le volume du texte intégral (voir `mesures.md`) est disproportionné par
rapport au disque disponible sur les serveurs, et le site n'a pas besoin de
republier les décisions pour informer.

## Utilisation

Téléchargement des archives vers la couche froide (Python 3.11 ou plus, sans
dépendance) :

```
python3 scripts/telecharger.py                  # plan seul : aucun téléchargement
python3 scripts/telecharger.py --telecharger    # exécute le plan
```

Options utiles : `--sources CE,CAA,TA`, `--depuis AAAAMM`, `--jusqua AAAAMM`,
`--archive TA_202609.zip`, `--max-go` (plafond de données par exécution),
`--limite-debit` (Mo/s). Tests : `python3 -m unittest discover -s tests`.

## Périmètre

Le reste est à définir. Les points qui le contraignent déjà sont dans
`recherche.md` : le pénal n'est pas encore ouvert (échéances 2027-2028) et le
profilage nominatif des magistrats est interdit par la loi.

## Licence

Code : [MIT](LICENSE). Statistiques publiées : licence à choisir.

## Contribuer

Les données restent hors du dépôt, qui est public. Après avoir cloné, activer
le garde-fou qui refuse les commits de données :

```
git config core.hooksPath scripts/hooks
```
