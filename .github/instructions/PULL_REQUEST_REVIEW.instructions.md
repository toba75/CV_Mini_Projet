---
applyTo: "**"
---

# Revue de Pull Request — ShelfScan

## Sortie obligatoire

À la fin de la revue, **produire un fichier de rapport** :
- **Chemin** : `docs/pr_review_copilot/<nom_de_branche>_review.md`
  - `<nom_de_branche>` = nom de la branche source de la PR (ex : `task/014-ocr-postprocess` → `task_014-ocr-postprocess_review.md`). Remplacer les `/` par `_`.
- **Contenu** : la grille d'audit ci-dessous, remplie avec les résultats (`[x]` = OK, `[ ]` = non conforme, `[N/A]` = non applicable), plus une section verdict final (APPROVE / REQUEST CHANGES) et la liste des remarques numérotées avec recommandations.

## Contexte repo

- **Spécification** : `docs/specifications/specifications.md`
- **Plan** : `docs/plan/implementation_plan.md` (WS1..WS5, M1..M4)
- **Tâches** : `docs/tasks/<milestone>/NNN__slug.md`
- **Code source** : `src/`
- **Tests** : `tests/` (pytest)
- **Linter** : ruff (`line-length = 100`, `target-version = "py310"`)

## Grille d'audit

### Structure branche & commits
- [ ] Branche `task/NNN-short-slug` depuis `main`.
- [ ] Commit RED : `[WS-X] #NNN RED: <résumé>` (tests uniquement).
- [ ] Commit GREEN : `[WS-X] #NNN GREEN: <résumé>` (implémentation + tâche).
- [ ] Pas de commits parasites entre RED et GREEN.

### Tâche associée
- [ ] `docs/tasks/<milestone>/NNN__slug.md` : statut DONE.
- [ ] Critères d'acceptation cochés `[x]`.
- [ ] Checklist cochée `[x]`.

### Tests
- [ ] Convention de nommage (`test_preprocess.py`, `test_ocr.py`, etc.).
- [ ] Couverture des critères d'acceptation.
- [ ] Cas nominaux + erreurs + bords.
- [ ] `pytest` GREEN, 0 échec.
- [ ] `ruff check src/ tests/` clean.
- [ ] Données synthétiques ou images de test locales (pas réseau).
- [ ] Tests déterministes (seeds fixées si aléatoire).

### Strict code (no fallbacks)
- [ ] Aucun `or default`, `value if value else default`.
- [ ] Aucun `except` trop large.
- [ ] Validation explicite + `raise`.

### Conventions image
- [ ] Pas de modification en place des images d'entrée.
- [ ] Conversion BGR↔RGB explicite aux bonnes frontières.
- [ ] Chemins construits avec `pathlib.Path`.

### Qualité
- [ ] snake_case.
- [ ] Pas de print(), code mort, TODO orphelin.
- [ ] Imports propres.
- [ ] DRY : pas de duplication de logique de prétraitement.

## Format du fichier de rapport

Le fichier `docs/pr_review_copilot/<nom_de_branche>_review.md` doit suivre cette structure :

```markdown
# PR Review — <titre de la PR>

**Branche** : `<nom_de_branche>`
**Date** : <date de la revue>
**Verdict** : APPROVE | REQUEST CHANGES

## Grille d'audit

<copier la grille ci-dessus avec les cases cochées/décochées>

## Remarques

1. [BLOQUANT|WARNING|MINEUR] <description>
   - Fichier : `<chemin>`
   - Ligne(s) : <numéros>
   - Suggestion : <correction proposée>

## Résumé

<synthèse en 2-3 phrases>
```
