# Revue globale — Milestone M4 (ShelfScan)

**Branche** : `milestone/M4`
**Date** : 2026-03-10
**Verdict** : **REQUEST CHANGES**

---

## Résumé

Le milestone M4 est globalement bien exécuté : 586 tests passent, ruff est propre, le code source est structuré et documenté. Le pipeline respecte les conventions image (BGR/RGB, `.copy()`, `pathlib.Path`), le CER est calculé correctement, et les modules s'enchaînent de manière cohérente. Les principales préoccupations sont : (1) les images de démo sont des placeholders synthétiques de 2.6KB, non des photos réelles comme requis par la tâche 031, (2) une dépendance morte `editdistance` dans `requirements.txt`, et (3) un fallback silencieux dans `eval_utils.py`.

---

## Résultats CI

| Outil | Résultat |
|-------|---------|
| `pytest tests/ -v` | **586 passed**, 0 failed (4.36s) |
| `ruff check src/ tests/` | **All checks passed** |

---

## Scans automatisés (§GREP)

| Règle | Scan | Résultat |
|-------|------|----------|
| §R1 — Fallbacks `or []`, `or {}`, etc. | `Select-String -Pattern ' or \[\]\| or \{\}'` | 0 occurrences réelles (tous faux positifs contextuels, détail ci-dessous) |
| §R1 — `except:` / `except Exception:` | `Select-String -Pattern 'except:$\|except Exception:'` | 2 occurrences (`pipeline.py:104`, `demo_benchmark.py:73`) — justifiées par la résilience du pipeline |
| §R7 — `print()` dans src/ | `Select-String -Pattern 'print\('` | **0 occurrences** ✅ |
| §R3 — Legacy random (`np.random.seed`) | `Select-String -Pattern 'np\.random\.seed\|random\.seed'` | **0 occurrences** ✅ — tous les tests utilisent `np.random.default_rng(42)` |
| §R7 — TODO/FIXME/HACK/XXX | `Select-String -Pattern 'TODO\|FIXME\|HACK\|XXX'` | 0 dans src/, occurrences dans tests uniquement dans `test_code_cleanup.py` (qui teste leur absence) ✅ |
| §R6 — Mutable default arguments | `Select-String -Pattern 'def .*=\[\]\|def .*=\{\}'` | **0 occurrences** ✅ |
| §R5 — Chemins hardcodés tests | `Select-String -Pattern '/tmp\|C:\\'` | **0 occurrences** ✅ |
| §R4 — `.copy()` sur images | `Select-String -Pattern '\.copy\(\)'` | 17+ occurrences dans src/ — copie systématique ✅ |
| §R4 — BGR/RGB conversion | `Select-String -Pattern 'COLOR_BGR2RGB'` | `ocr.py:180` (avant TrOCR), `visualization.py:187` (avant affichage) ✅ |
| §R5 — `pathlib.Path` | `Select-String -Pattern 'pathlib\|Path\('` | Utilisé dans tous les modules ✅ |
| §R5 — `os.path.join` | `Select-String -Pattern 'os\.path\.'` | **0 occurrences** ✅ |
| §R9 — Levenshtein/CER | `Select-String -Pattern 'Levenshtein'` | `eval_utils.py:8,73` — normalise par `len(ground_truth_text)` ✅ |
| §R6 — `open()` sans `with` | Scan `open(` dans src/ | Tous avec `with` ou `Path.read_text()`/`Path.write_text()` ✅ |

### Détail des faux positifs §R1

Les occurrences `if ... else` détectées par le scan sont toutes contextuellement correctes :

- `detect_text.py:149` — Type dispatch sur structure PaddleOCR (pas un fallback)
- `detect_text.py:199` — Guard against div-by-zero (`avg_height > 0 else 1.0`)
- `eval_utils.py:72` — Edge case CER (ground truth vide)
- `eval.py:169-170` — Ternaire d'affichage (✓/✗)
- `postprocess.py:59` — Classification de caractère Unicode
- `postprocess.py:114,151,153,173` — Parsing de réponses API externes (frontière système)
- `pipeline.py:179` — CLI `__main__` default (`"outputs"`) → voir M-1

