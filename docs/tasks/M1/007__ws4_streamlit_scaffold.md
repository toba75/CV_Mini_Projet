# Tâche — Scaffolder l'application Streamlit minimale

Statut : TODO
Ordre : 007
Workstream : WS4
Milestone : M1

## Contexte
L'interface de démonstration ShelfScan utilise Streamlit. En M1, il s'agit de mettre en place le squelette minimal de l'application : upload d'une image et affichage simple. Cette base sera enrichie en M2-M3 avec les résultats du pipeline.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M1 > WS4 — point 2)
- Spécification : `docs/specifications/specifications.md` (§7 Démonstration)
- Code : `src/app.py` (ou `app.py` à la racine)

Dépendances :
- Tâche 001 — Initialiser la structure du projet (doit être DONE)

## Objectif
Créer une application Streamlit minimale permettant d'uploader une image d'étagère et de l'afficher. L'app doit démarrer sans erreur et être prête à accueillir les résultats du pipeline.

## Règles attendues
- L'application doit être lançable via `streamlit run app.py` (ou `streamlit run src/app.py`).
- Le code Streamlit doit être séparé de la logique métier (pas de traitement d'image dans le fichier Streamlit).
- Interface en français (labels, titres).

## Évolutions proposées
- Créer `src/app.py` avec :
  - Titre de l'application : "ShelfScan — Inventaire de bibliothèque"
  - Widget d'upload d'image (`st.file_uploader`) acceptant JPEG et PNG
  - Affichage de l'image uploadée (`st.image`)
  - Zone placeholder pour les résultats futurs (`st.empty` ou `st.container`)
- Structure modulaire prête pour l'intégration du pipeline en M2.

## Critères d'acceptation
- [ ] `src/app.py` existe et contient une application Streamlit fonctionnelle
- [ ] L'application démarre sans erreur avec `streamlit run src/app.py`
- [ ] L'upload d'image (JPEG, PNG) fonctionne
- [ ] L'image uploadée s'affiche correctement
- [ ] L'interface contient un titre et des labels en français
- [ ] Le code Streamlit ne contient pas de logique de traitement d'image
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/007-streamlit-scaffold` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/007-streamlit-scaffold` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS4] #007 RED: tests scaffold Streamlit`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS4] #007 GREEN: scaffold Streamlit minimal`.
- [ ] **Pull Request ouverte** vers `main` : `[WS4] #007 — Scaffold Streamlit`.
