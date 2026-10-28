# Recherche préalable

Synthèse au 22 octobre 2026. Recherche légère, par web, sans accès aux API.
Les points marqués **[non vérifié]** n'ont pas été confirmés par une source
primaire.

---

## 1. Données accessibles

### Ordre judiciaire : Judilibre (Cour de cassation)

Base ouverte, gratuite, des décisions pseudonymisées et parfois enrichies
(sommaires, rapports, liens vers la décision attaquée). Accès par le site ou par
l'API sur le portail PISTE, après inscription.
Source : [data.gouv.fr, API Judilibre](https://www.data.gouv.fr/fr/datasets/api-judilibre/)

| Juridiction | État | Source |
|---|---|---|
| Cour de cassation | Ouvert, **569 520 décisions au 27/10/2026** (`/stats` de l'API, mesuré avec une clé de production) ; ~535 855 au 10/10/2024 | mesure du 27/10/2026 ; [Bases & Netsources](https://www.bases-netsources.com/articles-de-bases/judilibre-l-open-data-judiciaire-en-transformation) pour 2024 |
| Cours d'appel (civil, social, commercial) | Ouvert, **646 601 arrêts téléchargés le 28/10/2026** (`total` de `/scan`) ; ~392 000 au 10/10/2024 | mesure du 28/10/2026, détail dans `mesures.md` §7 ; idem pour 2024 |
| Tribunaux judiciaires (civil, social, commercial) | **765 280 jugements téléchargés le 28/10/2026**, de 2023 à 2026 ; 72 000 jugements de 48 tribunaux au 10/10/2024. Un rapport de 2025 compte plus de 1,3 M de décisions toutes juridictions confondues | mesure du 28/10/2026 ; idem ; [Actu-Juridique](https://www.actu-juridique.fr/breves/juridictions/open-data-des-decisions-de-justice-ouverture-a-lensemble-des-juridictions-de-lordre-judiciaire/) |
| Tribunaux de commerce | **202 072 décisions téléchargées le 28/10/2026**, de 2025 à 2026 | mesure du 28/10/2026, `mesures.md` §7 |
| Prud'hommes | Échéance fixée au 30/09/2026. **[non vérifié]** que la publication a eu lieu | [Actu-Juridique](https://www.actu-juridique.fr/breves/institutions-judiciaires/open-data-nouveau-report-pour-les-decisions-des-conseils-de-prud'hommes-et-les-decisions-penales/) |
| Pénal, premier degré délictuel | 31/12/2027 | arrêté du 29/08/2025 (JO du 03/09/2025, NOR JUST2523192A) |
| Pénal, cours d'appel, criminel, premier degré contraventionnel | 31/12/2028 | idem |

Le calendrier a déjà été repoussé trois fois (juin 2023, décembre 2024, août
2025). Source : [Sérendipidoc](https://www.serendipidoc.fr/open-data-jurisprudence/).

**Limites connues de Judilibre**

- Affaires jugées en chambre du conseil : seul le dispositif est publié.
- Avant le 15/04/2022 : seules les décisions publiques déjà portées en cassation
  ou déjà sur Légifrance sont disponibles.
- Recherche sans opérateurs booléens.
- L'API est en version bêta.
- Export : deux points d'entrée, `/export` (lots numérotés) et `/scan` (lots
  chaînés par le `next_batch` de la réponse, dont `searchAfter` ; `search_after` seul est ignoré), documentés dans le Swagger 2.0 lu le 23/10/2026
  (version 1.0.0, ajouté au portail le 19/08/2025). Taille de lot : 10 par défaut,
  1 000 au maximum. Le Swagger indique une limite « par défaut, pour une connexion
  non authentifiée » de 10 résultats par lot et 1 000 au total ; la limite avec une
  clé n'y figure pas. **Quotas de débit par application et dump complet : [non
  vérifié]**, à lire sur la page de l'application PISTE. Filtres : nature, matière,
  chambre, formation, juridiction, siège, niveau de publication, solution, dates
  (création ou mise à jour). Point d'entrée `/stats` : agrégats (année, mois,
  juridiction, matière, solution, type…) pour `cc`, `ca`, `tj`, `tcom`.
