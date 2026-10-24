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
  tiers, avocat, magistrat, greffier), ni adresse, ni numéro de dossier
  administratif. Quand une variable a besoin d'une telle information (commune),
  elle est transformée à l'extraction (département) et la donnée brute est jetée.
  **Seule exception, décidée par Alan le 24/10/2026 : la date de naissance du
  requérant** (`requerant_date_naissance`, groupe H), conservée complète dans la
  couche de travail (`work_dir`, hors du dépôt), jamais publiée, jamais commitée.
  Nationalité, pays d'origine, composition familiale et santé sont extraits en catégories ; avec l'âge et le
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
| `requerant_nature` | **une valeur par requérant**, dans l'ordre du texte : `physique` / `societe` / `association` / `syndicat` / `copropriete` / `collectivite` (commune, département, région, métropole, communauté) / `etat` (préfet, ministre, directions et services de l'État) / `etablissement_public` (hôpital, université, caisse, office, agence, ordre…) / `inconnue`. Lue dans le sujet de la première phrase de requête, par le début de chaque élément (« la société… », « l'association… », « M. X », « le préfet… ») | testé sur 4 500 décisions par ordre (5 mois) ; part des requérants, TA / CAA / CE : personne physique 82 % / 74 % / 55 %, société 7 % / 9 % / 15 %, État 4 % / 6 % / 6 %, collectivité 2 % / 3 % / 4 %, association 1 % / 1 % / 7 %, `inconnue` 4 % / 5 % / 8 % ; exactitude non mesurée |
| `defendeur_categorie` | État (préfecture, ministère) / collectivité / établissement public / organisme social… | non testé |
| `defendeur_departement` | pour une préfecture ou une collectivité : le département, pas le nom d'une personne | non testé |

## D. Litige

| Variable | Contenu | Statut |
|---|---|---|
| `domaine` | thème principal, lu d'abord dans les **codes visés** (CESEDA, CGI, code de l'urbanisme, code du travail…), puis à défaut par mots-clés dans la demande (`domaine_source` = `code` ou `mots_cles`). Priorité du spécifique au générique ; `domaines_trouves` garde tous les thèmes repérés, `domaine` est marqué ambigu s'il y en a plusieurs. Thèmes : étrangers, fiscal, urbanisme, fonction publique, travail et emploi, sécurité sociale et aides, logement, santé, environnement, éducation, commande publique, sécurité et police, électoral, collectivités et domaine public, commerce et assurance, civil, responsabilité et indemnisation, régulation et actes réglementaires | testé sur 2 700 décisions (3 mois par ordre) : thème trouvé pour 90 % des TA, 94 % des CAA, 86 % des CE ; les décisions sans thème sont surtout des non-admissions de pourvoi et des désistements, dont les visas ne citent que le code de justice administrative ; les 33 décisions TA de « Reconduite à la frontière » sont toutes classées étrangers ; les mots-clés de repli (25 % des TA) ne sont pas encore validés ; exactitude non mesurée |
| `sous_domaine` | nature principale du litige, lue dans la **décision attaquée** (texte qui suit « annuler / suspendre / enjoindre » dans la demande), à défaut dans tout le texte. Défini pour les étrangers (oqtf, titre_sejour, asile, retention_assignation, visa_regroupement, nationalite), le fiscal (impots_locaux, impot_revenu, tva_societes, penalites), l'urbanisme (permis_construire, declaration_amenagement, plu_documents), la fonction publique, les aides sociales et le logement ; pas encore pour les autres thèmes. Le titre du CESEDA (« …et du droit d'asile ») est neutralisé avant la recherche, sinon `asile` ressort partout | testé sur 1 475 décisions d'étrangers (4 mois, TA et CAA) : TA titre de séjour 54 %, OQTF 25 %, asile 11 % ; CAA OQTF 49 %, titre de séjour 36 %, asile 8 % ; mots-clés sur tout le texte surestimaient `asile` (32 % des décisions) ; faux positif connu : « visa portant la mention étudiant » déclenche `visa_regroupement` (3 % des décisions) ; exactitude non mesurée |
| `sous_domaines` | **tous** les sous-domaines mentionnés dans la demande et les motifs, pas seulement le principal (une même décision peut être une OQTF et un refus de titre de séjour) ; information secondaire, car une mention n'est pas un objet du litige (« débouté de sa demande d'asile » dans une affaire d'OQTF) | testé avec `sous_domaine` ; exactitude non mesurée |
| `titre_sejour_mentions` | pour le droit des étrangers : type de titre de séjour dont parle la décision, lu dans la formule « portant la mention « … » » : vie_privee_familiale, salarie, etudiant, travailleur_temporaire, travailleur_saisonnier, passeport_talent, visiteur, etranger_malade, recherche_emploi_creation_entreprise, entrepreneur_profession_liberale, resident_longue_duree_ue, protection_subsidiaire, parent_enfant_francais, membre_famille_citoyen_ue, scientifique_chercheur, autre. Catégories seulement, jamais le libellé brut. Peut être le titre demandé, détenu ou cité par la loi : le rôle n'est pas distingué ; plusieurs valeurs possibles (décision marquée ambiguë) | testé sur 1 475 décisions d'étrangers : mention trouvée dans 30 % des TA et 40 % des CAA ; plusieurs valeurs dans 3 % des TA et 5 % des CAA ; répartition : vie privée et familiale (363), salarié (106), étudiant (51), travailleur temporaire (13) ; la décision n°1 du relevé n°1 est reconnue « étudiant » ; exactitude non mesurée ; absent quand le texte ne donne pas la mention |
| `titre_sejour_regimes` | pour le droit des étrangers : régime du titre en litige (carte de séjour temporaire, pluriannuelle, carte de résident, certificat de résidence algérien, autorisation provisoire de séjour, récépissé, visa long séjour, admission exceptionnelle) lu dans la décision attaquée | **expérimental, non fiable** : trouvé dans 22 % des TA et 8 % des CAA seulement ; exclu des relevés |
| `decision_contestee_type`, `decision_contestee_date` | arrêté, décision implicite de rejet… ; auteur : catégorie seulement | non testé |
| `demandes` | annulation, décharge, indemnité, injonction, suspension, frais | non testé |
| `montant_indemnite_demande`, `montant_frais_demande` | € | testé pour la mention « somme de … euros » (69 % TA, 89 % CAA) |
| `moyens` | étiquettes : incompétence, insuffisance de motivation, erreur manifeste d'appréciation, article 8 CEDH… (liste à définir) | non testé |
| `textes_cites` | codes et articles | non testé |
| `oqtf` et attributs | présence d'une OQTF, délai de départ, interdiction de retour (durée), placement en rétention | testé : mention dans 17 % des TA, 37 % des CAA |

