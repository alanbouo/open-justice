# Mesures

Constats mesurés, avec leur méthode. Ce qui est extrapolé est signalé comme tel.
Mesures faites le 22 octobre 2026, depuis un poste local, sans toucher aux
serveurs.

---

## 1. Justice administrative : structure du téléchargement

Source : <https://opendata.justice-administrative.fr>.

- Une archive zip par mois et par ordre de juridiction :
  `/DCE/AAAA/MM/CE_AAAAMM.zip` (Conseil d'État),
  `/DCA/AAAA/MM/CAA_AAAAMM.zip` (cours administratives d'appel),
  `/DTA/AAAA/MM/TA_AAAAMM.zip` (tribunaux administratifs).
  L'index de chaque répertoire (`/DCE/`, `/DCA/`, `/DTA/`) liste les archives.
- Disponibles : CE de 2021-06 à 2026-10 (65 archives), CAA de 2022-03 à 2026-10
  (56), TA de 2022-06 à 2026-10 (53).
- Les archives ne répondent pas aux requêtes `HEAD` sans le bon chemin (404) ;
  avec le bon chemin, la taille s'obtient par `Content-Length`.
- Chaque répertoire contient aussi un fichier `*_documents_reverses.csv`
  (`CE_`, `CAA_`, `TA_`). Colonnes : nom du fichier XML, numéro de décision,
  date de lecture, date de reversement, archive concernée. Le fichier CE compte
  1 655 lignes. Des décisions anciennes y figurent avec un reversement récent
  (exemple : lecture le 05/07/2023, reversement le 07/05/2025). Lecture
  probable : une archive d'un mois passé peut être complétée ou modifiée après
  coup **[interprétation, non confirmée par la documentation]**. Conséquence :
  l'ingestion ne peut pas se limiter aux nouveaux mois. Encodage du CSV :
  pas de l'UTF-8 (accents corrompus à la lecture).

## 2. Volumes d'archives (zip, mesure par `Content-Length`)

| Ordre | Archives | Taille cumulée |
|---|---|---|
| Conseil d'État | 65 | 0,12 Go |
| Cours administratives d'appel | 56 | 0,62 Go |
| Tribunaux administratifs | 53 | 3,63 Go |
| **Total** | **174** | **4,37 Go** |

Les mois varient : août 2026 pèse 41,3 Mo pour les TA, septembre 2026 69,1 Mo.

## 3. Un mois complet : septembre 2026

Téléchargé et décompressé (CE, CAA, TA), 0 échec d'analyse XML.

| | CE | CAA | TA | Total |
|---|---|---|---|---|
| Décisions (fichiers XML) | 368 | 2 268 | 20 216 | **22 852** |
| Archive zip | 1,09 Mo | 10,62 Mo | 69,07 Mo | 80,77 Mo |
| XML décompressé | 2,90 Mo | 31,98 Mo | 192,52 Mo | 227,40 Mo |
| Texte intégral seul | 2,36 Mo | 28,16 Mo | 162,98 Mo | 193,49 Mo |

- Rapport XML / zip : environ 2,8.
- Longueur du texte intégral (caractères), médiane / 90e centile / maximum :
  CE 4 163 / 11 542 / 46 813 ; CAA 10 314 / 20 016 / 78 834 ;
  TA 5 977 / 14 901 / 62 207.
- Compression du texte, décision par décision (zlib niveau 6, sur les TA) :
  ratio 2,97 (163,3 Mo → 55,0 Mo). La compression de PostgreSQL (TOAST) est en
  principe moins efficace que zlib : le ratio réel sera inférieur
  **[non mesuré]**.
- Répartition (TA) : 10 036 décisions et 10 180 ordonnances.

## 4. Structure réelle des fichiers

Elle diffère en partie de la documentation du site.

- Racine : `Donnees_Techniques` (`Identification`, `Date_Mise_Jour`), `Dossier`,
  `Audience`, `Decision`.
- `Dossier` : `Code_Juridiction`, `Nom_Juridiction`, `Numero_Dossier`,
  `Date_Lecture`, `Type_Decision`, `Type_Recours`, `Code_Publication`,
  `Avocat_Requerant`, `Numero_ECLI` (CE seulement), et **`Solution`**, balise
  absente de la documentation.
- `Audience` : `Date_Audience`, `Numero_Role` (renseignés pour une partie des
  décisions seulement), `Formation_Jugement`.
- `Decision/Texte_Integral` : les retours à la ligne sont des balises `<br/>`
  (la documentation parle de `<p>`).
- `Numero_ECLI` est absent des CAA et des TA sur ce mois.
- `Code_Publication` est vide pour 811 décisions CAA sur 2 268 et pour 12 477
  décisions TA sur 20 216 ; valeurs vues en plus de A à D et Z : `C+` et `R`.
- `Solution` est renseignée pour presque toutes les décisions. Valeurs les plus
  fréquentes (TA) : Rejet 7 582, Désistement 2 406, Satisfaction partielle
  2 023, Satisfaction totale 1 781, Rejet irrecevabilité manifeste alinéa 4
  1 645, Non-lieu 1 442. C'est la donnée la plus directement utile pour des
  indicateurs sur l'issue des recours, sans passer par le texte.
- Aucune balise d'identité de magistrat : les noms éventuels ne figurent que
  dans le texte intégral. `Avocat_Requerant` est un champ propre à part.

## 5. Estimations pour l'historique complet

Extrapolations à partir de septembre 2026 et des tailles d'archives. Ce ne sont
pas des mesures.

- Nombre de décisions : de l'ordre de 1,2 million (4,37 Go ÷ 80,8 Mo × 22 852),
  avec une forte incertitude selon les mois.
- XML décompressé : de l'ordre de 12 Go (4,37 Go × 2,8).
- Texte intégral : de l'ordre de 10 Go avant compression.
- Texte stocké dans PostgreSQL après compression : de l'ordre de 3,5 Go en
  prenant le ratio zlib, plus si la compression est moins efficace.

## 6. Non mesuré

- Taille réelle dans PostgreSQL (tables, TOAST, WAL).
- Taille d'un index de recherche plein texte en français.
- Temps de chargement, mémoire consommée pendant l'ingestion.
- Taille des seules métadonnées, sans texte.
- Volumes de Judilibre (nécessite un accès PISTE).

Disque libre au 22/10/2026 : coolify-1 14 Go, coolify-2 11 Go, coolify-3 7,5 Go
(sur 38 Go chacun).
