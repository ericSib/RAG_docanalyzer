# Changelog

## [1.1.0] - 2025-02-13

### Optimisations de packaging

#### Gestion des DLLs et dépendances
- Optimisation du fichier PyInstaller .spec pour réduire la taille du package
- Mise en place d'un système de filtrage intelligent des DLLs
- Suppression des dépendances non essentielles

#### Améliorations spécifiques
1. **Gestion des DLLs**
   - Création d'une liste de DLLs essentielles par package
   - Implémentation d'un système de filtrage pour éviter les duplications
   - Protection des DLLs critiques contre la compression UPX

2. **Optimisation NumPy**
   - Résolution des avertissements array_api
   - Configuration optimisée pour NumPy dans PyInstaller
   - Exclusion des modules de test et outils de compilation

3. **Gestion PyTorch**
   - Optimisation des imports PyTorch et torchvision
   - Suppression des composants CUDA non utilisés
   - Réduction des dépendances redondantes

4. **Interface Graphique**
   - Optimisation des imports PyQt6
   - Suppression des frameworks GUI non utilisés
   - Protection des DLLs Qt essentielles

### Détails techniques

#### Modifications du fichier .spec
- Implémentation d'un système de filtrage des binaires
- Configuration précise des hooks PyInstaller
- Optimisation des imports de modules

#### Exclusions
- Modules de test et exemples
- Composants CUDA et MKL non utilisés
- Frameworks GUI alternatifs
- Modules système non essentiels

### Impact des modifications
- Réduction significative de la taille du package
- Amélioration des performances de chargement
- Meilleure gestion de la mémoire
- Suppression des avertissements de dépréciation
