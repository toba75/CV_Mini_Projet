# Tâche — Implémenter le fuzzy matching avec l'API bibliographique

Statut : TODO
Ordre : 015
Workstream : WS4
Milestone : M2

## Contexte
Le texte OCR contient souvent des erreurs qui empêchent une correspondance exacte avec les bases bibliographiques. Le fuzzy matching via `rapidfuzz` permet de scorer les résultats de l'API livres et de sélectionner le meilleur candidat malgré les erreurs de reconnaissance.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS4 — point 1)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 6 — Post-traitement et enrichissement, fuzzy matching)
- Code : `src/postprocess.py` (ou module dédié)

Dépendances :
- Tâche 006 — Test API bibliographique (doit être DONE)
- Tâche 014 — Post-traitement texte (doit être DONE)

## Objectif
Implémenter un module de fuzzy matching qui, pour chaque texte OCR post-traité, interroge l'API bibliographique et sélectionne le meilleur candidat en utilisant `rapidfuzz` pour scorer la similarité entre le texte OCR et les titres retournés par l'API.

## Règles attendues
- Utiliser `rapidfuzz` (pas `fuzzywuzzy`) pour le scoring de similarité.
- Seuil de confiance configurable (par défaut 60%) en dessous duquel aucun match n'est retourné.
- Les appels API doivent être mockés dans les tests (pas d'appels réseau).
- Gérer proprement les cas où l'API ne retourne aucun résultat.
- Le module doit être découplé du moteur OCR (reçoit du texte, pas des images).

## Évolutions proposées
- Fonction `fuzzy_match_title(ocr_text: str, candidates: list[dict], threshold: float = 60.0) -> dict | None` : compare le texte OCR avec les titres candidats via `rapidfuzz.fuzz.ratio`. Retourne le meilleur candidat au-dessus du seuil, ou `None`.
- Fonction `identify_book(ocr_text: str, provider: str = "openlibrary", threshold: float = 60.0) -> dict | None` : orchestre la recherche API + fuzzy matching. Retourne `{"title": str, "author": str, "isbn": str | None, "confidence": float, "provider": str}` ou `None`.
- Fonction `identify_books(spine_results: list[dict], provider: str = "openlibrary", threshold: float = 60.0) -> list[dict]` : applique `identify_book` sur une liste de résultats de post-traitement. Retourne un résultat enrichi par tranche.

## Critères d'acceptation
- [ ] `fuzzy_match_title` retourne le meilleur candidat quand le score dépasse le seuil
- [ ] `fuzzy_match_title` retourne `None` quand aucun candidat ne dépasse le seuil
- [ ] `fuzzy_match_title` gère une liste vide de candidats (retourne `None`)
- [ ] `identify_book` intègre correctement la recherche API et le fuzzy matching
- [ ] `identify_book` retourne `None` quand l'API ne retourne aucun résultat
- [ ] `identify_books` traite correctement une liste de résultats de post-traitement
- [ ] Le seuil de confiance est configurable et respecté
- [ ] Tests utilisent le mocking pour l'API (pas d'appels réseau)
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords (texte vide, aucun candidat, score limite)
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/015-fuzzy-matching` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/015-fuzzy-matching` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS4] #015 RED: tests fuzzy matching API`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS4] #015 GREEN: fuzzy matching implémenté`.
- [ ] **Pull Request ouverte** vers `main` : `[WS4] #015 — Fuzzy matching`.
