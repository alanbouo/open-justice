# Justice judiciaire : nature et volumes des affaires publiées

Calculé le 8 novembre 2026 sur les 2 183 473 décisions de Judilibre téléchargées le
28 octobre 2026 (`mesures.md` §7), par `scripts/agreger_judiciaire_volumes.py`.
Résultat complet : `site/agregats/judiciaire_volumes.json`. Agrégats seulement :
aucune cellule de moins de 300 décisions, les groupes plus petits sont fondus dans
« autres ». Rien n'est ventilé par magistrat, greffier, partie ou chambre d'une
juridiction du fond.

**Ce sont les décisions publiées, pas les décisions rendues.** Le rapport entre les
deux n'est pas mesuré ; le contrôle externe (§5) en donne un ordre de grandeur.

## Ce qui est calculé

- Volumes par juridiction (`cc`, `ca`, `tj`, `tcom`), par année et par mois de
  décision, et par source d'alimentation déclarée par Judilibre (`source`).
- Volumes par cour d'appel, tribunal judiciaire et tribunal de commerce (`location`),
  toutes années et pour 2025 seule. Libellés des lieux : référentiel public de
  Judilibre (dépôt `judilibre-search` de la Cour de cassation, commit `6cdd7e6` du
  29/10/2026) ; les 36 codes `ca`, 153 `tj` et 132 `tcom` y sont tous.
- Nombre de juridictions présentes par trimestre (mesure de l'entrée progressive
  dans Judilibre).
- Nature des affaires pour `ca` et `tj` par le code NAC (nomenclature des affaires
  civiles), aux trois niveaux, avec les intitulés officiels.
- Pour la Cour de cassation, qui n'a pas de NAC : chambre (les six chambres
  correspondent à des matières). Pour les tribunaux de commerce, qui n'ont ni NAC ni
  thème : classement du libellé de chambre par mots-clés.

### Source de la nomenclature

Ministère de la Justice, *Nomenclature des affaires civiles – Modifications
effectuées entre 2002 et 2022 [archive]*, data.gouv.fr, licence ouverte 2.0 :
<https://www.data.gouv.fr/datasets/634677f37b8614146f4090ff>, consulté le
8/11/2026. Le fichier (extension `.csv`, contenu au format Excel) donne pour 980
codes le niveau 1, le niveau 2 et l'intitulé, avec les années de création et de
suppression. La structure est documentée par la note *Nomenclatures des affaires
civiles et des procédures particulières* (DACS, 28/09/2022), publiée avec le
fichier : premier caractère = 9 grandes matières, deuxième = secteur, troisième =
objet de la demande. **Le fichier n'est plus mis à jour depuis juillet 2022.**

Correspondance avec Judilibre : 99,98 % des décisions `ca` codées et 99,8 % des `tj`
ont un code présent dans la table. Les codes absents (par exemple `48S`, `55C`,
`94F`) sont probablement postérieurs à 2022 **[non vérifié]** ; ils restent classés
par leur premier caractère, mais sans intitulé.

## 1. Volumes et couverture temporelle

| Juridiction | Décisions | Première date | Dernière date | Lieux |
|---|---|---|---|---|
| Tribunaux judiciaires | 765 280 | 14/12/2023 | 19/10/2026 | 153 |
| Cours d'appel | 646 601 | aberrante (an 0201) | 19/10/2026 | 36 |
| Cour de cassation | 569 520 | 01/08/1860 | 22/10/2026 | 1 |
| Tribunaux de commerce | 202 072 | 31/12/2024 | 19/10/2026 | 132 |

Volumes par année de décision, années pleines du flux régulier :

| Juridiction (source) | 2022 | 2023 | 2024 | 2025 | 2026 (au 22/10) |
|---|---|---|---|---|---|
| Cour de cassation (`jurinet`) | 16 231 | 17 236 | 16 351 | 16 277 | 12 900 |
| Cours d'appel (`jurica`) | 75 271 | 119 125 | 132 526 | 130 178 | 83 606 |
| Tribunaux judiciaires (`juritj`) | — | 2 274 | 165 377 | 326 104 | 271 525 |
| Tribunaux de commerce (`juritcom`) | — | — | — | 115 973 (avec le 31/12/2024) | 86 099 |

