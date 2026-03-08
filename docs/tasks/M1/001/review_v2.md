# Review v2 — Task #001 Project Structure Setup

**Branche** : task/001-project-structure-setup
**Date** : 2026-03-08
**Itération** : v2 (suite correction W-1 de la v1, commit `bf5f5fe`)

## Résultats d'exécution

| Check | Résultat |
|---|---|
| pytest | **48 passed** / 0 failed |
| ruff check | **All checks passed** |

## Vérification correction W-1 (v1)

Le W-1 de la v1 signalait l'absence de tests d'erreur et de bord. Le commit `bf5f5fe` a ajouté :

- **`TestErrorCases`** (1 test) : vérifie que l'import d'un module inexistant (`src.nonexistent_module`) lève bien `ModuleNotFoundError` via `pytest.raises`.
- **`TestEdgeCases`** (14 tests) : vérifie que les 7 fichiers source ne sont pas vides (`test_source_file_not_empty`) et contiennent une docstring de module (`test_source_file_has_docstring`).

Le commit ne modifie que `tests/test_project_structure.py` (38 lignes ajoutées) — conforme au scope de la correction.

**W-1 : RÉSOLU.**

## Scan automatisé (§GREP)

| Pattern recherché | Résultat |
|---|---|
| Fallbacks silencieux (`or []`, `or {}`, etc.) | 0 occurrences (grep exécuté) |
| Except trop large (`except:`, `except Exception:`) | 0 occurrences (grep exécuté) |
| Print résiduel (`print(`) | 0 occurrences (grep exécuté) |
| Legacy random (`np.random.seed`, `random.seed`) | 0 occurrences (grep exécuté) |
| TODO/FIXME/HACK/XXX | 0 occurrences (grep exécuté) |
| Chemins hardcodés (`/tmp`, `C:\`) | 0 occurrences (grep exécuté) |
| Mutable default arguments (`def f(x=[])`) | 0 occurrences (grep exécuté) |
| import * | 0 occurrences (grep exécuté) |
| img sans copy | 0 occurrences (N/A pour cette tâche) |
| editdistance/Levenshtein | 0 occurrences (N/A pour cette tâche) |
| BGR/RGB conversion | 0 occurrences (N/A pour cette tâche) |

## Lecture diff — Annotations par fichier

### `src/__init__.py`
- Docstring module présente (`"""ShelfScan source package."""`) — OK.

### `src/preprocess.py`, `src/segment.py`, `src/detect_text.py`, `src/ocr.py`, `src/postprocess.py`, `src/pipeline.py`
- Chaque fichier contient exactement une docstring de module descriptive — conforme.
- snake_case respecté, pas de code mort, pas d'imports inutilisés.

### `tests/test_project_structure.py`
- **L1** : docstring module présente.
- **L3-5** : imports propres (stdlib `pathlib` puis third-party `pytest`), ordre isort respecté.
- **L8** : `ROOT = Path(__file__).resolve().parent.parent` — chemin dynamique avec pathlib, pas de hardcoding.
- **L11-27** : `TestDirectoryStructure` — teste les 6 répertoires requis via parametrize.
- **L30-53** : `TestSourceFiles` — teste les 6 fichiers .py + `__init__.py` src + tests.
- **L56-84** : `TestModuleImportability` — teste l'import individuel et groupé.
- **L87-94** : `TestErrorCases` — teste l'import d'un module inexistant avec `pytest.raises(ModuleNotFoundError)`. Propre.
- **L97-122** : `TestEdgeCases` — teste fichiers non vides et présence de docstring via parametrize sur 7 fichiers. Utilise `read_text(encoding="utf-8")` (conforme §R5).
- **L125-152** : `TestRequirements` — teste existence et contenu de requirements.txt avec les 11 dépendances.

### Couverture des critères d'acceptation

| Critère | Test | Statut |
|---|---|---|
| Arborescence existe | `TestDirectoryStructure` (6 dirs) | OK |
| Fichiers .py présents | `TestSourceFiles` (6 fichiers) | OK |
| `__init__.py` existent | `test_src_init_exists`, `test_tests_init_exists` | OK |
| requirements.txt présent et complet | `TestRequirements` (11 deps) | OK |
| pip install sans erreur | Hors scope test unitaire | OK |
| Modules importables | `TestModuleImportability` (6 modules + import groupé) | OK |
| Tests nominaux + erreurs + bords | `TestErrorCases` + `TestEdgeCases` | OK |
| Suite verte | 48 passed | OK |
| ruff clean | All checks passed | OK |

## Vérification commits TDD

| Commit | Hash | Contenu | Conforme |
|---|---|---|---|
| RED | `c2f61cf` | `tests/__init__.py`, `tests/test_project_structure.py` | OK |
| GREEN | `2f429a5` | src/, data/, notebooks/, outputs/, .gitkeep, tâche mise à jour | OK |
| FIX W-1 | `bf5f5fe` | `tests/test_project_structure.py` uniquement | OK |

## BLOQUANTS (0)

Aucun.

## WARNINGS (0)

Aucun.

## MINEURS (0)

Aucun.

## Verdict

**CLEAN** — 0 bloquant, 0 warning, 0 mineur. Le W-1 de la v1 est résolu.
