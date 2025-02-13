# Architecture

## Structure du projet

- `src/core/` : Logique métier
  - `analyzer.py` : Analyse des documents
  - `models.py` : Gestion des modèles ML
  - `storage.py` : Gestion du stockage

- `src/ui/` : Interface utilisateur Qt
  - `windows/` : Fenêtres principales
  - `widgets/` : Composants réutilisables
  - `resources/` : Ressources UI

- `src/utils/` : Utilitaires
  - `config.py` : Configuration
  - `logger.py` : Logging

## Organisation du code

Le projet suit une architecture en couches :
1. Core : Logique métier indépendante de l'UI
2. UI : Interface utilisateur Qt
3. Utils : Services techniques partagés
