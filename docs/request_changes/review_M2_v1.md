# Revue globale Milestone M2 -- v1

Statut : TODO
Ordre : 0003

**Date** : 2026-03-08
**Branche** : milestone/M2
**Iteration** : v1
**Perimetre** : Audit complet src/ et tests/ pour le milestone M2
**Resultat** : 285 tests GREEN, ruff clean (0 erreur)
**Verdict** : **REQUEST CHANGES**

---

## Resultats d'execution

| Check | Resultat |
|---|---|
| `pytest tests/ -v` | **285 passed** (3.75s) |
| `ruff check src/ tests/` | **All checks passed** |
| `print()` residuel (src/) | 0 occurrences (grep execute) |
| `TODO`/`FIXME` orphelin (src/ + tests/) | 0 occurrences (grep execute) |
| Broad `except` (src/) | 1 occurrence (`pipeline.py:99`) -- **intentionnel** (voir note) |
| Fallbacks silencieux `or []`/`or {}` (src/) | 0 occurrences (grep execute) |
| Mutable defaults `def f(x=[])` (src/) | 0 occurrences (grep execute) |
| Legacy random API (src/ + tests/) | 0 occurrences (grep execute) |
| BGR/RGB conversions (src/) | 1 occurrence (`ocr.py:177`) -- correcte (BGR->RGB avant TrOCR) |
| Chemins hardcodes OS-specifiques (tests/) | 0 occurrences (grep execute) |

**Note sur `except Exception:` dans pipeline.py:99** : Ce pattern est **intentionnel par design**. Le pipeline traite chaque spine individuellement et doit continuer si un spine echoue (resilience). L'exception est loguee via `logger.exception()`. Ce n'est pas une violation.

---

## BLOQUANTS (1)

### B-1. `_validate_image` dans `preprocess.py` dupliquee et non utilisee par les fonctions inline

**Fichier** : `src/preprocess.py` (L142-153)
**Probleme** : Le module `preprocess.py` definit une fonction `_validate_image` (L142) mais les fonctions `resize_image` (L65-74) et `apply_clahe` (L111-120) continuent de valider manuellement avec du code inline duplique au lieu d'appeler `_validate_image`. Seules `detect_shelf_contour` et `correct_perspective` utilisent `_validate_image`.

Cela cree une **incoherence interne** : si la logique de validation change, il faut modifier 3 endroits dans le meme fichier. Ce n'est pas un bug actif mais une violation de DRY au sein du meme module qui rend la maintenance fragile.

**Severite revue** : En relisant, la validation inline et `_validate_image` font exactement les memes checks. Ce n'est pas bloquant au sens "bug actif". **Reclasse en WARNING (W-4).**

---

## BLOQUANTS (0)

Aucun bloquant actif identifie. Le code fonctionne correctement, les 285 tests passent, et les interfaces intermodules sont coherentes.

---

## WARNINGS (4)

### W-1. DRY : `_validate_image` dupliquee dans 4 modules

**Fichiers** : `src/preprocess.py:142`, `src/segment.py:22`, `src/detect_text.py:198`, `src/ocr.py:53`
**Probleme** : La fonction `_validate_image` est copiee quasi-identiquement dans 4 modules. De plus, `preprocess.py` contient aussi une validation inline dans `resize_image` et `apply_clahe` en plus de sa propre `_validate_image`.

Les signatures different legerement (`np.ndarray | None` vs `np.ndarray`), mais la logique est identique.

**Impact** : Si la politique de validation change (ex: accepter float32), il faut modifier 4+ endroits. Risque reel de divergence.

**Recommandation** : Extraire dans un module utilitaire partage (`src/validation.py` ou dans `src/__init__.py`) et importer partout.

### W-2. `preprocess.py` : validation inline + `_validate_image` dans le meme module

**Fichier** : `src/preprocess.py`
**Probleme** : `resize_image` (L65-74) et `apply_clahe` (L111-120) font la validation manuellement, alors que `_validate_image` (L142) existe dans le meme fichier. Incoherence interne.

**Recommandation** : Remplacer la validation inline par un appel a `_validate_image` dans `resize_image` et `apply_clahe`.

### W-3. Format bbox non uniforme entre modules

