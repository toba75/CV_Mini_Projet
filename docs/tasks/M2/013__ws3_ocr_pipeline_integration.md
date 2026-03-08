# Tâche — Intégrer le modèle OCR choisi dans le pipeline

Statut : DONE
Ordre : 013
Workstream : WS3
Milestone : M2

## Contexte
En M1, trois moteurs OCR ont été comparés qualitativement (PaddleOCR, TrOCR, Tesseract). Il faut maintenant intégrer le modèle retenu dans le pipeline automatisé pour que chaque zone de texte détectée et orientée soit transcrite automatiquement. Le module `src/ocr.py` doit exposer une interface unifiée quel que soit le moteur utilisé.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS3 — point 1)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 5 — Reconnaissance de caractères OCR)
- Code : `src/ocr.py`, `src/pipeline.py`

Dépendances :
- Tâche 005 — Comparaison modèles OCR (doit être DONE)
- Tâche 012 — Correction d'orientation (doit être DONE)

## Objectif
Adapter `src/ocr.py` pour fonctionner en mode pipeline : recevoir des crops orientés (texte redressé), appliquer la reconnaissance OCR, et retourner le texte brut avec un score de confiance. Exposer une interface unifiée supportant plusieurs moteurs.

## Règles attendues
- Conventions image : entrée BGR (crops orientés).
- Interface unifiée : même signature de fonction quel que soit le moteur OCR.
- Pas de modification en place des crops.
- Validation explicite des entrées + `raise ValueError`.
- Gérer le cas où l'OCR ne produit aucun résultat (retourner une chaîne vide avec confiance 0.0).
- Les modèles lourds doivent être chargés une seule fois (lazy loading ou singleton).

## Évolutions proposées
- Fonction `recognize_text(crop: np.ndarray, engine: str = "paddleocr") -> dict` : applique l'OCR sur un crop et retourne `{"text": str, "confidence": float, "engine": str}`.
- Fonction `recognize_batch(crops: list[np.ndarray], engine: str = "paddleocr") -> list[dict]` : applique l'OCR sur une liste de crops. Retourne un résultat par crop.
- Support des moteurs : `"paddleocr"`, `"trocr"`, `"tesseract"`. Lever `ValueError` pour un moteur inconnu.
- Mécanisme de lazy loading pour les modèles (éviter de recharger à chaque appel).
- Intégration dans `pipeline.py` : chaîner détection texte → orientation → OCR.

## Critères d'acceptation
- [x] `recognize_text` retourne un dict avec les clés `text`, `confidence`, `engine`
- [x] `recognize_text` retourne `{"text": "", "confidence": 0.0, ...}` si aucun texte reconnu
- [x] `recognize_text` supporte au moins deux moteurs OCR (ex : `paddleocr` et `tesseract`)
- [x] `recognize_text` lève `ValueError` pour un moteur inconnu
- [x] `recognize_batch` traite correctement une liste de crops et retourne un résultat par crop
- [x] Les modèles ne sont pas rechargés entre chaque appel (lazy loading vérifié)
- [x] Validation des entrées : `ValueError` sur crop None ou vide
- [x] Tests couvrent les scénarios nominaux + erreurs + bords (crop vide, moteur inconnu)
- [x] Tests utilisent le mocking pour les moteurs OCR (pas de dépendance aux modèles dans les tests unitaires)
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/013-ocr-pipeline-integration` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/013-ocr-pipeline-integration` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS3] #013 RED: tests intégration OCR pipeline`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS3] #013 GREEN: OCR intégré au pipeline`.
- [ ] **Pull Request ouverte** vers `main` : `[WS3] #013 — Intégration OCR pipeline`.
