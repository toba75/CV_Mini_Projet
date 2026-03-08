---
name: pr-reviewer
description: Revue systématique de Pull Request pour le projet ShelfScan. Vérifie conformité TDD, conventions image, strict code, qualité globale. À utiliser quand l'utilisateur demande « review la PR », « revue de la branche task/NNN-* », « vérifie avant merge ».
argument-hint: "[branche: task/NNN-short-slug] ou [PR number]"
---

# Agent Skill — PR Reviewer (ShelfScan)

## Objectif
Effectuer une revue systématique et exigeante d'une Pull Request (ou d'une branche `task/NNN-*`) avant merge vers `main`.

## Prérequis
> **Avant de commencer**, lire `.github/shared/coding_rules.md` (§R1-§R9) et les commandes de scan (§GREP).

## Contexte repo

- **Spécification** : `docs/specifications/specifications.md`
- **Plan** : `docs/plan/implementation_plan.md` (WS1..WS5, M1..M4)
- **Tâches** : `docs/tasks/<milestone>/NNN__slug.md`
- **Code source** : `src/`
- **Tests** : `tests/` (pytest)
- **Linter** : ruff (`line-length = 100`, `target-version = "py310"`)

## Workflow de revue

**Phase A** (compliance rapide) valide le processus TDD. Si elle échoue → REJECT immédiat sans Phase B.
**Phase B** (code review adversariale) représente **80% du temps de la revue**.

---

## PHASE A — Compliance rapide

### A1. Identifier le périmètre

```bash
git diff --name-only main...HEAD
```

### A2. Vérifier la structure de branche et commits

- [ ] La branche suit la convention `task/NNN-short-slug`.
- [ ] Il existe un commit RED au format `[WS-X] #NNN RED: <résumé>`.
- [ ] Il existe un commit GREEN au format `[WS-X] #NNN GREEN: <résumé>`.
- [ ] Le commit RED contient uniquement des fichiers de tests.
- [ ] Le commit GREEN contient l'implémentation + mise à jour de la tâche.

### A3. Vérifier la tâche associée

- [ ] Le fichier `docs/tasks/<milestone>/NNN__slug.md` est modifié dans la PR.
- [ ] `Statut` est passé à `DONE`.
- [ ] Tous les critères d'acceptation sont cochés `[x]`.
- [ ] Toute la checklist de fin de tâche est cochée `[x]`.

### A4. Exécuter la suite de validation

```bash
pytest tests/ -v --tb=short
ruff check src/ tests/
```

- [ ] **pytest GREEN** : NNN passed, 0 failed.
- [ ] **ruff clean** : 0 erreur.

> Si pytest RED ou ruff erreurs → **REJECT** immédiat.

---

## PHASE B — Code review adversariale

### B1. Scan automatisé obligatoire (GREP)

> Commandes et classification : voir `.github/shared/coding_rules.md` §GREP.
> Exécuter **toutes** les commandes listées et documenter chaque résultat.

### B2. Lecture du diff ligne par ligne (OBLIGATOIRE)

Pour **CHAQUE fichier source modifié** (`src/`), lire le diff complet :

```bash
git diff main...HEAD -- <fichier>
```

Pour chaque hunk de diff, appliquer cette grille :

1. **Type safety** : les fichiers image et textes sont-ils validés avant usage ?
2. **Edge cases** : que se passe-t-il si l'image est vide, mal formée, trop petite ?
3. **Conventions image** : BGR/RGB aux bonnes frontières, copy() sur images modifiées.
4. **Return contract** : le type de retour est-il garanti en toute circonstance ?
5. **Cohérence doc/code** : la docstring correspond-elle au comportement réel ?
6. **Chemins** : construits avec `pathlib.Path`, répertoires créés avant usage.

### B3. Vérifier les tests

- [ ] Chaque critère d'acceptation est couvert par au moins un test.
- [ ] Les tests couvrent : cas nominaux, cas d'erreur, cas de bords.
- [ ] Images de test : synthétiques (numpy arrays) ou fichiers locaux dans `tests/fixtures/`. Pas de réseau.
- [ ] Tests déterministes (seeds fixées si aléatoire).
- [ ] **Portabilité des chemins** (prouvé par scan B1) : pas de chemin hardcodé. Utiliser `tmp_path`.

### B4. Audit du code — Règles non négociables

#### B4a. Strict code (no fallbacks)
> Checklist : §R1. Preuve : scan B1.

