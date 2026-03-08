# Request Changes — Revue globale M3 v1

Statut : DONE
Ordre : 0001

**Date** : 2026-03-08
**Perimetre** : milestone/M3 complet (taches 019-028)
**Resultat** : 492 tests GREEN, 1 test RED, ruff clean (0 erreurs)
**Verdict** : REQUEST CHANGES

---

## Resultats d'execution

| Check | Resultat |
|-------|----------|
| `pytest tests/ -v --tb=short` | **492 passed**, 1 failed |
| `ruff check src/ tests/` | **All checks passed** (0 erreurs) |

Test en echec :
- `tests/test_detect_text.py::TestDetectTextOnSpines::test_returns_list_per_crop` — `ModuleNotFoundError: No module named 'paddleocr'`. Le mock patche `detect_text_regions` mais pas `init_detector`, ce qui provoque un appel reel a `init_detector("paddleocr")` (ligne 240 de `src/detect_text.py`).

---

## Scan automatise (GREP)

| Pattern recherche | Regle | Resultat | Classification |
|-------------------|-------|----------|----------------|
| Fallbacks silencieux (`or []`, `if...else`) | R1 | 4 occurrences | Voir detail ci-dessous |
| Except trop large (`except:`, `except Exception:`) | R1 | 0 occurrences (grep execute) | OK |
| Print residuel (`print(`) | R7 | 0 occurrences (grep execute) | OK |
| Legacy random (`np.random.seed`, `random.seed`) | R3 | 0 occurrences (grep execute) | OK |
| TODO/FIXME orphelins | R7 | 0 occurrences (grep execute) | OK |
| Chemins hardcodes OS-specifiques (tests) | R5 | 0 occurrences (grep execute) | OK |
| Mutable default arguments | R6 | 0 occurrences (grep execute) | OK |
| Images modifiees en place (sans copy) | R4 | 1 occurrence | Voir detail ci-dessous |
| CER / Levenshtein | R9 | 0 occurrences (grep execute) | OK |
| BGR/RGB conversion | R4 | 2 occurrences | Faux positifs (conversions correctes) |

### Detail des matches

**R1 — Fallbacks silencieux**

1. `src/detect_text.py:152` — `bbox_raw = detection[0] if isinstance(detection[0], list) else detection`
   - **Faux positif** : pattern ternaire de type-dispatch, pas un fallback silencieux. Les deux branches sont valides.

2. `src/detect_text.py:202` — `threshold = line_threshold * avg_height if avg_height > 0 else 1.0`
   - **Faux positif** : garde de division par zero, la valeur 1.0 est un seuil de dernier recours, pas un masquage d'erreur.

3. `src/eval.py:169-170` — `return "check" if value <= target else "cross"`
   - **Faux positif** : simple ternaire pour formater un indicateur visuel dans le rapport markdown. Pas un fallback.

**R4 — Images modifiees en place**

1. `src/app.py:156` — `img = Image.open(io.BytesIO(image_bytes))`
   - **Faux positif** : c'est un objet PIL ouvert depuis un flux, pas une modification d'image en place. L'image n'est utilisee que pour lire les dimensions.

**R4 — BGR/RGB**

1. `src/ocr.py:170` — `rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)` : Conversion correcte avant OCR TrOCR (modele deep learning). Conforme R4.
2. `src/visualization.py:187` — `return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)` : Fonction `bgr_to_rgb()` dediee. Conforme R4.

---

## BLOQUANTS (2)

### B1. Test RED : mock incomplet dans `test_detect_text.py`

- **Fichier** : `tests/test_detect_text.py`, ligne 339
- **Probleme** : `test_returns_list_per_crop` patche `src.detect_text.detect_text_regions` mais **pas** `src.detect_text.init_detector`. La fonction `detect_text_on_spines` appelle `init_detector(engine)` a la ligne 240 **avant** d'appeler `detect_text_regions`. Quand `paddleocr` n'est pas installe, le test echoue avec `ModuleNotFoundError`.
- **Impact** : 1 test RED. La suite de tests n'est pas entierement GREEN.
- **Correction** : Ajouter `@patch("src.detect_text.init_detector")` au test, ou mocker `init_detector` pour retourner un objet factice.

### B2. `except Exception` large dans `app.py` (R1)

- **Fichier** : `src/app.py`, lignes 134, 341, 347
- **Probleme** : Trois occurrences de `except Exception as exc:` qui capturent **toutes** les exceptions.
  - Ligne 134 : `_run_pipeline_with_progress` — capture puis re-raise en `RuntimeError`, ce qui masque le type original.
  - Lignes 341, 347 : dans `main()`, les blocs `except Exception as exc:` affichent l'erreur via `st.error()` mais continuent l'execution silencieusement. Cela viole R1 ("Aucun `except:` ou `except Exception:` trop large qui continue l'execution").
- **Note** : Le scan grep R1 "except trop large" n'a pas matche car le pattern recherche `except Exception:` (sans ` as exc`). Neanmoins, ces `except Exception as exc:` suivi de `st.error(...)` sans re-raise constituent un fallback silencieux au sens R1.
- **Correction** : Restreindre les types d'exception captures (ex: `except (RuntimeError, ValueError, FileNotFoundError) as exc:`) ou documenter explicitement pourquoi le catch-all est necessaire dans le contexte Streamlit.

---

## WARNINGS (3)

### W1. Fichier temporaire non nettoye dans `app.py`

- **Fichier** : `src/app.py`, lignes 312-316
- **Probleme** : `tempfile.NamedTemporaryFile(delete=False, ...)` cree un fichier temporaire qui n'est jamais supprime. Pas de bloc `finally` avec `os.unlink(tmp_path)`. En usage prolonge, cela accumule des fichiers temporaires sur disque.
- **Impact** : Fuite de ressources.
- **Correction** : Ajouter un bloc `finally` pour supprimer le fichier temporaire apres utilisation.

