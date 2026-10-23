# Variables à construire

Catalogue des variables à tirer des décisions de la justice administrative, établi
le 23 octobre 2026. Elles viennent soit des métadonnées (mesurées dans
`mesures.md`), soit du texte intégral. Le texte a été lu sur 7 décisions de
septembre 2025 (3 jugements de TA, 2 ordonnances de TA, 1 arrêt de CAA, 1
décision du CE) : sept exemples ne sont pas un échantillon représentatif, donc
chaque extraction est une hypothèse à valider sur un échantillon relu à la main.

Colonne **Statut** : `mesuré` (disponible tel quel dans les métadonnées) ; `testé`
(présence du motif vérifiée sur un échantillon, extraction non validée) ;
`non testé`.

## Règles pour toutes les variables

- **Aucun identifiant de personne physique n'est stocké ni calculé** : ni nom (partie,
  tiers, avocat, magistrat, greffier), ni adresse, ni date de naissance, ni numéro
  de dossier administratif. Quand une variable a besoin d'une telle information
  (âge, commune), elle est transformée à l'extraction (classe d'âge, département)
  et la donnée brute est jetée.
  Nationalité et composition familiale sont extraites en catégories ; avec l'âge et le
  département elles se recoupent : à ne publier qu'avec un effectif minimal par cellule.
- **Aucune clé permettant de relier des affaires différentes d'une même personne.**
  Les seuls liens sont ceux de la procédure elle-même (chaîne d'une même affaire,
  voir groupe F).
- Pas de variable par magistrat ni par greffier (article 33 de la loi de 2019).
- Chaque variable porte son indicateur d'extraction (trouvée, absente, ambiguë)
  pour mesurer les erreurs.

## A. Identification et métadonnées

