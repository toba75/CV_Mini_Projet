# Tâche — Implémenter le prétraitement d'image avec CLAHE

Statut : DONE
Ordre : 002
Workstream : WS1
Milestone : M1

## Contexte
Le prétraitement est la première étape du pipeline ShelfScan. Il doit charger une image, la redimensionner de manière adaptative et appliquer une amélioration de contraste via CLAHE sur le canal de luminance (espace LAB ou HLS). Cette étape conditionne la qualité de toutes les étapes suivantes.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M1 > WS1 — point 3)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 2 — Prétraitement)
- Code : `src/preprocess.py`

Dépendances :
- Tâche 001 — Initialiser la structure du projet (doit être DONE)

## Objectif
Écrire `src/preprocess.py` avec les fonctions de chargement d'image, redimensionnement adaptatif et application de CLAHE sur le canal de luminance.

## Règles attendues
- Conventions image : les fonctions reçoivent et retournent des images en BGR (convention OpenCV). Documenter clairement les conversions internes (BGR → LAB → BGR).
- Pas de modification en place : chaque fonction retourne une nouvelle image.
- Validation explicite des entrées + `raise ValueError` si l'image est None ou vide.
- Le redimensionnement doit conserver le ratio d'aspect.

## Évolutions proposées
- Fonction `load_image(path: str) -> np.ndarray` : charge l'image via `cv2.imread`, lève `FileNotFoundError` si le fichier n'existe pas, `ValueError` si l'image est invalide.
- Fonction `resize_image(image: np.ndarray, max_width: int = 1920) -> np.ndarray` : redimensionne en conservant le ratio si la largeur dépasse `max_width`.
- Fonction `apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple = (8, 8)) -> np.ndarray` : convertit en LAB, applique CLAHE sur le canal L, reconvertit en BGR.
- Fonction `preprocess(path: str) -> np.ndarray` : orchestre load → resize → CLAHE et retourne l'image prétraitée.

## Critères d'acceptation
- [x] `load_image` charge correctement une image existante et lève les bonnes exceptions
- [x] `resize_image` redimensionne en conservant le ratio d'aspect
- [x] `resize_image` ne modifie pas une image déjà plus petite que `max_width`
- [x] `apply_clahe` retourne une image de mêmes dimensions que l'entrée
- [x] `apply_clahe` améliore effectivement le contraste (écart-type des pixels augmenté ou inchangé)
- [x] `preprocess` enchaîne correctement les 3 étapes
- [x] Toutes les fonctions lèvent `ValueError` sur une entrée None ou vide
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/002-preprocess-clahe` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/002-preprocess-clahe` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS1] #002 RED: tests prétraitement CLAHE`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [x] **Commit GREEN** : `[WS1] #002 GREEN: prétraitement CLAHE implémenté`.
- [ ] **Pull Request ouverte** vers `main` : `[WS1] #002 — Prétraitement CLAHE`.
