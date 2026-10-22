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
