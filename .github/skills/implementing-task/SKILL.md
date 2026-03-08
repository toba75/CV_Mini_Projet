---
name: implementing-task
description: Implémenter une ou plusieurs tâches de docs/tasks/ via TDD strict (tests d'acceptation → rouge → vert), conventions du repo ShelfScan, mise à jour du fichier de tâche et commits. Orchestre 4 parties via custom agents. À utiliser quand l'utilisateur demande « implémente/exécute/travaille sur la tâche #NNN ».
---

# Agent Skill — Implementing Task (ShelfScan)

## Objectif
Orchestrer l'implémentation de tâches décrites dans `docs/tasks/<milestone>/NNN__slug.md` en déléguant le travail à des **custom agents spécialisés** via un workflow en 4 parties :

- **Partie A** : Agent `TDD-Implementer` (TDD strict RED→GREEN).
- **Partie B** : Agent `TDD-Reviewer` (revue de branche + rapport).
- **Partie C** (conditionnel) : Agent `TDD-Fixer` (corrections si la revue relève des items).
- **Partie Post-PR** : Agent `PR-Review-Fixer` (corrections post-review GitHub).

Les parties B+C sont itérées jusqu'à 5 fois maximum, ou jusqu'à obtention d'un verdict CLEAN.

## Agents workers

| Agent | Fichier | Rôle |
|---|---|---|
| `TDD-Implementer` | `.github/agents/tdd-implementer.agent.md` | Implémentation TDD RED→GREEN |
| `TDD-Reviewer` | `.github/agents/tdd-reviewer.agent.md` | Revue de branche (audit complet) |
| `TDD-Fixer` | `.github/agents/tdd-fixer.agent.md` | Corrections post-revue |
| `PR-Review-Fixer` | `.github/agents/pr-review-fixer.agent.md` | Corrections post-review GitHub |

## Contexte repo

- **Tâches** : `docs/tasks/<milestone>/NNN__slug.md`
- **Spécification** : `docs/specifications/specifications.md`
- **Plan** : `docs/plan/implementation_plan.md` (WS1..WS5, M1..M4)
- **Code source** : `src/` (modules Python du pipeline)
- **Tests** : `tests/` (pytest)
- **Linter** : ruff (`line-length = 100`, `target-version = "py310"`)
- **Langue** : anglais pour code/tests, français pour docs/tâches

## Principes non négociables

- **Zéro "ghost completion"** : ne jamais marquer une tâche `DONE` sans **code + tests** et **exécution vérifiée**.
- **TDD réel** : écrire les tests avant l'implémentation, vérifier qu'ils échouent, puis implémenter.
- **Strict code (no fallbacks)** : validation explicite + `raise`.
- **Conventions image** : BGR/RGB aux bonnes frontières, pas de modification en place.
- **Branche dédiée** : `task/NNN-short-slug` depuis `main`. Jamais de commit direct sur `main`.
- **Pull Request obligatoire** vers `main` — créée **uniquement par l'orchestrateur**.

---

# WORKFLOW ORCHESTRATEUR (1 tâche)

## Étape 0 — Préparation (orchestrateur)

1. **Pré-condition GREEN** : exécuter `pytest` → tous les tests existants doivent être GREEN.
2. **Lire la tâche** : ouvrir `docs/tasks/<milestone>/NNN__slug.md`.
3. **Créer le dossier de review** : `docs/tasks/<milestone>/<NNN>/` (s'il n'existe pas).
4. **Créer la branche dédiée** :
   ```bash
   git checkout main
   git pull
   git checkout -b task/NNN-short-slug
   ```
5. **Initialiser le compteur de review** : `review_iteration = 0`.

---

## Partie A — Implémentation (agent TDD-Implementer)

Lancer l'agent `TDD-Implementer` en passant le prompt suivant :

```
Implémente la tâche `docs/tasks/<milestone>/NNN__slug.md`.
Branche : `task/NNN-short-slug` (déjà créée et checkoutée).
Workstream : WS-X.
```

---

## Partie B — Revue de branche (agent TDD-Reviewer)

Incrémenter : `review_iteration += 1`.

Lancer l'agent `TDD-Reviewer` en passant :

```
Branche à auditer : `task/NNN-short-slug`
Tâche associée : `docs/tasks/<milestone>/NNN__slug.md`
Itération de revue : v<review_iteration>

Écris le rapport dans : `docs/tasks/<milestone>/<NNN>/review_v<review_iteration>.md`
```

### Décision de l'orchestrateur après Partie B

- **Si verdict = CLEAN** (0 bloquants, 0 warnings, 0 mineurs) → passer à la Partie Finale.
- **Si verdict = REQUEST CHANGES** ET `review_iteration < 5` → lancer la Partie C.
- **Si verdict = REQUEST CHANGES** ET `review_iteration >= 5` → stopper, informer l'utilisateur.

---

## Partie C — Corrections (agent TDD-Fixer, conditionnel)

```
Rapport de revue à traiter : `docs/tasks/<milestone>/<NNN>/review_v<review_iteration>.md`
Branche : `task/NNN-short-slug`.
Tâche : `docs/tasks/<milestone>/NNN__slug.md`
Workstream : WS-X, numéro tâche : NNN.
```

Après la Partie C, **reboucler sur la Partie B**.

---

## Partie Finale — Push et Pull Request (orchestrateur)

1. **Commiter les fichiers de revue** :
```bash
git add docs/tasks/<milestone>/<NNN>/
git commit -m "[WS-X] #NNN REVIEW: rapports de revue v1..v<review_iteration>"
```

2. **Push et création de la PR** :
```bash
git push -u origin task/NNN-short-slug
```
- Titre : `[WS-X] #NNN — <titre de la tâche>`

---

## Partie Post-PR — Review GitHub automatique

Après création de la PR, lancer `PR-Review-Fixer` sur les commentaires `copilot-pull-request-reviewer`.

---

## Format de commits

| Moment | Format | Contenu |
|---|---|---|
| Après tests RED (Partie A) | `[WS-X] #NNN RED: <résumé>` | Fichiers de tests uniquement |
| Clôture tâche (Partie A) | `[WS-X] #NNN GREEN: <résumé>` | Implémentation + tests + tâche |
| Corrections post-revue (Partie C) | `[WS-X] #NNN FIX: <résumé>` | Corrections demandées |
| Corrections post-review GitHub | `[WS-X] #NNN PR-FIX: <résumé>` | Corrections des commentaires GitHub |
