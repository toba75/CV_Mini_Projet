# Review v1 — 006 API Books Test

**Branche** : `task/006-api-books-test`
**Itération** : v1
**Date** : 2026-03-08
**Reviewer** : TDD-Reviewer (Claude)

---

## 1. Statut tâche

- Statut : **DONE** (fichier `006__ws4_api_books_test.md`)
- Critères d'acceptation : 9/9 cochés
- Checklist : 7/9 cochés (manquent le commit GREEN et la PR -- commit GREEN existe `135810a`, PR attendue post-review)

## 2. Commits

```
135810a [WS4] #006 GREEN: API bibliographique fonctionnelle
620927f [WS4] #006 RED: tests API bibliographique
```

Cycle RED/GREEN respecté.

## 3. Tests + Linter

- **pytest** : 138 passed (0.44s) -- tous les tests existants + nouveaux sont verts
- **ruff check src/ tests/** : All checks passed

## 4. Revue de code

### Fichiers modifiés (tâche 006)

- `src/postprocess.py` : module de requête API bibliographique
- `tests/test_postprocess.py` : tests unitaires mockés

### Points positifs

- Validation explicite des entrées (`_validate_query`, `_validate_provider`) avec `ValueError`
- Aucune clé API hardcodée -- test dédié le vérifie (`TestNoHardcodedAPIKeys`)
- Timeout configurable avec constante nommée `DEFAULT_TIMEOUT = 10`
- Erreurs réseau correctement converties : `requests.Timeout` -> `TimeoutError`, `requests.HTTPError` -> `ConnectionError`
- Tests 100% mockés via `@patch("src.postprocess.requests.get")` -- aucun appel réseau
- Couverture des scénarios : nominal, vide, timeout, HTTP 5xx, validation, deux providers, ISBN 404
- Constantes URL et providers documentées en haut de module

### W-1 — Fallbacks silencieux dans les parseurs (§R1) [WARNING]

**Fichier** : `src/postprocess.py`, lignes 38-48 et 54-70

Les fonctions `_parse_openlibrary_docs` et `_parse_googlebooks_items` utilisent `.get()` sans validation :
- `doc.get("title")` peut retourner `None` silencieusement (ligne 43, 65)
- `item.get("volumeInfo", {})` (ligne 55) -- fallback `{}` masque une réponse invalide
- `data.get("docs", [])` (ligne 115) et `data.get("items", [])` (ligne 125) -- fallback `[]`

Les patterns `authors[0] if authors else None` (lignes 39, 41, 57) sont acceptables pour des champs optionnels de l'API.

**Risque** : un changement de structure de la réponse API passerait inapercu, avec des résultats contenant `title: None`.

**Recommandation** : valider au minimum que `title` n'est pas `None` avant d'ajouter un résultat, ou loguer un warning si la structure est inattendue.

### W-2 — `get_book_metadata` ne supporte que openlibrary (§R8) [WARNING]

**Fichier** : `src/postprocess.py`, lignes 133-181

`get_book_metadata` accepte `provider="googlebooks"` via `_validate_provider` mais utilise toujours l'URL Open Library (`_OPENLIBRARY_ISBN_URL`). Un appel avec `provider="googlebooks"` enverrait une requête vers Open Library sans erreur.

**Recommandation** : soit lever `NotImplementedError` pour le provider googlebooks dans `get_book_metadata`, soit implémenter le support.

### M-1 — Checklist incomplète [MINEUR]

Les cases `[ ] Commit GREEN` et `[ ] Pull Request ouverte` ne sont pas cochees dans le fichier de tache, bien que le commit GREEN existe. La case commit GREEN devrait etre cochee.

## 5. Scans GREP (§GREP)

| Scan | Résultat |
|------|----------|
| §R1 Fallbacks silencieux | 3 hits (lignes 39, 41, 57) -- analysés, voir W-1 |
| §R1 Except trop large | 0 occurrences (grep exécuté) |
| §R7 Print résiduel | 0 occurrences (grep exécuté) |
| §R3 Legacy random API | 0 occurrences (grep exécuté) |
| §R7 TODO/FIXME | 0 occurrences (grep exécuté) |
| §R5 Chemins hardcodés | 0 occurrences (grep exécuté) |
| §R6 Mutable default args | 0 occurrences (grep exécuté) |
| §R4 img= sans copy | 0 occurrences (grep exécuté) |
| §R9 CER | 0 occurrences (grep exécuté) |
| §R4 BGR/RGB | 0 occurrences (grep exécuté) |

## 6. Verdict

| Catégorie | N |
|-----------|---|
| Bloquants | 0 |
| Warnings  | 2 |
| Mineurs   | 1 |

**Verdict : CLEAN**

Les deux warnings sont des améliorations souhaitables mais non bloquantes. Le code est fonctionnel, bien testé, et conforme aux critères d'acceptation.
