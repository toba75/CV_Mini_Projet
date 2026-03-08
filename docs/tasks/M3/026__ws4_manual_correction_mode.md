# Tâche — Mode correction manuelle dans Streamlit

Statut : DONE
Ordre : 026
Workstream : WS4
Milestone : M3

## Contexte
L'OCR n'est pas parfait. L'utilisateur doit pouvoir corriger manuellement les titres mal reconnus directement dans l'interface Streamlit avant l'export, améliorant ainsi la qualité de l'inventaire final.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS4)
- Spécification : `docs/specifications/specifications.md` (§7 — Démonstration)
- Code : `src/app.py`

Dépendances :
- Tâche 025 — Interface Streamlit complète (doit être DONE)

## Objectif
Ajouter un mode de correction manuelle dans l'interface Streamlit permettant à l'utilisateur d'éditer les titres, auteurs et autres champs mal reconnus par l'OCR.

## Règles attendues
- Les corrections doivent être prises en compte dans l'export CSV/JSON
- L'interface doit clairement distinguer les valeurs OCR originales des corrections manuelles
- Les corrections ne doivent pas nécessiter de relancer le pipeline

## Évolutions proposées
- Ajouter des champs éditables dans le tableau de l'onglet Inventaire
- Permettre l'édition inline du titre, auteur, et ISBN
- Marquer visuellement les champs modifiés manuellement
- Mettre à jour l'export CSV/JSON avec les valeurs corrigées
- Optionnel : bouton « Relancer l'enrichissement API » sur un titre corrigé

## Critères d'acceptation
- [x] Champs titre et auteur éditables dans le tableau de résultats
- [x] Les corrections sont reflétées dans l'export CSV/JSON
- [x] Les champs modifiés sont visuellement distingués
- [x] Les corrections persistent pendant la session (pas de perte au changement d'onglet)
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/026-manual-correction` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/026-manual-correction` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-4] #026 RED: tests mode correction manuelle`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-4] #026 GREEN: mode correction manuelle`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-4] #026 — Mode correction manuelle dans Streamlit`.
