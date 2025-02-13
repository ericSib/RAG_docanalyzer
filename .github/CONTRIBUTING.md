# Guide de Contribution

Merci de votre intérêt pour contribuer à RAG Document Analyzer ! Ce guide vous aidera à mettre en place votre environnement de développement et à comprendre notre processus de contribution.

## Prérequis

- Python 3.10 ou supérieur
- Git
- Un éditeur de code (VS Code recommandé)

## Installation de l'environnement de développement

1. Forker le dépôt sur GitHub

2. Cloner votre fork :
```bash
git clone https://github.com/votre-compte/rag-analyzer.git
cd rag-analyzer
```

3. Créer un environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows
```

4. Installer les dépendances de développement :
```bash
pip install -e ".[dev]"
```

## Standards de Code

Nous utilisons plusieurs outils pour maintenir la qualité du code :

- **Black** : Formatage automatique du code
  ```bash
  black src tests
  ```

- **isort** : Tri des imports
  ```bash
  isort src tests
  ```

- **mypy** : Vérification des types
  ```bash
  mypy src
  ```

- **pylint** : Analyse statique
  ```bash
  pylint src
  ```

Ces outils sont configurés dans `pyproject.toml`.

## Tests

Tous les nouveaux développements doivent être accompagnés de tests :

```bash
# Exécuter tous les tests
pytest

# Avec couverture de code
pytest --cov=src

# Tests spécifiques
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

## Structure du Projet

```
rag_analyzer/
├── src/                    # Code source
│   ├── domain/            # Modèles et règles métier
│   ├── application/       # Cas d'utilisation
│   ├── infrastructure/    # Implémentations techniques
│   └── presentation/      # Interface utilisateur Qt
├── tests/                 # Tests
│   ├── unit/             # Tests unitaires
│   ├── integration/      # Tests d'intégration
│   └── e2e/              # Tests end-to-end
└── config/               # Configuration
    └── defaults/         # Configurations par défaut
```

## Processus de Contribution

1. Créer une branche pour votre fonctionnalité :
```bash
git checkout -b feature/nom-de-la-fonctionnalite
```

2. Développer en suivant les standards de code

3. Écrire des tests

4. Commiter vos changements :
```bash
git add .
git commit -m "feat: description de la fonctionnalité"
```

Nous suivons les conventions de [Conventional Commits](https://www.conventionalcommits.org/).

5. Pousser vers votre fork :
```bash
git push origin feature/nom-de-la-fonctionnalite
```

6. Créer une Pull Request sur GitHub

## Pull Requests

- Donner un titre clair qui décrit les changements
- Inclure une description détaillée
- Référencer les issues liées
- S'assurer que tous les tests passent
- Obtenir une revue de code

## Questions et Support

- Créer une issue pour les bugs
- Utiliser les discussions GitHub pour les questions
- Consulter la documentation existante

Merci de contribuer à RAG Document Analyzer !
