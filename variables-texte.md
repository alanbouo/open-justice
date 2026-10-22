# Variables à extraire du texte intégral

Établi le 22 octobre 2026 à partir de la lecture de 7 décisions de septembre 2025
(3 jugements de TA : OQTF, fiscal, responsabilité ; 2 ordonnances de TA :
irrecevabilité manifeste, désistement ; 1 arrêt de CAA ; 1 décision du CE). Sept
exemples ne sont pas un échantillon représentatif : la liste est une hypothèse de
travail, chaque extraction doit être validée sur un échantillon relu à la main
avant publication.

## Structure constatée d'une décision

1. **Visas** (« Vu la procédure suivante ») : date de la requête, demandes,
   moyens, mémoire en défense, textes visés, désignation du juge, audience.
2. **Motifs** (« Considérant ce qui suit ») : numérotés, avec les articles
   cités et le raisonnement.
3. **Dispositif** (« DÉCIDE » / « ORDONNE », puis « Article 1er… ») : ce qui est
   effectivement jugé. C'est la partie la plus régulière.
4. **Bloc de clôture** : date de rendu, signatures, formule exécutoire.

Les ordonnances sont courtes (de 1 300 à 3 300 caractères dans les exemples) et
suivent un modèle quasi fixe ; l'extraction y est plus fiable que dans les
jugements.

## Variables candidates

**Procédure**
- Date(s) d'enregistrement de la requête et des mémoires (« enregistrés les 2 et
  10 septembre 2025 », « le 01/10/2014 » : formats variables).
- Date de clôture de l'instruction, date d'audience, date de rendu (« Rendu public
  par mise à disposition au greffe le… », « Décision rendue le… »).
- Formation : juge unique / magistrat désigné / collégiale ; audience tenue ou non ;
  rapporteur public dispensé ou non. **Rôles seulement, jamais de noms.**
- Défendeur : mémoire en défense produit ou non (« n'a pas produit de mémoire en
  défense »).

**Parties**
- Nature du requérant : personne physique, société, association, collectivité.
- Représenté par un avocat : oui / non (« représenté par Me… »). Ne pas conserver
  le nom.
- Défendeur (autorité) : préfet, ministre, commune, établissement public, lu dans les
  demandes et dans l'article de notification.

**Litige**
- Domaine : le plus fiable semble être les **codes visés** (« Vu le code de l'entrée
  et du séjour des étrangers », « code général des impôts », « code de la construction
  et de l'habitation »), plutôt que des mots-clés dans le corps.
- Décision contestée : type (arrêté, décision implicite de rejet), date, auteur.
- Demandes : annulation, décharge, indemnisation (montant demandé), injonction,
  suspension, frais (montant demandé).
- Moyens invoqués : incompétence, insuffisance de motivation, erreur manifeste
  d'appréciation, article 8 de la CEDH, etc. (étiquettes à définir).
- Textes cités : codes et articles (« article L. 761-1 », « R. 222-1 »).
- Si appel ou cassation : juridiction d'origine, date et numéro du jugement attaqué,
  son issue (« a rejeté sa demande »). Permet de calculer un taux d'infirmation.

**Dispositif (ce qui est décidé)**
- Pour chaque article : annulation, rejet, réformation, renvoi, injonction (délai,
  astreinte et son montant), frais, notification.
- Frais irrépétibles : montant, qui paie (l'État, la collectivité, le requérant),
  qui reçoit (le requérant ou son avocat).
- Montant de l'indemnité accordée, le cas échéant.
- Fondement d'un rejet par ordonnance (R. 222-1, alinéa 4 irrecevabilité,
  alinéa 1 désistement) et motif : tardiveté, requête prématurée, incompétence.
- **Qui l'emporte** : variable calculée à partir du dispositif (article 1er) et de
  `Solution`.

**Variables dérivées**
- Durée de jugement (rendu moins enregistrement de la requête) ; durée
  d'instruction (clôture) ; délai audience → rendu.
- Nombre d'articles du dispositif, présence d'une injonction, longueur des motifs.

## Points d'attention

- **Des noms de magistrats figurent hors du bloc de signature** : dans les visas
  (« la présidente a désigné M. … », « le rapport de M. … a été entendu », liste
  « siégeaient ») en plus des signatures, et en toutes lettres au Conseil d'État.
  Toute extraction doit exclure ces mentions : ne conserver que le rôle. Les
  noms d'avocats et de parties (initiales ou non) ne sont pas à conserver non plus.
- Une société n'est pas pseudonymisée dans l'exemple vu (désistement) : le texte brut
  ne doit pas être republié.
- **Dates incohérentes possibles** : une requête « enregistrée le 01/10/2014 » jugée
  en 2025 est peut-être une erreur de saisie ; à contrôler avant d'en tirer une
  durée.
- Le texte varie entre ordres (CE : « pourvoi », « non admis » ; CAA : rappel de la
  procédure de première instance) : prévoir une extraction par ordre et par type
  de décision.