Couverture réelle, constatée sur les dates :

- **Cour de cassation.** Deux fonds : `dila` (404 852 décisions, de 1860 à 2018, fonds
  historique) et `jurinet` (164 668, surtout depuis 2016). Avant 1987, moins de 3 000
  décisions par an ; à lire comme une sélection historique, pas comme l'activité.
- **Cours d'appel.** Deux fonds aussi : `dila` (61 544 arrêts de 1996 à 2021,
  sélection) et `jurica` (585 057). Le flux régulier commence en **avril 2022**
  (3 624 décisions ce mois-là, presque aucune de janvier à mars 2022) ;
  `jurica` contient aussi 44 422 décisions plus anciennes (2005 à mars 2022). Les
  36 cours sont présentes chaque trimestre depuis 2022. Quelques dates en l'an 0201,
  toutes du fonds `dila` (`mesures.md` §7), sont des erreurs de saisie probables ;
  elles sont fondues dans « autres années » du JSON.
- **Tribunaux judiciaires.** Flux ouvert en décembre 2023, avec une entrée
  **progressive** des tribunaux : 9 présents au 4ᵉ trimestre 2023, 28 au 1ᵉʳ
  trimestre 2024, 61 au 4ᵉ, 129 au 2ᵉ trimestre 2025, 145 en 2026. La hausse de
  2024 à 2025 mesure surtout cette entrée, pas une hausse d'activité.
- **Tribunaux de commerce.** Flux ouvert en janvier 2025 (101 tribunaux présents au
  1ᵉʳ trimestre 2025, 128 au 4ᵉ).
- **Creux d'août** dans toutes les juridictions (vacations judiciaires) ; 2026 et
  surtout octobre 2026 sont incomplets (photographie du 28/10/2026, décisions mises
  en ligne avec un délai **[délai non mesuré]**).

### Cours et tribunaux les plus représentés, année 2025

| Cour d'appel | 2025 | | Tribunal judiciaire | 2025 |
|---|---|---|---|---|
| Paris | 26 724 | | Paris | 40 169 |
| Aix-en-Provence | 16 052 | | Bobigny | 18 560 |
| Versailles | 8 738 | | Marseille | 18 174 |
| Lyon | 7 568 | | Lyon | 16 693 |
| Douai | 6 109 | | Toulouse | 12 455 |
| Montpellier | 5 619 | | Bordeaux | 10 855 |
| Rennes | 5 317 | | Lille | 10 589 |
| Toulouse | 5 269 | | Versailles | 10 570 |
| Nîmes | 4 983 | | Meaux | 8 323 |
| Bordeaux | 4 187 | | Strasbourg | 8 133 |

En 2025, 116 tribunaux judiciaires sur 153 présents dans la base dépassent le seuil
de 300 décisions ; les autres sont regroupés. Pour les tribunaux de commerce, le
plus représenté en 2025 est le tribunal des activités économiques de Paris
(14 495), puis celui de Nanterre (7 377). Liste complète dans le JSON
(`par_lieu`, `par_lieu_2025`).

## 2. Nature des affaires : cours d'appel et tribunaux judiciaires

Le code NAC est présent pour 540 768 décisions de cour d'appel sur 646 601
(83,6 %, et non 90,5 % : 44 289 portent la chaîne « null » en toutes lettres) et
pour 100 % des tribunaux judiciaires. **Depuis 2022, il est présent pour toutes les
décisions de cour d'appel** : les absences concernent le fonds `dila` et les
décisions `jurica` antérieures à 2022.

Niveau 1, part des décisions codées (%) :

