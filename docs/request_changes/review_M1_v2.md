# Revue globale Milestone M1 -- v2

Statut : TODO
Ordre : 0002

**Date** : 2026-03-08
**Branche** : milestone/M1
**Iteration** : v2 (apres corrections 26c3da1)
**Perimetre** : Re-audit complet src/ et tests/ apres corrections M-1 et M-2
**Resultat** : 170 tests GREEN, ruff clean (0 erreur)
**Verdict** : **APPROVE**

---

## Resultats d'execution

| Check | Resultat |
|---|---|
| `pytest tests/ -v` | **170 passed** (0.65s) |
| `ruff check src/ tests/` | **All checks passed** |
| `print()` residuel (src/) | 0 occurrences |
| `TODO`/`FIXME` orphelin (src/) | 0 occurrences |
| Broad `except` (src/) | 0 occurrences |
| Fallbacks silencieux `or []`/`or {}` (src/) | 0 occurrences |
| Mutable defaults `def f(x=[])` (src/) | 0 occurrences |

---

## Verification des corrections v1

### M-1. Validation ndim/dtype dans segment.py -- RESOLU

**Commit** : 26c3da1
**Verification** : `segment.py` valide desormais `image.ndim != 3` et `image.dtype != np.uint8` dans les 3 fonctions publiques :
- `detect_vertical_lines` (L55, L59-60)
- `split_spines` (L116, L120-121)
- `segment` (L173, L177-178)

Les 6 tests correspondants (`test_2d_image_raises`, `test_wrong_dtype_raises` pour chaque fonction) passent tous.

**Statut** : CONFIRME RESOLU

### M-2. Docstrings en style Google -- RESOLU

**Commit** : 26c3da1
**Verification** :
- 0 occurrences de style reST (`:param`, `:returns:`, `:rtype:`, `:raises`) dans src/
- 42 occurrences de sections Google (`Args:`, `Returns:`, `Raises:`) reparties sur 6 modules
- Modules couverts : `preprocess.py`, `segment.py`, `ocr.py`, `postprocess.py`, `detect_text.py`, `eval_utils.py`

**Statut** : CONFIRME RESOLU

---

## Regressions introduites par les corrections

Aucune regression detectee :
- +6 tests (164 -> 170), tous passent
- Ruff toujours clean
- Aucun nouveau print(), TODO, broad except, fallback silencieux ou mutable default

---

## BLOQUANTS (0)

Aucun bloquant identifie.

---

## WARNINGS (3) -- inchanges depuis v1

Les 3 warnings identifies en v1 restent valides. Ils sont tous des faux positifs M1 (travail prevu pour M2) et ne bloquent pas l'approbation du milestone.

| # | Warning | Scope | Action prevue |
|---|---|---|---|
| W-1 | Format bounding boxes non uniforme (tuples vs polygones) | `segment.py`, `detect_text.py` | Unifier en M2 lors de l'implementation de `pipeline.py` |
| W-2 | `pipeline.py` est un placeholder vide | `pipeline.py` | Implementer l'orchestration en M2 |
| W-3 | `postprocess.py` sans nettoyage OCR ni fuzzy matching | `postprocess.py` | Ajouter nettoyage texte, NFC, fuzzy en M2 |

---

## MINEURS (0)

Les 2 mineurs de v1 ont ete corriges dans 26c3da1 et confirmes resolus ci-dessus.

---

## Compteurs

| Severite | v1 | v2 | Delta |
|---|---|---|---|
| Bloquant | 0 | 0 | = |
| Warning | 3 (faux positifs M1) | 3 (inchanges) | = |
| Mineur | 2 | **0** | -2 |
| Tests | 164 passed | **170 passed** | +6 |
| Ruff | clean | clean | = |

---

## Verdict final

**APPROVE** -- Milestone M1 est complet et conforme.

- 170/170 tests passent
- 0 erreur ruff
- 0 bloquant, 0 mineur
- 3 warnings acceptes (faux positifs pour M1, actions planifiees M2)
- Les 8 taches M1 sont DONE avec code + tests correspondants
- Les 2 corrections demandees en v1 sont confirmees resolues
