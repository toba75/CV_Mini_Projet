# Review v1 — 005 Comparaison modèles OCR

**Branche** : `task/005-ocr-models-comparison`
**Itération** : v1
**Date** : 2026-03-08
**Verdict** : **REQUEST CHANGES**

---

## 1. Checklist tâche

| Critère | Statut |
|---------|--------|
| Statut DONE | OK |
| Critères d'acceptation cochés | OK (10/10) |
| Checklist fin de tâche | PARTIEL — lignes 58-59 non cochées (commit GREEN + PR) |

---

## 2. Commits RED/GREEN

| Commit | Hash | Contenu |
|--------|------|---------|
| RED | `1af1214` | `tests/test_ocr.py` uniquement (205 lignes ajoutées) |
| GREEN | `c961381` | `src/ocr.py` (232 lignes) + mise à jour tâche |

Cycle TDD respecté : RED avant GREEN, tests dans un commit séparé de l'implémentation.

---

## 3. Tests et linter

- **pytest** : 123 tests passés (dont 16 pour `test_ocr.py`), 0 failures.
- **ruff check** : `All checks passed!`

---

## 4. Revue de code

### 4.1 `src/ocr.py`

**Validation (§R1)** : `_validate_image` lève `ValueError` pour None, empty, ndim != 3, dtype != uint8. Strict, pas de fallback sur la validation.

**Conventions image (§R4)** :
- Entrée BGR documentée. `.copy()` appelé dans `recognize_text` (ligne 131).
- `_recognize_trocr` : conversion explicite BGR -> RGB via `cv2.cvtColor` (ligne 177). Correct.
- `_recognize_tesseract` : conversion explicite BGR -> GRAY via `cv2.cvtColor` (ligne 191). Correct.
- `_recognize_paddle` : PaddleOCR accepte BGR nativement, pas de conversion nécessaire. Correct.

**Interface unifiée** : `recognize_text` retourne toujours `list[dict[str, object]]` avec clés `"text"` et `"confidence"`. Conforme.

**Constantes** :
- `SUPPORTED_ENGINES` : tuple nommé. OK.
- `TROCR_MODEL_NAME` : constante configurable. OK (§R2).
- `TESSERACT_MIN_CONF` : constante nommée. OK.

**Imports** : lazy imports avec patch targets déclarés au niveau module. Propre.

### 4.2 `tests/test_ocr.py`

**Mocks** : tous les tests sont mockés, aucune dépendance réseau ou modèle lourd. Déterministes.

**Couverture** :
- `init_ocr_engine` : 3 moteurs + erreur. OK.
- `recognize_text` : Paddle, TrOCR, Tesseract, None image, empty image, 1x1 image. OK.
- `compare_engines` : dict keys, résultats par moteur, None image, empty image. OK.

**`default_rng(42)`** utilisé dans `_make_image`. Reproductible (§R3). OK.

---

## 5. Problèmes identifiés

### W-1 — Fallback silencieux dans `_recognize_paddle` (§R1) — WARNING

**Fichier** : `src/ocr.py`, lignes 159 et 162.

```python
if result is None:
    return results
...
if line_group is None:
    continue
```

PaddleOCR retourne `None` quand il ne détecte rien. Ce comportement est documenté dans l'API PaddleOCR et retourner une liste vide est sémantiquement correct (pas de texte trouvé). Cependant, cela crée un fallback silencieux qui masquerait un vrai problème (moteur mal initialisé, crash interne).

**Recommandation** : ajouter un `logging.debug` pour tracer le cas `result is None` afin de distinguer "pas de texte" de "erreur silencieuse".

### W-2 — Pas de test `test_original_image_not_modified` (§R4) — WARNING

**Fichier** : `tests/test_ocr.py`.

Le code fait `.copy()` dans `recognize_text` (ligne 131), ce qui est correct. Cependant, aucun test ne vérifie que l'image d'entrée n'est pas modifiée. Les tâches 003 et 004 avaient ce test.

**Recommandation** : ajouter un test qui vérifie `np.array_equal(image_before, image_after)` après appel à `recognize_text`.

### M-1 — Confiance TrOCR hardcodée à 1.0 (§R2) — MINEUR

**Fichier** : `src/ocr.py`, ligne 184.

```python
results.append({"text": str(text), "confidence": 1.0})
```

Le commentaire ligne 183 documente que TrOCR ne fournit pas de confiance. La valeur `1.0` est un placeholder raisonnable, mais elle devrait idéalement être une constante nommée (ex : `TROCR_DEFAULT_CONFIDENCE = 1.0`) pour être cohérent avec `TESSERACT_MIN_CONF`.

### M-2 — Checklist fin de tâche incomplète — MINEUR

**Fichier** : `docs/tasks/M1/005__ws3_ocr_models_comparison.md`, lignes 58-59.

Les items "Commit GREEN" et "Pull Request ouverte" ne sont pas cochés alors que le commit GREEN existe (`c961381`). L'item commit GREEN devrait etre coché.

---

## 6. Scans GREP (§GREP)

| Scan | Résultat |
|------|----------|
| §R1 — Fallbacks silencieux (`or []`, etc.) | 0 occurrences (grep exécuté) |
| §R1 — Except trop large | 0 occurrences (grep exécuté) |
| §R7 — Print résiduel | 0 occurrences (grep exécuté) |
| §R3 — Legacy random API | 0 occurrences (grep exécuté) |
| §R7 — TODO/FIXME | 0 occurrences (grep exécuté) |
| §R5 — Chemins hardcodés | 0 occurrences (grep exécuté) |
| §R6 — Mutable default args | 0 occurrences (grep exécuté) |
| §R4 — img= sans copy | 0 occurrences (grep exécuté) |
| §R9 — CER sans normalisation | 0 occurrences (grep exécuté) |
| §R4 — BGR/RGB conversion | 1 occurrence : ligne 177 `COLOR_BGR2RGB` — **faux positif**, conversion correcte pour TrOCR |

---

## 7. Résumé

| Catégorie | # | Détails |
|-----------|---|---------|
| Bloquants | 0 | — |
| Warnings | 2 | W-1 fallback silencieux Paddle, W-2 test no-modify manquant |
| Mineurs | 2 | M-1 constante TrOCR confidence, M-2 checklist incomplète |

---

## 8. Actions requises pour v2

1. **W-1** : ajouter un `logging.debug` quand PaddleOCR retourne `None` dans `_recognize_paddle`.
2. **W-2** : ajouter un test `test_original_image_not_modified` dans `TestRecognizeText`.
3. **M-1** : extraire `1.0` en constante `TROCR_DEFAULT_CONFIDENCE`.
4. **M-2** : cocher la case "Commit GREEN" dans la checklist de la tâche.
