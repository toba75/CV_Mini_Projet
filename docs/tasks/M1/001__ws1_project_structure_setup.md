# Tâche — Initialiser la structure du projet et installer les dépendances

Statut : DONE
Ordre : 001
Workstream : WS1
Milestone : M1

## Contexte
Le projet ShelfScan nécessite une structure de dossiers standardisée et un environnement Python fonctionnel avant toute implémentation. Cette tâche pose les fondations techniques du repo.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M1 > WS1 — points 1 et 2)
- Spécification : `docs/specifications/specifications.md` (§4 Stack technique)
- Code : `src/` (création des fichiers vides)

Dépendances :
- Aucune (tâche racine)

## Objectif
Créer l'arborescence du projet conforme au plan et installer toutes les dépendances nécessaires au pipeline ShelfScan.

## Règles attendues
- La structure doit correspondre exactement à celle décrite dans le plan d'implémentation.
- Les modules Python dans `src/` doivent être importables (présence de `__init__.py`).
- `requirements.txt` doit lister les dépendances avec des versions compatibles.

## Évolutions proposées
- Créer l'arborescence complète :
  ```
  shelfscan/
  ├── src/
  │   ├── __init__.py
  │   ├── preprocess.py
  │   ├── segment.py
  │   ├── detect_text.py
  │   ├── ocr.py
  │   ├── postprocess.py
  │   └── pipeline.py
  ├── data/
  │   ├── raw/
  │   └── ground_truth/
  ├── outputs/
  ├── notebooks/
  ├── tests/
  │   └── __init__.py
  ├── requirements.txt
  └── README.md
  ```
- Rédiger `requirements.txt` avec : opencv-python, paddleocr, paddlepaddle, torch, torchvision, streamlit, pillow, pandas, pytesseract, rapidfuzz, requests.
- Vérifier que `pip install -r requirements.txt` s'exécute sans erreur.
- Chaque fichier `.py` dans `src/` contient un placeholder minimal (docstring de module).

## Critères d'acceptation
- [x] L'arborescence `src/`, `data/raw/`, `data/ground_truth/`, `outputs/`, `notebooks/`, `tests/` existe
- [x] Tous les fichiers `.py` listés dans le plan sont présents dans `src/`
- [x] `src/__init__.py` et `tests/__init__.py` existent
- [x] `requirements.txt` est présent et liste toutes les dépendances de la stack technique
- [x] `pip install -r requirements.txt` s'exécute sans erreur
- [x] Les modules sont importables : `from src import preprocess, segment, detect_text, ocr, postprocess, pipeline`
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/001-project-structure-setup` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/001-project-structure-setup` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS1] #001 RED: <résumé>` (fichiers de tests uniquement).
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [x] **Commit GREEN** : `[WS1] #001 GREEN: <résumé>`.
- [x] **Pull Request ouverte** vers `main` : `[WS1] #001 — Initialiser la structure du projet`.