#### B4b. Conventions image
> Checklist : §R4. Preuve : scan B1 + lecture diff B2.

#### B4c. Gestion des fichiers et I/O
> Checklist : §R5. Preuve : lecture diff B2.

#### B4d. Anti-patterns Python / numpy
> Checklist : §R6. Preuve : scan B1 + lecture diff B2.

### B5. Qualité du code
> Checklist : §R7. Preuve : scan B1 + lecture diff B2.

### B6. Cohérence avec les specs

- [ ] Le code est conforme à la spécification (`docs/specifications/specifications.md`).
- [ ] Le code est conforme au plan d'implémentation.
- [ ] Pas d'exigence inventée hors des documents source.

### B7. Cohérence intermodule
> Checklist : §R8. Preuve : grep des signatures + lecture diff B2.

### B8. Bonnes pratiques CV / OCR
> Checklist : §R9. Preuve : lecture diff B2.

---

## Format du rapport de revue

```markdown
# Revue PR — [WS-X] #NNN — <titre de la tâche>

Branche : `task/NNN-short-slug`
Tâche : `docs/tasks/<milestone>/NNN__slug.md`
Date : YYYY-MM-DD

## Verdict global : ✅ APPROVE | ⚠️ REQUEST CHANGES | ❌ REJECT

## Résumé
[2-3 phrases résumant les changements et le verdict]

---

## Phase A — Compliance

### Structure branche & commits
| Critère | Verdict | Preuve |
|---|---|---|
| Convention de branche | ✅/❌ | `git branch` output |
| Commit RED présent | ✅/❌ | hash + `git show --stat` |
| Commit GREEN présent | ✅/❌ | hash + `git show --stat` |

### Tâche
| Critère | Verdict |
|---|---|
| Statut DONE | ✅/❌ |
| Critères d'acceptation cochés | ✅/❌ (N/N) |

### CI
| Check | Résultat |
|---|---|
| `pytest tests/ -v --tb=short` | **NNN passed**, 0 failed |
| `ruff check src/ tests/` | **All checks passed** / N erreurs |

---

## Phase B — Code Review

### Résultats du scan automatisé (B1)

| Pattern recherché | Commande | Résultat |
|---|---|---|
| Fallbacks silencieux | `grep 'or []...'` | 0 occurrences |
| Except trop large | `grep 'except:$...'` | 0 occurrences |
| Print résiduel | `grep 'print('` | 0 occurrences |
| Mutable defaults | `grep 'def.*=[]...'` | 0 occurrences |
| TODO/FIXME orphelins | `grep 'TODO\|FIXME...'` | 0 occurrences |

### Annotations par fichier (B2)

#### `src/<module>.py`
- **L<N>** `<extrait>` : <observation>. Sévérité : ... Suggestion : ...

### Tests (B3)
| Critère | Verdict | Preuve |
|---|---|---|
| Couverture des critères | ✅/❌ | |
| Cas nominaux + erreurs + bords | ✅/❌ | |
| Données synthétiques | ✅/❌ | |
| Portabilité chemins | ✅/❌ | |

### Code — Règles non négociables (B4)
| Règle | Verdict | Preuve |
|---|---|---|
| Strict code | ✅/❌ | |
| Conventions image | ✅/❌ | |
| Gestion fichiers I/O | ✅/❌ | |
| Anti-patterns Python | ✅/❌ | |

### Qualité (B5)
| Critère | Verdict |
|---|---|
| snake_case | ✅/❌ |
| Pas de code mort/debug | ✅/❌ |
| Imports propres | ✅/❌ |

### Conformité spec (B6)
| Critère | Verdict |
|---|---|
| Spécification | ✅/❌ |
| Plan d'implémentation | ✅/❌ |

### Bonnes pratiques CV/OCR (B8)
| Critère | Verdict |
|---|---|
| BGR/RGB correct | ✅/❌ |
| CER calculé correctement | ✅/❌ |
| Bounding boxes cohérentes | ✅/❌ |

---

## Remarques mineures
- [Remarque mineure 1]

## Actions requises (si REQUEST CHANGES)
1. [Action corrective 1]
```

## Règles de verdict

| Verdict | Condition |
|---|---|
| **✅ APPROVE** | Tous les critères non négociables satisfaits. |
| **⚠️ REQUEST CHANGES** | Au moins un critère partiellement violé. |
| **❌ REJECT** | Violation grave : strict code violé, tests RED, absence de TDD. |
