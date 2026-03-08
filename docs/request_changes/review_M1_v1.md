# Request Changes — Revue globale Milestone M1

Statut : TODO
Ordre : 0001

**Date** : 2026-03-08
**Branche** : milestone/M1
**Perimetre** : Audit complet de tous les modules src/ et tests/ pour le milestone M1
**Resultat** : 164 tests GREEN, ruff clean (0 erreur)
**Verdict** : CLEAN

---

## Resultats d'execution

| Check | Resultat |
|---|---|
| `pytest tests/ -v` | **164 passed** (0.65s) |
| `ruff check src/ tests/` | **All checks passed** |
| `print()` residuel (src/) | 0 occurrences (grep execute) |
| `TODO`/`FIXME` orphelin (src/ + tests/) | 0 occurrences (grep execute) |
| Broad `except` (src/) | 0 occurrences (grep execute) |
| Fallbacks silencieux `or []`/`or {}`/`or ""`/`or 0` (src/) | 0 occurrences (grep execute) |
| `value if value else` (src/) | 0 occurrences (grep execute) |
| `np.random.seed` / `random.seed` (src/) | 0 occurrences (grep execute) |
| Chemins hardcodes `C:\\` / `/tmp` (src/ + tests/) | 0 occurrences (grep execute) |
| Mutable defaults `def f(x=[])` (src/) | 0 occurrences (grep execute) |
| `import *` (src/) | 0 occurrences (grep execute) |
| `.copy()` sur images d'entree (src/) | 8 occurrences -- toutes conformes |
| Conversions BGR/RGB (src/) | 1 occurrence dans `ocr.py` L186 (TrOCR) -- conforme |
| `editdistance` / `Levenshtein` (src/) | 0 occurrences (grep execute) -- CER non encore implemente (M2) |

---

## BLOQUANTS (0)

Aucun bloquant identifie.

---

## WARNINGS (3)

### W-1. Format des bounding boxes non uniforme entre modules

> **FAUX POSITIF M1** : Les modules ne sont pas connectes en M1. L'unification
> du format bbox est prevue lors de l'implementation de `pipeline.py` en M2.

**Fichiers** : `src/segment.py`, `src/detect_text.py`
**Regle** : R9 (bounding boxes coherentes)

`segment.py` utilise des tuples `(x1, y1, x2, y2)` pour les lignes verticales detectees, tandis que `detect_text.py` retourne des polygones a 4 points `[[x, y], [x, y], [x, y], [x, y]]` (format PaddleOCR). Ces deux formats coexistent dans le pipeline.

Pour M1 (prototype), cela ne pose pas de probleme fonctionnel car ces deux representations servent des etapes differentes. Neanmoins, lorsque `pipeline.py` sera implemente en M2, il faudra definir un format uniforme pour les bboxes a travers tout le pipeline.

**Action** : Definir et documenter un format bbox unique (recommande : `(x1, y1, x2, y2)`) lors de l'implementation de `pipeline.py` en M2. Ajouter des fonctions de conversion si necessaire.

### W-2. pipeline.py est un placeholder vide

> **FAUX POSITIF M1** : Le placeholder est explicitement prevu par la tache #001.
> L'orchestration sera implementee en M2.

**Fichiers** : `src/pipeline.py` (L1)
**Regle** : R8 (coherence intermodule)

`pipeline.py` ne contient qu'une docstring d'une ligne. Il n'orchestre aucune etape du pipeline. Ceci est acceptable pour M1 selon la spec ("placeholder OK pour M1"), mais doit etre prioritaire en M2.

**Action** : Implementer l'orchestration du pipeline en M2 (preprocess -> segment -> detect_text -> ocr -> postprocess).

### W-3. postprocess.py ne contient pas encore la logique de nettoyage OCR

> **FAUX POSITIF M1** : Le scope M1 couvre uniquement l'API search/metadata.
> Le nettoyage texte, normalisation NFC, fuzzy matching sont prevus pour M2.

**Fichiers** : `src/postprocess.py`
**Regle** : Conformite spec section 3, etape 6

Le module `postprocess.py` implemente correctement les fonctions `search_book` et `get_book_metadata` pour l'enrichissement via API bibliographique, mais il manque :
- Le nettoyage du texte brut (suppression artefacts, normalisation unicode NFC)
- Les heuristiques de separation titre / auteur
- Le fuzzy matching (rapidfuzz est dans requirements.txt mais pas utilise)

