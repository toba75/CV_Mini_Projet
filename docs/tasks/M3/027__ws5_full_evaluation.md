# Tâche — Évaluation complète sur le dataset annoté

Statut : DONE
Ordre : 027
Workstream : WS5
Milestone : M3

## Contexte
Les métriques d'évaluation ont été implémentées en M2 (tâche 018). Il faut maintenant lancer l'évaluation complète du pipeline sur l'ensemble du dataset annoté et produire le tableau de résultats attendu pour la soutenance.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS5)
- Spécification : `docs/specifications/specifications.md` (§6 — Métriques d'évaluation)
- Code : `src/eval_utils.py`, `src/pipeline.py`

Dépendances :
- Tâche 018 — Métriques d'évaluation (doit être DONE)
- Tâche 017 — Expansion dataset (doit être DONE)
- Tâche 019 — Cas limites segmentation (doit être DONE)

## Objectif
Exécuter le pipeline complet sur tout le dataset annoté, calculer les 4 métriques cibles (taux de détection, CER, taux d'identification, temps moyen), et produire un tableau de résultats formaté.

## Règles attendues
- Évaluation sur l'intégralité du dataset annoté (20-30 images)
- Les 4 métriques de la spec doivent être calculées
- Les résultats doivent être reproductibles (script unique)
- Comparer aux cibles définies dans la spécification

## Évolutions proposées
- Créer un script `eval.py` (ou étendre `eval_utils.py`) qui exécute le pipeline sur tout le dataset
- Calculer pour chaque image : taux de détection, CER, taux d'identification, temps
- Agréger les résultats : moyennes, médianes, écart-types
- Produire le tableau récapitulatif au format markdown et CSV :
  | Métrique | Résultat | Cible |
- Identifier les images avec les pires performances (entrée pour tâche 028)

## Critères d'acceptation
- [x] Évaluation exécutée sur l'intégralité du dataset annoté
- [x] Taux de détection calculé (cible ≥ 80%)
- [x] CER moyen calculé (cible ≤ 20%)
- [x] Taux d'identification calculé (cible ≥ 60%)
- [x] Temps moyen par image calculé (cible < 30s)
- [x] Tableau récapitulatif généré (markdown + CSV)
- [x] Script reproductible en une commande
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/027-full-evaluation` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/027-full-evaluation` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-5] #027 RED: tests évaluation complète`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [x] **Commit GREEN** : `[WS-5] #027 GREEN: évaluation complète dataset`.
- [x] **Pull Request ouverte** vers `main` : `[WS-5] #027 — Évaluation complète sur le dataset annoté`.
