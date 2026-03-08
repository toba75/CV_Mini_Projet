# AGENTS.md — ShelfScan

## Projet

ShelfScan — Inventaire de bibliothèque par reconnaissance visuelle : pipeline de Computer Vision qui prend en entrée une photographie d'étagère et produit en sortie une liste structurée des ouvrages identifiés (titre, auteur, métadonnées bibliographiques via API).

## Stack

- **Langage** : Python 3.10+
- **Tests** : pytest
- **Linter** : ruff (`line-length = 100`, `target-version = "py310"`)
- **Traitement image** : OpenCV, Pillow
- **Détection texte** : CRAFT ou PaddleOCR
- **OCR** : PaddleOCR / TrOCR / Tesseract
- **Deep Learning** : PyTorch
- **Interface démo** : Streamlit ou Gradio
- **Données** : images JPEG/PNG (`data/raw/`) + annotations CSV (`data/ground_truth/`)
- **Sorties** : JSON et CSV (`outputs/`)

## Documents de référence

- **Spécification** : `docs/specifications/specifications.md`
- **Plan** : `docs/plan/implementation_plan.md` (WS1..WS5, M1..M4)
- **Tâches** : `docs/tasks/<milestone>/NNN__slug.md` (ex : `docs/tasks/M1/001__ws1_preprocess_clahe.md`)

## Règles non négociables

### TDD strict

1. **Pré-condition** : `pytest` GREEN avant de commencer toute tâche.
2. **RED** : écrire les tests d'abord, constater l'échec.
3. **Commit RED** : `git commit -m "[WS-X] #NNN RED: <résumé>"` (fichiers de tests uniquement).
4. **GREEN** : implémenter le minimum pour passer.
5. **Commit GREEN** : `git commit -m "[WS-X] #NNN GREEN: <résumé>"`
   Condition : tests GREEN + critères d'acceptation validés + checklist cochée.
6. Aucun commit intermédiaire sauf refactoring mineur (tests verts).
7. **Branche dédiée** : `task/NNN-short-slug` depuis `main`. Jamais de commit direct sur `main`.
8. **Pull Request obligatoire** vers `main` après commit GREEN.

### Zéro ghost completion

Ne jamais marquer une tâche `DONE` ni cocher `[x]` sans code + tests + exécution vérifiée.

### Reproductibilité

Tout traitement doit être relançable à l'identique avec les mêmes paramètres et les mêmes images d'entrée. Seeds fixées pour toute opération aléatoire.

### Strict code (no fallbacks)

- Le code d'implémentation doit être strict : **aucun fallback silencieux**, aucune valeur par défaut masquant une entrée invalide.
- Préférer la validation explicite + échec (`raise`) à un comportement « best-effort ».
- Éviter les patterns `or default`, `value if value else default`, `except:` trop large.
- Si une décision d'implémentation est ambiguë → **ne rien implémenter** : clarifier la spec d'abord.

### Conventions image

- Ne jamais modifier en place une image d'entrée — travailler sur une copie (`.copy()`).
- Conversions BGR/RGB explicites aux bonnes frontières (OpenCV ↔ modèles deep learning).
- Chemins de fichiers construits avec `pathlib.Path`, pas de concaténation de strings.
- Répertoires de sortie créés avant usage (`mkdir(parents=True, exist_ok=True)`).

### Ambiguïté

Si specs ou tâche ambiguës → demander des clarifications avant d'implémenter.

---

## Structure des workstreams

