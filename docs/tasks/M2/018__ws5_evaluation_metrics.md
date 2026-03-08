# Tâche — Implémenter le script de calcul des métriques d'évaluation

Statut : DONE
Ordre : 018
Workstream : WS5
Milestone : M2

## Contexte
Pour mesurer la performance du pipeline, il faut calculer les métriques définies dans la spécification : taux de détection des tranches, CER moyen sur le texte brut, et taux d'identification des livres via l'API. Le module `src/eval_utils.py` existant doit être étendu pour couvrir ces trois métriques.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS5 — point 2)
- Spécification : `docs/specifications/specifications.md` (§6 Métriques d'évaluation — taux détection, CER, taux identification)
- Code : `src/eval_utils.py`

Dépendances :
- Tâche 016 — Structure JSON sortie pipeline (doit être DONE)
- Tâche 017 — Extension dataset (doit être DONE)

## Objectif
Étendre `src/eval_utils.py` pour calculer les trois métriques principales du pipeline : taux de détection des tranches, CER moyen, et taux d'identification. Implémenter un script d'évaluation qui compare les sorties du pipeline avec le ground truth CSV.

## Règles attendues
- Le CER doit utiliser la distance d'édition de Levenshtein (bibliothèque `editdistance`).
- Les métriques doivent être calculées par image et en moyenne sur tout le dataset.
- Les résultats doivent être exportables en JSON et affichables en console.
- Pas d'appels réseau dans le calcul des métriques (utiliser les sorties JSON pré-calculées).
- Les fonctions doivent être testables avec des données synthétiques.

## Évolutions proposées
- Fonction `compute_detection_rate(predicted_count: int, ground_truth_count: int) -> float` : calcule le taux de détection pour une image. Retourne un ratio entre 0.0 et 1.0.
- Fonction `compute_cer(predicted_text: str, ground_truth_text: str) -> float` : calcule le Character Error Rate entre le texte prédit et le ground truth. Retourne un ratio >= 0.0.
- Fonction `compute_identification_rate(predicted_titles: list[str], ground_truth_titles: list[str], threshold: float = 60.0) -> float` : calcule le taux d'identification via fuzzy matching. Retourne un ratio entre 0.0 et 1.0.
- Fonction `evaluate_image(pipeline_result: dict, ground_truth: dict) -> dict` : calcule les trois métriques pour une image. Retourne `{"detection_rate": float, "cer": float, "identification_rate": float}`.
- Fonction `evaluate_dataset(results_dir: str | Path, ground_truth_dir: str | Path) -> dict` : évalue tout le dataset et retourne les métriques moyennes + par image.
- Script CLI : `python -m src.eval_utils --results outputs/ --ground-truth data/ground_truth/`.

## Critères d'acceptation
- [x] `compute_detection_rate` retourne 1.0 quand le nombre prédit == ground truth
- [x] `compute_detection_rate` retourne un ratio < 1.0 quand il y a des tranches manquées
- [x] `compute_detection_rate` gère le cas ground_truth_count == 0 (retourne 0.0)
- [x] `compute_cer` retourne 0.0 pour des textes identiques
- [x] `compute_cer` retourne un CER > 0 pour des textes différents
- [x] `compute_cer` utilise la distance de Levenshtein (via `editdistance`)
- [x] `compute_identification_rate` retourne 1.0 quand tous les titres sont correctement identifiés
- [x] `compute_identification_rate` gère les listes vides
- [x] `evaluate_image` retourne un dict avec les trois métriques
- [x] `evaluate_dataset` calcule les moyennes sur tout le dataset
- [x] Tests couvrent les scénarios nominaux + erreurs + bords (texte vide, aucune tranche, dataset vide)
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/018-evaluation-metrics` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/018-evaluation-metrics` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS5] #018 RED: tests métriques évaluation`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [x] **Commit GREEN** : `[WS5] #018 GREEN: métriques d'évaluation implémentées`.
- [x] **Pull Request ouverte** vers `main` : `[WS5] #018 — Métriques évaluation`.
