# Tâche — Affiner la segmentation des tranches et produire des crops individuels

Statut : TODO
Ordre : 010
Workstream : WS1
Milestone : M2

## Contexte
La segmentation naïve de M1 (Canny + HoughLinesP) produit des résultats bruts qui contiennent des lignes parasites (trop courtes, trop inclinées) et ne gère pas les cas où deux livres adjacents n'ont pas de séparation visible. L'affinage est nécessaire pour obtenir des crops propres et exploitables par les étapes suivantes du pipeline.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS1 — points 2 et 3)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 3 — Segmentation des tranches)
- Code : `src/segment.py`

Dépendances :
- Tâche 003 — Segmentation naïve Hough (doit être DONE)
- Tâche 009 — Correction de perspective (doit être DONE)

## Objectif
Améliorer `src/segment.py` pour filtrer les lignes parasites, gérer les cas sans séparation visible entre livres (fallback sur la largeur moyenne), et produire des crops individuels propres pour chaque tranche détectée.

## Règles attendues
- Conventions image : entrée BGR, sorties (crops) en BGR.
- Pas de modification en place.
- Validation explicite des entrées + `raise ValueError`.
- Les crops doivent avoir une largeur minimale configurable (éviter les micro-crops parasites).
- Le fallback sur largeur moyenne doit être activé quand l'écart entre deux lignes dépasse un seuil (ex : 2× la largeur médiane).

## Évolutions proposées
- Fonction `filter_lines(lines: list[tuple], image_height: int, min_length_ratio: float = 0.3, max_angle_deg: float = 15.0) -> list[tuple]` : supprime les lignes trop courtes (< ratio de la hauteur image) et trop inclinées (> angle max par rapport à la verticale).
- Fonction `split_wide_gaps(lines: list[tuple], image_width: int, median_width: float) -> list[tuple]` : si un gap entre deux lignes consécutives dépasse 2× la largeur médiane, insère des lignes virtuelles pour subdiviser.
- Fonction `crop_spines(image: np.ndarray, lines: list[tuple], min_width: int = 20) -> list[np.ndarray]` : produit des crops individuels propres à partir des lignes filtrées. Ignore les crops trop étroits (< min_width).
- Mise à jour de la fonction `segment` existante pour intégrer le filtrage et le fallback.

## Critères d'acceptation
- [ ] `filter_lines` supprime correctement les lignes trop courtes et trop inclinées
- [ ] `filter_lines` conserve les lignes quasi-verticales de longueur suffisante
- [ ] `split_wide_gaps` insère des lignes virtuelles quand le gap dépasse le seuil
- [ ] `split_wide_gaps` ne modifie pas les gaps normaux
- [ ] `crop_spines` retourne des crops de largeur >= `min_width`
- [ ] `crop_spines` retourne au moins 1 crop (image entière si aucune ligne)
- [ ] Les crops couvrent toute la largeur de l'image (pas de zone manquante)
- [ ] `segment` intègre le filtrage et le fallback de manière transparente
- [ ] Validation des entrées : `ValueError` sur image None ou vide
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords (aucune ligne, une seule ligne, gap très large)
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/010-refined-segmentation` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/010-refined-segmentation` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS1] #010 RED: tests segmentation affinée`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS1] #010 GREEN: segmentation affinée avec filtrage et crops`.
- [ ] **Pull Request ouverte** vers `main` : `[WS1] #010 — Segmentation affinée`.
