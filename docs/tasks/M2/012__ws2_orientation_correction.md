# Tâche — Implémenter la correction d'orientation automatique du texte

Statut : TODO
Ordre : 012
Workstream : WS2
Milestone : M2

## Contexte
Le texte sur les tranches de livres est souvent orienté verticalement ou légèrement incliné. Pour que l'OCR fonctionne correctement, il faut estimer l'angle dominant des bounding boxes de texte détectées et appliquer une rotation pour redresser le texte à l'horizontale avant de le passer à la reconnaissance.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS2 — point 2)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 4 — Correction d'orientation, §8 Risques — texte vertical)
- Code : `src/detect_text.py`

Dépendances :
- Tâche 011 — Intégration détection texte pipeline (doit être DONE)

## Objectif
Implémenter dans `src/detect_text.py` une correction d'orientation automatique : estimer l'angle dominant des zones de texte détectées, puis appliquer une rotation pour redresser le texte avant l'OCR.

## Règles attendues
- Conventions image : entrée BGR, sortie BGR.
- Pas de modification en place.
- Validation explicite des entrées + `raise ValueError`.
- L'estimation d'angle doit utiliser les bounding boxes orientées (angle médian ou dominant).
- La rotation doit préserver le contenu (utiliser `cv2.getRotationMatrix2D` + `cv2.warpAffine` avec bordures adaptées).
- Si l'angle estimé est proche de 0° (< seuil), ne pas appliquer de rotation inutile.

## Évolutions proposées
- Fonction `estimate_text_angle(bboxes: list[dict]) -> float` : estime l'angle dominant du texte à partir des bounding boxes détectées. Retourne l'angle en degrés.
- Fonction `rotate_image(image: np.ndarray, angle: float) -> np.ndarray` : applique une rotation de l'angle donné autour du centre de l'image. Ajuste les dimensions pour ne pas couper le contenu.
- Fonction `correct_orientation(crop: np.ndarray, bboxes: list[dict], angle_threshold: float = 2.0) -> np.ndarray` : orchestre estimation d'angle → rotation si nécessaire. Si l'angle < seuil, retourne le crop tel quel.
- Intégration dans le flux : segmentation → détection texte → correction orientation → OCR.

## Critères d'acceptation
- [ ] `estimate_text_angle` retourne un angle cohérent pour du texte vertical (~90° ou ~-90°)
- [ ] `estimate_text_angle` retourne ~0° pour du texte horizontal
- [ ] `estimate_text_angle` gère une liste vide de bboxes (retourne 0.0)
- [ ] `rotate_image` redresse correctement une image avec un angle connu (vérifiable sur image synthétique)
- [ ] `rotate_image` ne coupe pas le contenu de l'image (dimensions ajustées)
- [ ] `correct_orientation` ne fait rien si l'angle est inférieur au seuil
- [ ] `correct_orientation` redresse le texte vertical pour le rendre horizontal
- [ ] Validation des entrées : `ValueError` sur image None ou vide
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords (pas de bboxes, texte déjà horizontal, texte à 90°)
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/012-orientation-correction` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/012-orientation-correction` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS2] #012 RED: tests correction orientation texte`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS2] #012 GREEN: correction d'orientation automatique implémentée`.
- [ ] **Pull Request ouverte** vers `main` : `[WS2] #012 — Correction orientation`.
