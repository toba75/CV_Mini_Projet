---
name: implementing-request-change
description: Implémenter les corrections issues d'un document request_changes (revue globale ou PR). Traite les items BLOQUANT/WARNING/MINEUR par ordre de sévérité, avec tests, validation et commits structurés. À utiliser quand l'utilisateur demande « implémente les request changes 0001 », « corrige les bloquants du rapport ».
argument-hint: "[fichier: docs/request_changes/NNNN_slug.md] [scope: all|bloquants|warnings|mineurs|B-1,W-3]"
---

# Agent Skill — Implementing Request Change (ShelfScan)

## Objectif
Implémenter méthodiquement les corrections identifiées dans `docs/request_changes/NNNN_slug.md`, en respectant les conventions du projet ShelfScan.

## Contexte repo

- **Request changes** : `docs/request_changes/NNNN_slug.md`
- **Spécification** : `docs/specifications/specifications.md`
- **Code source** : `src/`
- **Tests** : `tests/` (pytest)
- **Linter** : ruff (`line-length = 100`, `target-version = "py310"`)

## Principes non négociables

- **Zéro régression** : chaque correction doit laisser la suite de tests GREEN.
- **Strict code (no fallbacks)** : validation explicite + `raise`.
- **Conventions image** : BGR/RGB, copy(), pathlib.Path.
- **Cohérence intermodule** : chaque correction propagée à tous les modules impactés du pipeline.
- **Ambiguïté** : si l'action est ambiguë → demander des clarifications avant d'implémenter.

## Workflow standard

### 0. Pré-condition GREEN
`pytest` → **tous les tests existants doivent être GREEN**.

### 1. Lire le document request_changes
Extraire :
- Le **statut** (`TODO`, `IN_PROGRESS`, `DONE`).
- La liste des items avec sévérité.
- Pour chaque item : fichiers impactés, description, action demandée.

### 2. Trier et planifier
**Ordre obligatoire** : BLOQUANTS → WARNINGS → MINEURS.
Regrouper par module impacté.

### 3. Analyser l'impact de chaque item

1. **Lire les fichiers référencés**.
2. **Identifier tous les modules impactés** — pas seulement ceux listés. Utiliser grep.
3. **Évaluer l'effet domino** sur les étapes du pipeline.

### 4. Implémenter la correction

#### 4a. Écrire ou adapter les tests
- Test manquant → l'écrire.
- Test masquant un bug → le corriger.
- Comportement modifié → adapter les tests + ajouter un test du nouveau comportement.

#### 4b. Appliquer le fix
- Modifier **tous** les fichiers impactés en une seule passe.
- Conventions image respectées.

#### 4c. Corrections en cascade
Si le fix révèle un problème non listé :
- Corriger immédiatement si trivial.
- Documenter dans le commit si substantiel.

### 5. Valider

```bash
ruff check src/ tests/
pytest
```

**Ne jamais** passer au commit si `ruff check` ou `pytest` échoue.

### 6. Audit post-correction

- [ ] Aucune divergence de format entre modules du pipeline.
- [ ] Aucun test existant cassé.
- [ ] L'action demandée est entièrement réalisée.

### 7. Commit

```bash
git add <fichiers modifiés>
git commit -m "[RC-NNNN] FIX B-1: <résumé de la correction>"
```

**Convention de préfixe** :
- `[RC-NNNN] FIX B-1:` — item BLOQUANT.
- `[RC-NNNN] FIX W-3:` — item WARNING.
- `[RC-NNNN] FIX M-2:` — item MINEUR.

### 8. Mettre à jour le document request_changes

- Au **premier item corrigé** : `Statut : TODO` → `Statut : IN_PROGRESS`.
- Quand **tous les items** traités : → `Statut : DONE`.
- Marquer chaque item traité :
  ```markdown
  ### B-1. ~~Description~~ ✅ RÉSOLU
  > **Résolu** : commit `abc1234` — `[RC-0001] FIX B-1: ...`
  ```

### 9. Validation finale

```bash
ruff check src/ tests/
pytest
git push
```

## Gestion des effets domino

| Situation | Action |
|---|---|
| Fix trivial (< 10 lignes, même module) | Corriger immédiatement, documenter dans le commit. |
| Fix substantiel (> 10 lignes) | Documenter le nouveau problème, demander à l'utilisateur. |
| Contradiction avec la spec | **Stopper**. Signaler à l'utilisateur. |

## Procédure d'abandon

1. Documenter le blocage dans le document request_changes.
2. Informer l'utilisateur avec la raison précise.
3. Passer à l'item suivant.
4. Ne pas marquer l'item comme résolu.