- Champs d'une décision (`decisionFull`) : texte intégral pseudonymisé, zones,
  visas (textes appliqués), **décision attaquée (`contested`) et décision suivante
  (`forward`)**, rapprochements, chronologie (`timeline`), thèmes, sommaire, ECLI,
  numéros de pourvoi, solution, niveau de publication, code NAC.
- **Accès de production (vérifié le 27/10/2026).** L'API attend la clé de l'application dans l'en-tête `KeyId`, sans client id ni secret OAuth ([tutoriel officiel de la Cour de cassation](https://github.com/Cour-de-cassation/judilibre-tutoriels)). L'application créée automatiquement à l'inscription est de type bac à sable et n'était abonnée à aucune API : ses appels renvoyaient 403 en bac à sable. Pour la production, il a fallu créer une seconde application, l'abonner à JUDILIBRE (production) et accepter les conditions d'utilisation de JUDILIBRE en production. Avant cet abonnement, la production répondait 400, avec ou sans clé, y compris sur `/healthcheck`. Le téléchargement complet des quatre types de juridiction est fait (28/10/2026, 2 183 473 décisions, environ 27 Go, sans doublon) ; totaux, tailles et contenu des champs dans `mesures.md` §7. `/stats` ne renvoie que la Cour de cassation ; les autres totaux viennent de `/scan`. Un lot de 1 000 décisions pèse de 5 Mo (Cour de cassation) à 13-16 Mo (cours d'appel) ; il se télécharge en 6 à 40 secondes. Quotas de débit : **non mesurés**. Python.org 3.14 sur macOS n'a pas de certificats racine par défaut : `Install Certificates.command` règle le défaut de vérification TLS.
- PISTE propose 39 entrées d'API (une trentaine d'API distinctes) sur le compte
  d'Alan au 23/10/2026. Justice : JUDILIBRE et « Justice back » (version 0.1, ajoutée
  le 22/07/2026), qui sert le contenu du site justice.fr (lieux de justice,
  communes, simulateurs, fiches) et non des décisions. Aussi : Légifrance, DECP et
  DUME (marchés publics), Chorus Pro et G2B (facturation), CaptchEtat, E-Signature,
  Ingres (nomenclatures RH). La liste varie selon l'organisation du compte.
