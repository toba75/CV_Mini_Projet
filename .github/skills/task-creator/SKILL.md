---
name: task-creator
description: Analyse la spécification ShelfScan et le plan d'implémentation pour générer des tâches d'implémentation structurées. À utiliser quand l'utilisateur demande de créer des tâches pour un WS, un milestone ou une section de spec.
argument-hint: "[scope: WS1..WS5/M1..M4/section] [nb_taches]"
---

# Agent Skill — Task Creator (ShelfScan)

## Objectif
Générer des fichiers de tâches clairs, actionnables et traçables à partir des documents de cadrage du projet ShelfScan.

## Contexte repo (chemins réels)

- **Spécification** : `docs/specifications/specifications.md`
- **Plan de réalisation** : `docs/plan/implementation_plan.md` (WS1..WS5, M1..M4)
- **Répertoire des tâches** : `docs/tasks/<milestone>/` (ex : `docs/tasks/M1/`, `docs/tasks/M2/`, etc. — à créer si absent)
- **Code source** : `src/`
- **Tests** : `tests/`
- **Langue** : français pour docs/tâches, anglais pour code/tests
- **Mode de travail** : TDD strict (RED → GREEN)

## Rôle de l'agent

Tu dois :
- détecter les écarts entre spécification, plan, et tâches existantes ;
- proposer des tâches atomiques (une intention technique claire par fichier) ;
- garder l'alignement avec les workstreams WS1..WS5, milestones M1..M4 ;
- éviter les tâches vagues, non testables, ou non traçables.

## Workflow de génération

1. **Analyser la spec**
   - Lire les sections pertinentes de `docs/specifications/specifications.md`.
   - Extraire les exigences : étapes du pipeline, modèles OCR à comparer, formats de sortie, métriques.

2. **Lire le plan d'implémentation**
   - Prioriser via `docs/plan/implementation_plan.md` (WS, milestones, critères de validation).

3. **Auditer les tâches existantes**
   - Lister `docs/tasks/` et ses sous-répertoires.
   - Identifier : numérotation max, doublons, trous de couverture.

4. **Générer les tâches manquantes**
   - Créer uniquement des tâches nécessaires, ordonnées et testables.
   - Ajouter les références précises (fichier + section).

## Format des fichiers de tâche

```markdown
# Tâche — [Titre descriptif en français]

Statut : TODO
Ordre : [NNN]
Workstream : [WS1|WS2|WS3|WS4|WS5]
Milestone : [M1|M2|M3|M4]

## Contexte
[Explication brève du contexte et pourquoi cette tâche existe]

Références :
- Plan : `docs/plan/implementation_plan.md` (section ciblée)
- Spécification : `docs/specifications/specifications.md` (§X)
- Code : `src/[fichier.py]` (si applicable)

Dépendances :
- Tâche NNN — [titre] (doit être DONE)

## Objectif
[Énoncé clair de ce qui doit être accompli]

## Règles attendues
- [Règle clé 1 : strict code, conventions image, etc.]
- [Règle clé 2]

## Évolutions proposées
- [Changement proposé 1]
- [Changement proposé 2]

## Critères d'acceptation
- [ ] [Critère vérifiable 1]
- [ ] [Critère vérifiable 2]
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/NNN-short-slug` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/NNN-short-slug` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS-X] #NNN RED: <résumé>` (fichiers de tests uniquement).
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-X] #NNN GREEN: <résumé>`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-X] #NNN — <titre>`.
```

## Convention de nommage

Répertoire : `docs/tasks/<milestone>/` — un sous-répertoire par milestone (`M1`, `M2`, `M3`, `M4`).

Fichiers : `NNN__short_slug.md`

- `NNN` : numéro séquentiel sur 3 chiffres (001, 002, ...), **global** à tout le projet
- `__` : séparateur fixe
- `short_slug` : minuscule, underscores, orienté action

Exemples :
- `docs/tasks/M1/001__ws1_preprocess_clahe.md`
- `docs/tasks/M1/002__ws2_craft_detection.md`
- `docs/tasks/M2/003__ws3_paddleocr_integration.md`
- `docs/tasks/M2/004__ws4_streamlit_scaffold.md`

## Référentiel rapide (ShelfScan)

Sujets typiquement à couvrir en tâches :

**M1 — Setup & Prototype (WS1, WS2, WS3, WS4, WS5)** :
- `preprocess.py` : chargement, redimensionnement, CLAHE sur canal L
- Segmentation naïve : Canny + HoughLinesP
- Test CRAFT/PaddleOCR en mode détection seule
- Comparaison qualitative PaddleOCR / TrOCR / Tesseract sur crops manuels
- Test API Google Books / Open Library
- Scaffold Streamlit minimal
- 10 premières photos + annotation CSV ground truth

**M2 — Pipeline complet (WS1, WS2, WS3, WS4, WS5)** :
- Correction de perspective (homographie OpenCV)
- Affinage segmentation : filtrage lignes parasites
- Crops individuels par tranche
- Correction d'orientation automatique (rotation)
- `postprocess.py` : nettoyage texte, séparation titre/auteur, fusion fragments
- Fuzzy matching via `rapidfuzz` + API livres
- Structure JSON de sortie complète
- `eval.py` : taux de détection, CER, taux d'identification
- Dataset 20-30 photos annotées

**M3 — Intégration & Évaluation (WS1, WS2, WS3, WS4, WS5)** :
- Cas limites : étagères partielles, livres fins, non-livres
- Visualisation bounding boxes sur image originale
- Comparaison quantitative modèles OCR (CER par modèle)
- Fallback OCR si confiance < seuil
- Interface Streamlit complète : onglets, tableau, export CSV, correction manuelle
- Évaluation complète sur tout le dataset

**M4 — Finalisation & Soutenance (WS1, WS2, WS3, WS4, WS5)** :
- Nettoyage code : code mort, commentaires, docstrings
- Images de démo fiables pour la soutenance
- README final (installation, architecture, résultats)
- Slides (~10 diapositives)

## Principes clés

1. **Alignement plan/spec** : chaque tâche indique son workstream, milestone et section de spec.
2. **Tâches testables** : critères d'acceptation mesurables (pas d'énoncés vagues).
3. **Commits TDD** : RED (tests échouants) puis GREEN (implémentation).
4. **Branche et PR** : `task/NNN-short-slug` depuis `main`, PR vers `main`.
5. **Dépendances explicites** : dans `Contexte > Dépendances`.
6. **Granularité** : une tâche = un résultat livrable principal. Si trop large, découper.

## Valeurs de statut

- `TODO` — non commencée
- `IN_PROGRESS` — en cours
- `DONE` — terminée, critères validés
