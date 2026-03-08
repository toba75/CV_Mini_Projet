# Revue TDD — 003 Segmentation naïve Hough — v2

**Branche** : `task/003-segment-naive-hough`
**Commit reviewé** : `6fb5247` (FIX: constantes nommées et test no-modify)
**Date** : 2026-03-08
**Itération** : v2 (après corrections W-1, W-2 de la revue v1)

---

## 1. Tests

| Suite | Total | Passed | Failed | Skipped |
|-------|-------|--------|--------|---------|
| tests/ | 85 | 85 | 0 | 0 |

Temps d'exécution : 0.34 s

## 2. Linter

```
ruff check src/ tests/ → All checks passed!
```

## 3. Vérification des warnings v1

### W-1 — Magic numbers (RÉSOLU)

Les valeurs magiques `5` et `0.02` dans `split_spines` sont maintenant extraites en constantes nommées au niveau du module :

- `MIN_GAP_PX: int = 5` (ligne 17)
- `MIN_GAP_RATIO: float = 0.02` (ligne 19)

Les valeurs par défaut des paramètres de fonction (`canny_low=50`, `canny_high=150`, etc.) sont correctement documentées dans les docstrings et exposées en tant que paramètres nommés de l'API — aucun problème.

### W-2 — Test no-modify pour detect_vertical_lines (RÉSOLU)

Le test `TestDetectVerticalLines::test_does_not_modify_input` (ligne 77 de `test_segment.py`) vérifie que l'image d'entrée n'est pas modifiée en place. Il utilise une image aléatoire, en fait une copie, appelle la fonction, puis compare avec `np.testing.assert_array_equal`.

## 4. Scans GREP

| Pattern | Résultat |
|---------|----------|
| `print()` dans src/segment.py | Aucun |
| `print()` dans tests/test_segment.py | Aucun |
| `except (Exception\|BaseException\|:)` | Aucun |
| `TODO / FIXME / HACK / XXX` | Aucun |

## 5. Critères d'acceptation

| # | Critère | Statut |
|---|---------|--------|
| 1 | `detect_vertical_lines` retourne liste triée par x croissant | OK |
| 2 | Lignes non verticales filtrées (angle > seuil) | OK |
| 3 | `split_spines` retourne des crops non vides (w > 0, h > 0) | OK |
| 4 | `split_spines` couvre toute la largeur de l'image | OK |
| 5 | `segment` retourne >= 1 crop même sans lignes (fallback image entière) | OK |
| 6 | Validation entrées : ValueError sur None / vide | OK |
| 7 | Tests couvrent nominaux + erreurs + bords | OK |
| 8 | Suite de tests verte | OK (85/85) |
| 9 | `ruff check` passe sans erreur | OK |

## 6. Qualité du code

- Docstrings complètes avec Parameters / Returns / Raises pour chaque fonction.
- Convention BGR respectée (entrée et sortie).
- Pas de modification en place : `image.copy()` et `crop.copy()` systématiques.
- Fusion des coupes proches via `min_gap` pour éviter les doublons.
- Fallback correct dans `segment()` si `crops` est vide.

## 7. Bloquants / Warnings / Mineurs

- **Bloquants** : 0
- **Warnings** : 0
- **Mineurs** : 0

## 8. Verdict

**CLEAN** — La branche est prête à être mergée.
