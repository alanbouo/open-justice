# Statistiques réalisables sur la justice administrative

État au 22 octobre 2026. Base : 1 155 525 décisions (`mesures.md`). Chaque ligne
dit sur quoi elle repose. Ce qui n'est pas testé est marqué **[non testé]**.

Règle commune : aucune ventilation par magistrat ni par greffier (article 33 de
la loi de 2019, article L.10 du CJA). Les parties sont déjà pseudonymisées ; ne
jamais publier de cellule trop petite pour rester anonyme (seuil à fixer).

## A. Métadonnées seules (mesuré, réalisable maintenant)

1. **Volumes** de décisions publiées, par ordre, juridiction (50 codes), mois,
   année. Décision ou ordonnance.
2. **Issue des recours** (`Solution`, 177 libellés) : part de rejets,
   satisfactions totale et partielle, désistements, non-lieux, par ordre,
   juridiction, type de recours, année. Demande un référentiel regroupant les
   libellés. Limite : ne dit pas qui gagne (voir B).
3. **Rejets par voie rapide** : ordonnances de rejet sans audience
   (irrecevabilité manifeste, R.222-1, non-admission des pourvois au Conseil
   d'État), part dans l'ensemble, évolution.
4. **Nature du contentieux** (`Type_Recours`, 35 libellés) : excès de pouvoir,
   plein contentieux, pensions, exécution, etc. ; 9 % de vides côté TA.
5. **Part des ordonnances** et, parmi elles, leur issue (désistement, rejet).
6. **Délai audience → lecture** (médiane de 14 à 23 jours), pour les 46 à 61 %
   de décisions qui ont une date d'audience. Ce n'est pas la durée du procès.
7. **Composition de jugement** (`Formation_Jugement`) : juge des référés,
   « reconduite à la frontière », chambres, formation à 3 ; couverture
   TA 46 %, CAA 76 %, CE 98 %. Regrouper les libellés ; rester au niveau de la
   formation, jamais des personnes.
8. **Longueur des décisions** (médiane, p90) par ordre et type de décision.
9. **Comparaison entre juridictions** (taux de satisfaction, part
   d'ordonnances) : à normaliser par la nature du contentieux avant de publier,
   sinon la comparaison est trompeuse.
10. **Lien appel / cassation** : taux de renvoi (« Renvoi après cassation » : 2 289
    décisions CE sur 39 857). Rapprocher un jugement et son appel n'est pas
    possible avec les seules métadonnées **[non testé]**.

## B. Avec le texte intégral (faisabilité testée sur un échantillon)

Échantillon : un mois de 2025 tiré au hasard par ordre (TA 3 000, CAA 2 540,
CE 517 décisions). Les pourcentages sont la part de décisions contenant le motif
et non une statistique exacte ; les extractions elles-mêmes sont à valider.

11. **Date d'enregistrement de la requête** : formule « enregistrée le … »
    présente dans 95 % (TA), 95 % (CAA), 46 % (CE). Si elle s'extrait sans
    erreur, elle donne **la durée de jugement** (requête → lecture), la
    statistique la plus attendue. Plusieurs dates et formulations (requête,
    mémoires) : **extraction non validée**.
12. **Frais irrépétibles** (article L.761-1 du CJA) : cité dans 65 % (TA),
    87 % (CAA), 77 % (CE). Montants alloués (« somme de … euros ») présents dans
    69 %, 89 % et 76 %. Permet : montant médian alloué, part des décisions qui
    en allouent, à qui (État, collectivité) **[non testé]**.
13. **Qui gagne** : croiser `Solution` avec la qualité du défendeur (État,
    commune, département, établissement public) lue dans le texte **[non testé]**.
    Donnerait le taux de réussite des citoyens contre les administrations.
14. **Thèmes** par mots-clés ou classification : étrangers (titre de séjour,
    OQTF : 17 % des décisions TA, 37 % CAA), fonction publique, fiscal (7 %
    TA), urbanisme (6 %), pensions (16 %). Mots-clés bruts, très imparfaits
    (le motif « étrangers » ratisse trop large) : **non fiable en l'état**.
15. **Contentieux de masse** (étrangers, référés, fiscal) : poids de chaque
    thème et issue par thème, une fois la classification validée.
16. **Visas et textes cités** (codes, articles les plus invoqués) **[non testé]**.
17. **Délais de référé** et mesures d'urgence, si la date de saisine s'extrait
    **[non testé]**.

## C. Hors de portée avec ces données

- Qui l'emporte, côté citoyen ou administration, sans lecture du texte (B13).
- Toute statistique sur la pratique d'un magistrat ou d'un greffier : interdite.
- Représentativité par rapport au total des décisions rendues : non mesurée.
- Justice judiciaire et pénale : autre source (Judilibre), pas encore chargée.
- Évolution avant 2021 (CE) ou 2022 (CAA, TA) : les données ne remontent pas.

## D. Résultats calculés (provisoires)

Calculés le 26 octobre 2026 sur les 1 155 525 décisions, avec les variables
de `variables-texte.md` dont l'exactitude n'est pas mesurée (accord de 90 à 94 %
avec la solution codée par la juridiction pour l'issue). À lire comme des ordres de
grandeur, pas comme des taux précis. Agrégats seulement : aucune cellule
inférieure à 300 décisions n'est publiée ici.

### D1. Issue du recours selon le domaine

`issue_requerant` est vue du côté de **celui qui saisit le juge**. En appel et en
cassation, c'est l'appelant, qui peut être l'administration : la séparation selon
la nature de l'appelant est en D2. Les ordonnances sont incluses, d'où une forte
part de `neutre` (désistement, non-lieu, radiation, transmission, expertise).
Part de chaque issue en % ; « sans domaine » = aucun thème trouvé (surtout des
ordonnances).

| Tribunaux administratifs | Décisions | Gagne | Partiel | Perd | Neutre |
|---|---|---|---|---|---|
| Étrangers | 427 499 | 7,6 | 17,3 | 60,0 | 15,1 |
| Sans domaine | 104 643 | 5,6 | 2,6 | 43,5 | 48,3 |
| Fonction publique | 85 701 | 6,1 | 11,3 | 52,1 | 30,5 |
| Sécurité sociale, aides | 69 936 | 5,6 | 7,4 | 67,4 | 19,7 |
| Logement | 56 294 | 38,0 | 19,4 | 28,3 | 14,2 |
| Urbanisme | 44 197 | 10,7 | 11,5 | 49,3 | 28,4 |
| Sécurité et police | 41 633 | 5,8 | 10,3 | 61,0 | 22,9 |
| Fiscal | 41 299 | 3,4 | 8,8 | 62,4 | 25,4 |
| Électoral | 4 922 | 55,8 | 5,7 | 34,8 | 3,6 |

| Cours administratives d'appel | Décisions | Gagne | Partiel | Perd | Neutre |
|---|---|---|---|---|---|
| Étrangers | 68 562 | 6,8 | 8,0 | 82,7 | 2,5 |
| Fiscal | 11 396 | 8,6 | 12,9 | 72,1 | 6,4 |
| Fonction publique | 8 496 | 11,0 | 15,9 | 63,3 | 9,8 |
| Urbanisme | 7 959 | 12,3 | 11,3 | 62,6 | 13,7 |

| Conseil d'État | Décisions | Gagne | Partiel | Perd | Neutre |
|---|---|---|---|---|---|
| Sans domaine | 4 993 | 3,8 | 1,7 | 71,5 | 23,0 |
| Fiscal | 4 870 | 17,8 | 4,7 | 71,9 | 5,6 |
| Étrangers | 4 451 | 7,5 | 3,3 | 84,5 | 4,7 |
| Fonction publique | 4 101 | 7,4 | 6,4 | 79,1 | 7,1 |

Lecture, avec les réserves :
- Les taux de `gagne` + `partiel` les plus élevés sont logement (57 % des TA) et électoral (62 %). Je n'ai pas vérifié leur cause ; l'hypothèse pour le logement est le recours pour droit au logement opposable, pas relu.
- Parmi les décisions rendues au fond (hors ordonnances, issues gagne, partiel ou perd), la requête est accueillie en tout ou partie dans 35 % des cas en TA et en CAA, 21 % au CE.
- Droit des étrangers au TA, part de `perd` selon le sous-domaine (ordonnances incluses) : titre de séjour 56,2 % (234 967 décisions), OQTF 68,9 % (100 767), asile 62,9 % (48 434) ; le sous-domaine n'est pas précisé pour 11 165 décisions.
- Le domaine « sans domaine » regroupe des affaires closes sans examen du fond ; il sous-représente ces affaires dans chaque domaine nommé.

### D2. Issue du recours selon la nature de l'appelant ou du requérant

La nature est celle du premier requérant du texte (`requerants_natures`) : `État`
(préfet, ministre, directions), `physique` (particulier), `morale` (société,
association, syndicat, collectivité, établissement public). `inconnue` = nature non
déterminée. Décisions au sens strict (hors ordonnances). Part en %.

| Ordre | Qui saisit | Décisions | Gagne | Partiel | Perd | Neutre |
|---|---|---|---|---|---|---|
| TA | Particulier | 449 862 | 9,3 | 21,3 | 59,0 | 10,4 |
| TA | Personne morale | 64 484 | 11,6 | 18,2 | 57,1 | 13,0 |
| TA | État | 23 951 | 35,7 | 11,3 | 44,7 | 8,3 |
| CAA | Particulier | 41 452 | 10,7 | 18,3 | 69,5 | 1,5 |
| CAA | Personne morale | 15 689 | 14,3 | 20,4 | 62,3 | 3,0 |
| CAA | État | 7 496 | 37,9 | 18,8 | 41,6 | 1,7 |
| CE | Particulier | 12 928 | 10,1 | 4,7 | 83,7 | 1,5 |
| CE | Personne morale | 9 286 | 14,6 | 7,2 | 76,2 | 1,9 |
| CE | État | 1 499 | 35,6 | 23,6 | 38,4 | 2,4 |

Droit des étrangers en CAA (ordonnances incluses), part d'accueil total ou partiel
(`gagne` + `partiel`) : **48,6 %** quand l'appelant est l'État (5 507 arrêts),
**11,3 %** quand c'est un particulier (58 521 arrêts). Dans la même cour, les
particuliers perdent 86,9 % de leurs appels en droit des étrangers.

Lecture, avec les réserves :
- Une part de l'écart entre l'État et les particuliers vient de la nature des affaires : l'État fait appel de jugements qui ont déjà annulé sa décision, donc d'affaires où il a perdu en première instance. Le chiffre mesure le succès de l'appelant, pas la qualité des arguments.
- La nature repose sur le premier requérant cité ; les affaires à plusieurs requérants de natures différentes sont classées selon le premier.
- Les natures `inconnue` (7 498 arrêts de CAA, 2 521 du CE) ne sont pas ventilées ici.
- Ces taux ne disent pas qui avait raison, seulement qui a obtenu satisfaction.

### D3. Durée entre l'enregistrement de la requête et la lecture de la décision

Durée en jours entre `date_requete` (première date d'enregistrement citée dans les
visas) et `date_lecture` (métadonnées). Calculée pour 96,7 % des TA, 96,5 % des CAA
et seulement **63,4 % du CE** ; l'écart est dû à l'absence de la formule
d'enregistrement dans les visas du CE, donc les durées du CE ne valent que pour ces
décisions. Sont écartées les dates antérieures à 2000 ou postérieures à la décision
(712 décisions). Médiane, premier et troisième quartiles (q1, q3), 9ᵉ décile (p90).

| Ordre | Type | Décisions | q1 | Médiane | q3 | p90 |
|---|---|---|---|---|---|---|
| TA | Décision | 571 193 | 28 | **193** | 615 | 914 |
| TA | Ordonnance | 384 266 | 10 | 75 | 253 | 609 |
| CAA | Décision | 70 427 | 263 | **441** | 674 | 855 |
| CAA | Ordonnance | 52 327 | 74 | 141 | 244 | 436 |
| CE | Décision | 13 888 | 32 | 179 | 338 | 548 |
| CE | Ordonnance | 11 367 | 63 | 114 | 180 | 337 |

Selon le type de procédure (tous ordres de décisions confondus) :

| Ordre | Procédure | Décisions | Médiane (jours) | p90 |
|---|---|---|---|---|
| TA | Au fond | 732 165 | 225 | 906 |
| TA | Référé-liberté | 41 632 | 2 | 8 |
| TA | Référé-suspension | 100 752 | 14 | 34 |
| TA | Référé conservatoire | 56 431 | 24 | 85 |
| TA | Référé-provision | 5 784 | 170 | 636 |
| CAA | Au fond | 118 626 | 288 | 772 |
| CE | Référé-liberté | 2 122 | 13 | 119 |

Selon le domaine, au TA, décisions seulement (hors ordonnances) :

| Domaine | Décisions | Médiane (jours) | p90 |
|---|---|---|---|
| Électoral | 4 158 | 50 | 85 |
| Étrangers | 309 224 | 70 | 509 |
| Logement | 20 483 | 336 | 767 |
| Sécurité sociale, aides | 30 869 | 492 | 917 |
| Urbanisme | 27 573 | 669 | 1 174 |
| Fonction publique | 45 075 | 681 | 1 098 |
| Fiscal | 25 756 | 808 | 1 232 |
| Civil | 7 184 | 952 | 1 227 |

Au sein du droit des étrangers (TA, décisions) : rétention et assignation 17 jours,
asile 25, OQTF 85, titre de séjour 86, visa et regroupement familial 316. En CAA,
le droit des étrangers a une médiane de 298 jours, le fiscal 632, l'urbanisme 610.

Lecture, avec les réserves :
- Ce n'est **pas la durée totale du litige**. En CAA et au CE, la durée part de l'enregistrement de l'appel ou du pourvoi, sans compter la première instance.
- Les décisions publiées ne sont pas toutes les décisions rendues (représentativité non mesurée), et la lecture est la date de la décision, pas celle de la notification.
- Les décisions des dernières années sont plus courtes mécaniquement : seules celles déjà rendues sont dans la base (biais de censure à droite). Les médianes TA par année de lecture (162 jours en 2022, 211 en 2025, 188 en 2026) ne sont donc pas une tendance fiable.
- La médiane du droit des étrangers (70 jours) mélange des procédures accélérées (OQTF avec délai court, rétention) et ordinaires ; elle ne dit pas qu'un recours ordinaire dure 70 jours.
- `date_requete` n'a pas été relue à la main hors du relevé n°1.

### D4. Sort des jugements en appel et en cassation

`confirmation_premiere_instance` : `confirme` = l'appel (ou le pourvoi) est rejeté et le
jugement attaqué subsiste ; `infirme_partiellement` = jugement réformé en partie ;
`infirme_totalement` = jugement annulé (au CE, `annule_et_renvoie` pour une cassation avec
renvoi). Sont exclues les décisions « sans objet » (désistement, non-lieu) et celles où le
sort n'est pas lu (8 117 CAA, 2 172 CE). Les ordonnances sont à part : elles
confirment à 99,6 % en CAA (rejets par voie rapide). Décisions au sens strict ; part en %.

| Ordre | Qui fait appel | Décisions | Confirmé | Réformé en partie | Infirmé ou annulé |
|---|---|---|---|---|---|
| CAA | Toutes | 66 945 | 70,2 | 11,1 | 18,6 |
| CAA | Particulier | 39 193 | 75,6 | 8,2 | 16,3 |
| CAA | Personne morale | 14 264 | 70,2 | 14,5 | 15,3 |
| CAA | État | 6 888 | 43,8 | 17,2 | 39,0 |
| CE | Toutes | 23 923 | 86,1 | 1,6 | 12,3 |
| CE | Particulier | 12 274 | 90,0 | 0,9 | 9,1 |
| CE | Personne morale | 8 355 | 85,7 | 1,1 | 13,2 |
| CE | État | 1 315 | 56,8 | 8,8 | 34,4 |

Par domaine en CAA (décisions, plus de 500 par ligne) : la part d'arrêts qui confirment va de
50,4 % (sécurité sociale et aides, où 32,3 % sont réformés en partie) et 59,1 %
(commande publique) à 76,6 % (fiscal) et 75,0 % (urbanisme). Droit des étrangers :
68,5 % de confirmations (27 336 arrêts), 74,1 % quand l'appelant est un particulier, 43,8 %
quand c'est l'État.

Lecture, avec les réserves :
- Le taux de confirmation est stable d'une année à l'autre en CAA (69,3 à 70,9 % de 2022 à 2026).
- Au CE, 12 457 des 23 923 décisions sont des non-admissions de pourvoi, comptées comme confirmations : le jugement subsiste, sans examen au fond. La cassation avec renvoi concerne 2 516 décisions (10,5 %).
- Quand l'État fait appel, « infirmé » veut dire que le tribunal avait donné raison au citoyen et que la cour renverse ce jugement ; le tableau ne distingue pas le sens du jugement de première instance.
- `confirmation_premiere_instance` a été relue sur dix décisions (relevé n°1, cinq arrêts) sans erreur constatée ; la cohérence interne avec `issue_requerant` est de 99,3 % sur échantillon ; l'exactitude n'est pas mesurée.
