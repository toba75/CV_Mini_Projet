# Tâche — Création des diapositives de soutenance

Statut : TODO
Ordre : 033
Workstream : WS5
Milestone : M4

## Contexte
Les diapositives sont un livrable obligatoire (spec §9, point 1). La présentation orale dure 20 minutes et doit couvrir la problématique, l'architecture, les choix techniques, les résultats et une démo live. Le plan imposé contient 10 diapositives.

Références :
- Plan : `docs/plan/implementation_plan.md` (M4 > WS5 — « Créer les slides (~10 diapositives) »)
- Spécification : `docs/specifications/specifications.md` (§9 — Livrables, point 1 : diapositives de présentation)
- Code : N/A (livrable documentaire)

Dépendances :
- Tâche 032 — README final (doit être DONE)
- Tâche 027 — Évaluation complète (doit être DONE)

## Objectif
Créer un jeu de ~10 diapositives Markdown (ou export PDF) dans `docs/slides/` couvrant le plan imposé : titre, problématique, état de l'art, architecture, prétraitement, détection, OCR, post-traitement, résultats, démo et conclusion.

## Règles attendues
- Contenu en français.
- Visuels inclus : schéma du pipeline, captures d'écran des étapes, tableau de métriques.
- Chaque diapositive doit pouvoir être présentée en ~2 minutes.
- Les résultats quantitatifs doivent correspondre aux métriques de l'évaluation M3.
- Préparer les réponses aux questions probables (dans des notes de présentation).

## Évolutions proposées
- Création du répertoire `docs/slides/`.
- Création du fichier `docs/slides/soutenance.md` (format Marp / reveal.js) avec les 10 diapositives :
  1. Titre + équipe.
  2. Problématique et motivation.
  3. État de l'art (OCR scene text, méthodes du cours).
  4. Architecture du pipeline (schéma).
  5. Prétraitement et segmentation (avec visuels).
  6. Détection de texte + correction d'orientation (avec visuels).
  7. Reconnaissance OCR — comparaison des modèles.
  8. Post-traitement et enrichissement API.
  9. Résultats quantitatifs (tableau de métriques) + cas d'échec.
  10. Démo live + conclusion et perspectives.
- Création de `docs/slides/notes_orateur.md` avec les réponses aux questions probables :
  - « Pourquoi ce modèle OCR plutôt qu'un autre ? »
  - « Comment gérez-vous le texte vertical ? »
  - « Quelles sont les limites ? »
  - « Comment améliorer les résultats ? »

## Critères d'acceptation
- [ ] Répertoire `docs/slides/` créé avec le fichier de diapositives.
- [ ] 10 diapositives couvrant le plan imposé (titre → conclusion).
- [ ] Schéma d'architecture du pipeline inclus dans les slides.
- [ ] Tableau de métriques avec résultats quantitatifs réels inclus.
- [ ] Notes de présentation avec réponses aux 4 questions probables.
- [ ] Contenu cohérent avec le README et les résultats d'évaluation.
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords.
- [ ] Suite de tests verte après implémentation.
- [ ] `ruff check` passe sans erreur.

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/033-slides-presentation` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/033-slides-presentation` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS-5] #033 RED: <résumé>` (fichiers de tests uniquement).
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-5] #033 GREEN: <résumé>`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-5] #033 — Création des diapositives de soutenance`.
