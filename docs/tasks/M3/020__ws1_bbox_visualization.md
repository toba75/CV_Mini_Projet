# Tâche — Visualisation des bounding boxes sur l'image originale

Statut : DONE
Ordre : 020
Workstream : WS1
Milestone : M3

## Contexte
Pour le débogage, la démo Streamlit et la soutenance, il est nécessaire de pouvoir superposer les bounding boxes des tranches segmentées sur l'image originale. Cette visualisation est aussi utile pour l'évaluation qualitative du pipeline.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS1)
- Spécification : `docs/specifications/specifications.md` (§7 — Démonstration)
- Code : `src/segment.py`, `src/pipeline.py`

Dépendances :
- Tâche 010 — Affinage segmentation (doit être DONE)

## Objectif
Implémenter une fonction de visualisation qui dessine les bounding boxes colorées des tranches segmentées sur l'image originale, avec légendes optionnelles (numéro de tranche, score de confiance).

## Règles attendues
- La visualisation ne doit pas modifier l'image originale (travailler sur une copie)
- Couleurs distinctes pour chaque tranche (palette cyclique)
- Compatible avec l'affichage Streamlit (retour d'un array numpy ou d'une image PIL)

## Évolutions proposées
- Créer une fonction `draw_spine_boxes(image, spines, show_labels=True) -> np.ndarray`
- Dessiner les rectangles avec des couleurs distinctes par tranche
- Afficher optionnellement le numéro de tranche et le score de confiance
- Supporter l'affichage des zones de texte détectées en superposition

## Critères d'acceptation
- [x] Fonction `draw_spine_boxes` implémentée et testée
- [x] Chaque tranche a une couleur distincte visible
- [x] Les labels (numéro, confiance) sont lisibles sur l'image
- [x] L'image originale n'est pas modifiée (copie)
- [x] Fonctionne avec les sorties du pipeline existant
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/020-bbox-visualization` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/020-bbox-visualization` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-1] #020 RED: tests visualisation bounding boxes`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [x] **Commit GREEN** : `[WS-1] #020 GREEN: visualisation bounding boxes`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-1] #020 — Visualisation des bounding boxes sur l'image originale`.
