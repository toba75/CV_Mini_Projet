# Tâche — Tester l'API bibliographique Google Books / Open Library

Statut : DONE
Ordre : 006
Workstream : WS4
Milestone : M1

## Contexte
L'enrichissement des résultats OCR passe par une requête vers une API bibliographique pour corriger les erreurs et récupérer les métadonnées complètes. Avant d'intégrer cette fonctionnalité dans le pipeline, il faut valider que l'API fonctionne correctement : envoi d'un titre connu, vérification du retour JSON, gestion des cas d'erreur.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M1 > WS4 — point 1)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 6 — Post-traitement et enrichissement, §4 Stack technique)
- Code : `src/postprocess.py` (ou un module dédié `src/book_api.py`)

Dépendances :
- Tâche 001 — Initialiser la structure du projet (doit être DONE)

## Objectif
Implémenter un module de requête vers l'API Google Books et/ou Open Library. Vérifier que l'envoi d'un titre connu retourne des métadonnées correctes (titre, auteur, ISBN).

## Règles attendues
- Utiliser la bibliothèque `requests` pour les appels HTTP.
- Gérer proprement les erreurs réseau (timeout, HTTP 4xx/5xx) avec des exceptions explicites.
- Ne pas stocker de clés API en dur dans le code (utiliser des variables d'environnement si nécessaire).
- Les fonctions doivent être testables sans appel réseau réel (prévoir le mocking).

## Évolutions proposées
- Fonction `search_book(query: str, provider: str = "openlibrary") -> list[dict]` : recherche un livre par titre/texte et retourne une liste de candidats avec `{"title": str, "author": str, "isbn": str | None, "provider": str}`.
- Fonction `get_book_metadata(isbn: str, provider: str = "openlibrary") -> dict | None` : récupère les métadonnées complètes d'un livre par ISBN.
- Support de deux providers : `"openlibrary"` (gratuit, sans clé) et `"googlebooks"`.
- Gestion du timeout (défaut 10s) et des réponses vides.

## Critères d'acceptation
- [x] `search_book` retourne une liste de dictionnaires avec les clés `title`, `author`, `isbn`, `provider`
- [x] `search_book("Le Petit Prince")` retourne au moins un résultat pertinent (test avec mock)
- [x] `search_book` retourne une liste vide pour une requête sans résultat (pas d'exception)
- [x] Les erreurs réseau (timeout, 5xx) lèvent des exceptions explicites (`ConnectionError`, `TimeoutError`)
- [x] Aucune clé API n'est codée en dur dans le source
- [x] Tests utilisent le mocking (pas d'appels réseau réels dans les tests unitaires)
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/006-api-books-test` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/006-api-books-test` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS4] #006 RED: tests API bibliographique`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS4] #006 GREEN: API bibliographique fonctionnelle`.
- [ ] **Pull Request ouverte** vers `main` : `[WS4] #006 — API bibliographique`.
