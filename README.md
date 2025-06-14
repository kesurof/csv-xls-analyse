# CSV/XLS Analyse

Cette application Streamlit permet d’importer plusieurs fichiers CSV ou ZIP,
de fusionner les données et de télécharger un fichier Excel contenant deux
onglets :

- **Fusion** : toutes les lignes regroupées.
- **Moyenne conso DATA** : synthèse mensuelle des volumes par numéro
  d’utilisateur.

La logique complète de génération de la feuille « Moyenne conso DATA » est
détaillée dans [docs/Moyenne_conso_DATA.md](docs/Moyenne_conso_DATA.md).

## Prérequis

Installez les dépendances nécessaires :

```bash
pip install -r requirements.txt
```

## Exécution

Lancez l’application avec Streamlit :

```bash
streamlit run app.py
```

Un navigateur s’ouvrira avec l’interface d’upload et de conversion.