## E. Dispositif (ce qui est décidé)

| Variable | Contenu | Statut |
|---|---|---|
| `issue_articles` | par article : accueil (annulation, réformation, décharge, suspension, injonction, condamnation), rejet, désistement donné acte, non-lieu, radiation, transmission, aide juridictionnelle, frais. Les articles consacrés aux frais (L. 761-1, dépens) sont isolés et n'entrent pas dans le résultat | testé (voir `issue_requerant`) |
| `issue_requerant` | `gagne` / `partiel` / `perd` / `neutre` (désistement, non-lieu, radiation, transmission, aide juridictionnelle seule), **du point de vue de celui qui saisit le juge** (requérant, appelant, auteur du pourvoi) ; `issue_sous_cas` garde le détail (accueil, rejet, accueil_et_rejet, appel_accueilli, cassation_renvoi, non_admission…). Le « partiel » inclut « accueil + surplus des conclusions rejeté », que la juridiction code « satisfaction totale » dans environ 30 % des cas : ambiguïté propre aux données | testé sur 2 700 décisions (3 mois par ordre), comparé à la solution codée par la juridiction (`Solution`) : accord de 88 % (TA), 86 % (CAA) et 94 % (CE) sur les cas comparables ; les écarts viennent surtout du « surplus rejeté » et de conventions différentes (« Renvoi après cassation » = neutre côté juridiction, gagne côté requérant) ; ni la solution de la juridiction ni mon calcul ne sont une vérité, exactitude non mesurée |
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
| `nb_requerants` | nombre de requérants de la décision (un couple, une fratrie, une famille : plusieurs), personnes morales comprises (sociétés, associations, collectivités). Lu dans le sujet de la première phrase de requête. Décidé par Alan le 24/10/2026. Un fragment qui ne débute pas comme un requérant (adresse, nom propre d'une liste) est rattaché au précédent. Marqué ambigu si une nature est `inconnue` ou si le sujet énumère une liste de personnes morales (« les sociétés A, B et C » : nombre estimé) | testé sur 4 500 décisions par ordre (5 mois) : fiable pour 88 % des TA, 89 % des CAA, 86 % des CE ; ambigu pour 4 %, 6 %, 10 % ; absent pour 4 à 8 % ; exactitude non mesurée |
| `nb_requerants_personnes_physiques`, `nb_requerants_personnes_morales` | décomptes de `nb_requerants` selon `requerant_nature` : les personnes physiques sont seules concernées par les dates de naissance | testé avec `nb_requerants` |
| `requerant_date_naissance` | **une date par requérant**, rangée par ordre d'apparition dans le texte (rang 1, 2…), sans nom ni lien avec l'identité. Date complète telle que le texte l'énonce, si elle y figure ; couche de travail seulement. Ne sert **jamais** à rapprocher des décisions entre elles ni à publier (voir règle de non-liaison) ; seule la classe d'âge ci-dessous est publiable | testé sur 4 500 décisions TA et CAA : date trouvée dans 24 % des TA et 32 % des CAA, ~1 % du CE ; ambiguë dans moins de 0,5 % ; exactitude non mesurée. Les dates sont rangées par ordre d'apparition : le rang ne garantit pas la correspondance avec le requérant de même rang dans `nb_requerants`. Plusieurs dates pour un même requérant (identités multiples) : à traiter ; un sujet à plusieurs requérants avec leurs dates est rare (4 à 7 décisions sur 1 500) |
| `requerant_age` | âge en années à la date de la décision, par requérant, calculé depuis `requerant_date_naissance` | testé (aucun âge hors de 0 à 110 ans) ; exactitude non mesurée |
| `requerant_classe_age` | tranche d'âge dérivée de `requerant_age` ; c'est la seule forme publiée | non testé |
| `requerant_civilite` | M. / Mme | non testé |
| `departement` | du lieu du litige ou du défendeur, jamais la commune | non testé |
| `mineur_concerne` | oui / non | non testé |
| `nationalite` | pays de nationalité tel que le texte l'énonce (« ressortissante tunisienne ») ; regroupement par zone géographique pour publier | testé sur un mois par ordre (mars et septembre 2025) : « de nationalité … » dans 7 % des TA, 14 % des CAA ; « ressortissant(e) … » dans 31 % des TA, 53 % des CAA ; au moins l'une des deux dans 33 à 34 % des TA, 58 % des CAA, 2 % des CE. Les deux formules se recoupent. Quelques « ressortissant français » : à traiter |
| `situation_familiale` | marié(e) / célibataire / pacsé(e) ; conjoint en France oui / non | non testé |
| `enfants` | nombre d'enfants ; au moins un enfant mineur ; enfant né en France ; enfant scolarisé | non testé (enfant mineur : 4 à 7 % des décisions par mot-clé) |
| `pays_origine` | pays dont le texte dit que la personne est originaire : « pays d'origine », « originaire de… », lieu de naissance suivi d'un pays. Distinct de `nationalite` (on peut être d'un pays et originaire d'un autre) ; garder les deux et noter laquelle des formulations a servi | testé sur le motif seul (septembre 2025) : « pays d'origine » dans 11 % des TA, 33 % des CAA, mais souvent dans une citation de la loi ou un énoncé de principe sans pays nommé ; « né(e) à … (pays) » 3 à 5 % ; « originaire de » moins de 1 %. Extraction du pays nommé non validée |
| `pays_destination_renvoi` | pays vers lequel l'éloignement est fixé (décision d'OQTF) | testé : formule dans 17 % des TA, 51 % des CAA ; pays nommé non validé |
| `sante_invoquee` | oui / non : la santé du requérant ou d'un proche est invoquée | testé par mots-clés : maladie ou pathologie 8 % TA, 14 % CAA ; handicap, invalidité ou taux d'incapacité 6 % ; état de santé ou article L. 425-9 du CESEDA (titre de séjour pour soins) 7 % TA, 14 % CAA ; collège de médecins de l'OFII 4 % TA, 7 % CAA ; troubles psychiques 3 à 4 % ; grossesse 2 % |
| `sante_categorie` | catégorie seulement : maladie grave, handicap ou invalidité, trouble psychique, grossesse, autre. **Jamais le diagnostic ni le texte libre** | non testé |
| `sante_beneficiaire` | le requérant, un enfant, un conjoint, un proche | non testé |
| `avis_medical_pris` | avis du collège de médecins de l'OFII, ou expertise, mentionné et son sens (favorable, défavorable) | non testé |

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