| Matière (niveau 1 NAC) | CA 2024 | CA 2025 | TJ 2025 | TJ toutes années |
|---|---|---|---|---|
| 1 Droit des personnes | 17,6 | 20,2 | 14,2 | 12,9 |
| 2 Droit de la famille | 2,1 | 2,2 | 10,2 | 10,3 |
| 3 Droit des affaires | 5,9 | 5,7 | 5,5 | 5,8 |
| 4 Entreprises en difficulté, surendettement | 4,3 | 4,8 | 2,3 | 2,4 |
| 5 Contrats | 23,3 | 23,0 | 39,4 | 39,5 |
| 6 Responsabilité et quasi-contrats | 3,8 | 3,7 | 5,2 | 5,3 |
| 7 Biens, propriété littéraire et artistique | 7,1 | 7,3 | 11,1 | 11,3 |
| 8 Travail et protection sociale | 33,6 | 30,9 | 11,7 | 11,9 |
| 9 Relations avec les personnes publiques | 2,2 | 2,1 | 0,4 | 0,5 |
| **Décisions codées** | **132 526** | **130 178** | **326 104** | **765 280** |

Regroupements faits par Open Justice à partir des intitulés officiels (ce ne sont pas
des catégories du ministère ; définitions dans le script) :

| Regroupement | CA décisions | CA % | TJ décisions | TJ % |
|---|---|---|---|---|
| Baux (habitation, professionnels, ruraux, commerciaux) | 40 141 | 7,4 | 169 016 | 22,1 |
| Étrangers : rétention et zone d'attente | 82 777 | 15,3 | 34 315 | 4,5 |
| Soins psychiatriques sans consentement, isolement, contention | 12 035 | 2,2 | 59 483 | 7,8 |
| Divorce et séparation de corps | sous le seuil | | 55 232 | 7,2 |
| Surendettement des particuliers | 8 440 | 1,6 | 16 940 | 2,2 |
| Entreprises en difficulté (hors surendettement) | 16 375 | 3,0 | 1 793 | 0,2 |
| Relations individuelles de travail | 119 024 | 22,0 | 471 | 0,1 |
| Protection sociale et risques professionnels | 57 049 | 10,5 | 84 923 | 11,1 |

Parts calculées sur les décisions codées, toutes années (CA 540 768, TJ 765 280).

Codes les plus fréquents :

