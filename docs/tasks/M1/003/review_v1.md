# Revue TDD — Tâche 003 — Segmentation naïve Hough (v1)

**Branche** : `task/003-segment-naive-hough`
**Date** : 2026-03-08
**Reviewer** : TDD-Reviewer (Claude)
**Itération** : v1

---

## 1. Statut de la tâche

- Statut : **DONE** (marqué dans le fichier de tâche)
- Critères d'acceptation : **9/9 cochés**
- Checklist de fin : **6/8 cochés** (les 2 non cochés sont le commit GREEN et la PR, mais le commit GREEN existe bien : `7060f7a`)

## 2. Commits TDD

```
d39c1d6 [WS1] #003 RED: tests segmentation naïve Hough
7060f7a [WS1] #003 GREEN: segmentation naïve Canny+Hough implémentée
```

- Format RED/GREEN : **conforme**
- Ordre : RED avant GREEN : **conforme**

## 3. Tests et linter

- `pytest tests/ -v --tb=short` : **84 passed** (0 failed)
- `ruff check src/ tests/` : **All checks passed**

## 4. Revue de code

### src/segment.py

| Critère | Verdict | Commentaire |
|---------|---------|-------------|
| §R1 Validation explicite | OK | `raise ValueError` sur None et empty dans les 3 fonctions |
| §R4 Convention BGR | OK | Docstrings documentent BGR, pas de conversion BGR->RGB |
| §R4 .copy() / pas de modification en place | OK | `gray = image.copy()` (L64), `image.copy()` (L125, L149, L185) |
| §R2 Paramètres Hough | OK | Exposés comme paramètres de fonction avec defaults nommés |
| §R9 Hough documenté | OK | Docstring référence §R9, paramètres documentés avec defaults |
| §R7 snake_case | OK | Nommage cohérent |
| §R7 Pas de print() | OK | Aucun print() |
| §R7 Imports propres | OK | stdlib (math) -> third-party (cv2, numpy), pas d'import * |
| §R6 Mutable defaults | OK | Aucun |
| §R2 Magic numbers | WARNING | `min_gap = max(5, int(width * 0.02))` (L135) : les valeurs 5 et 0.02 sont des littéraux non nommés. Commentaire présent mais pas de constante nommée. |

### tests/test_segment.py

| Critère | Verdict | Commentaire |
|---------|---------|-------------|
| Scénarios nominaux | OK | Lignes triées, type retour, filtrage non-verticales, crops non vides, couverture largeur |
| Scénarios erreur | OK | None et empty testés pour les 3 fonctions |
| Scénarios bord | OK | Image sans lignes, petite image, lignes vides |
| does_not_modify_input | WARNING | Testé pour `split_spines` mais absent pour `detect_vertical_lines` et `segment` |
| §R3 Reproductibilité | OK | Utilise `np.random.default_rng(42)` |

## 5. Scans GREP (§GREP)

| Scan | Résultat |
|------|----------|
| §R1 Fallbacks silencieux | 0 occurrences (grep exécuté) |
| §R1 Broad except | 0 occurrences (grep exécuté) |
| §R7 print() | 0 occurrences (grep exécuté) |
| §R3 Legacy random | 0 occurrences (grep exécuté) |
| §R7 TODO/FIXME | 0 occurrences (grep exécuté) |
| §R5 Hardcoded paths | 0 occurrences (grep exécuté) |
| §R6 Mutable defaults | 0 occurrences (grep exécuté) |
| §R4 Image in-place | 0 occurrences (grep exécuté) |
| §R9 CER | 0 occurrences (grep exécuté) -- non applicable |
| §R4 BGR/RGB | 0 occurrences (grep exécuté) -- non applicable |
| import * | 0 occurrences (grep exécuté) |

## 6. Items relevés

### Warnings (W)

**W-1 (§R2) — Magic numbers dans `split_spines` (L135)**
`min_gap = max(5, int(width * 0.02))` : les valeurs `5` et `0.02` devraient etre extraites en constantes nommees en haut du module (ex: `_MIN_GAP_PX = 5`, `_MIN_GAP_RATIO = 0.02`) pour conformite avec §R2.

**W-2 (§R4) — Test `does_not_modify_input` manquant pour `detect_vertical_lines`**
Le test `does_not_modify_input` existe pour `split_spines` mais pas pour `detect_vertical_lines`. L'implementation est correcte (utilise `.copy()`), mais le test devrait verifier ce contrat explicitement.

### Bloquants

Aucun.

### Mineurs

Aucun.

## 7. Verdict

**REQUEST CHANGES** — 2 warnings a traiter.

| Categorie | Nombre |
|-----------|--------|
| Bloquants | 0 |
| Warnings  | 2 |
| Mineurs   | 0 |
