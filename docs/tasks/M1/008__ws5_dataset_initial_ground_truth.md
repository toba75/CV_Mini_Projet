# Tâche — Constituer le dataset initial et annoter le ground truth

Statut : DONE
Ordre : 008
Workstream : WS5
Milestone : M1

## Contexte
L'évaluation du pipeline ShelfScan nécessite un dataset de référence avec des annotations manuelles (ground truth). 15 photos d'étagères sont déjà disponibles dans `data/` (IMG_3046.jpeg à IMG_3061.jpeg). Il reste à les organiser dans la structure du projet et à annoter manuellement les titres visibles dans un fichier CSV structuré.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M1 > WS5 — points 1 et 2)
- Spécification : `docs/specifications/specifications.md` (§5 Données, §6 Métriques d'évaluation)
- Données : `data/` (photos existantes), `data/raw/`, `data/ground_truth/`

Dépendances :
- Tâche 001 — Initialiser la structure du projet (doit être DONE)

## Objectif
Organiser les 15 photos existantes dans `data/raw/`, puis produire un fichier CSV d'annotations ground truth listant les titres visibles pour chaque photo.

## Règles attendues
- Les photos doivent être en résolution suffisante (min 1920×1080 px recommandé).
- Les conditions doivent varier : éclairage naturel/artificiel, angles légèrement différents, densités de livres différentes.
- Le format CSV doit être standardisé et lisible par pandas.
- Les noms de fichiers doivent suivre une convention claire.

## Évolutions proposées
- Déplacer les 15 photos existantes de `data/` vers `data/raw/` (IMG_3046.jpeg à IMG_3061.jpeg). Les photos sont déjà prises, il n'y a pas besoin d'en capturer de nouvelles.
- Créer `data/ground_truth/ground_truth.csv` avec les colonnes :
  ```
  image_filename,spine_index,title,author
  shelf_01.jpg,1,"Le Petit Prince","Antoine de Saint-Exupéry"
  shelf_01.jpg,2,"1984","George Orwell"
  ...
  ```
- Écrire un script utilitaire ou une fonction `src/eval_utils.py:load_ground_truth(csv_path: str) -> pd.DataFrame` pour charger et valider le CSV.
- Documenter les conditions de prise de vue (lieu, éclairage, appareil) dans un fichier `data/README.md`.

## Critères d'acceptation
- [x] 15 photos existantes déplacées dans `data/raw/` au format JPEG
- [x] Les photos couvrent au moins 3 conditions d'éclairage ou d'angle différentes
- [x] `data/ground_truth/ground_truth.csv` existe avec les colonnes `image_filename`, `spine_index`, `title`, `author`
- [x] Chaque photo a au moins 3 titres annotés dans le CSV
- [x] Le CSV est chargeable par pandas sans erreur
- [x] `load_ground_truth` charge et valide le CSV (colonnes attendues, pas de lignes vides)
- [x] Tests couvrent le chargement du CSV (colonnes, types, cas d'erreur)
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/008-dataset-ground-truth` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/008-dataset-ground-truth` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS5] #008 RED: tests chargement ground truth`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS5] #008 GREEN: dataset initial et ground truth`.
- [ ] **Pull Request ouverte** vers `main` : `[WS5] #008 — Dataset initial et ground truth`.
