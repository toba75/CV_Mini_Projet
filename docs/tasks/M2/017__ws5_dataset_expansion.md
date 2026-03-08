# Tâche — Étendre le dataset à 20-30 photos annotées

Statut : TODO
Ordre : 017
Workstream : WS5
Milestone : M2

## Contexte
Le dataset initial de M1 contient 15 photos d'étagères (IMG_3046 à IMG_3061) avec des annotations CSV de ground truth. Pour évaluer le pipeline de manière significative, il faut atteindre 20 à 30 photos couvrant des conditions variées (éclairage, angle, densité, types de livres) et compléter les annotations.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS5 — point 1)
- Spécification : `docs/specifications/specifications.md` (§5.1 Dataset de développement — 20-30 photos)
- Données : `data/raw/`, `data/ground_truth/`

Dépendances :
- Tâche 008 — Dataset initial et ground truth (doit être DONE)

## Objectif
Étendre le dataset à 20-30 photos d'étagères variées. Annoter manuellement chaque nouvelle photo avec les titres visibles dans un fichier CSV de ground truth, en suivant le format établi en M1.

## Règles attendues
- Les photos doivent être en JPEG, résolution minimale 1920×1080.
- Variété des conditions : éclairages différents, angles légers, étagères denses et clairsemées, livres de tailles variées.
- Le format CSV de ground truth doit être cohérent avec celui de M1.
- Chaque photo doit avoir au moins 3 livres visibles avec texte lisible.
- Les annotations doivent être vérifiées (pas de fautes de frappe dans les titres).

## Évolutions proposées
- Ajouter 5-15 nouvelles photos dans `data/raw/`.
- Créer/mettre à jour les fichiers CSV correspondants dans `data/ground_truth/`.
- Documenter les conditions de prise de vue pour chaque lot de photos (éclairage, angle, appareil).
- Vérifier que le script de chargement existant (`src/eval_utils.py` ou équivalent) fonctionne avec les nouvelles photos.

## Critères d'acceptation
- [ ] Le dataset contient au moins 20 photos d'étagères
- [ ] Chaque photo a un fichier CSV de ground truth associé
- [ ] Le format CSV est cohérent avec celui de M1 (mêmes colonnes et conventions)
- [ ] Les photos couvrent au moins 3 conditions d'éclairage différentes
- [ ] Les photos incluent des étagères denses (>10 livres) et clairsemées (<5 livres)
- [ ] Les annotations sont vérifiées et sans fautes de frappe évidentes
- [ ] Le script de chargement existant fonctionne avec les nouvelles photos
- [ ] Suite de tests verte après ajout (pas de régression)
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/017-dataset-expansion` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/017-dataset-expansion` créée depuis `main`.
- [ ] Nouvelles photos ajoutées dans `data/raw/`.
- [ ] Annotations CSV créées dans `data/ground_truth/`.
- [ ] Vérification du chargement avec le code existant.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS5] #017 GREEN: dataset étendu à 20+ photos annotées`.
- [ ] **Pull Request ouverte** vers `main` : `[WS5] #017 — Extension dataset`.
