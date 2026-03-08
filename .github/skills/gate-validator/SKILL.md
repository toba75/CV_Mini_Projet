---
name: gate-validator
description: Valide les gates du plan ShelfScan (M1..M4, G-Segment, G-OCR, G-Pipeline, G-Eval) en vérifiant les livrables, tests, et conformité spec. À utiliser pour auditer un gate avant revue de milestone.
argument-hint: "[gate: M1|M2|M3|M4|G-Segment|G-OCR|G-Pipeline|G-Eval|all] [mode: check|report]"
---

# Agent Skill — Gate Validator (ShelfScan)

## Objectif
Auditer un ou plusieurs gates du plan d'implémentation ShelfScan et produire un verdict structuré (GO / NO-GO / GO AVEC RÉSERVES) avec preuves.

## Contexte repo

- **Plan (source des gates)** : `docs/plan/implementation_plan.md`
- **Spécification** : `docs/specifications/specifications.md`
- **Tâches** : `docs/tasks/`
- **Code source** : `src/`
- **Tests** : `tests/`
- **Outputs** : `outputs/`
- **Data** : `data/ground_truth/`

## Registre des gates

### Gates intra-milestone

#### G-Segment — Segmentation des tranches fonctionnelle (après WS1.M2, avant WS2.M2)

| # | Critère | Seuil | Preuve attendue |
|---|---|---|---|
| S.1 | Crops individuels produits | ≥ 1 crop par image test | Test sur image de test avec livres connus |
| S.2 | Canny + HoughLinesP paramétré | Params documentés et justifiés | Code commenté + test avec image synthétique |
| S.3 | Correction de perspective | Homographie appliquée si détectée | Test avec image inclinée synthétique |
| S.4 | Crops reproductibles | Résultats identiques sur relance | Test de déterminisme |

#### G-OCR — Comparaison OCR et sélection du modèle (après WS3.M1, avant WS3.M2)

| # | Critère | Seuil | Preuve attendue |
|---|---|---|---|
| O.1 | Trois modèles testés | PaddleOCR + TrOCR + Tesseract | Notebook de comparaison ou script de test |
| O.2 | CER calculé correctement | Distance Levenshtein / len(ref) | Test unitaire sur exemple calculé à la main |
| O.3 | Modèle principal sélectionné | Décision documentée | Commentaire dans `src/ocr.py` ou README |

#### G-Pipeline — Pipeline bout-en-bout fonctionnel (après M2)

| # | Critère | Seuil | Preuve attendue |
|---|---|---|---|
| P.1 | `pipeline.py` prend une image en entrée | Fonctionnel | `python src/pipeline.py --image data/raw/test.jpg` |
| P.2 | Sortie JSON produite | Format conforme à la spec | Test de parsing JSON sur la sortie |
| P.3 | Temps de traitement | < 30s par image | Mesure sur laptop standard |
| P.4 | Pas de crash sur 3 images variées | 0 exception non gérée | Test d'intégration sur images de test |

#### G-Eval — Métriques calculées sur dataset annoté (après M3)

| # | Critère | Seuil | Preuve attendue |
|---|---|---|---|
| E.1 | Dataset annoté | ≥ 20 photos + ground truth CSV | Fichier `data/ground_truth/*.csv` |
| E.2 | Taux de détection | ≥ 80% | `python src/eval.py` → rapport |
| E.3 | CER moyen | ≤ 20% | Rapport `eval.py` |
| E.4 | Taux d'identification | ≥ 60% | Rapport `eval.py` |
| E.5 | Temps moyen / image | < 30s | Rapport `eval.py` |

### Gates de milestone

#### M1 — Setup & Prototype

| # | Critère | Preuve attendue |
|---|---|---|
| M1.1 | Repo structuré | `src/`, `data/`, `outputs/`, `tests/`, `requirements.txt` présents |
| M1.2 | Dépendances installables | `pip install -r requirements.txt` sans erreur |
| M1.3 | Pipeline naïf fonctionnel | Une image en entrée → texte brut en sortie (même grossier) |
| M1.4 | Premier test API livres | Requête sur titre connu → JSON retourné |

#### M2 — Pipeline complet

| # | Critère | Preuve attendue |
|---|---|---|
| M2.1 | G-Segment GO | Tous critères S.1-S.4 |
| M2.2 | G-OCR GO | Tous critères O.1-O.3 |
| M2.3 | G-Pipeline GO | Tous critères P.1-P.4 |
| M2.4 | Tests unitaires GREEN | `pytest tests/ -v` → 0 échec |

#### M3 — Intégration & Évaluation

| # | Critère | Preuve attendue |
|---|---|---|
| M3.1 | G-Eval GO | Tous critères E.1-E.5 |
| M3.2 | Interface Streamlit fonctionnelle | Démo jouable bout-en-bout |
| M3.3 | Export CSV fonctionnel | Fichier CSV généré et parseable |
| M3.4 | Cas limites documentés | 3-5 cas d'échec identifiés dans le rapport |

#### M4 — Finalisation

| # | Critère | Preuve attendue |
|---|---|---|
| M4.1 | README complet | Installation + architecture + résultats + limites |
| M4.2 | Slides préparées | ~10 diapositives |
| M4.3 | Démo tourne en < 30s | Mesure sur laptop utilisé en soutenance |
| M4.4 | Code nettoyé | 0 `print()` debug, 0 TODO orphelin (`ruff check` clean) |

## Workflow de validation

1. **Identifier le gate demandé** (ou `all`).
2. **Vérifier les prérequis** : gates intra-milestone avant gate de milestone.
3. **Parcourir le registre** : pour chaque critère, vérifier la preuve.
4. **Exécuter les tests** si mode `check`.
5. **Produire le verdict** par critère.

## Format du rapport de sortie

```markdown
# Rapport de validation — Gate [ID]

Date : [YYYY-MM-DD]
Milestone : [M1..M4]
Verdict global : [GO | NO-GO | GO AVEC RÉSERVES]

## Détail par critère

| # | Critère | Verdict | Preuve / Remarque |
|---|---|---|---|
| X.1 | … | GO | `chemin/vers/preuve` |
| X.2 | … | NO-GO | Absent : [ce qui manque] |

## Actions requises (si NO-GO)
1. [Action corrective 1]
```

## Ordre d'exécution des gates

```
M1 → G-Segment → G-OCR → M2 → G-Pipeline → M3 → G-Eval → M4
```

## Principes

- **Factuel** : ne pas inférer de conformité sans preuve tangible.
- **Traçable** : chaque verdict cite le chemin du fichier ou le nom du test.
- **Incrémental** : un gate peut être audité plusieurs fois ; seul le dernier rapport fait foi.
