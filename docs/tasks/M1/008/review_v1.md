# Review v1 — 008 Dataset initial et ground truth

**Branche** : `task/008-dataset-ground-truth`
**Itération** : v1
**Date** : 2026-03-08
**Verdict** : CLEAN

---

## 1. Tâche

- Statut : DONE
- Critères d'acceptation : tous cochés (9/9)
- Checklist de fin : 7/9 cochés (les 2 non cochés sont le commit GREEN et la PR, voir M-1)

## 2. Commits

```
fcc0291 [WS5] #008 GREEN: dataset initial et ground truth
b25faf3 [WS5] #008 RED: tests chargement ground truth
```

Cycle RED -> GREEN respecté. Messages conformes.

## 3. Tests & linter

- `pytest tests/ -v --tb=short` : **164 passed** (0.65s)
- `ruff check src/ tests/` : **All checks passed**

## 4. Revue de code — `src/eval_utils.py`

| Critère | Résultat |
|---|---|
| `raise ValueError` pour fichier manquant | OK (ligne 24) |
| `raise ValueError` pour colonnes manquantes | OK (ligne 30) |
| `raise ValueError` pour titres vides/blancs | OK (lignes 32-36) |
| `pathlib.Path` pour les chemins | OK (ligne 22) |
| Pas de fallbacks silencieux | OK |
| `REQUIRED_COLUMNS` en constante nommée | OK (ligne 7) |
| Pas de `print()` | OK |
| Imports propres (stdlib, third-party, local) | OK |

## 5. Revue de code — `tests/test_eval_utils.py`

| Critère | Résultat |
|---|---|
| CSV synthétique dans `tmp_path` | OK (helper `_write_csv`) |
| Test fichier introuvable (ValueError) | OK |
| Test colonnes manquantes (ValueError) | OK |
| Test titre vide (ValueError) | OK |
| Test titre whitespace-only (ValueError) | OK |
| Test 15 images uniques | OK |
| Test >= 3 titres par image | OK |
| Test nombre de lignes correct | OK |
| 9 tests au total, tous passants | OK |

## 6. Ground truth CSV — `data/ground_truth/ground_truth.csv`

| Critère | Résultat |
|---|---|
| Colonnes `image_filename, spine_index, title, author` | OK |
| 15 images distinctes | OK (15 exactement) |
| >= 3 titres par image | OK (min = 3, max = 9) |
| 99 lignes de données | OK |
| Chargeable par pandas sans erreur | OK |
| Correspondance 1:1 CSV <-> fichiers dans `data/raw/` | OK |
| Pas de titres vides | OK |

## 7. Photos — `data/raw/`

- 15 fichiers JPEG présents : IMG_3046 a IMG_3057, IMG_3059 a IMG_3061
- IMG_3058 absent (gap dans la numerotation originale, coherent entre CSV et raw)

## 8. Scans GREP (fichiers modifies : `src/eval_utils.py`, `tests/test_eval_utils.py`)

| Scan | Resultat |
|---|---|
| §R1 — Fallbacks silencieux | 0 occurrences (grep execute) |
| §R1 — Except trop large | 0 occurrences (grep execute) |
| §R7 — Print residuel | 0 occurrences (grep execute) |
| §R3 — Legacy random API | 0 occurrences (grep execute) |
| §R7 — TODO/FIXME orphelins | 0 occurrences (grep execute) |
| §R5 — Chemins hardcodes OS-specifiques | 0 occurrences (grep execute) |
| §R6 — Mutable default arguments | 0 occurrences (grep execute) |
| §R4 — Images modifiees en place | 0 occurrences (grep execute) |
| §R9 — CER calcule sans normalisation | 0 occurrences (grep execute) |
| §R4 — BGR/RGB non converti | 0 occurrences (grep execute) |

Matches detectes dans des fichiers hors scope de cette tache (`detect_text.py`, `postprocess.py`, `ocr.py`) — faux positifs par rapport au diff de la tache 008.

## 9. Bloquants

Aucun.

## 10. Warnings

Aucun.

## 11. Mineurs

| # | Description | Ref |
|---|---|---|
| M-1 | Checklist de fin : les cases "Commit GREEN" et "Pull Request" ne sont pas cochees dans le fichier de tache, bien que le commit GREEN existe (`fcc0291`). La PR est attendue apres review. Cocher la case du commit GREEN. | §Checklist |

---

**Bloquants : 0 | Warnings : 0 | Mineurs : 1**