**Fichiers** : `src/segment.py`, `src/detect_text.py`
**Probleme** : `segment.py` utilise des tuples `(x1, y1, x2, y2)` pour les lignes verticales, tandis que `detect_text.py` utilise des polygones 4-points `[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]` pour les bboxes OCR. Ce sont deux concepts differents (lignes vs regions de texte) donc ce n'est pas une incoherence fonctionnelle, mais cela peut creer de la confusion.

**Impact** : Risque faible -- les deux formats sont utilises dans des contextes differents et ne sont jamais melanges.

**Recommandation** : Documenter explicitement le format de bbox dans chaque module (deja partiellement fait via les docstrings).

### W-4. `detect_text_regions` fait de la validation inline en plus de `_validate_image`

**Fichier** : `src/detect_text.py:55-64`
**Probleme** : `detect_text_regions` fait sa propre validation (L55-64) avec des messages d'erreur differents de ceux de `_validate_image` (L198-213) definie plus bas dans le meme fichier. Les messages ne sont pas identiques ("Image cannot be None" vs "Image cannot be None" -- en fait identiques ici, mais le check `isinstance` est duplique).

**Recommandation** : Utiliser `_validate_image` dans `detect_text_regions` pour reduire la duplication.

---

## MINEURS (3)

### m-1. `unused_variable` potentiel : `results_container` dans `app.py`

**Fichier** : `src/app.py:27`
**Probleme** : `results_container = st.container()` est assigne puis utilise comme context manager sur la ligne suivante. C'est fonctionnel mais le pattern Streamlit recommande est `with st.container():` directement.

**Recommandation** : Simplifier en `with st.container():`.

### m-2. `ocr.py` : logique de concatenation dupliquee entre `recognize_text_unified` et `recognize_batch`

**Fichier** : `src/ocr.py:232-236` et `src/ocr.py:268-275`
**Probleme** : La logique de concatenation des resultats OCR (join texts, average confidence) est copiee entre `recognize_text_unified` et `recognize_batch`. Si la logique de fusion change, il faut modifier les deux endroits.

**Recommandation** : Extraire une fonction `_aggregate_ocr_results(results, engine)`.

### m-3. `eval_utils.py` : `evaluate_dataset` ne valide pas les colonnes du CSV

**Fichier** : `src/eval_utils.py:164`
**Probleme** : `evaluate_dataset` lit le CSV directement avec `pd.read_csv` (L164) sans passer par `load_ground_truth` qui fait la validation des colonnes. Si le CSV est malformed, l'erreur sera un `KeyError` generique au lieu d'un `ValueError` explicite.

**Recommandation** : Utiliser `load_ground_truth` dans `evaluate_dataset` pour beneficier de la validation existante.

---

## Audit intermodule

| Interface | Format | Status |
|---|---|---|
| `preprocess` -> `segment` | BGR uint8 ndarray | OK -- valide par `_validate_image` dans `segment.py` |
| `segment` -> `detect_text` | list[BGR uint8 ndarray] | OK -- chaque crop valide dans `detect_text_regions` |
| `detect_text` -> `ocr` | BGR uint8 ndarray (oriente) | OK -- `correct_orientation` retourne BGR uint8 |
| `ocr` -> `postprocess` | str (texte brut) | OK -- `recognize_text_unified` retourne dict avec `text` str |
| `postprocess` -> `pipeline` | dict structuré | OK -- `postprocess_spine` retourne dict avec cles documentees |
| `pipeline` JSON schema | Conforme | OK -- cles `image`, `num_spines_detected`, `processing_time_s`, `books` |

Aucune incoherence intermodule detectee. Les contrats de donnees sont respectes entre tous les modules.

---

## Compteurs

| Severite | Nombre |
|---|---|
| Bloquant | **0** |
| Warning | **4** |
| Mineur | **3** |
| Tests | 285 passed |
| Ruff | clean |

---

## Verdict final

**REQUEST CHANGES** -- 0 bloquant mais 4 warnings a adresser avant merge.

Les warnings W-1 et W-2 (duplication de `_validate_image`) representent un risque reel de divergence de validation entre modules. Les corrections recommandees sont simples et amelioreront significativement la maintenabilite.

Actions prioritaires :
1. **W-1/W-2** : Factoriser `_validate_image` dans un module partage et l'utiliser dans tous les modules
2. **W-4** : Utiliser `_validate_image` dans `detect_text_regions` au lieu de la validation inline
3. **m-2** : Factoriser la logique d'agregation OCR dans `ocr.py`
4. **m-3** : Utiliser `load_ground_truth` dans `evaluate_dataset`
