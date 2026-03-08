# Tâche — Comparaison quantitative des modèles OCR

Statut : DONE
Ordre : 023
Workstream : WS3
Milestone : M3

## Contexte
En M1, une comparaison qualitative des modèles OCR a été réalisée (tâche 005). Il faut maintenant produire une comparaison quantitative rigoureuse sur le dataset annoté, en mesurant le CER par modèle, pour justifier le choix du modèle principal lors de la soutenance.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS3)
- Spécification : `docs/specifications/specifications.md` (§5 — OCR, §6 — Métriques)
- Code : `src/ocr.py`, `src/eval_utils.py`

Dépendances :
- Tâche 013 — Intégration OCR pipeline (doit être DONE)
- Tâche 018 — Métriques d'évaluation (doit être DONE)

## Objectif
Évaluer quantitativement les modèles OCR (PaddleOCR, TrOCR, Tesseract) sur le dataset annoté et produire un tableau comparatif de CER par modèle.

## Règles attendues
- Utiliser le même dataset et ground truth pour tous les modèles
- Le CER doit être calculé avec la distance de Levenshtein (conforme au cours)
- Les résultats doivent être reproductibles (scripts, pas de calcul manuel)

## Évolutions proposées
- Créer un script/fonction de benchmark qui exécute chaque modèle OCR sur le dataset
- Calculer le CER par modèle, par image, et global
- Produire un tableau récapitulatif (modèle × métrique)
- Mesurer aussi le temps d'inférence par modèle
- Sauvegarder les résultats dans un fichier (CSV ou JSON) pour référence

## Critères d'acceptation
- [x] Benchmark exécuté sur au moins 3 modèles OCR (PaddleOCR, TrOCR, Tesseract)
- [x] CER calculé par modèle sur le dataset annoté complet
- [x] Temps d'inférence mesuré par modèle
- [x] Tableau récapitulatif généré (format CSV ou JSON)
- [x] Résultats reproductibles via un script unique
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/023-ocr-comparison` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/023-ocr-comparison` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-3] #023 RED: tests comparaison quantitative OCR`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-3] #023 GREEN: comparaison quantitative OCR`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-3] #023 — Comparaison quantitative des modèles OCR`.
