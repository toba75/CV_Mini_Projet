# Revue TDD — Tâche 004 — Détection de texte (v1)

**Date** : 2026-03-08
**Branche** : `task/004-text-detection-test`
**Commits** : `fe7771f` (RED), `28c9bae` (GREEN)
**Fichiers audités** : `src/detect_text.py`, `tests/test_detect_text.py`

---

## 1. Statut tâche

| Critère | Résultat |
|---------|----------|
| Statut DONE | OK |
| Critères d'acceptation cochés | OK (tous cochés) |
| Checklist de fin cochée | **PARTIEL** — lignes "Commit GREEN" et "Pull Request" non cochées |

## 2. Commits RED/GREEN

| Commit | Contenu | Verdict |
|--------|---------|---------|
| `fe7771f` RED | Tests uniquement (`tests/test_detect_text.py`) | OK |
| `28c9bae` GREEN | Implémentation (`src/detect_text.py`) + mise à jour tâche + ajustements tests | OK |

Cycle TDD respecté : RED avant GREEN, séparation correcte.

## 3. Tests et linter

| Vérification | Résultat |
|--------------|----------|
| `pytest tests/ -v` | **100 passed** (dont 15 tests detect_text) |
| `ruff check src/ tests/` | **All checks passed** |

## 4. Analyse du code

### 4.1 `src/detect_text.py`

**Validation des entrees (R1)** : OK — `raise ValueError` pour `None`, non-ndarray, et image vide.

**Problemes identifies** :

#### B-1 — Fallback silencieux sur confidence (R1) — BLOQUANT

Ligne 68-72 :
```python
confidence = (
    float(detection[1])
    if isinstance(detection, (list, tuple)) and len(detection) > 1
    else 1.0
)
```
Si la confidence est absente de la detection, le code assigne silencieusement `1.0` au lieu de signaler l'anomalie. Cela viole R1 (pas de fallback silencieux) et peut masquer un probleme dans la sortie du modele. Le code devrait lever une erreur ou au minimum logger un warning explicite.

#### W-1 — Pas de validation `ndim`/`dtype` (R4) — WARNING

La validation d'entree verifie `None`, type et `size == 0`, mais ne verifie pas que l'image est bien 3D (`ndim == 3`) ni `uint8`. Une image grayscale 2D ou float64 serait acceptee silencieusement et pourrait produire des resultats imprevisibles.

Correction suggeree :
```python
if image.ndim != 3:
    raise ValueError("Image must be 3-dimensional (H, W, C).")
if image.dtype != np.uint8:
    raise ValueError("Image must be uint8.")
```

#### W-2 — Pas de copie defensive de l'image (R4) — WARNING

L'image est passee directement a `detector.ocr()` sans `.copy()`. Si le detecteur modifie l'image en place, l'appelant sera affecte. R4 exige de ne jamais modifier en place une image d'entree.

#### M-1 — `model_name="craft"` accepte mais leve ValueError (R1) — MINEUR

`init_detector` accepte `"craft"` dans la validation initiale (ligne 18), mais leve immediatement une `ValueError` a la ligne 30. L'erreur n'est pas une anomalie logicielle mais le message est confus : l'utilisateur pourrait croire que "craft" est supporte. Suggestion : inclure "craft" dans le message d'erreur du premier check, ou indiquer clairement "not yet implemented" dans la docstring.

### 4.2 `tests/test_detect_text.py`

**Tests mockes** : OK — aucun import de PaddleOCR reel, tous les tests utilisent des mocks.

**Couverture des scenarios** :
- Nominal (format sortie, detection, appel detector) : OK
- Erreurs (None, vide, non-array) : OK
- Bords (petite image, grayscale 3-channel, pas de texte) : OK

**Reproductibilite (R3)** : OK — `np.random.default_rng(42)` utilise.

**Pas de test de non-modification de l'image d'entree** : absence liee au W-2 ci-dessus.

## 5. Scans GREP

| Scan | Fichier(s) | Resultat |
|------|-----------|----------|
| R1 — Fallbacks (`or []`, `or {}`, `if...else`) | `src/detect_text.py` | 1 match ligne 65 — **faux positif** (disambiguation de format PaddleOCR, pas un fallback) |
| R1 — Except trop large | `src/detect_text.py` | 0 occurrences (grep execute) |
| R7 — `print()` | `src/detect_text.py`, `tests/test_detect_text.py` | 0 occurrences (grep execute) |
| R3 — Legacy random | `tests/test_detect_text.py` | 0 occurrences (grep execute) |
| R7 — TODO/FIXME | `src/detect_text.py`, `tests/test_detect_text.py` | 0 occurrences (grep execute) |
| R5 — Chemins hardcodes | `tests/test_detect_text.py` | 0 occurrences (grep execute) |
| R6 — Mutable defaults | `src/detect_text.py`, `tests/test_detect_text.py` | 0 occurrences (grep execute) |
| R7 — `import *` | `src/detect_text.py`, `tests/test_detect_text.py` | 0 occurrences (grep execute) |
| R4 — BGR/RGB conversion | `src/detect_text.py` | 0 occurrences (grep execute) — note : PaddleOCR accepte BGR nativement, pas de conversion necessaire |

## 6. Verdict

| Categorie | ID | Description |
|-----------|----|-------------|
| **BLOQUANT** | B-1 | Fallback silencieux `else 1.0` sur confidence (R1) |
| **WARNING** | W-1 | Pas de validation `ndim == 3` / `dtype == uint8` (R4) |
| **WARNING** | W-2 | Image passee sans `.copy()` au detecteur (R4) |
| **MINEUR** | M-1 | `"craft"` accepte a la validation mais leve ensuite ValueError |

---

**Verdict : REQUEST CHANGES**

- Bloquants : 1
- Warnings : 2
- Mineurs : 1
