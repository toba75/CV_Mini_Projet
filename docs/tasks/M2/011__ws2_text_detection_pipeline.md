# Tâche — Intégrer la détection de texte dans le pipeline

Statut : TODO
Ordre : 011
Workstream : WS2
Milestone : M2

## Contexte
En M1, la détection de texte (CRAFT/PaddleOCR) a été testée de manière isolée sur des images de tranches. Il faut maintenant l'intégrer dans le pipeline automatisé pour que chaque crop issu de la segmentation passe automatiquement par la détection de zones de texte, avec gestion des cas multi-lignes (titre sur plusieurs lignes d'une même tranche).

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS2 — points 1 et 3)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 4 — Détection des zones de texte)
- Code : `src/detect_text.py`, `src/pipeline.py`

Dépendances :
- Tâche 004 — Test détection de texte (doit être DONE)
- Tâche 010 — Segmentation affinée (doit être DONE)

## Objectif
Adapter `src/detect_text.py` pour fonctionner en mode pipeline : recevoir un crop de tranche, retourner les bounding boxes des zones de texte détectées de manière structurée. Gérer les cas multi-lignes en regroupant les bounding boxes d'une même tranche.

## Règles attendues
- Conventions image : entrée BGR (crops issus de la segmentation).
- Les bounding boxes retournées doivent être dans un format normalisé : `list[dict]` avec clés `bbox`, `confidence`, `text` (si disponible).
- Pas de modification en place des crops.
- Validation explicite des entrées + `raise ValueError`.
- Gérer le cas où aucune zone de texte n'est détectée (retourner une liste vide, pas d'exception).

## Évolutions proposées
- Fonction `detect_text_regions(crop: np.ndarray, engine: str = "paddleocr") -> list[dict]` : détecte les zones de texte sur un crop de tranche. Retourne une liste de `{"bbox": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], "confidence": float, "text": str | None}`.
- Fonction `group_text_lines(regions: list[dict], line_threshold: float = 0.5) -> list[list[dict]]` : regroupe les régions de texte par ligne logique (proximité verticale). Utile pour les tranches avec titre multi-lignes.
- Fonction `detect_text_on_spines(crops: list[np.ndarray], engine: str = "paddleocr") -> list[list[dict]]` : applique la détection sur une liste de crops (batch). Retourne une liste de résultats par crop.
- Intégration dans `pipeline.py` : chaîner segmentation → détection de texte.

## Critères d'acceptation
- [ ] `detect_text_regions` retourne une liste de dicts avec les clés `bbox`, `confidence`, `text`
- [ ] `detect_text_regions` retourne une liste vide si aucun texte détecté (pas d'exception)
- [ ] `group_text_lines` regroupe correctement les régions proches verticalement
- [ ] `group_text_lines` garde les régions isolées dans leur propre groupe
- [ ] `detect_text_on_spines` traite correctement une liste de crops et retourne un résultat par crop
- [ ] Validation des entrées : `ValueError` sur crop None ou vide
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords (crop sans texte, crop avec texte multi-lignes)
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/011-text-detection-pipeline` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/011-text-detection-pipeline` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS2] #011 RED: tests intégration détection texte pipeline`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS2] #011 GREEN: détection de texte intégrée au pipeline`.
- [ ] **Pull Request ouverte** vers `main` : `[WS2] #011 — Détection texte pipeline`.
