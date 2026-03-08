# Tâche — Comparer les modèles OCR sur des crops manuels de tranches

Statut : TODO
Ordre : 005
Workstream : WS3
Milestone : M1

## Contexte
Trois modèles OCR sont envisagés pour le projet : PaddleOCR, TrOCR (Microsoft) et Tesseract 5. Avant de choisir le modèle principal, il faut les tester qualitativement sur des crops manuels de tranches de livres et comparer leurs sorties. Cette tâche produit un module OCR fonctionnel et un rapport de comparaison.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M1 > WS3 — points 1 et 2)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 5 — Reconnaissance OCR, §4 Stack technique)
- Code : `src/ocr.py`

Dépendances :
- Tâche 001 — Initialiser la structure du projet (doit être DONE)

## Objectif
Implémenter `src/ocr.py` avec une interface unifiée pour exécuter l'OCR via PaddleOCR, TrOCR et Tesseract. Tester chaque modèle sur 3-4 crops manuels de tranches et documenter les résultats qualitatifs pour guider le choix du modèle principal.

## Règles attendues
- Conventions image : entrée en BGR (conversion interne si le modèle attend RGB ou grayscale).
- L'interface doit être uniforme quel que soit le moteur OCR utilisé.
- Validation explicite des entrées + `raise ValueError`.
- Les résultats de comparaison doivent être traçables (loggés ou sauvegardés).

## Évolutions proposées
- Fonction `init_ocr_engine(engine_name: str) -> object` : initialise le moteur OCR demandé (`"paddleocr"`, `"trocr"`, `"tesseract"`). Lève `ValueError` si le nom est inconnu.
- Fonction `recognize_text(image: np.ndarray, engine: object) -> list[dict]` : exécute l'OCR et retourne une liste de `{"text": str, "confidence": float}`.
- Fonction `compare_engines(image: np.ndarray, engine_names: list[str]) -> dict` : exécute l'OCR avec chaque moteur et retourne un dictionnaire `{engine_name: [results]}` pour comparaison.
- Préparer 3-4 crops manuels dans `data/raw/` pour les tests.

## Critères d'acceptation
- [ ] `init_ocr_engine` initialise correctement chacun des 3 moteurs (PaddleOCR, TrOCR, Tesseract)
- [ ] `init_ocr_engine` lève `ValueError` pour un nom de moteur inconnu
- [ ] `recognize_text` retourne une liste de dictionnaires avec clés `text` et `confidence`
- [ ] La confiance est un float entre 0 et 1
- [ ] Sur un crop contenant du texte lisible, au moins un résultat non vide est retourné
- [ ] `compare_engines` retourne des résultats pour chaque moteur demandé
- [ ] Validation des entrées : `ValueError` sur image None ou vide
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/005-ocr-models-comparison` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/005-ocr-models-comparison` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS3] #005 RED: tests comparaison modèles OCR`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS3] #005 GREEN: comparaison OCR PaddleOCR/TrOCR/Tesseract`.
- [ ] **Pull Request ouverte** vers `main` : `[WS3] #005 — Comparaison modèles OCR`.
