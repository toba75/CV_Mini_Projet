# Tâche — Interface Streamlit complète avec onglets

Statut : DONE
Ordre : 025
Workstream : WS4
Milestone : M3

## Contexte
Le scaffold Streamlit minimal (M1, tâche 007) permet l'upload d'image et l'affichage basique. Il faut maintenant construire l'interface complète avec une vue étape par étape du pipeline, un tableau interactif des résultats, et un bouton d'export CSV.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS4)
- Spécification : `docs/specifications/specifications.md` (§7 — Démonstration)
- Code : `src/app.py`, `src/pipeline.py`

Dépendances :
- Tâche 007 — Scaffold Streamlit (doit être DONE)
- Tâche 016 — Structure JSON sortie (doit être DONE)
- Tâche 020 — Visualisation bounding boxes (doit être DONE)

## Objectif
Finaliser l'interface Streamlit avec une navigation par onglets montrant chaque étape du pipeline, un tableau interactif des résultats avec scores de confiance, et un export CSV.

## Règles attendues
- Interface en français pour les labels et en anglais pour le code
- L'interface doit être responsive et utilisable sans documentation
- Chaque onglet doit afficher les résultats intermédiaires de l'étape correspondante

## Évolutions proposées
- Implémenter 5 onglets : Original → Prétraitement → Segmentation → OCR → Inventaire
- Onglet Original : image uploadée + métadonnées (taille, résolution)
- Onglet Prétraitement : image après CLAHE et correction de perspective
- Onglet Segmentation : image avec bounding boxes des tranches (via tâche 020)
- Onglet OCR : texte détecté par tranche avec score de confiance
- Onglet Inventaire : tableau interactif (titre, auteur, ISBN, confiance) + bouton export CSV
- Ajouter une barre de progression pendant le traitement

## Critères d'acceptation
- [x] 5 onglets fonctionnels correspondant aux étapes du pipeline
- [x] Chaque onglet affiche les résultats intermédiaires pertinents
- [x] Tableau interactif des résultats avec tri et filtrage
- [x] Bouton d'export CSV fonctionnel générant un fichier téléchargeable
- [x] Barre de progression pendant le traitement
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/025-streamlit-full-interface` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `milestone/M3` utilisée (selon instructions).
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-4] #025 RED: tests interface Streamlit complète`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [x] **Commit GREEN** : `[WS-4] #025 GREEN: interface Streamlit complète`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-4] #025 — Interface Streamlit complète avec onglets`.
