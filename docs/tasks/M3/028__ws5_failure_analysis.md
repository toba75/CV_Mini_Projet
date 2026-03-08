# Tâche — Analyse des cas d'échec pour la soutenance

Statut : DONE
Ordre : 028
Workstream : WS5
Milestone : M3

## Contexte
Pour la soutenance, il est important de montrer une compréhension des limites du système. Cette tâche consiste à identifier et analyser les 3 à 5 cas d'échec les plus fréquents du pipeline, et à préparer une discussion argumentée.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS5)
- Spécification : `docs/specifications/specifications.md` (§8 — Risques)
- Code : `src/eval_utils.py`, `src/pipeline.py`

Dépendances :
- Tâche 027 — Évaluation complète dataset (doit être DONE)
- Tâche 022 — Test cas difficiles (doit être DONE)

## Objectif
Identifier les 3 à 5 types d'échec les plus fréquents du pipeline, les documenter avec des exemples visuels, et préparer des éléments de discussion pour la soutenance (causes, pistes d'amélioration).

## Règles attendues
- Analyse basée sur les résultats réels de l'évaluation (tâche 027)
- Chaque cas d'échec doit être illustré par un exemple concret (image + sortie pipeline)
- Proposer des pistes d'amélioration réalistes pour chaque type d'échec

## Évolutions proposées
- Analyser les résultats de l'évaluation pour identifier les patterns d'échec
- Catégoriser les échecs : segmentation, détection, OCR, enrichissement
- Pour chaque catégorie, sélectionner l'exemple le plus représentatif
- Créer un document de synthèse avec :
  - Type d'échec + fréquence
  - Exemple visuel (image source + sortie pipeline)
  - Cause probable
  - Piste d'amélioration
- Ce document servira de support pour les slides de soutenance (M4)

## Critères d'acceptation
- [x] 3 à 5 types d'échec identifiés et documentés
- [x] Chaque type d'échec illustré par un exemple concret
- [x] Causes probables analysées pour chaque type
- [x] Pistes d'amélioration proposées pour chaque type
- [x] Document de synthèse rédigé (markdown)
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/028-failure-analysis` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/028-failure-analysis` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-5] #028 RED: tests analyse cas d'échec`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-5] #028 GREEN: analyse cas d'échec`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-5] #028 — Analyse des cas d'échec pour la soutenance`.
