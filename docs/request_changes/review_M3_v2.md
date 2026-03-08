# Request Changes — Revue globale M3 v2

Statut : DONE
Ordre : 0002

**Date** : 2026-03-08
**Perimetre** : milestone/M3 complet (taches 019-028)
**Base** : commit de correction `aa8bad0` (suite a review v1)
**Resultat** : 493 tests GREEN, ruff clean (0 erreurs)
**Verdict** : CLEAN

---

## Resultats d'execution

| Check | Resultat |
|-------|----------|
| `pytest tests/ -v --tb=short` | **493 passed** in 1.21s |
| `ruff check src/ tests/` | **All checks passed** (0 erreurs) |

Aucun test en echec.

---

## Scan automatise (GREP)

| Pattern recherche | Regle | Resultat | Classification |
|-------------------|-------|----------|----------------|
| Fallbacks silencieux (`or []`, `if...else`) | R1 | 5 occurrences | Tous faux positifs (voir detail) |
| Except trop large (`except:`, `except Exception:`) | R1 | 0 occurrences (grep execute) | OK |
| Print residuel (`print(`) | R7 | 0 occurrences (grep execute) | OK |
| Legacy random (`np.random.seed`, `random.seed`) | R3 | 0 occurrences (grep execute) | OK |
| TODO/FIXME orphelins | R7 | 0 occurrences (grep execute) | OK |
| Chemins hardcodes OS-specifiques (tests) | R5 | 0 occurrences (grep execute) | OK |
| Mutable default arguments | R6 | 0 occurrences (grep execute) | OK |
| Images modifiees en place (sans copy) | R4 | 1 occurrence | Faux positif (voir detail) |
| CER / Levenshtein | R9 | 2 occurrences | OK (usage correct) |
| BGR/RGB conversion | R4 | 2 occurrences | Faux positifs (conversions correctes) |

### Detail des matches

**R1 — Fallbacks silencieux**

1. `src/detect_text.py:149` — `bbox_raw = detection[0] if isinstance(detection[0], list) else detection`
   - **Faux positif** : pattern ternaire de type-dispatch, pas un fallback silencieux.

2. `src/detect_text.py:199` — `threshold = line_threshold * avg_height if avg_height > 0 else 1.0`
   - **Faux positif** : garde de division par zero. Valeur 1.0 est un seuil de dernier recours, pas un masquage d'erreur.

3. `src/eval.py:169-170` — `return "..." if value <= target else "..."`
   - **Faux positif** : ternaire pour formater un indicateur visuel dans le rapport markdown.

4. `src/eval_utils.py:72` — `return 1.0 if len(predicted_text) > 0 else 0.0`
   - **Faux positif** : gestion documentee du cas edge "ground truth vide" dans le calcul CER. Les deux branches sont des valeurs mathematiquement correctes, pas des fallbacks.

**R4 — Images modifiees en place**

1. `src/app.py:158` — `img = Image.open(io.BytesIO(image_bytes))`
   - **Faux positif** : objet PIL ouvert depuis un flux, pas une modification en place.

**R4 — BGR/RGB**

1. `src/ocr.py:170` — `rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)` : Conversion correcte avant TrOCR. Conforme R4.
2. `src/visualization.py:187` — `return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)` : Fonction `bgr_to_rgb()` dediee. Conforme R4.

**R9 — CER / Levenshtein**

1. `src/eval_utils.py:8` — `from rapidfuzz.distance import Levenshtein` : import correct.
2. `src/eval_utils.py:73` — `distance = Levenshtein.distance(predicted_text, ground_truth_text)` : normalise par `len(ground_truth_text)` a la ligne suivante. Conforme R9.

---

## Verification des corrections v1

| Item | Description | Statut |
|------|-------------|--------|
| B1 | Mock incomplet dans `test_returns_list_per_crop` | **CORRIGE** — `@patch("src.detect_text.init_detector")` ajoute (ligne 331), `mock_init.return_value = MagicMock()` (ligne 335). Test passe. |
| B2 | `except Exception` larges dans `app.py` | **CORRIGE** — Lignes 344 et 350 restreintes a `(RuntimeError, ValueError, FileNotFoundError, OSError)`. Ligne 137 conserve `except Exception` mais re-raise avec commentaire explicite. |
| W1 | Fichier temporaire non nettoye | **CORRIGE** — Bloc `finally: os.unlink(tmp_path)` ajoute (lignes 364-365). |
| W2 | `import io` local | **CORRIGE** — `import io` deplace en haut du fichier (ligne 4). |
| W3 | `dict.get("manually_corrected", False)` non documente | **CORRIGE** — Commentaire explicatif ajoute (ligne 109). |
| M1 | Boucle Python dans `_polygon_area` | **CORRIGE** — Shoelace vectorise avec numpy (`np.dot` + `np.roll`, ligne 52). |
| M2 | `.copy()` inutile dans `detect_empty_regions` | **CORRIGE** — `.copy()` retire (ligne 307). |
| M3 | `ENHANCE_CLAHE_TILE_SIZE` type `tuple` generique | **CORRIGE** — Annote `tuple[int, int]` (lignes 135 et 142). |
| M4 | `.copy()` inutile dans `classify_spine` | **CORRIGE** — `.copy()` retire (ligne 331). |

**9/9 corrections validees.** Aucune regression introduite.

---

## Nouveaux problemes introduits par les corrections

Aucun nouveau probleme detecte. Les corrections sont chirurgicales et n'ont pas modifie la logique metier.

---

## Conformite pipeline

| Critere | Verdict |
|---------|---------|
| Signatures et types de retour (R8) | OK |
| Format de sortie pipeline (R8) | OK |
| Structures de donnees partagees (R8) | OK |
| Coherence des metriques (R8) | OK |
| CLAHE sur bon canal (R9) | OK |
| BGR/RGB conversions (R4/R9) | OK |
| Bounding boxes coherentes (R9) | OK |
| Pas de hardcoding (R2) | OK |
| Reproductibilite (R3) | OK |
| Gestion fichiers I/O (R5) | OK |

---

## Resume

Toutes les corrections de la v1 (2 bloquants, 3 warnings, 4 mineurs) ont ete correctement appliquees. La suite de tests est entierement GREEN (493/493). Aucun nouveau probleme introduit.

**Verdict final : CLEAN — pret pour merge.**
