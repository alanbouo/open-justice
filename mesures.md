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
- Disponibles : CE de 2021-06 à 2026-10 (64 archives : août 2021 est absent de
  l'index), CAA de 2022-03 à 2026-10 (56), TA de 2022-06 à 2026-10 (53).
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
| Conseil d'État | 64 | 0,12 Go |
| Cours administratives d'appel | 56 | 0,62 Go |
| Tribunaux administratifs | 53 | 3,63 Go |
| **Total** | **173** | **4,37 Go** |

Téléchargement complet effectué le 22/10/2026 : 173 archives et 3 fichiers CSV
(176 éléments), 4,37 Go, sommes de contrôle et tailles vérifiées, aucun fichier
manquant ni partiel. Stockés dans la couche froide (provisoire, sur le Mac).

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
- Aucune balise d'identité de magistrat. Mais le texte intégral porte leurs noms :
  dans le bloc de signature et aussi dans les visas (désignation du juge, rapport
  entendu à l'audience, liste des membres de la formation), constaté sur 7
  décisions (voir `variables-texte.md` ; fréquence sur l'ensemble **[non mesurée]**). Les parties
  sont pseudonymisées (initiales). `Avocat_Requerant` est un champ propre à
  part. Toute extraction doit donc exclure ces mentions.

## 5. Historique complet : décisions (mesuré le 22/10/2026)

Script : `scripts/extraire_metadonnees.py` (lecture directe des 173 archives, 27 s,
métadonnées seules vers `work/metadonnees.csv`, 193 Mo, hors dépôt).

- **1 155 525 décisions** (l'estimation initiale était d'environ 1,2 million).
  22 fichiers XML n'ont pas pu être analysés (non localisés).
- Par ordre : CE 39 857 (2021-06 à 2026-10), CAA 127 209 (2022-03 à 2026-10),
  TA 988 459 (2022-06 à 2026-10).
- Par an de lecture (TA) : 2023 208 548, 2024 217 453, 2025 246 804 ; 2026
  (jusqu'en octobre) 217 225. Mois d'archive TA : de 271 à 27 787, médiane 18 776.
- Le nom de fichier seul n'identifie pas une décision (8 815 noms apparaissent
  plusieurs fois). Le triplet ordre + code juridiction + nom de fichier est unique.
- Aucune décision hors de son mois d'archive (date de lecture = mois de l'archive).
- Texte intégral : 10,3 milliards de caractères (CE 248 M, CAA 1 604 M, TA 8 463 M).
  Médiane : CE 4 315, CAA 10 857, TA 6 956 caractères ; maximum 280 799.
- Limite : ce ne sont pas toutes les décisions rendues, ce sont les décisions **publiées**. Le
  rapport au nombre total de décisions rendues **[non mesuré]**.

## 6. Contenu des métadonnées (premier regard)

- 50 codes de juridiction distincts. Plus gros volumes : TA Paris 116 211, TA Nantes
  68 095, TA Cergy-Pontoise 67 079 ; CAA Paris 23 350. Le CE est identifié
  « Section du Contentieux » (39 848 sur 39 857).
- Type de décision : TA 586 580 décisions et 401 879 ordonnances ; CAA 72 135 et
  55 074 ; CE 26 234 et 13 623. Plus d'un tiers des décisions sont des ordonnances.
- Type de recours : excès de pouvoir 679 643 et plein contentieux 214 979 (TA) ;
  vide pour 88 757 décisions TA (9 %). 35 libellés distincts, casse différente
  selon l'ordre (« Excès de pouvoir » / « excès de pouvoir »). Mesuré le
  24/10/2026 : 28 libellés après passage en minuscules et suppression des
  espaces ; restent des variantes de fond (« exécution d'un jugement » et
  « exécution décision justice adm » ; « rectif. erreur matérielle » et
  « rectif. d'erreur matérielle » ; « contentieux répressif » avec un espace
  double ; « fiscal » et « contentieux fiscal »).
- `Solution` : 177 libellés distincts, jamais vide sauf CE (8,7 %). TA : rejet 42,1 %,
  satisfaction partielle 11,4 %, satisfaction totale 10,7 %, désistement 8,7 %,
  rejet par irrecevabilité manifeste 7,4 %, non-lieu 5,9 %. CAA : rejet 44,5 %,
  rejet R.222-1 (appel manifestement infondé) 29,0 %, satisfaction partielle 9,4 %,
  totale 7,1 %. CE : rejet par non-admission (PAPC) 27,8 %, rejet 15,5 %.
  **Défaut mesuré le 24/10/2026 : pour 24 982 ordonnances (TA 24 465, CAA 517),
  `Solution` contient un nom de juridiction (« TA Montreuil », « TA Caen »…) et
  non une solution.** Toutes sont des ordonnances ; le sens n'est pas documenté
  (lecture probable : renvoi vers la juridiction nommée **[non vérifié]**). Le
  référentiel `solution_norm` doit les traiter à part, sinon elles gonflent le
  nombre de libellés et faussent les parts d'issue.
  **Un « rejet » n'est pas un résultat pour le requérant ou l'administration** :
  la partie qui gagne n'est pas dans les métadonnées. Les libellés changent
  d'un ordre à l'autre ; il faudra un référentiel.
- `Code_Publication` vide pour 480 680 décisions TA sur 988 459 (49 %) et 34 737
  CAA sur 127 209 (27 %). Sens du code **[non documenté, non vérifié]**.
  Mesuré le 24/10/2026, le code suit le type de décision : au CE, `Z` couvre
  13 049 ordonnances sur 13 623 et 583 décisions, `C` et `D` presque uniquement
  des décisions ; au TA, `D` couvre 133 385 ordonnances et 82 641 décisions, `C`
  262 060 décisions et 27 851 ordonnances. Les valeurs `R` (TA 152, CAA 1) et
  `""` (TA 2, guillemets littéraux) sont rares. Corrélation seulement : le sens
  des lettres reste à trouver dans la documentation de l'éditeur.
- `Date_Audience` renseignée : TA 46 %, CAA 55 %, CE 61 %. Pour celles où elle
  existe, délai audience → lecture : médiane 14 jours (TA), 19 (CAA), 23 (CE).
  **Ce n'est pas la durée du procès** : la date d'enregistrement de la requête
  n'est pas dans les métadonnées.
- `Formation_Jugement` : TA 46 % (« Reconduite à la frontière » 36 264, chambres),
  CAA 76 %, CE 98 %. Libellés non normalisés (« 1ère chambre » / « 1ère Chambre »).
  Mesuré le 24/10/2026 : pour les CAA, « Juge des référés » ne désigne pas un référé. Sur 800
  arrêts examinés (janvier 2023, juin 2025), 146 portent ce libellé, presque tous des
  ordonnances, et les trois dont j'ai lu les visas sont des appels de fond (refus de titre de
  séjour, restitution fiscale). Dans les 422 décisions de CAA de l'échantillon élargi qui
  portent le libellé, 18 seulement citent un article de référé du CJA. Au CE, au contraire,
  100 des 103 décisions étiquetées « référé » en citent un. `formation_norm` doit donc se
  méfier de ce libellé pour les CAA **[échantillon limité, cause non identifiée]**.
- ECLI : CE 94,6 % ; CAA et TA 0 %.
- `Date_Mise_Jour` : pour 98 155 des 98 429 décisions TA des archives de 2022, elle
  est postérieure de plus d'un an à la lecture ; 0 en 2026. Cause **[inconnue]**
  (nouvelle version, repseudonymisation ?). À élucider avant de s'en servir.
  Mesuré le 24/10/2026 : pour les décisions TA lues en 2022, 86 dates de mise à
  jour distinctes, concentrées du 17 au 26 mars 2025 (au plus 18 321 le 21 mars) ;
  tous millésimes de lecture confondus, 167 156 décisions TA portent une mise à
  jour en mars 2025. Écart de plus d'un an : TA 2023 39 123 décisions sur
  208 548, 2024 5 518, 2025 2 671, 2026 0 ; il existe aussi pour le CE (2021
  1 712 sur 3 561) et les CAA (2023 3 804). Cela ressemble à une opération en
  lot de mars 2025 **[cause non confirmée]**, qui touche aussi les décisions de
  2023.

## 7. Judilibre : téléchargement complet et contenu des champs (mesuré le 28/10/2026)

Téléchargement par `/scan`, lots de 1 000, clé de production, dans `cold/judilibre/`
(hors dépôt). Lots chaînés par le `next_batch` renvoyé par l'API (dont `searchAfter`) ;
`search_after` seul, avec un identifiant, est ignoré et redonne toujours le même lot.
Aucun doublon d'identifiant dans les quatre juridictions. Photographie du 28/10/2026 :
les mises à jour ultérieures ne sont pas traitées.

| Juridiction | Décisions | Total lu avant téléchargement | Taille | Période de `decision_date` |
|---|---|---|---|---|
| Cour de cassation (`cc`) | 569 520 | 569 520 | 4,4 Go | 1860 à 2026 (10 000 à 17 000 par an depuis 2019) |
| Cours d'appel (`ca`) | 646 601 | 646 242 | 12 Go | 547 800 en 2020 ou après, 1 868 en 2021, 75 271 en 2022 ; 6 dates aberrantes (année 0201) |
| Tribunaux judiciaires (`tj`) | 765 280 | 764 444 | 9,4 Go | 2023 (2 274) à 2026 ; 326 104 en 2025 |
| Tribunaux de commerce (`tcom`) | 202 072 | 201 338 | 1,4 Go | 2025 et 2026 (5 en 2024) |

L'écart entre les décisions stockées et le total lu avant téléchargement est
probablement dû à des ajouts pendant le téléchargement **[non vérifié]**. `/stats` ne
renvoie que `cc` ; les totaux de `ca`, `tj` et `tcom` viennent du champ `total` de `/scan`.
Ce que représente Judilibre par rapport à l'ensemble des décisions rendues : **non mesuré**.

Texte (`text`, en caractères) : présent pour 100 % des décisions.

| | Médiane | 10 % à 90 % | Minimum |
|---|---|---|---|
| `cc` | 3 879 | 1 706 à 15 452 | 90 |
| `ca` | 13 360 | 3 724 à 34 351 | 1 |
| `tj` | 9 993 | 2 603 à 20 973 | 32 |
| `tcom` | 4 939 | 2 241 à 12 534 | 325 |

Part de décisions dont le champ est présent et non vide :

| Champ | `cc` | `ca` | `tj` | `tcom` |
|---|---|---|---|---|
| `solution` (code) | 100 % | 100 %, mais 612 028 sur 646 601 valent « other » | 100 %, 232 libellés | absent |
| `solution_alt` (issue en toutes lettres) | 7,8 % | 89,8 % (173 libellés) | absent | absent |
| `nac` (code de nature d'affaire) | 0 % | 90,5 % (641 codes) | 100 % (590 codes) | 0 % |
| `themes` | 34,6 % (107 060 libellés distincts, mots-clés libres) | 76,3 % (6 666) | 28,7 % (622) | absent |
| `chamber` | 100 % (11 valeurs) | 90,5 % (597) | 100 % (1 493 libellés, variantes d'écriture) | 78,5 % (601) |
| `zones` (introduction, exposé, motivations, dispositif) | 66,1 % | 90,2 % | 99,3 % | 99,9 % |
| `contested` (décision attaquée) | 88,8 % | 2,7 % | 0 % | 0 % |
| `visa` | 43,8 % | 1,0 % | 0 % | 0 % |
| `summary` | 22,0 % | absent | absent | absent |

`portalis` est vide partout. `files` et `rapprochements` sont vides pour `ca`, `tj` et
`tcom`. Les libellés de `solution_alt` de `ca` portent des espaces en fin de chaîne qui
dédoublent les valeurs distinctes. Cours d'appel les plus représentées : Paris 136 467,
Aix-en-Provence 71 871, Versailles 43 005. Nombre de textes presque vides (sous un seuil
d'exploitation) : **non mesuré**. Pseudonymisation du texte : **non vérifiée**.

## 8. Non mesuré

- Taille réelle dans PostgreSQL (tables, TOAST, WAL).
- Taille d'un index de recherche plein texte en français.
- Temps de chargement, mémoire consommée pendant l'ingestion.
- Quotas de débit de l'API Judilibre.

Disque libre au 22/10/2026 : coolify-1 14 Go, coolify-2 11 Go, coolify-3 7,5 Go
(sur 38 Go chacun).
