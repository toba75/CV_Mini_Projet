---
name: plan-coherence
description: "Revue de cohérence intrinsèque du plan d'implémentation ShelfScan et correction séquentielle des incohérences. À utiliser quand l'utilisateur demande « revue du plan », « cohérence du plan », « vérifie le plan », « audit plan »."
argument-hint: "[plan: docs/plan/implementation_plan.md]"
---

# Agent Skill — Revue de cohérence du plan d'implémentation (ShelfScan)

## Objectif

Auditer la **cohérence intrinsèque** du plan d'implémentation (`docs/plan/implementation_plan.md`), puis corriger les incohérences détectées une par une.

Le skill opère en deux phases :
- **Phase A** : analyse du plan seul, production d'un rapport.
- **Phase B** : correction séquentielle de chaque incohérence.

## Contexte repo

- **Plan** : `docs/plan/implementation_plan.md` (WS1..WS5, M1..M4)
- **Rapport de cohérence** : `docs/review_coherence_plan.md`
- **Tâches** : `docs/tasks/<milestone>/NNN__slug.md`

## Phase A — Analyse de cohérence intrinsèque

### Principe fondamental

L'analyse porte **exclusivement** sur le contenu du plan. Aucun autre fichier (spec, code, tests) ne doit être consulté.

### Périmètre de lecture

Lire **intégralement** `docs/plan/implementation_plan.md`.

### Axes d'analyse

#### A1. Cohérence des dépendances
- Les dépendances déclarées entre WS sont-elles respectées dans l'ordonnancement des milestones ?
- Un WS dépend-il d'un autre WS planifié dans un milestone ultérieur ?
- Y a-t-il des dépendances circulaires ?

#### A2. Cohérence des identifiants et références croisées
- Les workstreams WS1..WS5 sont-ils référencés de manière cohérente ?
- Les noms de modules/fichiers (`preprocess.py`, `ocr.py`, etc.) sont-ils cohérents entre sections ?

#### A3. Cohérence du contenu sémantique
- Les descriptions de tâches au sein d'un même WS sont-elles mutuellement cohérentes ?
- Les responsabilités sont-elles clairement attribuées sans recouvrement ni trou entre WS ?
- Les entrées/sorties sont-elles compatibles entre WS producteurs/consommateurs ?
- Les critères de milestone sont-ils cohérents avec le contenu des WS ?

#### A4. Cohérence structurelle
- Le plan est-il complet (tous WS détaillés pour chaque milestone) ?
- Les milestones couvrent-ils tous les WS ?
- La numérotation est-elle homogène ?

#### A5. Cohérence des milestones
- Chaque milestone a-t-il des critères de validation définis ?
- Les critères sont-ils vérifiables avec les livrables ?

### Sortie de la Phase A

Produire `docs/review_coherence_plan.md` :

```markdown
# Revue de cohérence — Plan d'implémentation ShelfScan

**Date** : YYYY-MM-DD
**Document audité** : `docs/plan/implementation_plan.md`

## Résumé

<nombre d'incohérences par axe, synthèse en 2-3 phrases>

## Incohérences détectées

### I-1. <titre court>

- **Axe** : A1|A2|A3|A4|A5
- **Sévérité** : BLOQUANT|WARNING|MINEUR
- **Localisation** : <sections du plan>
- **Description** : <description factuelle avec citations>
- **Recommandation** : <correction suggérée>

## Conclusion

<verdict : plan cohérent / incohérences mineures / incohérences structurelles>
```

**Règles de sévérité** :
- **BLOQUANT** : incohérence rendant l'implémentation impossible (dépendance circulaire, module partagé entre WS avec comportements différents).
- **WARNING** : ambiguïté créant un risque d'interprétation divergente.
- **MINEUR** : incohérence cosmétique sans impact fonctionnel.

## Phase B — Correction séquentielle

### Workflow

#### B1. Lire le rapport
Lire `docs/review_coherence_plan.md` et extraire la liste des incohérences.

#### B2. Créer les TODOs
Pour **chaque** incohérence I-N, créer une entrée TODO.

#### B3. Traiter chaque TODO via agent Plan-Corrector
Lancer l'agent `Plan-Corrector` pour chaque incohérence dans un contexte isolé.

> Instructions : `.github/agents/plan-corrector.agent.md`.

Prompt :
```
## Incohérence à corriger
<copier le bloc I-N>

## Milestones déjà implémentés
<liste des milestones DONE>
```

#### B4. Mettre à jour le rapport
Marquer chaque incohérence ✅ RÉSOLU ou ⚠️ NON RÉSOLU.

#### B5. Itérer jusqu'à convergence
Les corrections peuvent introduire de nouvelles incohérences. Itérer (Phase A → Phase B) jusqu'à convergence. **Garde-fou** : 3 itérations maximum.

## Agents workers

| Agent | Fichier | Rôle |
|---|---|---|
| `Plan-Corrector` | `.github/agents/plan-corrector.agent.md` | Correction d'une incohérence |
| `Plan-Analyzer` | `.github/agents/plan-analyzer.agent.md` | Analyse complète (itérative) |

## Contraintes

- **Phase A** : le plan seul. Rien d'autre.
- **Phase B** : le plan + minimum de contexte pour chaque correction.
- **Jamais** : modifier le code ou les tests. Ce skill ne touche que les documents de planification.