Pour M1 (test de l'API), c'est acceptable. Ces fonctionnalites sont prevues pour M2.

**Action** : Implementer le nettoyage texte, la normalisation NFC, la separation titre/auteur et le fuzzy matching en M2.

---

## MINEURS (2)

### M-1. Pas de validation ndim/dtype dans segment.py -- RESOLU

**Fichiers** : `src/segment.py` (L60-63, L124-127, L181-184)

Les fonctions `detect_vertical_lines`, `split_spines` et `segment` valident `None` et `size == 0`, mais ne verifient pas `ndim == 3` ni `dtype == uint8` comme le font `detect_text.py` et `ocr.py`. Le code fonctionne grace a `cvtColor` qui echouerait sur un mauvais format, mais la validation explicite aux frontieres est recommandee par R4.

**Action** : ~~Ajouter des assertions `image.ndim == 3` et `image.dtype == np.uint8` en entree de chaque fonction publique de `segment.py`.~~ Fait. Validation ajoutee + 6 tests dans `tests/test_segment.py`.

### M-2. Style docstring inconsistant entre modules -- RESOLU

**Fichiers** : `src/detect_text.py`, `src/postprocess.py` vs `src/preprocess.py`, `src/segment.py`, `src/ocr.py`

`preprocess.py`, `segment.py` et `ocr.py` utilisent le style numpy docstring (avec sections `Parameters`, `Returns`, `Raises`). `detect_text.py` et certaines fonctions de `postprocess.py` utilisent le style Google (`Args:`, `Returns:`, `Raises:`). Les deux styles sont valides, mais la coherence au sein du projet serait preferable.

**Action** : ~~Harmoniser le style de docstring (recommande : numpy) lors d'un refactoring futur.~~ Fait. Toutes les docstrings sont maintenant en style Google (Args/Returns/Raises) dans `preprocess.py`, `segment.py`, `ocr.py`, `postprocess.py`.

---

## Conformite pipeline (spec S3)

| Etape | Module | Implemente | Conforme | Remarques |
|---|---|---|---|---|
| Pretraitement | `src/preprocess.py` | oui | oui | Load, resize, CLAHE sur canal L (LAB). Conforme R9. |
| Segmentation | `src/segment.py` | oui | oui | Canny + HoughLinesP, crops verticaux. Parametres configures (R2). |
| Detection texte | `src/detect_text.py` | oui | oui | PaddleOCR det-only. Bboxes 4-points. Validation stricte. |
| OCR | `src/ocr.py` | oui | oui | 3 engines (PaddleOCR, TrOCR, Tesseract). compare_engines(). BGR->RGB pour TrOCR. |
| Post-traitement | `src/postprocess.py` | partiel | oui (M1) | API search/metadata OK. Nettoyage texte et fuzzy a faire en M2. |
| Pipeline | `src/pipeline.py` | placeholder | oui (M1) | Placeholder docstring uniquement. Orchestration prevue M2. |
| Evaluation | `src/eval_utils.py` | partiel | oui (M1) | load_ground_truth OK. CER/metriques a implementer en M2. |
| Interface | `src/app.py` | scaffold | oui (M1) | Streamlit minimal : upload + affichage image. Pipeline a integrer M2. |

---

## Conformite plan -> code

| WS | Taches DONE | Module(s) code | Code present | Tests presents |
|---|---|---|---|---|
| WS1 | #001, #002, #003 | `src/preprocess.py`, `src/segment.py` | oui | oui (test_preprocess.py, test_segment.py) |
| WS2 | #004 | `src/detect_text.py` | oui | oui (test_detect_text.py) |
| WS3 | #005 | `src/ocr.py` | oui | oui (test_ocr.py) |
| WS4 | #006, #007 | `src/postprocess.py`, `src/app.py` | oui | oui (test_postprocess.py, test_app.py) |
| WS5 | #008 | `src/eval_utils.py` | oui | oui (test_eval_utils.py) |

Toutes les 8 taches M1 sont marquees DONE et ont du code + tests correspondants.

---

## Audit des regles non negociables

| Regle | Statut | Detail |
|---|---|---|
| R1 -- Strict code | CONFORME | Aucun fallback silencieux. Validation explicite (raise ValueError/FileNotFoundError) dans tous les modules. |
| R2 -- Pas de hardcoding | CONFORME | Seuils Canny/Hough en parametres. Constantes nommees (MIN_GAP_PX, DEFAULT_DET_CONFIDENCE, TROCR_MODEL_NAME, etc.). URLs API en constantes de module. |
| R3 -- Reproductibilite | CONFORME | Pas de legacy random API. Tests utilisent `np.random.default_rng(42)`. |
| R4 -- Conventions image | CONFORME | `.copy()` sur toutes les images d'entree. CLAHE sur canal L (LAB). BGR->RGB explicite avant TrOCR. |
| R5 -- Gestion fichiers | CONFORME | Chemins via `pathlib.Path`. Validation des fichiers dans `load_image`. |
| R6 -- Anti-patterns | CONFORME | Pas de mutable defaults. Pas de boucles Python sur arrays numpy (sauf parsing de resultats OCR -- acceptable). |
| R7 -- Qualite code | CONFORME | Pas de print(), pas de TODO/FIXME, imports propres, snake_case coherent. |
| R8 -- Coherence inter | CONFORME (M1) | Interfaces compatibles entre modules adjacents. Pipeline placeholder acceptable pour M1. |
| R9 -- CV/OCR | CONFORME (M1) | CLAHE sur L (LAB). CER non encore implemente (prevu M2). Format bboxes a unifier en M2 (W-1). |

---

## Resume des actions

| # | Severite | Action | Fichier(s) |
|---|---|---|---|
| W-1 | WARNING | Unifier le format bbox (x1,y1,x2,y2) lors de l'implementation pipeline M2 | `src/segment.py`, `src/detect_text.py` |
| W-2 | WARNING | Implementer l'orchestration dans pipeline.py en M2 | `src/pipeline.py` |
| W-3 | WARNING | Ajouter nettoyage texte, normalisation NFC, fuzzy matching en M2 | `src/postprocess.py` |
| M-1 | MINEUR | ~~Ajouter validation ndim/dtype dans segment.py~~ **RESOLU** | `src/segment.py` |
| M-2 | MINEUR | ~~Harmoniser le style de docstring~~ **RESOLU** (style Google partout) | `src/preprocess.py`, `src/segment.py`, `src/ocr.py`, `src/postprocess.py` |