- **WS1** Prétraitement & Segmentation : chargement image, redimensionnement, CLAHE, correction perspective, Canny + HoughLinesP, crops individuels par tranche
- **WS2** Détection & Orientation : CRAFT ou PaddleOCR en détection seule, bounding boxes orientées, correction d'angle automatique
- **WS3** OCR & Post-traitement : comparaison PaddleOCR / TrOCR / Tesseract, sélection du modèle principal, nettoyage texte, séparation titre/auteur, fusion fragments, fuzzy matching API bibliographique
- **WS4** Interface & Enrichissement : démo Streamlit, appel Google Books API ou Open Library API, export CSV/JSON, mode correction manuelle
- **WS5** Évaluation & Présentation : dataset annoté (20-30 photos), `eval.py` (CER, taux de détection, taux d'identification), tableau de résultats, slides, README final

## Milestones

- **M1** Setup & Prototype rapide (WS1..WS5) : environnement fonctionnel, premier résultat end-to-end sur une image — photo en entrée, texte brut en sortie
- **M2** Pipeline complet fonctionnel (WS1..WS5) : `pipeline.py` automatisé sur n'importe quelle photo, sortie JSON structurée
- **M3** Intégration, évaluation et optimisation (WS1..WS5) : démo Streamlit complète, métriques calculées, cas limites traités
- **M4** Finalisation et soutenance (WS1..WS5) : code nettoyé, README final, slides (~10), répétition orale

## Priorisation

M1 → M2 → M3 → M4 (séquentiel, chaque milestone dépend du précédent).

---

## Skills

Les skills `.github/skills/*/SKILL.md` fournissent des workflows spécialisés invocables par Copilot.

| Skill | Déclencheur | Description |
|---|---|---|
| `implementing-milestone` | « implémente le milestone M1 », « lance MX » | Orchestre le milestone complet : branche milestone, implémentation de chaque tâche via `implementing-task`, revue globale itérative (jusqu'à 5×), PR vers `main`, review GitHub automatique, merge. |
| `implementing-task` | « implémente la tâche #NNN » | Orchestre 4 agents workers : TDD-Implementer (RED→GREEN), TDD-Reviewer (revue), TDD-Fixer (corrections), PR-Review-Fixer (post-review GitHub). Boucle B+C jusqu'à 5× max. |
| `implementing-request-change` | « implémente les request changes 0001 », « corrige les bloquants » | Corrections issues d'un rapport request_changes, par sévérité |
| `pr-reviewer` | « review la PR », « vérifie avant merge » | Revue systématique de PR |
| `task-creator` | « crée les tâches pour WS1 » | Génération de tâches structurées depuis spec/plan |
| `gate-validator` | « valide le gate M2 », « valide G-OCR » | Audit Go/No-Go des gates M1–M4, G-Segment, G-OCR, G-Pipeline, G-Eval |
| `global-review` | « revue globale », « audit du code », « revue de la branche » | Revue complète : cohérence inter-modules pipeline, conformité spec, qualité |
| `test-adherence` | « vérifie l'adhérence des tests », « tests vs spec », « matrice couverture » | Audit croisé tests ↔ spec ↔ tâches : comportements, métriques, anti-patterns |
| `plan-coherence` | « revue du plan », « cohérence du plan », « audit plan » | Orchestre Plan-Corrector + Plan-Analyzer. Itère jusqu'à convergence. |
| `spec-coherence` | « vérifie la cohérence de la spec », « audit des spécifications » | Audit de cohérence intrinsèque : terminologie, flux I/O pipeline, métriques, périmètre |
| `markdown-redaction` | « rédige un document Markdown » | Conventions GFM, mode Corporate FR, templates |

## Custom Agents (workers)

Les agents `.github/agents/*.agent.md` sont des workers invocables comme subagents par les skills orchestrateurs. Ils ne sont pas visibles directement dans le dropdown Copilot (`user-invocable: false`).

> **Modèle** : par défaut, chaque agent hérite du modèle sélectionné dans la session principale. Pour forcer un modèle spécifique, décommenter la ligne `model:` dans le frontmatter de l'agent.

| Agent | Fichier | Utilisé par | Rôle |
|---|---|---|---|
| `TDD-Implementer` | `.github/agents/tdd-implementer.agent.md` | `implementing-task` | Implémentation TDD RED→GREEN |
| `TDD-Reviewer` | `.github/agents/tdd-reviewer.agent.md` | `implementing-task` | Revue de branche (audit complet) |
| `TDD-Fixer` | `.github/agents/tdd-fixer.agent.md` | `implementing-task` | Corrections post-revue |
| `PR-Review-Fixer` | `.github/agents/pr-review-fixer.agent.md` | `implementing-task` | Corrections post-review GitHub |
| `Plan-Corrector` | `.github/agents/plan-corrector.agent.md` | `plan-coherence` | Correction d'une incohérence plan |
| `Plan-Analyzer` | `.github/agents/plan-analyzer.agent.md` | `plan-coherence` | Analyse de cohérence complète (itérative) |

## Instructions automatiques

Les fichiers `.github/instructions/*.instructions.md` sont injectés automatiquement par VS Code Copilot selon le pattern `applyTo` défini dans leur front matter.

| Instruction | Pattern | Description |
|---|---|---|
| `PULL_REQUEST_REVIEW.instructions.md` | `**` (tous fichiers) | Grille d'audit complète pour les revues de PR |

## Conventions de code

- **Nommage** : snake_case (modules, fonctions, variables). Anglais pour le code, français pour la documentation et les tâches.
- **Modules** : `preprocess.py`, `segment.py`, `detect_text.py`, `ocr.py`, `postprocess.py`, `pipeline.py`, `eval.py`.
- **Tests** : structurés par module sous `tests/` (ex. `test_preprocess.py`, `test_ocr.py`). Identifiant tâche `#NNN` dans les docstrings, pas dans les noms de fichiers.
- **Images de test** : synthétiques (numpy arrays) ou fichiers locaux dans `tests/fixtures/`. Jamais de requêtes réseau dans les tests.
- **Chemins** : `pathlib.Path` uniquement. `tmp_path` de pytest pour les fichiers temporaires.
- **Linter** : `ruff check src/ tests/` avant chaque commit.

## Discipline de contexte

- Lire **ciblé** : utiliser grep/recherche et ne charger que les sections pertinentes de la spec.
- Ne pas charger la spécification par défaut : la lire **uniquement si nécessaire**.
- Préférer **exécuter** une commande plutôt que décrire longuement.
