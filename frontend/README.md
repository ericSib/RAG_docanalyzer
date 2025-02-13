# Frontend RAG Document Analyzer

Interface utilisateur basée sur Streamlit pour l'analyseur de documents RAG.

## Fonctionnalités

- Upload et analyse de documents
- Visualisation des métriques d'analyse
- Estimation des coûts d'implémentation RAG
- Interface intuitive et responsive

## Installation

1. Assurez-vous d'avoir installé toutes les dépendances :
```bash
pip install -r ../requirements.txt
```

2. Lancez l'application Streamlit :
```bash
streamlit run app.py
```

L'application sera accessible à l'adresse : http://localhost:8501

## Structure

- `app.py` : Application Streamlit principale
- `assets/` : Ressources statiques (images, styles, etc.)

## Utilisation

1. Ouvrez l'application dans votre navigateur
2. Uploadez un document (.txt, .md, ou .rst)
3. Attendez l'analyse
4. Consultez les résultats et recommandations

## Notes

- L'API backend doit être en cours d'exécution sur http://localhost:8000
- Taille maximale des fichiers : 10MB
- Formats supportés : .txt, .md, .rst
