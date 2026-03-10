# Tâche — Nettoyage complet du code source

Statut : TODO
Ordre : 029
Workstream : WS1
Milestone : M4

## Contexte
Le code source du pipeline ShelfScan est fonctionnel après M3, mais doit être nettoyé avant la soutenance : suppression du code mort, vérification des imports, ajout des docstrings manquantes, et conformité ruff stricte sur l'ensemble du projet.

Références :
- Plan : `docs/plan/implementation_plan.md` (M4 > WS1/WS2/WS3 — Code)
- Spécification : `docs/specifications/specifications.md` (§9 — Livrables, point 2 : code source)
- Code : `src/*.py`

Dépendances :
- Tâche 028 — Analyse des échecs (doit être DONE)

## Objectif
Nettoyer l'ensemble des modules `src/` et `tests/` : supprimer le code mort, les `print()` de debug, les `TODO` orphelins, vérifier que tous les imports sont utilisés, et ajouter les docstrings de module manquantes. Le code doit être prêt pour une revue de soutenance.

## Règles attendues
- Aucun `print()` résiduel dans `src/` (sauf `app.py` pour Streamlit où `st.*` est utilisé).
- Aucun `# TODO`, `# FIXME`, `# HACK`, `# XXX` orphelin.
- Aucun import inutilisé.
- Aucune variable assignée mais jamais lue.
- Docstring de module présente dans chaque fichier `src/*.py`.
- `ruff check src/ tests/` passe sans erreur ni warning.

## Évolutions proposées
- Passe de nettoyage sur chaque fichier `src/*.py` : suppression code mort, imports inutilisés.
- Ajout de docstrings de module manquantes (une ligne descriptive par fichier).
- Vérification que chaque fonction publique a une docstring minimale.
- Suppression des commentaires obsolètes ou redondants.
- Exécution de `ruff check --fix src/ tests/` pour corriger les problèmes auto-fixables.

## Critères d'acceptation
- [ ] `ruff check src/ tests/` retourne 0 erreur, 0 warning.
- [ ] `grep -r "print(" src/` ne retourne aucun résultat (hors `app.py` utilisant `st.*`).
- [ ] `grep -rn "# TODO\|# FIXME\|# HACK\|# XXX" src/ tests/` ne retourne aucun résultat.
- [ ] Chaque fichier `src/*.py` possède une docstring de module.
- [ ] Aucun import inutilisé détecté par ruff (F401).
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords (pas de régression).
- [ ] Suite de tests verte après implémentation.
- [ ] `ruff check` passe sans erreur.

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/029-code-cleanup` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/029-code-cleanup` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS-1] #029 RED: <résumé>` (fichiers de tests uniquement).
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-1] #029 GREEN: <résumé>`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-1] #029 — Nettoyage complet du code source`.
