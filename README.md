# CSV/XLS Analyse

Cette application Streamlit permet d’importer plusieurs fichiers CSV ou ZIP, de fusionner les données et de télécharger un fichier Excel contenant une feuille "Fusion" regroupant toutes les lignes et une feuille "Moyenne conso DATA" cumulant les volumes par numéro d’utilisateur.

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
