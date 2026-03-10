# Tâche — Rédaction du README final

Statut : DONE
Ordre : 032
Workstream : WS5
Milestone : M4

## Contexte
Le README est un livrable obligatoire de la soutenance (spec §9). Il doit documenter l'installation, l'architecture du pipeline, la stack technique, les instructions de démo, et les résultats obtenus avec leurs limites. C'est la porte d'entrée du dépôt pour l'évaluateur.

Références :
- Plan : `docs/plan/implementation_plan.md` (M4 > WS5 — « Rédiger le README final »)
- Spécification : `docs/specifications/specifications.md` (§9 — Livrables, point 3 : README)
- Code : `README.md` (à créer à la racine du projet)

Dépendances :
- Tâche 030 — Reproductibilité pipeline (doit être DONE)
- Tâche 031 — Images de démo (doit être DONE)

## Objectif
Rédiger un `README.md` complet à la racine du projet couvrant : installation, architecture du pipeline (avec schéma ASCII ou Mermaid), stack technique, instructions pour reproduire la démo, résultats quantitatifs obtenus, et limites identifiées.

## Règles attendues
- Rédigé en français (langue du projet et de la soutenance).
- Schéma d'architecture du pipeline inclus (ASCII art ou diagramme Mermaid).
- Instructions d'installation testées et reproductibles.
- Résultats quantitatifs issus de l'évaluation M3 (taux de détection, CER, taux d'identification, temps).
- Limites honnêtement documentées.

## Évolutions proposées
- Création de `README.md` à la racine avec les sections suivantes :
  1. Titre et description du projet.
  2. Installation et dépendances (`pip install -r requirements.txt`).
  3. Stack technique (Python, OpenCV, PaddleOCR/TrOCR/Tesseract, Streamlit, etc.).
  4. Architecture du pipeline (schéma 6 étapes).
  5. Utilisation : ligne de commande (`pipeline.py`) et interface Streamlit (`app.py`).
  6. Résultats obtenus (tableau de métriques).
  7. Limites et perspectives d'amélioration.
  8. Structure du dépôt.
- Ajout d'un test vérifiant l'existence et la structure minimale du README.

## Critères d'acceptation
- [x] Fichier `README.md` présent à la racine du projet.
- [x] Section installation avec commandes `pip install` exactes.
- [x] Section architecture avec schéma du pipeline (6 étapes).
- [x] Section stack technique listant les composants principaux.
- [x] Section utilisation avec exemples de commande (pipeline CLI + Streamlit).
- [x] Section résultats avec tableau de métriques (taux détection, CER, taux identification, temps).
- [x] Section limites avec au moins 3 limites identifiées.
- [x] Tests couvrent les scénarios nominaux + erreurs + bords.
- [x] Suite de tests verte après implémentation.
- [x] `ruff check` passe sans erreur.

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/032-readme-final` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/032-readme-final` créée depuis `milestone/M4`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-5] #032 RED: tests pour README final (existence, sections, métriques, limites)`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [x] **Commit GREEN** : `[WS-5] #032 GREEN: README final rédigé`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-5] #032 — Rédaction du README final`.