---

## Tableau de conformité pipeline

| Module | Entrée | Sortie | Validation frontière | `.copy()` | BGR/RGB | Cohérence |
|--------|--------|--------|---------------------|-----------|---------|-----------|
| `preprocess.py` | `str` (chemin) | `np.ndarray` BGR uint8 | `validate_image` + `FileNotFoundError` | ✅ | CLAHE sur canal L (LAB) ✅ | ✅ |
| `segment.py` | `np.ndarray` BGR | `list[np.ndarray]` BGR | `validate_image` | ✅ | N/A | ✅ |
| `detect_text.py` | `np.ndarray` BGR | `list[dict]` bbox+confidence | `validate_image` | ✅ | N/A (PaddleOCR reçoit BGR) | ✅ |
| `ocr.py` | `np.ndarray` BGR | `list[dict]` text+confidence | `validate_image` | ✅ | BGR→RGB avant TrOCR ✅ | ✅ |
| `postprocess.py` | `list[str]` | `dict` title/author | Validation query/provider | N/A | N/A | ✅ |
| `pipeline.py` | `str\|Path` | `dict` JSON-sérialisable | `FileNotFoundError` + extension check | ✅ (via modules) | ✅ (via modules) | ✅ |
| `eval_utils.py` | CSV + JSON | `dict` métriques | `load_ground_truth` validation | N/A | N/A | ✅ |
| `visualization.py` | `np.ndarray` BGR | `np.ndarray` BGR/RGB | `validate_image` | ✅ | `bgr_to_rgb()` explicite ✅ | ✅ |

---

## BLOQUANTS

*Aucun bloquant identifié.*

---

## WARNINGS

### W-1 — Images de démo synthétiques (non conformes tâche 031)

- **Fichier(s)** : `data/demo/shelf_demo_01.png`, `shelf_demo_02.png`, `shelf_demo_03.png`
- **Description** : Les 3 images de démo font chacune 2 602 octets. Le fichier `expected_results.json` les décrit explicitement comme *"Synthetic demo shelf image — solid color placeholder for pipeline testing"*. La tâche 031 exige : *"Les images de démo doivent être des photos réelles (pas synthétiques)"* et *"Chaque image doit produire au minimum 3 livres correctement identifiés"*. Des placeholders unicolores ne peuvent pas produire de résultats OCR réels. Les tests de benchmark (`test_demo_images.py`) contournent le problème en mockant `run_pipeline`, ce qui ne vérifie pas la performance réelle.
- **Impact** : La démo live en soutenance ne fonctionnera pas avec ces images. Le critère "pipeline < 30s sur des images réelles" n'est pas validé.
- **Action corrective** : Remplacer les 3 placeholders par des photos réelles d'étagères (>100KB chacune, format JPEG ou PNG). Mettre à jour `expected_results.json` avec les résultats réellement produits par le pipeline. Ajouter un test d'intégration non-mocké vérifiant la performance sur au moins une image réelle.

### W-2 — Fallback silencieux dans `evaluate_dataset`

- **Fichier(s)** : `src/eval_utils.py` (lignes 162-168)
- **Description** : La fonction `evaluate_dataset` capture `ValueError` levée par `load_ground_truth` et retourne silencieusement un résultat vide (métriques à 0.0) au lieu de propager l'erreur. C'est un fallback silencieux (§R1) : si le CSV de ground truth est malformé, l'évaluation retourne des zéros sans signaler de problème.
- **Impact** : Masque les erreurs de données d'évaluation. Un ground truth corrompu passe inaperçu.
- **Action corrective** : Propager le `ValueError` de `load_ground_truth` plutôt que de le capturer, ou au minimum logger un warning. Même traitement pour le cas `csv_files` vide (lignes 158-162) qui pourrait lever une `ValueError`.