| Cours d'appel | Décisions | | Tribunaux judiciaires | Décisions |
|---|---|---|---|---|
| 80A Indemnités liées à la rupture du contrat de travail | 77 126 | | 5AA Bail d'habitation : loyers impayés, résiliation, expulsion | 108 838 |
| 14G Rétention et maintien en zone d'attente d'un étranger | 37 165 | | 14K Contrôle périodique d'une hospitalisation complète sans consentement | 46 664 |
| 14H Mainlevée de la rétention demandée par l'étranger | 26 969 | | 20L Divorce autre que par consentement mutuel (art. 1107 CPC) | 43 600 |
| 14Q Prolongation de la rétention d'un étranger | 15 825 | | 53B Remboursement d'un prêt | 33 947 |
| 88A Contestation d'une décision d'un organisme social | 14 554 | | 72A Copropriété : paiement des charges | 28 872 |
| 80J Contestation du motif non économique d'un licenciement | 13 557 | | 14Q Prolongation de la rétention d'un étranger | 27 753 |
| 80C Indemnités ou salaires | 13 538 | | 54G Construction : demande du maître de l'ouvrage | 26 906 |
| 53B Remboursement d'un prêt | 13 485 | | 30B Bail commercial : loyers impayés, résiliation | 22 758 |
| 51A Bail : loyers impayés, résiliation, expulsion (code d'avant 2022) | 13 452 | | 88B Annulation d'une mise en demeure ou d'une contrainte | 20 169 |
| 54G Construction : demande du maître de l'ouvrage | 11 225 | | 54Z Construction : autres demandes | 17 440 |

Intitulés abrégés ici ; intitulés officiels complets dans le JSON (`nac_codes`).

Un point de qualité : **159 210 décisions de cour d'appel portent un code que la
table déclare supprimé** avant 2022, dont 80A (supprimé en 2014 selon la table,
77 126 décisions, toutes de 2021 ou après) et 14G (supprimé en 2021, 37 165). Les
juridictions continuent donc d'utiliser d'anciens codes, ou la table d'archive ne
reflète pas la nomenclature en vigueur **[cause non vérifiée]**. Le premier
caractère reste interprétable ; l'intitulé fin peut être daté.

## 3. Cour de cassation : chambres

| Chambre | Depuis 2020 | % | Toutes années | % |
|---|---|---|---|---|
| Chambre criminelle | 21 867 | 21,2 | 104 815 | 18,4 |
| Chambre sociale | 16 048 | 15,5 | 146 258 | 25,7 |
| Deuxième chambre civile | 15 571 | 15,1 | 78 396 | 13,8 |
| Première chambre civile | 10 770 | 10,4 | 74 319 | 13,0 |
| Troisième chambre civile | 9 882 | 9,6 | 73 076 | 12,8 |
| Chambre commerciale | 9 697 | 9,4 | 71 259 | 12,5 |
| Ordonnances, assemblée plénière, chambre mixte, autres | 19 435 | 18,8 | 21 397 | 3,8 |
| **Total** | **103 270** | | **569 520** | |

Les ordonnances (rendues par un magistrat seul) sont regroupées avec les petites
formations et ne sont pas détaillées. Les mots-clés `themes` (34,6 % de présence,
107 060 libellés libres) ne sont pas exploitables en l'état.

## 4. Tribunaux de commerce : libellés de chambre

Ni NAC, ni thème, ni solution, ni type de décision : seul le libellé de chambre,
saisi librement par chaque greffe (601 valeurs), dit quelque chose de la matière.

| Libellé de chambre (classement par mots-clés) | Décisions | % |
|---|---|---|
| Mentionne les procédures collectives (redressement, liquidation, sauvegarde) | 38 155 | 18,9 |
| Mentionne les référés | 9 880 | 4,9 |
| Autre libellé (« Chambre 04 », jour d'audience…) | 108 584 | 53,7 |
| Sans libellé | 45 453 | 22,5 |

La part des procédures collectives est une **borne basse** : une chambre qui en juge
peut porter un libellé neutre. La nature réelle des affaires commerciales publiées
n'est pas mesurable sans lire le texte.

## 5. Contrôle externe

Source : ministère de la Justice, *Les chiffres clés de la Justice*, édition 2025
(données 2024), p. 10 (justice civile) et p. 17 (justice pénale), <https://www.justice.gouv.fr/sites/default/files/2026-03/Chiffres_Cles_2025_corrV2.pdf>,
et *Références statistiques Justice* 2024, fiche 4.1,
<https://www.justice.gouv.fr/sites/default/files/2025-09/RSJ2024%204_1.pdf>.
Relus le 8/11/2026 (chiffres déjà repris dans `site/references/justice-civile-2025.json`).

**Volumes.** Les populations diffèrent : le ministère compte des *affaires*
(terminées ou nouvelles, au fond et en référé), Judilibre des *décisions publiées*
(arrêts, ordonnances, jugements, y compris avant dire droit).

| Juridiction, 2024 | Judilibre (décisions publiées) | Ministère (affaires terminées, civil) | Rapport |
|---|---|---|---|
| Cours d'appel | 132 526 | 195 093 | 68 % |
| Cour de cassation, hors chambre criminelle | 13 036 | 14 731 | 88 % |
| Cour de cassation, chambre criminelle | 3 315 | 7 280 arrêts pénaux prononcés | 46 % |
| Tribunaux judiciaires | 165 377 (2025 : 326 104) | 1 380 333 (hors ruptures d'union et procédures spéciales) | non comparable |
| Juridictions commerciales | (2025 : 115 973) | 148 953 (avec les chambres commerciales des TJ) | non comparable |

Les rapports ne sont pas des taux de publication : une affaire terminée peut donner
plusieurs décisions publiées ou aucune. Pour les tribunaux judiciaires et de
commerce, l'année 2024 de Judilibre est incomplète (entrée progressive) et 2025 n'a
pas encore de chiffre officiel.

**Nature des affaires en cour d'appel.** Le ministère publie la répartition des
*affaires nouvelles* 2024 des cours d'appel, hors référés, par grande matière de la
NAC (graphique p. 10, valeurs lues sur le graphique).

| Matière | Ministère, affaires nouvelles 2024 (%) | Judilibre, décisions 2024 (%) |
|---|---|---|
| Droit des personnes | 18 | 17,6 |
| Droit de la famille | 19 | 2,1 |
| Droit des affaires | 4 | 5,9 |
| Surendettement, entreprises en difficulté | 3 | 4,3 |
| Contrats | 16 | 23,3 |
| Responsabilité | 3 | 3,8 |
| Biens | 5 | 7,1 |
| Travail et protection sociale | 22 | 33,6 |
| Personnes publiques | 6 | 2,2 |
| Indéterminée | 4 | — |

L'écart majeur porte sur le **droit de la famille** : 19 % des affaires nouvelles
des cours d'appel, 2 % des décisions publiées. Les autres matières sont du même ordre
de grandeur, le travail et les contrats étant surreprésentés par effet de vases
communicants. Hypothèse : les décisions familiales, rendues hors la présence du
public, sont pour l'essentiel exclues de la diffusion **[non vérifié : la règle
d'exclusion n'a pas été lue]**. Les populations diffèrent aussi (affaires nouvelles
contre décisions rendues, référés exclus d'un côté seulement).

## Lecture, avec les réserves

- **Biais de publication.** Judilibre ne publie pas tout ce qui est rendu, et ce qui
  manque n'est pas tiré au hasard : le droit de la famille est quasi absent des
  cours d'appel publiées. Toute part par matière décrit le flux publié, pas
  l'activité des juridictions.
- **Représentativité non mesurée.** Le rapport entre décisions publiées et décisions
  rendues n'est connu ni par juridiction, ni par matière, ni par lieu. Les comparaisons
  du §5 donnent des ordres de grandeur sur des populations différentes.
- **Couverture.** Séries comparables d'une année sur l'autre : cours d'appel de 2023
  à 2025, Cour de cassation depuis 2016 environ. Pour les tribunaux judiciaires et
  de commerce, les volumes suivent l'arrivée des tribunaux dans la base ; un
  classement entre tribunaux mesure leur ancienneté dans Judilibre autant que leur
  activité. En 2025, 37 tribunaux judiciaires présents dans la base ont moins de 300 décisions publiées, dont 9 aucune.
- **Nombre de juridictions.** Judilibre compte 36 cours d'appel, 153 tribunaux
  judiciaires et 132 tribunaux de commerce ou des activités économiques ; les
  chiffres clés 2025 annoncent 34 cours d'appel, 164 tribunaux judiciaires,
  122 tribunaux de commerce, 12 tribunaux des activités économiques et 7 tribunaux
  mixtes de commerce. L'écart sur les cours d'appel n'est pas expliqué **[non
  vérifié]** ; pour les tribunaux judiciaires, une dizaine sont absents de la base.
- **Codes NAC.** Table officielle figée en juillet 2022 ; anciens codes encore
  utilisés ; le regroupement par premier caractère est documenté par le ministère,
  les regroupements thématiques du §2 sont ceux d'Open Justice.
- **Une décision n'est pas une affaire.** Une même affaire peut produire plusieurs
  décisions (avant dire droit, rectification, ordonnance du conseiller de la mise en
  état) ; les volumes ne se lisent pas comme un nombre de litiges.
- **Différences entre tableaux.** Les groupes sous le seuil sont fondus dans
  « autres » ; certaines différences entre deux listes du JSON (par exemple un
  niveau 1 moins ses niveaux 2 publiés) peuvent faire apparaître un reste inférieur
  à 300. Ces restes portent sur des natures d'affaires au niveau national ou sur des
  lieux, jamais sur des personnes.

### Non vérifié

- Cause des codes NAC absents de la table et des codes « supprimés » encore utilisés.
- Règle d'exclusion des décisions familiales de la diffusion.
- Délai de mise en ligne (part de 2026 qui manque encore).
- Écart entre les 36 cours d'appel de Judilibre et les 34 des chiffres clés.
