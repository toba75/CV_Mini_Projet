---
name: test-adherence
description: Vérifie que les tests adhèrent exactement à la spécification ShelfScan. Pour chaque module testé, croise les critères d'acceptation des tâches et les descriptions de la spec pour détecter les écarts, oublis et assertions incorrectes. À utiliser quand l'utilisateur demande « vérifie l'adhérence des tests », « les tests collent à la spec ? », « audit tests vs spec ».
argument-hint: "[scope: all|module_name|WS1..WS5] [severity: strict|normal]"
---

# Agent Skill — Test Adherence (ShelfScan)

## Objectif

Auditer l'adhérence des tests (`tests/`) à la spécification (`docs/specifications/specifications.md`) et aux tâches (`docs/tasks/<milestone>/NNN__slug.md`). Détecter :

1. **Tests manquants** : critères d'acceptation sans test correspondant.
2. **Tests incorrects** : assertions qui ne valident pas le comportement décrit dans la spec.
3. **Tests divergents** : tests qui valident un comportement différent de la spec.
4. **Tests orphelins** : tests sans critère d'acceptation correspondant.

## Contexte repo

- **Spécification** : `docs/specifications/specifications.md`
- **Plan** : `docs/plan/implementation_plan.md`
- **Tâches** : `docs/tasks/<milestone>/NNN__slug.md`
- **Code source** : `src/`
- **Tests** : `tests/`

## Workflow

### 0. Déterminer le périmètre

```bash
find tests/ -name "test_*.py" -not -path "*__pycache__*" | sort
grep -rl "Statut : DONE" docs/tasks/ | sort
```

### 1. Construire la matrice spec → tâche → test

Pour chaque module dans le périmètre :

1. **Identifier la section de spec** applicable (étape du pipeline concernée).
2. **Lire la tâche** et extraire les critères d'acceptation.
3. **Lire le fichier de test** et inventorier les fonctions avec leurs docstrings.
4. **Mapper** chaque critère vers un ou plusieurs tests.

### 2. Vérifier l'adhérence comportement par comportement

#### 2a. Comportements clés à vérifier

| Section spec | Comportement | Test attendu |
|---|---|---|
| §3 Étape 2 | CLAHE sur canal L (pas RGB) | Valeur pixel vérifié avant/après |
| §3 Étape 3 | Canny + HoughLinesP produit ≥ 1 ligne | Test sur image avec séparations claires |
| §3 Étape 4 | Correction d'angle avant OCR | Image tournée → bounding boxes droites |
| §3 Étape 5 | CER = edit_distance / len(ref) | Calcul à la main sur exemple connu |
| §3 Étape 6 | Fuzzy matching : seuil minimal configurable | Test avec titre approchant |
| §6 | Taux de détection = livres trouvés / livres réels | Calcul vérifié sur cas simple |
| §6 | CER normalisé par longueur de la référence | Test unitaire |

#### 2b. Conventions image
- [ ] Tests vérifient les dimensions et types des images (`ndim == 3`, `dtype == uint8`).
- [ ] Tests vérifient que les images d'entrée ne sont pas modifiées en place.
- [ ] Tests vérifient les conversions BGR/RGB aux bons endroits.

#### 2c. Formats de sortie
- [ ] Tests vérifient la structure du JSON de sortie (clés `image`, `books`, `title`, `author`, `confidence`).
- [ ] Tests vérifient que le CSV exporté est parseable.

#### 2d. Comportement aux bornes
- [ ] Image avec 0 livre détecté → JSON avec liste vide (pas d'exception).
- [ ] Image de très faible résolution → erreur explicite ou warning.
- [ ] Texte OCR vide → confidence = 0 ou tranche ignorée.
- [ ] API bibliographique indisponible → mode dégradé (texte brut sans enrichissement).

### 3. Vérifier la couverture des critères d'acceptation

```
Pour chaque critère [x] dans la tâche :
  - Trouver le(s) test(s) qui le couvrent.
  - Vérifier que le test exécute réellement le scénario décrit.
  - Si aucun test → signaler comme MANQUANT.
  - Si test existe mais n'exerce pas le critère → signaler comme INSUFFISANT.
```

### 4. Détecter les anti-patterns de test

- [ ] **Tautologie** : test qui vérifie que le code renvoie ce que le code renvoie.
- [ ] **Test réseau** : test qui appelle une API externe réelle (doit être mocké).
- [ ] **Image hardcodée** : test qui dépend d'un fichier image externe sans fallback synthétique.
- [ ] **Assertion absente** : test qui exécute du code sans `assert`.
- [ ] **Paramètre hardcodé** : seuil OCR ou angle de rotation hardcodé dans le test.

### 5. Produire le rapport

```markdown
# Test Adherence — <scope audité>

**Date** : YYYY-MM-DD
**Périmètre** : <modules audités>
**Verdict** : ✅ CONFORME | ⚠️ ÉCARTS DÉTECTÉS | ❌ NON-CONFORMITÉS CRITIQUES

---

## Résumé exécutif

<2-3 phrases>

## Matrice de couverture spec → tests

| Section spec | Comportement/Règle | Tâche(s) | Test(s) | Verdict |
|---|---|---|---|---|
| §3 Étape 2 | CLAHE canal L | #001 | `test_preprocess.py::test_clahe_on_l_channel` | ✅ |
| §6 | CER normalisé | #012 | `test_eval.py::test_cer_calculation` | ✅ |
| ... | ... | ... | ... | ... |

## Critères d'acceptation non couverts

| Tâche | Critère | Statut |
|---|---|---|
| #NNN | <critère> | ❌ MANQUANT |

## Écarts spec ↔ test

### B-N. <Titre>
**Spec** : §X — <comportement attendu>
**Test** : `tests/test_xxx.py::test_method`
**Écart** : <description précise>
**Action** : <correction>

## Anti-patterns détectés

| Test | Anti-pattern | Sévérité |
|---|---|---|
| `test_xxx.py::test_yyy` | Test réseau sans mock | WARNING |

## Résumé des actions

| # | Sévérité | Action | Fichier(s) |
|---|---|---|---|
| B-1 | BLOQUANT | <action> | `tests/test_xxx.py` |
```

## Niveaux de sévérité

| Niveau | Définition |
|---|---|
| **BLOQUANT** | Comportement de test en contradiction avec la spec. Critère obligatoire non couvert. |
| **WARNING** | Couverture partielle. Test tautologique. API externe non mockée. |
| **MINEUR** | Test orphelin valide. Docstring #NNN manquant. |
