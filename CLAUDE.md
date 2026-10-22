# Contexte du dépôt

Open Justice : projet de plateforme ouverte pour informer les citoyens sur le
fonctionnement de la justice en France, à partir des décisions et des
statistiques publiées en open data. Le projet est à l'état d'idée.

Ce dépôt est **public** et le reste. Rien de personnel, aucun secret, aucune clé
d'API, aucune donnée issue de la vie privée d'Alan. Les identifiants d'accès aux
API (par exemple PISTE) ne s'écrivent jamais dans les fichiers.

---

## RÈGLE DE LECTURE — à appliquer avant toute réponse

Les fichiers de ce dépôt font autorité sur tes suppositions. Ils ne sont pas
chargés automatiquement : **tu dois les lire.**

| Si la demande porte sur… | Lire avant de répondre |
|---|---|
| Les données disponibles, leur couverture, les acteurs existants | `recherche.md` |
| Volumes, tailles, structure réelle des fichiers, ce qui est mesuré | `mesures.md` |
| L'objectif, le périmètre, le nom | `README.md` |

---

## Règles de fond

1. **Ne pas inventer de donnée.** Aucun volume, prix, date ou statut qui ne
   vienne pas d'une source citée. Ce qui n'est pas vérifié se marque comme tel.
2. **Dire quand on ne sait pas.** Un point ouvert se nomme comme ouvert, il ne
   se comble pas par une supposition plausible.
3. **Respecter la contrainte légale.** L'article 33 de la loi de réforme de la
   justice de 2019 interdit de réutiliser les données identifiantes des
   magistrats pour évaluer ou prédire leur pratique. Aucune fonctionnalité ne
   doit y contrevenir.
4. **Ne pas présenter une hypothèse comme un fait.** Le projet n'a ni
   utilisateurs, ni audience, ni produit lancé.
5. **Citer les sources.** Chaque fait de `recherche.md` renvoie à son origine,
   avec la date de vérification quand elle compte.

---

## RÈGLE D'ÉCRITURE DES FICHIERS

**Mise à jour = réécriture.** Ne jamais empiler une section « mise à jour
<mois> » sous une version périmée. Le fichier reflète l'état actuel, l'historique
est dans git.

**Source unique.** Si une information existe à deux endroits, elles divergeront.
Signaler toute duplication constatée.

---

## Git

Commit après chaque modification de fichier, message d'une ligne en français,
préfixé par le fichier concerné. Exemple : `recherche: calendrier pénal vérifié`.
