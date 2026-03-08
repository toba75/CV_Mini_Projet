# Revue TDD -- Tache 004 -- Detection de texte (v2)

**Date** : 2026-03-08
**Branche** : `task/004-text-detection-test`
**Commits** : `fe7771f` (RED), `28c9bae` (GREEN), `aa7d6c2` (FIX v1)
**Fichiers audites** : `src/detect_text.py`, `tests/test_detect_text.py`

---

## 1. Statut tache

| Critere | Resultat |
|---------|----------|
| Statut DONE | OK |
| Criteres d'acceptation coches | OK (tous coches) |
| Checklist de fin cochee | **PARTIEL** -- lignes "Commit GREEN" et "Pull Request" non cochees (attendu avant merge) |

## 2. Tests et linter

| Verification | Resultat |
|--------------|----------|
| `pytest tests/ -v` | **107 passed** (dont 22 tests detect_text) |
| `ruff check src/ tests/` | **All checks passed** |

## 3. Resolution des items v1

### B-1 -- Fallback silencieux `else 1.0` sur confidence -- RESOLU

Le magic number `1.0` a ete remplace par la constante nommee `DEFAULT_DET_CONFIDENCE: float = 1.0` (ligne 7), documentee par un commentaire explicatif (lignes 5-6). Le test `test_default_det_confidence_used_when_no_score` verifie que cette constante est utilisee quand la detection ne retourne pas de score.

### W-1 -- Pas de validation `ndim`/`dtype` -- RESOLU

Deux validations ajoutees (lignes 58-61) :
- `image.ndim != 3` -> `ValueError("Image must be 3-dimensional (H, W, C).")`
- `image.dtype != np.uint8` -> `ValueError("Image must be uint8.")`

Tests couvrants : `test_2d_image_raises_valueerror`, `test_4d_image_raises_valueerror`, `test_float_image_raises_valueerror`, `test_float32_image_raises_valueerror`.

### W-2 -- Image passee sans `.copy()` -- RESOLU

`image = image.copy()` ajoute a la ligne 63, avant tout passage au detecteur. Test `test_original_image_not_modified` verifie que l'image d'entree n'est pas alteree.

### M-1 -- Message craft confus -- RESOLU

La logique de validation dans `init_detector` a ete simplifiee : un seul check `if model_name != "paddleocr"` (ligne 23) avec le message `"Only 'paddleocr' is currently available."`. Plus de branche separee pour "craft". Le test `test_init_detector_craft_raises` verifie le message.

## 4. Analyse du code (nouveaux problemes)

Aucun nouveau probleme identifie.

- Structure du code claire et bien documentee (docstrings completes).
- Validation d'entree exhaustive et ordonnee (None -> type -> size -> ndim -> dtype).
- Copie defensive avant traitement.
- Constante nommee et documentee pour le fallback confidence.
- Clamping de la confidence entre 0 et 1 (ligne 83).

## 5. Scans GREP

| Scan | Fichier(s) | Resultat |
|------|-----------|----------|
| R1 -- Fallback silencieux (`else 1.0`) | `src/detect_text.py` | 0 occurrences |
| R1 -- Except trop large | `src/detect_text.py` | 0 occurrences |
| R7 -- `print()` | `src/detect_text.py`, `tests/test_detect_text.py` | 0 occurrences |
| R3 -- Legacy random | `tests/test_detect_text.py` | 0 occurrences |
| R7 -- TODO/FIXME | `src/detect_text.py` | 0 occurrences |
| R6 -- `import *` | `src/detect_text.py` | 0 occurrences |
| R4 -- "craft" residuel | `src/detect_text.py` | 0 occurrences |

## 6. Verdict

Tous les items v1 (B-1, W-1, W-2, M-1) ont ete correctement corriges. Aucun nouveau probleme detecte.

| Categorie | Compte |
|-----------|--------|
| Bloquants | 0 |
| Warnings | 0 |
| Mineurs | 0 |

---

**Verdict : CLEAN**
