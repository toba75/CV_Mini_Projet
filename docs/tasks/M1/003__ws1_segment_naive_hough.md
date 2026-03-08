# Tâche — Implémenter la segmentation naïve par Canny + HoughLinesP

Statut : DONE
Ordre : 003
Workstream : WS1
Milestone : M1

## Contexte
La segmentation des tranches de livres est l'étape qui isole chaque livre individuellement sur la photo d'étagère. En M1, une approche naïve basée sur la détection de lignes verticales (Canny + HoughLinesP) est suffisante pour obtenir un premier résultat end-to-end.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M1 > WS1 — point 4)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 3 — Segmentation des tranches)
- Code : `src/segment.py`

Dépendances :
- Tâche 002 — Prétraitement CLAHE (doit être DONE)

## Objectif
Écrire `src/segment.py` avec une segmentation naïve des tranches de livres par détection de lignes verticales (Canny + transformée de Hough probabiliste), puis découpage de l'image en bandes verticales.

## Règles attendues
- Conventions image : entrée en BGR, sorties (crops) en BGR.
- Pas de modification en place.
- Validation explicite des entrées + `raise ValueError`.
- Les lignes détectées doivent être filtrées : garder uniquement les lignes quasi-verticales (angle proche de 90°).

## Évolutions proposées
- Fonction `detect_vertical_lines(image: np.ndarray, ...) -> list[tuple]` : convertit en niveaux de gris, applique Canny, puis HoughLinesP. Filtre les lignes pour ne garder que les quasi-verticales. Retourne les coordonnées des lignes triées par position x.
- Fonction `split_spines(image: np.ndarray, lines: list[tuple]) -> list[np.ndarray]` : découpe l'image en bandes verticales entre les lignes détectées. Retourne la liste des crops (tranches individuelles).
- Fonction `segment(image: np.ndarray) -> list[np.ndarray]` : orchestre detect_vertical_lines → split_spines et retourne les crops.

## Critères d'acceptation
- [x] `detect_vertical_lines` retourne une liste de lignes triées par position x croissante
- [x] Les lignes non verticales (angle > seuil) sont correctement filtrées
- [x] `split_spines` retourne des crops non vides dont la largeur et hauteur sont > 0
- [x] `split_spines` couvre toute la largeur de l'image (pas de zone manquante entre les bords et les premières/dernières lignes)
- [x] `segment` retourne au moins 1 crop même si aucune ligne n'est détectée (image entière comme fallback)
- [x] Validation des entrées : `ValueError` sur image None ou vide
- [x] Tests couvrent les scénarios nominaux + erreurs + bords (image sans lignes, image avec une seule ligne)
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/003-segment-naive-hough` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/003-segment-naive-hough` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS1] #003 RED: tests segmentation naïve Hough`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS1] #003 GREEN: segmentation naïve Canny+Hough implémentée`.
- [ ] **Pull Request ouverte** vers `main` : `[WS1] #003 — Segmentation naïve Hough`.
