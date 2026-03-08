# Tâche — Gestion des cas limites de segmentation

Statut : DONE
Ordre : 019
Workstream : WS1
Milestone : M3

## Contexte
Le pipeline de segmentation (M2) fonctionne sur les cas nominaux, mais échoue sur les cas limites : étagères partiellement vides, objets non-livres (bibelots, cadres), et livres très fins (< 1 cm). Cette tâche ajoute la robustesse nécessaire pour un usage réel.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS1)
- Spécification : `docs/specifications/specifications.md` (§3 — Segmentation, §8 — Risques)
- Code : `src/segment.py`

Dépendances :
- Tâche 010 — Affinage segmentation (doit être DONE)
- Tâche 009 — Correction de perspective (doit être DONE)

## Objectif
Rendre la segmentation robuste face aux cas limites : étagères partiellement vides, présence d'objets non-livres, et livres très fins difficiles à isoler.

## Règles attendues
- Ne pas casser la segmentation des cas nominaux (tests de régression)
- Les objets non-livres doivent être filtrés ou signalés (flag `is_book: false`)
- Les tranches très fines doivent être détectées si la résolution le permet, sinon signalées comme non lisibles

## Évolutions proposées
- Ajouter un filtre de largeur minimale/maximale pour les tranches détectées
- Implémenter une heuristique de détection d'espaces vides (zones sans texture)
- Ajouter un classificateur simple (ratio aspect, variance de texture) pour distinguer livres/non-livres
- Fusionner les tranches trop fines adjacentes si elles semblent appartenir au même livre

## Critères d'acceptation
- [x] Les étagères avec des espaces vides sont correctement segmentées (pas de faux livres dans les zones vides)
- [x] Les objets non-livres sont identifiés et exclus ou signalés
- [x] Les livres fins (< 1 cm apparent) sont détectés ou signalés comme non lisibles
- [x] Tests de régression : les cas nominaux (M2) restent GREEN
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/019-edge-cases-segmentation` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/019-edge-cases-segmentation` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-1] #019 RED: tests cas limites segmentation`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-1] #019 GREEN: gestion cas limites segmentation`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-1] #019 — Gestion des cas limites de segmentation`.