- API : endpoints `/search`, `/decision`, `/export`, `/taxonomy`,
  `/transactionalhistory` (journal des créations, mises à jour et suppressions,
  prévu pour synchroniser une base locale). Authentification par en-tête
  `KeyId` après création d'un compte PISTE et validation des CGU. Bac à sable :
  `sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0`, production :
  `api.piste.gouv.fr/cassation/judilibre/v1.0`. Le texte est découpé en zones
  (`introduction`, `expose`, `moyens`, `motivations`, `dispositif`, `annexes`)
  par fragments `start`/`end`. Source :
  [Cour-de-cassation/judilibre-search](https://github.com/Cour-de-cassation/judilibre-search).
  Paramètres de `/export` et quotas : non documentés dans cette source.
- Taux d'échec de pseudonymisation et couverture réelle : **[non vérifié]**. Le
  rapport officiel
  [ODDJ 2025](https://www.justice.gouv.fr/sites/default/files/2025-08/rapport_oddj_2025.pdf)
  n'a pas pu être lu (site en maintenance au moment de la recherche).

### Ordre administratif

Plateforme opendata.justice-administrative.fr : Conseil d'État (depuis le
30/09/2021), cours administratives d'appel (depuis le 31/03/2022), tribunaux
administratifs (depuis le 30/06/2022). Licence Ouverte 2.0 et CGU du
18/01/2022. Volumes : non détaillés ici.
Sources : [Conseil d'État](https://www.conseil-etat.fr/decisions-de-justice/open-data),
[aide](https://opendata.justice-administrative.fr/aide.html),
[CGU](https://opendata.justice-administrative.fr/cgu.html).

- **Publication** : répertoires par année puis par mois (date de lecture),
  chacun téléchargeable en archive compressée contenant des fichiers XML. Mise
  en ligne le lendemain du prononcé pour le Conseil d'État, du mardi au samedi.
- **Balises XML documentées** : `Identification`, `Date_Mise_Jour`,
  `Code_Juridiction`, `Nom_Juridiction`, `Numero_Dossier`, `Date_Lecture`,
  `Numero_ECLI`, `Avocat_Requerant`, `Type_Decision`, `Type_Recours`,
  `Code_Publication` (A, B, C, D, Z), `Date_Audience`, `Numero_Role`,
  `Formation_Jugement`, `Texte_Integral` (paragraphes en `<p>`).
- **Téléchargement en masse** : archives mensuelles à URL directe, listées
  dans les index `/DCE/`, `/DCA/` et `/DTA/`. Détail, tailles et structure réelle
  des fichiers dans [`mesures.md`](mesures.md) (la structure réelle diffère en
  partie de la liste de balises ci-dessus).

### Statistiques ministérielles

- [Chiffres clés de la Justice](https://www.justice.gouv.fr/documentation/etudes-et-statistiques/chiffres-cles-justice-2025),
  édition 2025 (publiée le 28/10/2025) : PDF d'environ 40 pages, agrégé.
- Sur [data.gouv.fr](https://www.data.gouv.fr/organizations/ministere-de-la-justice),
  l'organisation du ministère liste 11 jeux de données, dont un fichier géocodé
  des structures de la Justice (Licence Ouverte).
- Aucun jeu ouvert détaillé sur les délais de jugement ni sur l'exécution des
  peines n'a été trouvé.
- Existence d'un portail data.justice.gouv.fr : **[non vérifié]**.

### Fondement légal

Article 21 de la loi n° 2016-1321 du 7 octobre 2016 (mise à disposition
gratuite de l'ensemble des décisions de justice) ; décret n° 2021-1276 du
30/09/2021.

---

## 2. Offre de jurimétrie existante

Source des prix et des positionnements :
[AlphaDeep](https://www.alphadeep.fr/guides/comparatif-ia-juridique-france-2026),
éditeur d'un produit concurrent, donc source intéressée. Prix à revérifier chez
chaque éditeur.

| Acteur | Cible | Prix indiqué | Jurimétrie |
|---|---|---|---|
| Predictice | Avocats, juristes, assureurs | dès 250 € HT/mois, engagement annuel | Oui, cœur de l'offre |
| Doctrine | Avocats, directions juridiques | Sur devis | Moteur de recherche, non décrit comme jurimétrie |
| GenIA-L (Lefebvre Dalloz) | Avocats, juristes d'entreprise | dès 213 € HT/mois | Non décrit |
| Ordalie | Petits cabinets, notaires | gratuit, puis 69-99 € HT/mois | Non décrit |
| Jimini AI | Cabinets avec leurs propres documents | Sur devis | Non décrit |
| Lexis+ avec Protégé (LexisNexis) | Clients LexisNexis | Sur devis, lancement France annoncé sept. 2026 **[non vérifié]** | Non décrit |
| Case Law Analytics | Quantification du risque judiciaire | Inconnu | Statut « acquis » sur une base tierce ([Coverager](https://coverager.com/company/case-law-analytics/)), acquéreur et date inconnus |

**Consolidation** (sources secondaires, **[non vérifié]** en source primaire) :

- Doctrine a racheté Predictice le 17/09/2025 et Maite.ai en février 2026.
- Promesse d'achat de Doctrine par RELX (maison-mère de LexisNexis) signée le
  28/04/2026, non finalisée début juillet 2026. Pas d'information postérieure.

Tous ces acteurs sont payants et orientés professionnels. Le CNB a classé les
acteurs de jurimétrie dans un
[rapport de 2020](https://www.ccbe.eu/fileadmin/speciality_distribution/public/documents/Events/20201027_Online_Roundtable/Rapport-CNB-sur-la-jurime-trie-adopte-9-10-20.pdf)
(Predictice, Case Law Analytics, Jurisdata Analytics, Legalmetrics).

---

## 3. Initiatives ouvertes et gratuites

- [justicelibre.org](https://github.com/Dahliyaal/justicelibre) : serveur MCP
  gratuit (code MIT, données sous Licence Ouverte), plus de 3,9 M de décisions
  (Cour de cassation, Conseil d'État, juridictions administratives, Conseil
  constitutionnel, CEDH, CJUE). Tourné vers les utilisateurs d'assistants IA et
  les développeurs. Le dépôt public n'est plus maintenu, le développement
  continue dans un dépôt privé.
- Aucune plateforme grand public qui vulgarise les décisions ou en tire des
  indicateurs sur le fonctionnement de la justice n'a été trouvée. La recherche
  civic tech a été peu fructueuse : ce n'est pas une preuve d'absence.
- Aucun projet français nommé « Open Justice » trouvé. Terme générique, usage
  international **[non vérifié]**.

---

## 4. Contraintes

- **Interdiction du profilage** (article 33 de la loi de réforme de la justice
  de 2019 ; pour la justice administrative, article L. 10, 4e alinéa, du code
  de justice administrative) : les données d'identité des magistrats et des
  membres du greffe ne peuvent être réutilisées pour **évaluer, analyser,
  comparer ou prédire** leurs pratiques professionnelles, réelles ou supposées.
  Sanction pénale (articles 226-18, 226-24 et 226-31 du code pénal). Sources :
  [CGU justice administrative, art. VI](https://opendata.justice-administrative.fr/cgu.html),
  [ABA Journal](https://www.abajournal.com/news/article/france-bans-and-creates-criminal-penalty-for-judicial-analytics).
  Le verbe « analyser » est plus large que « prédire ». Les analyses par
  juridiction, type de contentieux ou délai ne sont pas concernées par cette
  lecture, à confirmer juridiquement **[non vérifié]**.
- **Conditions de réutilisation (CGU justice administrative, art. V)**, fondées
  sur l'article L. 322-1 du CRPA :
  - ne pas altérer les décisions ni en dénaturer le sens ; chaque décision
    réutilisée garde son numéro, la juridiction, la formation, le siège et la
    date de prononcé ;
  - un extrait est permis si son caractère partiel est indiqué et que la
    décision intégrale reste accessible ; un commentaire est libre mais doit
    être nettement distingué du texte de la décision ;
  - mentionner la source (base Données ouvertes du Conseil d'État) ;
  - mentionner la date de dernière mise à jour, sous la forme « Document chargé
    sur le site source le … » (date de chargement par le réutilisateur, non
    celle de la décision) ;
  - le réutilisateur est responsable de traitement RGPD et doit tenir ses
    données à jour ; le Conseil d'État peut corriger ou supprimer une décision
    à tout moment, sans préavis.
- Les CGU de Judilibre (Cour de cassation) et de PISTE s'appliquent séparément
  aux données judiciaires. Leur contenu détaillé n'a pas été lu **[non
  vérifié]**.
- **Pénal non ouvert avant 2027-2028** : pas de décisions de condamnation ni
  d'application des peines aujourd'hui.
- **Exécution des peines** : relève des statistiques ministérielles, pas des
  décisions publiées. Aucun jeu ouvert détaillé identifié.

---

## 5. Domaines (vérification du 22/10/2026)

Interrogation directe du registre AFNIC. Un domaine « libre » n'est pas réservé
tant qu'il n'est pas enregistré chez un registrar. Marques non vérifiées (INPI).

| Domaine | État |
|---|---|
| `open-justice.fr` | Nom retenu, enregistré par Alan le 22/10/2026 (déclaration d'Alan, non revérifiée au registre) |
| `justiceopen.fr`, `openjustice-france.fr` | Libres |
| `openjustice.fr` | Pris |
| `justicevisible.fr` | Libre, alternative écartée |
| `open-justice.com`, `open-justice.org`, `openjustice.eu` | Pris |
| `open-justice.eu` | Sans DNS, probablement libre **[non vérifié]** |

---

## 6. Points à vérifier

1. Quotas et export en masse de l'API Judilibre (Swagger PISTE).
2. Publication effective des décisions prud'homales au 30/09/2026.
3. Existence et contenu de data.justice.gouv.fr.
4. Statut du rachat de Doctrine par RELX et sort de Case Law Analytics.
5. Rapport ODDJ 2025, à relire quand le site est de nouveau en ligne.
6. Volumes de la justice administrative.
7. Marque « Open Justice » (INPI) et usage du nom en France.
8. Sens exact des fichiers `*_documents_reverses.csv` (voir `mesures.md`).
9. CGU de Judilibre et de PISTE (lecture complète).