### W-3 — Dépendance morte `editdistance` dans `requirements.txt`

- **Fichier(s)** : `requirements.txt` (ligne 25), `pyproject.toml` (ligne 27)
- **Description** : Le package `editdistance>=0.6,<1` est listé dans les dépendances mais n'est jamais importé dans le code source. Le CER est calculé via `rapidfuzz.distance.Levenshtein` (dans `eval_utils.py`). C'est une dépendance fantôme qui alourdit l'installation inutilement.
- **Impact** : Dépendance inutile installée. Confusion potentielle sur la bibliothèque réellement utilisée.
- **Action corrective** : Supprimer `editdistance>=0.6,<1` de `requirements.txt` et `pyproject.toml`.

---

## MINEURS

### M-1 — README : stack technique mentionne `editdistance` au lieu de `rapidfuzz`

- **Fichier(s)** : `README.md` (section Stack technique)
- **Description** : Le tableau Stack technique indique *"Évaluation : editdistance (CER), métriques custom"*. Mais le code utilise `rapidfuzz.distance.Levenshtein` pour le calcul du CER.
- **Impact** : Incohérence documentation/code. Pourrait induire en erreur lors de la soutenance.
- **Action corrective** : Remplacer `editdistance (CER)` par `rapidfuzz (CER via Levenshtein)` dans le tableau Stack technique du README.

### M-2 — `pipeline.py` : chemin de sortie par défaut hardcodé dans `__main__`

- **Fichier(s)** : `src/pipeline.py` (ligne 179)
- **Description** : Le bloc `__main__` utilise `sys.argv[2] if len(sys.argv) > 2 else "outputs"`. La chaîne `"outputs"` est un chemin hardcodé sans constante nommée. Bien que ce soit acceptable pour un point d'entrée CLI, cela viole légèrement §R2 (pas de hardcoding).
- **Impact** : Faible. Fonctionnel mais pas conforme à la convention de nommage des constantes.
- **Action corrective** : Extraire `"outputs"` en constante nommée `DEFAULT_OUTPUT_DIR = "outputs"`.

### M-3 — `expected_results.json` : titres de livres fictifs

- **Fichier(s)** : `data/demo/expected_results.json`
- **Description** : Les titres attendus sont génériques (*"Demo Book A1"*, *"Demo Book B2"*, etc.). Même après remplacement des images par des photos réelles (W-1), ce fichier devra être mis à jour avec les vrais titres identifiés par le pipeline.
- **Impact** : Lié à W-1. Les résultats attendus ne correspondent à aucune donnée réelle.
- **Action corrective** : Mettre à jour les titres en parallèle de W-1 pour refléter les livres réellement présents sur les photos de démo.

---

## Résumé des actions

| ID | Sévérité | Action |
|----|----------|--------|
| W-1 | WARNING | Remplacer les images de démo synthétiques par des photos réelles d'étagères |
| W-2 | WARNING | Propager (ou logger) le `ValueError` dans `eval_utils.evaluate_dataset` au lieu de retourner silencieusement des zéros |
| W-3 | WARNING | Supprimer la dépendance `editdistance` de `requirements.txt` et `pyproject.toml` |
| M-1 | MINEUR | Corriger la mention `editdistance` → `rapidfuzz` dans le README |
| M-2 | MINEUR | Extraire le chemin `"outputs"` en constante nommée dans `pipeline.py` |
| M-3 | MINEUR | Mettre à jour les titres fictifs dans `expected_results.json` |

---

## Verdict

- **Bloquants** : 0
- **Warnings** : 3
- **Mineurs** : 3
- **Verdict** : **REQUEST CHANGES**

Le code source est propre, les tests passent, les conventions sont respectées. Les warnings sont tous corrigeables rapidement. L'action la plus importante est W-1 (images de démo réelles) car elle impacte directement la soutenance.
