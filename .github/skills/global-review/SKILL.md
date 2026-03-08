---
name: global-review
description: Revue de code globale du projet ShelfScan. Audite la cohérence inter-modules du pipeline, la conformité spec, les conventions image/OCR, la qualité et produit un rapport structuré. À utiliser quand l'utilisateur demande « revue globale », « audit du code », « revue de la branche ».
argument-hint: "[branche: main ou nom de branche] [scope: all|src|tests|pipeline|ocr]"
---

# Agent Skill — Global Review (ShelfScan)

## Objectif
Effectuer un audit de code complet et transversal, en évaluant la **cohérence globale** entre tous les modules du pipeline ShelfScan, la conformité aux specs, les conventions et la qualité. Produire un rapport structuré dans `docs/request_changes/NNNN_slug.md`.

## Contexte repo

- **Spécification** : `docs/specifications/specifications.md`
- **Plan** : `docs/plan/implementation_plan.md` (WS1..WS5, M1..M4)
- **Code source** : `src/` (preprocess.py, segment.py, detect_text.py, ocr.py, postprocess.py, pipeline.py)
- **Tests** : `tests/` (pytest)
- **Request changes précédentes** : `docs/request_changes/NNNN_slug.md`

## Workflow de revue globale

### 1. Établir le périmètre

```bash
find src/ -name "*.py" -not -path "*__pycache__*"
find tests/ -name "*.py" -not -path "*__pycache__*"
```

### 2. Exécuter la suite de validation

```bash
pytest tests/ -v --tb=short
ruff check src/ tests/
```

Résultats attendus : **tous tests GREEN**, **ruff clean**.

### 3. Audit des interfaces inter-modules

Le pipeline ShelfScan est séquentiel : `preprocess.py` → `segment.py` → `detect_text.py` → `ocr.py` → `postprocess.py` → `pipeline.py`.

Pour chaque interface entre modules :

#### 3a. Contrat de données
- [ ] Les types numpy/OpenCV produits par le module N sont-ils ceux attendus par le module N+1 ?
- [ ] Le format des bounding boxes est-il uniforme (ex : `(x, y, w, h)` ou `(x1, y1, x2, y2)`) ?
- [ ] Les crops produits par `segment.py` sont-ils compatibles avec `detect_text.py` ?

#### 3b. Interface pipeline
- [ ] `pipeline.py` orchestre correctement les étapes dans l'ordre prévu ?
- [ ] Chaque module expose une interface publique claire (fonctions documentées) ?

### 4. Audit des règles non négociables (transversal)

#### 4a. Strict code — sur TOUT le code source
- [ ] Aucun fallback silencieux dans `src/`.
- [ ] Validation explicite des entrées (fichiers image existants, dimensions, types).

#### 4b. Conventions image — sur TOUT le code source
- [ ] Aucune modification en place d'une image d'entrée sans `.copy()`.
- [ ] Conversions BGR/RGB explicites aux bonnes frontières.
- [ ] Chemins construits avec `pathlib.Path`.

#### 4c. Reproductibilité
- [ ] Seeds fixées pour toute opération aléatoire.

### 5. Audit de la qualité du code (transversal)

#### 5a. DRY
- [ ] Pas de duplication du code de prétraitement entre modules.
- [ ] Helpers de test réutilisés via `tests/conftest.py`.

#### 5b. Conventions
- [ ] `snake_case` cohérent.
- [ ] Aucun `print()` résiduel.
- [ ] Aucun `TODO`, `FIXME` orphelin.
- [ ] Imports propres.

### 6. Conformité avec la spécification

> Pour chaque étape du pipeline décrite dans la spec, vérifier que le module correspondant implémente bien ce qui est décrit.

| Section spec | Module | Vérifications |
|---|---|---|
| §3 Étape 2 — Prétraitement | `src/preprocess.py` | Redimensionnement, CLAHE sur canal L, correction perspective |
| §3 Étape 3 — Segmentation | `src/segment.py` | Canny + HoughLinesP, crops individuels |
| §3 Étape 4 — Détection texte | `src/detect_text.py` | CRAFT ou PaddleOCR, bounding boxes orientées, correction angle |
| §3 Étape 5 — OCR | `src/ocr.py` | PaddleOCR / TrOCR / Tesseract, choix du modèle |
| §3 Étape 6 — Post-traitement | `src/postprocess.py` | Nettoyage texte, séparation titre/auteur, fuzzy matching API |
| §6 Métriques | `src/eval.py` | CER (Levenshtein), taux de détection, taux d'identification |

