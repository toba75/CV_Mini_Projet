# Revue globale Milestone M2 -- v2

Statut : TODO
Ordre : 0004

**Date** : 2026-03-08
**Branche** : milestone/M2
**Iteration** : v2 (re-audit apres corrections v1)
**Perimetre** : Verification des corrections v1 + scan de regression
**Resultat** : 285 tests GREEN, ruff clean (0 erreur)
**Verdict** : **CLEAN**

---

## Resultats d'execution

| Check | Resultat |
|---|---|
| `pytest tests/ -v` | **285 passed** (3.08s) |
| `ruff check src/ tests/` | **All checks passed** |
| `print()` residuel (src/) | 0 occurrences |
| `TODO`/`FIXME` orphelin (src/) | 0 occurrences |
| Broad `except:` nu (src/) | 0 occurrences |
| `except Exception` (src/) | 1 occurrence (`pipeline.py:99`) -- **intentionnel** (resilience par spine, logue via `logger.exception`) |
| Fallbacks silencieux `or []`/`or {}` (src/) | 0 occurrences |
| Mutable defaults `def f(x=[])` (src/) | 0 occurrences |

---

## Verification des corrections v1

### W-1/W-2 : `validate_image` factorisee dans `src/__init__.py`

**Statut** : CORRIGE

- `validate_image` definie dans `src/__init__.py` (L6-27) avec validation complete (None, ndarray, size, ndim, dtype).
- Importee via `from src import validate_image` dans les 4 modules :
  - `src/preprocess.py` (L13) -- utilisee dans `resize_image` (L67) et `apply_clahe` (L104)
  - `src/segment.py` (L16) -- aliasee `_validate_image` (L25), utilisee partout
  - `src/detect_text.py` (L8) -- utilisee directement dans `detect_text_regions` (L57)
  - `src/ocr.py` (L19) -- aliasee `_validate_image` (L56), utilisee partout
- Plus aucune validation inline dupliquee dans `preprocess.py`.

### W-3 : Format bbox non uniforme

**Statut** : IGNORE (faux positif confirme en v1 -- concepts differents : lignes vs regions texte)

### W-4 : `detect_text_regions` utilise `validate_image`

**Statut** : CORRIGE

- `detect_text_regions` (L57) appelle `validate_image(image)` directement.
- Plus de validation inline dans cette fonction.

### m-1 : `app.py` simplifie

**Statut** : CORRIGE

- `with st.container():` utilise directement (L27), plus de variable intermediaire.

### m-2 : `_aggregate_ocr_results` extraite dans `ocr.py`

**Statut** : CORRIGE

- Fonction `_aggregate_ocr_results` definie (L197-215) avec docstring complete.
- Utilisee par `recognize_text_unified` (L243) et `recognize_batch` (L275).
- Logique de concatenation centralisee (join texts, mean confidence).

### m-3 : `evaluate_dataset` utilise `load_ground_truth`

**Statut** : CORRIGE

- `evaluate_dataset` (L165) appelle `load_ground_truth(str(csv_files[0]))` au lieu de `pd.read_csv` direct.
- Validation des colonnes et des titres vides desormais assuree.

---

## Scan de regression

Aucun nouveau probleme introduit par les corrections :
- Les alias `_validate_image = validate_image` dans chaque module assurent la retro-compatibilite interne.
- Les tests existants (285) passent tous sans modification.
- Ruff ne signale aucune erreur.
- Pas de `print()`, `TODO`, mutable defaults, ou broad `except:` nu.

---

## Audit intermodule

| Interface | Format | Status |
|---|---|---|
| `preprocess` -> `segment` | BGR uint8 ndarray | OK |
| `segment` -> `detect_text` | list[BGR uint8 ndarray] | OK |
| `detect_text` -> `ocr` | BGR uint8 ndarray (oriente) | OK |
| `ocr` -> `postprocess` | str (texte brut) | OK |
| `postprocess` -> `pipeline` | dict structure | OK |
| `pipeline` JSON schema | Conforme | OK |

---

## Compteurs

| Severite | Nombre |
|---|---|
| Bloquant | **0** |
| Warning | **0** |
| Mineur | **0** |
| Tests | 285 passed |
| Ruff | clean |

---

## Verdict final

**CLEAN** -- Toutes les corrections v1 ont ete appliquees correctement. Aucun nouveau probleme detecte. Le code est pret pour merge.
