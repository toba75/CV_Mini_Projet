# Tâche — Vérification reproductibilité du pipeline

Statut : TODO
Ordre : 030
Workstream : WS5
Milestone : M4

## Contexte
Avant la soutenance, il faut s'assurer que le pipeline est reproductible : installation propre via `requirements.txt`, exécution de `pipeline.py` de bout en bout sur une image, et résultat déterministe. C'est un prérequis pour que la démo soit fiable.

Références :
- Plan : `docs/plan/implementation_plan.md` (M4 > WS1/WS2/WS3 — « Vérifier que pip install + python pipeline.py fonctionne sur une machine propre »)
- Spécification : `docs/specifications/specifications.md` (§9 — Livrables, point 2 : code source)
- Code : `src/pipeline.py`, `requirements.txt`

Dépendances :
- Tâche 029 — Nettoyage du code (doit être DONE)

## Objectif
Valider que le pipeline complet s'exécute sans erreur depuis une installation propre : `pip install -r requirements.txt` suivi de l'appel à `pipeline.py` sur une image de test. Vérifier que le résultat JSON est produit et cohérent.

## Règles attendues
- Le `requirements.txt` doit contenir toutes les dépendances nécessaires avec des bornes de version.
- `pipeline.py` doit être exécutable en ligne de commande avec un chemin d'image en argument.
- Le résultat doit être un fichier JSON valide dans `outputs/`.
- Aucune dépendance implicite (variable d'environnement, fichier de config non versionné).

## Évolutions proposées
- Vérification et correction du `requirements.txt` : bornes de version compatibles, pas de dépendance manquante.
- Ajout d'un test d'intégration qui exécute le pipeline de bout en bout sur une image synthétique.
- Vérification que `pipeline.py` accepte un argument en ligne de commande et produit un JSON valide.
- Test que les répertoires de sortie sont créés automatiquement.

## Critères d'acceptation
- [ ] `pip install -r requirements.txt` s'exécute sans erreur sur Python 3.10+.
- [ ] `python -m src.pipeline <image_path>` produit un fichier JSON dans `outputs/`.
- [ ] Le JSON de sortie est valide et contient les clés attendues (titre, auteur, confiance).
- [ ] Un test d'intégration valide le pipeline de bout en bout sur une image synthétique.
- [ ] Aucune variable d'environnement requise non documentée.
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords.
- [ ] Suite de tests verte après implémentation.
- [ ] `ruff check` passe sans erreur.

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/030-pipeline-reproducibility` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/030-pipeline-reproducibility` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS-5] #030 RED: <résumé>` (fichiers de tests uniquement).
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-5] #030 GREEN: <résumé>`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-5] #030 — Vérification reproductibilité du pipeline`.
