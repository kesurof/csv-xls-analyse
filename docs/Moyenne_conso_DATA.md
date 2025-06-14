# Feuille "Moyenne conso DATA"

Ce document décrit la logique de génération de la feuille **Moyenne conso DATA**
produite par l'application. Les étapes ci-dessous reprennent le traitement
réalisé dans `compute_moyenne_conso` du fichier `app.py`.

## Source et filtrage des données

- Point d'entrée : fichier Excel fusionné ou CSV brut.
- Seules les lignes dont **Nom de la sous-rubrique** commence par `Echanges`
  sont conservées.

## Agrégation par utilisateur

- Les données sont groupées par **Numéro de l’utilisateur**.
- Pour chaque utilisateur, on conserve les informations d’identité :
  - Numéro du centre de facturation
  - Numéro de l’utilisateur
  - Nom et prénom
  - Numéro de téléphone

## Génération des colonnes mensuelles

- La date de la colonne **Période de la facture** (format `JJ/MM/AAAA`) est
  convertie au mois correspondant.
- On liste tous les mois distincts et on crée une colonne pour chacun, nommée
  `<mois en toutes lettres>-<AA>` (exemple : `juillet-24`).
- Les colonnes mensuelles sont triées du plus récent au plus ancien.

## Calculs de consommation

- Chaque colonne mensuelle contient la somme des volumes du mois au format
  texte `X Go Y Mo Z Ko`.
- **Total (Go)** : somme de toutes les consommations mensuelles, exprimée en Go
  avec deux décimales.
- **Moyenne (Go) 4 mois** : moyenne des quatre derniers mois disponibles,
  également en Go (2 déc.).
- **Moyenne (Go) total** : moyenne sur l'ensemble des mois disponibles (2 déc.).

## Mise en forme

- La feuille résultante est nommée `Moyenne conso DATA`.
- Les colonnes fixes d'identité sont placées à gauche, suivies des calculs et des
  colonnes mensuelles.
- Si une feuille portant déjà ce nom existe, elle est remplacée.
