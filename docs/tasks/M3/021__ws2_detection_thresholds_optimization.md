# Tâche — Optimisation des seuils de détection de texte

Statut : DONE
Ordre : 021
Workstream : WS2
Milestone : M3

## Contexte
La détection de texte (M2) produit des faux positifs sur les éléments non textuels : logos d'éditeur, décorations, motifs graphiques sur les tranches. Il faut affiner les seuils de confiance et les filtres pour améliorer la précision sans perdre en rappel.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS2)
- Spécification : `docs/specifications/specifications.md` (§3 — Détection zones texte)
- Code : `src/detect_text.py`

Dépendances :
- Tâche 011 — Intégration détection texte pipeline (doit être DONE)
- Tâche 018 — Métriques d'évaluation (doit être DONE)

## Objectif
Réduire les faux positifs de la détection de texte en optimisant les seuils de confiance et en ajoutant des filtres sur les bounding boxes, tout en maintenant un rappel acceptable.

## Règles attendues
- Les seuils doivent être configurables (paramètres, pas de valeurs hardcodées)
- Mesurer l'impact sur le dataset annoté avant/après optimisation
- Documenter les seuils choisis et leur justification

## Évolutions proposées
- Ajouter un paramètre `confidence_threshold` configurable dans `detect_text.py`
- Filtrer les bounding boxes trop petites (bruit) ou trop grandes (faux positifs sur fond)
- Filtrer les détections avec un ratio aspect aberrant (trop carré pour du texte de tranche)
- Évaluer sur le dataset annoté et choisir le meilleur compromis précision/rappel

## Critères d'acceptation
- [x] Seuil de confiance configurable via paramètre
- [x] Filtres de taille et ratio aspect implémentés
- [x] Réduction mesurable des faux positifs sur le dataset annoté
- [x] Le rappel reste acceptable (pas de perte > 5% sur les vrais positifs)
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/021-detection-thresholds` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `milestone/M3` utilisée (workflow milestone).
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-2] #021 RED: tests optimisation seuils détection`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [x] **Commit GREEN** : `[WS-2] #021 GREEN: optimisation seuils détection`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-2] #021 — Optimisation des seuils de détection de texte`.
