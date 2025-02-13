# RAG Document Analyzer

Application d'analyse de documents basée sur le Retrieval-Augmented Generation (RAG).

## Fonctionnalités

- Interface graphique Qt moderne et intuitive
- Analyse sémantique de documents avec sentence-transformers
- Stockage local des documents et embeddings
- Recherche sémantique dans les documents

## Installation

### Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation depuis les sources

1. Cloner le dépôt :
```bash
git clone https://github.com/votre-compte/rag-analyzer.git
cd rag-analyzer
```

2. Créer un environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -e ".[dev]"  # Installation avec dépendances de développement
# ou
pip install -e .         # Installation minimale
```

## Développement

### Structure du projet

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

### Tests

Exécuter les tests :
```bash
pytest                 # Tous les tests
pytest tests/unit      # Tests unitaires uniquement
pytest tests/e2e      # Tests end-to-end uniquement
```

### Outils de développement

- `black` : Formatage du code
- `isort` : Tri des imports
- `mypy` : Vérification des types
- `pylint` : Analyse statique

Configuration dans `pyproject.toml`.

## Licence

MIT License. Voir le fichier LICENSE pour plus de détails.
