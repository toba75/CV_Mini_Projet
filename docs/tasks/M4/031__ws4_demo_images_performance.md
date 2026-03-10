# Tâche — Préparation images de démo et validation performance

Statut : TODO
Ordre : 031
Workstream : WS4
Milestone : M4

## Contexte
Pour la soutenance, il faut disposer de 3-4 images de démo fiables produisant de bons résultats, et s'assurer que le pipeline s'exécute en moins de 30 secondes par image sur un laptop standard. Ces images serviront à la démo live.

Références :
- Plan : `docs/plan/implementation_plan.md` (M4 > WS4 — « Préparer 3-4 images de démo fiables » + « démo tourne en < 30s »)
- Spécification : `docs/specifications/specifications.md` (§6 — Métriques, temps de traitement < 30s ; §7 — Démonstration)
- Code : `src/pipeline.py`, `src/app.py`

Dépendances :
- Tâche 029 — Nettoyage du code (doit être DONE)

## Objectif
Sélectionner et valider 3-4 images d'étagères produisant des résultats OCR corrects et visuellement convaincants. Mesurer le temps d'exécution du pipeline sur chaque image et s'assurer qu'il reste sous 30 secondes. Stocker ces images dans `data/demo/` avec un fichier décrivant les résultats attendus.

## Règles attendues
- Les images de démo doivent être des photos réelles (pas synthétiques) présentes dans le dépôt.
- Chaque image doit produire au minimum 3 livres correctement identifiés.
- Le temps d'exécution complet (prétraitement → JSON) doit être < 30s par image.
- Les résultats attendus doivent être documentés pour vérification rapide en soutenance.

## Évolutions proposées
- Création du répertoire `data/demo/` avec 3-4 images sélectionnées.
- Création d'un fichier `data/demo/expected_results.json` avec les résultats attendus par image.
- Ajout d'un script ou test de benchmark mesurant le temps d'exécution sur chaque image de démo.
- Vérification que `app.py` (Streamlit) charge et traite les images de démo sans erreur.

## Critères d'acceptation
- [ ] 3-4 images de démo présentes dans `data/demo/`.
- [ ] Chaque image produit au moins 3 livres correctement identifiés par le pipeline.
- [ ] Temps d'exécution du pipeline < 30s par image (mesuré et documenté).
- [ ] Fichier `data/demo/expected_results.json` décrivant les résultats attendus.
- [ ] L'interface Streamlit charge et traite les images de démo sans erreur.
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords.
- [ ] Suite de tests verte après implémentation.
- [ ] `ruff check` passe sans erreur.

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/031-demo-images-performance` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/031-demo-images-performance` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS-4] #031 RED: <résumé>` (fichiers de tests uniquement).
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-4] #031 GREEN: <résumé>`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-4] #031 — Préparation images de démo et validation performance`.
