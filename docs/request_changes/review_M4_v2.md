# Revue globale v2 — Milestone M4 (ShelfScan)

**Branche** : `milestone/M4`
**Date** : 2026-03-10
**Itération** : 2 (suite corrections v1)
**Verdict** : **CLEAN**

---

## Résumé

Toutes les corrections demandées en v1 (W-2, W-3, M-1, M-2) sont correctement implémentées. Aucune régression introduite. Les 586 tests passent, ruff est propre. Les items W-1 et M-3 (images de démo réelles) restent non corrigés comme convenu (hors portée automatisation). Aucun nouveau problème détecté.

---

## Résultats CI

| Outil | Résultat |
|-------|---------|
| `pytest tests/ -v --tb=short` | **586 passed**, 0 failed (4.28s) |
| `ruff check src/ tests/` | **All checks passed** |

---

## Vérification des corrections v1

### W-2 — `eval_utils.evaluate_dataset` : fallback silencieux → ✅ CORRIGÉ

- **Avant** : `try/except ValueError` capturait l'erreur et retournait des métriques à 0.
- **Après** : `ValueError` est levée directement si aucun CSV trouvé (lignes 158-160). Plus aucun `try/except` dans `eval_utils.py` (vérifié par grep). `load_ground_truth` propage naturellement ses erreurs.
- **Preuve** : `Select-String -Path src\eval_utils.py -Pattern 'try:|except'` → 0 occurrences.

### W-3 — Dépendance morte `editdistance` → ✅ CORRIGÉ

- **Avant** : `editdistance>=0.6,<1` dans `requirements.txt` et `pyproject.toml`.
- **Après** : Supprimé des deux fichiers.
- **Preuve** : `Select-String -Path requirements.txt,pyproject.toml -Pattern 'editdistance'` → 0 occurrences.

### M-1 — README mentionne `editdistance` → ✅ CORRIGÉ

- **Avant** : *"Évaluation : editdistance (CER), métriques custom"*.
- **Après** : *"Évaluation : rapidfuzz (CER via Levenshtein), métriques custom"* (README.md ligne 56).
- **Preuve** : `Select-String -Path README.md -Pattern 'rapidfuzz'` → 1 match confirmé.

### M-2 — Chemin `"outputs"` hardcodé dans `pipeline.py` → ✅ CORRIGÉ

- **Avant** : `sys.argv[2] if len(sys.argv) > 2 else "outputs"`.
- **Après** : Constante `_DEFAULT_OUTPUT_DIR = "outputs"` (ligne 19), utilisée ligne 181.
- **Preuve** : `Select-String -Path src\pipeline.py -Pattern '_DEFAULT_OUTPUT_DIR'` → 2 matches (définition + usage).

### W-1 — Images de démo synthétiques → NON CORRIGÉ (attendu)

Nécessite des photos réelles manuelles, hors portée de l'automatisation. Non re-signalé.

### M-3 — Titres fictifs dans `expected_results.json` → NON CORRIGÉ (attendu)

Lié à W-1. Non re-signalé.

---

## Scans automatisés (§GREP)

| Règle | Scan | Résultat |
|-------|------|----------|
| §R1 — Fallbacks `or []`, `or {}`, etc. | `Select-String -Pattern 'or \[\]\|or \{\}'` | 0 occurrences dans src/ ✅ |
| §R1 — `if ... else` (ternaires) | `Select-String -Pattern 'if .* else'` | 11 occurrences — tous faux positifs contextuels (identiques à v1) ✅ |
| §R1 — `except:` / `except Exception:` | `Select-String -Pattern 'except\s*:\|except\s+Exception'` | 2 occurrences : `pipeline.py:106` (résilience pipeline), `demo_benchmark.py:73` (benchmark robuste) — justifiées ✅ |
| §R7 — `print()` dans src/ | `Select-String -Pattern 'print\('` | **0 occurrences** ✅ |
| §R3 — Legacy random (`np.random.seed`) | `Select-String` sur src/ + tests/ | **0 occurrences** ✅ |
| §R7 — TODO/FIXME/HACK/XXX | `Select-String` sur src/ | **0 occurrences** ✅ |
| §R6 — Mutable default arguments | `Select-String -Pattern 'def .*=\[\]\|def .*=\{\}'` | **0 occurrences** ✅ |
| §R5 — Chemins hardcodés tests (`/tmp`, `C:\`) | `Select-String` sur tests/ | **0 occurrences** ✅ |
| §R4 — `.copy()` sur images | `Select-String -Pattern '\.copy\(\)'` | 17 occurrences dans src/ — copie systématique ✅ |
| §R4 — BGR/RGB conversion | `Select-String -Pattern 'COLOR_BGR2RGB'` | `ocr.py:180` (avant TrOCR), `visualization.py:187` (avant affichage) ✅ |
| §R5 — `pathlib.Path` | `Select-String -Pattern 'pathlib\|Path\('` | 27 occurrences dans src/ ✅ |
| §R5 — `os.path.join` | `Select-String -Pattern 'os\.path\.'` | **0 occurrences** ✅ |
| §R9 — `editdistance` dans src/ | `Select-String -Pattern 'editdistance'` | **0 occurrences** ✅ |
| §R9 — Levenshtein/CER | `Select-String -Pattern 'Levenshtein'` | `eval_utils.py` — normalise par `len(ground_truth_text)` ✅ |
| §R6 — `open()` sans `with` | Scan `open(` dans src/ | 1 occurrence (`app.py:159` — `Image.open(io.BytesIO(...))`) — pattern PIL standard, BytesIO in-memory, pas un fichier ✅ |
| §R7 — Code mort / blocs commentés | `Select-String -Pattern '^\s*#\s*(def \|class \|return )'` | **0 occurrences** ✅ |

---

## BLOQUANTS

*Aucun.*

---

## WARNINGS

*Aucun nouveau warning.*

---

## MINEURS

*Aucun nouveau mineur.*

---

## Verdict

- **Bloquants** : 0
- **Warnings** : 0 (nouveaux)
- **Mineurs** : 0 (nouveaux)
- **Verdict** : **CLEAN**

Les 4 corrections applicables de v1 sont toutes vérifiées. Aucune régression, aucun nouveau problème. Le code est prêt pour merge, sous réserve de la note W-1/M-3 (images de démo réelles à fournir manuellement avant soutenance).