### W2. Import non standard dans `_display_original_tab`

- **Fichier** : `src/app.py`, lignes 151-152
- **Probleme** : `from PIL import Image` et `import io` sont importes localement dans la fonction. L'import de `io` (stdlib) devrait etre en haut du fichier conformement aux conventions (R7 imports propres). L'import local de PIL est acceptable pour eviter un import lourd au demarrage.
- **Impact** : Mineur, mais `io` est stdlib et devrait etre importe en tete de fichier.

### W3. `book.get("manually_corrected", False)` dans `prepare_editable_dataframe` (R1)

- **Fichier** : `src/app.py`, ligne 107
- **Probleme** : Utilisation de `dict.get(..., False)` qui constitue un fallback implicite. Si la cle est absente, la valeur par defaut `False` est utilisee silencieusement. Dans ce contexte precis (champ optionnel ajoute par `apply_manual_corrections`), c'est le comportement attendu, mais cela contrevient formellement a R1.
- **Impact** : Faible. Le pattern est comprehensible ici mais devrait etre documente.

---

## MINEURS (4)

### M1. Boucle Python dans `_polygon_area` (R6)

- **Fichier** : `src/detect_text.py`, lignes 47-51
- **Probleme** : Boucle Python sur les points du polygone pour calculer l'aire. Pourrait etre vectorise avec numpy (`np.cross` ou Shoelace vectorise). En pratique, les polygones ont toujours 4 points donc l'impact performance est negligeable.

### M2. Boucle Python dans `detect_empty_regions` (R6)

- **Fichier** : `src/segment.py`, lignes 303-307
- **Probleme** : Boucle Python sur les crops avec `cv2.cvtColor` et `np.var` pour chaque crop. Acceptable car chaque crop est une image independante, mais le pattern `crop.copy()` avant `cvtColor` est inutile puisque `cvtColor` retourne deja une nouvelle image.

### M3. Constante `ENHANCE_CLAHE_TILE_SIZE` typee `tuple` au lieu de `tuple[int, int]`

- **Fichier** : `src/preprocess.py`, ligne 134
- **Probleme** : L'annotation de type est `tuple` generique au lieu de `tuple[int, int]`. Le parametre `tile_grid_size` de `enhance_for_difficult_text` est aussi annote `tuple` au lieu de `tuple[int, int]`.

### M4. Copie inutile dans `classify_spine`

- **Fichier** : `src/segment.py`, ligne 326
- **Probleme** : `cv2.cvtColor(crop.copy(), cv2.COLOR_BGR2GRAY)` — le `.copy()` est inutile car `cvtColor` cree deja une nouvelle image. Pas de risque de mutation de l'entree.

---

## Conformite pipeline

| Critere | Verdict | Detail |
|---------|---------|--------|
| Signatures et types de retour (R8) | OK | Les nouvelles fonctions (`segment_robust`, `segment_with_positions`, `draw_spine_boxes`, `recognize_with_fallback`, etc.) respectent les conventions du pipeline existant. |
| Format de sortie pipeline (R8) | OK | Les bounding boxes sont en format `(x_start, x_end)` coherent avec le module `visualization.py`. Les dicts de crops (`crop`, `x_start`, `x_end`) sont utilises de maniere uniforme. |
| Structures de donnees partagees (R8) | OK | Le format `{"books": [...]}` est respecte entre `pipeline.py`, `app.py` et `eval.py`. |
| Coherence des metriques (R8) | OK | CER calcule via `eval_utils.compute_cer` dans `benchmark.py` et `eval.py`. |
| CLAHE sur bon canal (R9) | OK | `enhance_for_difficult_text` applique CLAHE sur le canal L en espace LAB. |
| BGR/RGB conversions (R4/R9) | OK | Conversions correctement placees aux frontieres deep learning (TrOCR, Streamlit display). |
| Bounding boxes coherentes (R9) | OK | Format `(x_start, x_end)` utilise de maniere uniforme dans `visualization.py` et `segment.py`. |
| Pas de hardcoding (R2) | OK | Seuils en constantes nommees (`CONFIDENCE_THRESHOLD`, `MIN_REGION_AREA`, `DEFAULT_FALLBACK_CONFIDENCE_THRESHOLD`, etc.). |
| Reproductibilite (R3) | OK | Pas d'operations aleatoires dans le code M3. |
| Gestion fichiers I/O (R5) | OK | `mkdir(parents=True, exist_ok=True)` utilise dans `eval.py`, `benchmark.py`, `failure_analysis.py`. Paths construits avec `pathlib.Path`. |

---

## Resume des actions

### Bloquants (a corriger avant merge)
1. **B1** : Corriger le mock dans `test_detect_text.py::test_returns_list_per_crop` pour aussi patcher `init_detector` et obtenir 493/493 tests GREEN.
2. **B2** : Restreindre les `except Exception` dans `src/app.py` (lignes 134, 341, 347) a des types d'exception specifiques, ou justifier le catch-all par un commentaire explicite dans le contexte Streamlit UI.

### Warnings (recommandes)
3. **W1** : Nettoyer le fichier temporaire dans `app.py` avec `os.unlink()` dans un `finally`.
4. **W2** : Deplacer `import io` en haut de `app.py`.
5. **W3** : Documenter le `dict.get("manually_corrected", False)` comme pattern volontaire.

### Mineurs (optionnels)
6. **M1-M4** : Corrections cosmetiques (copies inutiles, annotations de type, vectorisation optionnelle).
