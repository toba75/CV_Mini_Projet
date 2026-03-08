# Tâche — Implémenter la correction de perspective automatique par homographie

Statut : TODO
Ordre : 009
Workstream : WS1
Milestone : M2

## Contexte
Lorsqu'une photo d'étagère est prise sous un angle non frontal, les tranches de livres apparaissent déformées, ce qui dégrade la segmentation et l'OCR. La correction de perspective via une transformation homographique permet de redresser l'image pour obtenir une vue frontale de l'étagère.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS1 — point 1)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 2 — Prétraitement, correction de perspective)
- Code : `src/preprocess.py`

Dépendances :
- Tâche 002 — Prétraitement CLAHE (doit être DONE)
- Tâche 003 — Segmentation naïve Hough (doit être DONE)

## Objectif
Ajouter dans `src/preprocess.py` une fonction de correction de perspective automatique basée sur la détection des contours de l'étagère et l'application d'une homographie OpenCV pour redresser l'image.

## Règles attendues
- Conventions image : entrée BGR, sortie BGR.
- Pas de modification en place de l'image d'entrée.
- Validation explicite des entrées + `raise ValueError`.
- Utiliser `cv2.findContours` ou `cv2.approxPolyDP` pour détecter les contours de l'étagère.
- Utiliser `cv2.getPerspectiveTransform` ou `cv2.findHomography` + `cv2.warpPerspective`.
- Si aucun contour d'étagère n'est détecté, retourner l'image originale sans erreur (comportement dégradé explicite).

## Évolutions proposées
- Fonction `detect_shelf_contour(image: np.ndarray) -> np.ndarray | None` : détecte le contour principal de l'étagère (quadrilatère). Retourne les 4 coins ordonnés ou `None` si non détecté.
- Fonction `correct_perspective(image: np.ndarray, corners: np.ndarray | None = None) -> np.ndarray` : applique la transformation homographique pour redresser l'image. Si `corners` est `None`, appelle `detect_shelf_contour`. Si aucun contour trouvé, retourne l'image telle quelle.
- Intégration dans le flux de prétraitement existant (appel optionnel avant ou après CLAHE).

## Critères d'acceptation
- [ ] `detect_shelf_contour` retourne un array de 4 points ordonnés (top-left, top-right, bottom-right, bottom-left) ou `None`
- [ ] `correct_perspective` redresse une image déformée (vérifiable sur image synthétique avec transformation connue)
- [ ] `correct_perspective` retourne l'image originale si aucun contour n'est détecté (pas d'exception)
- [ ] La sortie a des dimensions raisonnables (pas d'image dégénérée 0×0)
- [ ] Validation des entrées : `ValueError` sur image None ou vide
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords (image sans contour, image déjà frontale)
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/009-perspective-correction` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/009-perspective-correction` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS1] #009 RED: tests correction de perspective homographie`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS1] #009 GREEN: correction de perspective automatique implémentée`.
- [ ] **Pull Request ouverte** vers `main` : `[WS1] #009 — Correction de perspective`.
