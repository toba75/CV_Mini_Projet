# Tâche — Tester la détection de texte avec CRAFT ou PaddleOCR

Statut : DONE
Ordre : 004
Workstream : WS2
Milestone : M1

## Contexte
Avant d'intégrer la détection de texte dans le pipeline, il faut valider que le modèle choisi (CRAFT ou PaddleOCR en mode détection seule) fonctionne correctement sur des images de tranches de livres, en particulier sur du texte vertical. Cette tâche est exploratoire : elle produit un module fonctionnel de détection avec des résultats vérifiés qualitativement.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M1 > WS2 — points 1 et 2)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 4 — Détection des zones de texte)
- Code : `src/detect_text.py`

Dépendances :
- Tâche 001 — Initialiser la structure du projet (doit être DONE)

## Objectif
Implémenter `src/detect_text.py` avec une fonction de détection de zones de texte utilisant PaddleOCR (mode détection seule) ou CRAFT. Vérifier que les bounding boxes retournées sont cohérentes sur du texte vertical.

## Règles attendues
- Conventions image : entrée en BGR.
- Les bounding boxes retournées doivent être dans un format standardisé (liste de polygones ou rectangles avec coordonnées).
- Le module doit être utilisable indépendamment du reste du pipeline.
- Validation explicite des entrées + `raise ValueError`.

## Évolutions proposées
- Fonction `init_detector(model_name: str = "paddleocr") -> object` : initialise et retourne le modèle de détection (lazy loading).
- Fonction `detect_text_regions(image: np.ndarray, detector: object = None) -> list[dict]` : détecte les zones de texte et retourne une liste de dictionnaires `{"bbox": [...], "confidence": float}`.
- Les bounding boxes doivent être des polygones à 4 points (compatible texte orienté/vertical).
- Tester sur au moins 2 images : une tranche avec texte horizontal, une avec texte vertical.

## Critères d'acceptation
- [x] `init_detector` retourne un objet detector fonctionnel sans erreur
- [x] `detect_text_regions` retourne une liste (éventuellement vide) de dictionnaires avec clés `bbox` et `confidence`
- [x] Chaque `bbox` contient 4 points (polygone) avec des coordonnées numériques valides
- [x] La confiance est un float entre 0 et 1
- [x] Sur une image contenant du texte lisible, au moins une région est détectée
- [x] Validation des entrées : `ValueError` sur image None ou vide
- [x] Tests couvrent les scénarios nominaux + erreurs + bords (image sans texte, image vide)
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/004-text-detection-test` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/004-text-detection-test` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS2] #004 RED: tests détection de texte`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS2] #004 GREEN: détection de texte PaddleOCR/CRAFT fonctionnelle`.
- [ ] **Pull Request ouverte** vers `main` : `[WS2] #004 — Détection de texte`.