| Variable | Contenu | Statut |
|---|---|---|
| `id_decision` | ordre + code juridiction + nom de fichier (unique ; le nom seul ne l'est pas) | mesuré |
| `ordre`, `juridiction`, `date_lecture`, `annee`, `mois` | | mesuré |
| `type_decision` | décision / ordonnance | mesuré |
| `type_recours_norm` | 35 libellés regroupés (casse, variantes par ordre) | mesuré, référentiel à faire |
| `solution_norm` | 177 libellés regroupés (rejet, satisfaction totale ou partielle, désistement, non-lieu, rejet par voie rapide…) | mesuré, référentiel à faire |
| `code_publication` | sens non documenté ; vide pour 49 % des décisions TA | mesuré |
| `formation_norm` | juge des référés, chambre, formation à 3, reconduite à la frontière… ; rôle seulement | mesuré (couverture TA 46 %) |
| `date_audience` | 46 % TA, 55 % CAA, 61 % CE | mesuré |
| `longueur_texte` | nombre de caractères | mesuré |

## B. Procédure (texte)

| Variable | Contenu | Statut |
|---|---|---|
| `date_requete` | date d'enregistrement de la requête (la première, pas celle d'un mémoire) | testé : formule présente dans 95 % des TA et CAA, 46 % des CE |
| `dates_memoires`, `nb_memoires` | | non testé |
| `date_cloture` | clôture d'instruction | non testé |
| `date_rendu` | « Rendu public par mise à disposition au greffe le… » | non testé |
| `formation_type` | juge unique / magistrat désigné / collégiale (rôle, pas le nom) | non testé |
| `audience_tenue` | oui / non (les ordonnances n'en ont pas) | non testé |
| `rapporteur_public_dispense` | oui / non | non testé |
| `memoire_defense` | produit / non produit | non testé |
| `requerant_avocat` | oui / non (« représenté par Me… ») ; champ `Avocat_Requerant` des métadonnées en complément | non testé |

## C. Parties

| Variable | Contenu | Statut |
|---|---|---|
| `requerant_nature` | personne physique / société / association / collectivité | non testé |
| `defendeur_categorie` | État (préfecture, ministère) / collectivité / établissement public / organisme social… | non testé |
| `defendeur_departement` | pour une préfecture ou une collectivité : le département, pas le nom d'une personne | non testé |

## D. Litige

| Variable | Contenu | Statut |
|---|---|---|
| `domaine` | lu dans les **codes visés** (CESEDA, CGI, code de la construction et de l'habitation, code des pensions…), plus fiable que les mots du corps | non testé (mots-clés bruts testés : trop larges) |
| `sous_domaine` | OQTF, refus de titre de séjour, asile, DALO, taxe d'habitation, permis de construire, indemnisation… | non testé |
| `decision_contestee_type`, `decision_contestee_date` | arrêté, décision implicite de rejet… ; auteur : catégorie seulement | non testé |
| `demandes` | annulation, décharge, indemnité, injonction, suspension, frais | non testé |
| `montant_indemnite_demande`, `montant_frais_demande` | € | testé pour la mention « somme de … euros » (69 % TA, 89 % CAA) |
| `moyens` | étiquettes : incompétence, insuffisance de motivation, erreur manifeste d'appréciation, article 8 CEDH… (liste à définir) | non testé |
| `textes_cites` | codes et articles | non testé |
| `oqtf` et attributs | présence d'une OQTF, délai de départ, interdiction de retour (durée), placement en rétention | testé : mention dans 17 % des TA, 37 % des CAA |

## E. Dispositif (ce qui est décidé)

| Variable | Contenu | Statut |
|---|---|---|
| `issue_articles` | par article : annulation, rejet, réformation, renvoi, non-lieu, désistement donné acte, injonction | non testé |
| `issue_requerant` | gagne / perd / partiel / neutre, calculée depuis les articles et `Solution` | non testé |
| `injonction` | oui / non ; délai en jours ; astreinte en € | non testé |
| `frais_l761` | montant alloué ; qui paie (État, collectivité, requérant) ; qui reçoit (requérant, avocat) | testé : article L.761-1 cité dans 65 % TA, 87 % CAA, 77 % CE |
| `indemnite_accordee` | montant | non testé |
| `motif_rejet` | irrecevabilité (tardiveté, requête prématurée, incompétence, défaut d'intérêt) ou rejet au fond | non testé |
| `fondement_ordonnance` | article R.222-1, alinéa (désistement, irrecevabilité manifeste…) | non testé |

## F. Chaînage d'une même affaire

| Variable | Contenu | Statut |
|---|---|---|
| `decision_attaquee` | juridiction, numéro, date du jugement ou de l'arrêt attaqué | testé : cité avec numéro et date dans 79 % des arrêts de CAA |
| `id_decision_attaquee` | lien vers la base, par juridiction + numéro + date | testé : 85 % des citations retrouvées ; rapprochement à affiner (tribunal compris, ordonnances) |
| `issue_premiere_instance` | issue de la décision attaquée, lue dans l'arrêt ou dans la base | non testé |
| `degres_parcourus` | tribunal, appel, cassation | non testé |
| `auteur_appel` | requérant initial ou administration | non testé |

## G. Répétition, calculée au niveau de la décision

Indicateurs par décision, jamais par personne : le texte d'une décision signale
ou non une procédure antérieure ; aucune décision n'est croisée avec une autre
sur la base de l'identité du requérant.

| Variable | Contenu | Statut |
|---|---|---|
| `procedure_anterieure_citee` | oui / non / ambigu | non testé |
| `nb_procedures_anterieures_citees` | | non testé |
| `mesure_eloignement_anterieure` | mention d'une mesure d'éloignement antérieure, **hors** citation de la loi et hors négation | testé et **non fiable** : 15,8 % des décisions d'OQTF, mais 3 passages sur 6 relus sont des citations de la loi ou des négations |
| `reexamen_ou_nouvelle_demande` | demande de réexamen, nouvelle demande, second recours | non testé |

Borne basse : le juge ne cite le passé que s'il pèse sur la décision.

## H. Profil, en catégories larges

| Variable | Contenu | Statut |
|---|---|---|
| `requerant_classe_age` | calculée à l'extraction (âge à la date de la décision, par tranche) puis date de naissance jetée | non testé |
| `requerant_civilite` | M. / Mme | non testé |
| `departement` | du lieu du litige ou du défendeur, jamais la commune | non testé |
| `mineur_concerne` | oui / non | non testé |
| `nationalite` | pays de nationalité tel que le texte l'énonce (« ressortissante tunisienne ») ; regroupement par zone géographique pour publier | testé : mention « de nationalité … » dans 7 % des TA, 14 % des CAA ; la mention « ressortissant(e) » n'a pas été comptée |
| `situation_familiale` | marié(e) / célibataire / pacsé(e) ; conjoint en France oui / non | non testé |
| `enfants` | nombre d'enfants ; au moins un enfant mineur ; enfant né en France ; enfant scolarisé | non testé (enfant mineur : 4 à 7 % des décisions par mot-clé) |
| santé | **non extraite** : non vérifié ; mention de handicap, maladie ou invalidité dans 7 à 15 % des décisions, par mot-clé | non vérifié |

## I. Dérivées

| Variable | Calcul | Statut |
|---|---|---|
| `duree_jugement_jours` | `date_rendu` − `date_requete` ; contrôler les dates aberrantes (une requête de 2014 jugée en 2025) | non testé |
| `duree_instruction_jours` | `date_cloture` − `date_requete` | non testé |
| `delai_audience_rendu_jours` | `date_rendu` − `date_audience` | mesuré (médiane 14 à 23 jours) |
| `duree_totale_affaire` | de la requête de première instance à la dernière décision de la chaîne | non testé |
| `delai_appel_jours` | date de l'arrêt moins date du jugement attaqué | non testé |

## J. Contrôle qualité

`extraction_statut` (trouvée / absente / ambiguë) pour chaque variable, `version_extracteur`,
`echantillon_relu` (marque les décisions relues à la main pour mesurer les erreurs).

## Structure d'une décision (pour l'extraction)

1. **Visas** (« Vu la procédure suivante ») : requête, demandes, moyens, mémoire en
   défense, textes, désignation du juge, audience.
2. **Motifs** (« Considérant ce qui suit »).
3. **Dispositif** (« DÉCIDE » / « ORDONNE », « Article 1er… ») : la partie la plus
   régulière.
4. **Clôture** : date de rendu, signatures, formule exécutoire.

Les ordonnances sont courtes (1 300 à 3 300 caractères dans les exemples) et
suivent un modèle quasi fixe. Le texte varie selon l'ordre (CE : pourvoi, non-admission ;
CAA : rappel de la première instance) : prévoir une extraction par ordre et par type.

## Points d'attention

- Des **noms de magistrats** figurent hors du bloc de signature (visas, formation) ;
  en toutes lettres au Conseil d'État. Ne conserver que le rôle.
- Une **société** n'était pas pseudonymisée dans l'exemple vu (désistement) : le
  texte brut ne se republie jamais.
- Les motifs de mots-clés bruts attrapent des citations de la loi et des négations :
  toute extraction doit les exclure et être mesurée.
