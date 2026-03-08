# Tâche — Initialiser la structure du projet et installer les dépendances

Statut : TODO
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
- [ ] L'arborescence `src/`, `data/raw/`, `data/ground_truth/`, `outputs/`, `notebooks/`, `tests/` existe
- [ ] Tous les fichiers `.py` listés dans le plan sont présents dans `src/`
- [ ] `src/__init__.py` et `tests/__init__.py` existent
- [ ] `requirements.txt` est présent et liste toutes les dépendances de la stack technique
- [ ] `pip install -r requirements.txt` s'exécute sans erreur
- [ ] Les modules sont importables : `from src import preprocess, segment, detect_text, ocr, postprocess, pipeline`
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/001-project-structure-setup` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/001-project-structure-setup` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS1] #001 RED: <résumé>` (fichiers de tests uniquement).
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS1] #001 GREEN: <résumé>`.
- [ ] **Pull Request ouverte** vers `main` : `[WS1] #001 — Initialiser la structure du projet`.