### 7. Conformité avec le plan d'implémentation

- [ ] Les modules `src/*.py` listés dans le plan sont présents.
- [ ] Les tâches DONE ont un code et des tests correspondants.
- [ ] Les tâches marquées DONE sans code sont signalées.

### 8. Bonnes pratiques CV / OCR

- [ ] CER calculé correctement (distance d'édition / longueur de la référence).
- [ ] CLAHE appliqué sur le bon canal.
- [ ] Normalisation unicode (NFC) des sorties OCR.
- [ ] Bounding boxes dans un format uniforme.

### 9. Produire le rapport

Écrire dans `docs/request_changes/NNNN_slug.md`.

## Niveaux de sévérité

| Niveau | Définition |
|---|---|
| **BLOQUANT** | Bug actif, interface cassée, violation de règle non négociable. |
| **WARNING** | Risque réel mais non déclenché (edge case, convention violée). |
| **MINEUR** | Amélioration de qualité, DRY, cosmétique. |

## Format du rapport

```markdown
# Request Changes — <titre de la revue>

Statut : TODO
Ordre : NNNN

**Date** : YYYY-MM-DD
**Périmètre** : <description>
**Résultat** : NNN tests GREEN/RED, ruff clean/N erreurs
**Verdict** : ✅ CLEAN | ⚠️ REQUEST CHANGES | ❌ BLOCAGES CRITIQUES

---

## Résultats d'exécution

| Check | Résultat |
|---|---|
| `pytest tests/` | **NNN passed** / X failed |
| `ruff check src/ tests/` | **All checks passed** / N erreurs |
| `print()` résiduel | Aucun / N occurrences |
| `TODO`/`FIXME` orphelin | Aucun / N occurrences |
| Broad `except` | Aucun / N occurrences |

---

## BLOQUANTS (N)

### B-1. <Titre>
**Fichiers** : `src/fichier.py` (LNNN)
<Description du problème>
**Action** : <Action corrective>

---

## WARNINGS (N)

### W-1. <Titre>
**Fichiers** : `src/fichier.py` (LNNN)
<Description>
**Action** : <Action>

---

## MINEURS (N)

### M-1. <Titre>
<Description>
**Action** : <Action>

---

## Conformité pipeline (spec §3)

| Étape | Module | Implémenté | Conforme | Remarques |
|---|---|---|---|---|
| Prétraitement | `src/preprocess.py` | ✅/❌ | ✅/❌ | |
| Segmentation | `src/segment.py` | ✅/❌ | ✅/❌ | |
| Détection texte | `src/detect_text.py` | ✅/❌ | ✅/❌ | |
| OCR | `src/ocr.py` | ✅/❌ | ✅/❌ | |
| Post-traitement | `src/postprocess.py` | ✅/❌ | ✅/❌ | |
| Évaluation | `src/eval.py` | ✅/❌ | ✅/❌ | |

---

## Conformité plan → code

| WS | Tâches DONE | Module(s) code | Code présent | Tests présents |
|---|---|---|---|---|
| WS1 | #NNN, ... | `src/preprocess.py`, `src/segment.py` | ✅/❌ | ✅/❌ |
| WS2 | #NNN, ... | `src/detect_text.py` | ✅/❌ | ✅/❌ |
| WS3 | #NNN, ... | `src/ocr.py`, `src/postprocess.py` | ✅/❌ | ✅/❌ |
| WS4 | #NNN, ... | Streamlit app | ✅/❌ | ✅/❌ |
| WS5 | #NNN, ... | `src/eval.py` | ✅/❌ | ✅/❌ |

---

## Résumé des actions

| # | Sévérité | Action | Fichier(s) |
|---|---|---|---|
| B-1 | BLOQUANT | <action> | `src/fichier.py` |
```
