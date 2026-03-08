# Tâche — Test et gestion des cas difficiles de détection

Statut : DONE
Ordre : 022
Workstream : WS2
Milestone : M3

## Contexte
Certaines tranches de livres présentent des cas difficiles pour la détection de texte : texte en arc de cercle, texte très petit, polices fantaisie ou décoratives, texte doré sur fond sombre. Il faut tester systématiquement ces cas et adapter le pipeline si possible.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS2)
- Spécification : `docs/specifications/specifications.md` (§8 — Risques : polices décoratives)
- Code : `src/detect_text.py`, `src/ocr.py`

Dépendances :
- Tâche 021 — Optimisation seuils détection (doit être DONE)
- Tâche 012 — Correction d'orientation (doit être DONE)

## Objectif
Identifier et documenter les cas difficiles de détection/reconnaissance, et implémenter des améliorations ciblées là où c'est faisable dans le cadre du projet.

## Règles attendues
- Constituer un sous-ensemble de test dédié aux cas difficiles
- Documenter les résultats qualitatifs (captures, taux de succès)
- Ne pas sur-optimiser : accepter les limites et les documenter pour la soutenance

## Évolutions proposées
- Identifier dans le dataset existant les images contenant des cas difficiles
- Créer des crops de test dédiés (texte arc, petit texte, police fantaisie, texte doré)
- Tester le pipeline actuel sur ces cas et mesurer les performances
- Implémenter des améliorations ciblées (prétraitement renforcé, seuils adaptatifs)
- Documenter les cas où le pipeline échoue (utile pour la soutenance, tâche 028)

## Critères d'acceptation
- [x] Au moins 5 cas difficiles identifiés et documentés
- [x] Résultats du pipeline mesurés sur chaque cas difficile
- [x] Améliorations ciblées implémentées si faisable
- [x] Documentation des limites pour chaque type de cas difficile
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Cas difficiles identifiés et limites

### 1. Texte très petit (fine texture)
- **Symptôme** : texte de quelques pixels de haut, illisible par OCR.
- **Amélioration** : sharpening via `enhance_for_difficult_text()` augmente la netteté (Laplacian variance).
- **Limite** : si le texte fait < 8px de haut, même le sharpening ne suffit pas ; l'OCR ne peut pas reconnaître.

### 2. Faible contraste (texte doré sur fond sombre)
- **Symptôme** : delta luminosité < 15 entre texte et fond, détection et OCR échouent.
- **Amélioration** : CLAHE agressive (`clip_limit=4.0`, `tile_grid_size=(4,4)`) dans `enhance_for_difficult_text()` augmente le range d'intensité.
- **Limite** : si le contraste original est < 5 niveaux, le CLAHE amplifie aussi le bruit.

### 3. Spine très étroit (< 30px de large)
- **Symptôme** : très peu de pixels pour le texte, détections avec area < 100 filtrées.
- **Amélioration** : les filtres `filter_small_regions` et `filter_by_aspect_ratio` éliminent les faux positifs.
- **Limite** : le texte réel sur un spine < 20px est rarement détectable ; accepté comme limite du projet.

### 4. Image très bruitée
- **Symptôme** : bruit gaussien fort génère des fausses détections.
- **Amélioration** : le pipeline ne crash pas ; les filtres de taille et ratio éliminent les artefacts.
- **Limite** : si le SNR est très bas, les détections valides sont aussi filtrées.

### 5. Image uniforme (pas de texte)
- **Symptôme** : aucune détection retournée.
- **Amélioration** : le pipeline retourne une liste vide sans crash.
- **Limite** : aucune — comportement correct attendu.

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/022-difficult-cases` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/022-difficult-cases` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-2] #022 RED: tests cas difficiles détection`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [x] **Commit GREEN** : `[WS-2] #022 GREEN: gestion cas difficiles détection`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-2] #022 — Test et gestion des cas difficiles de détection`.
