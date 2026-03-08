# Tâche — Implémenter le post-traitement du texte OCR

Statut : TODO
Ordre : 014
Workstream : WS3
Milestone : M2

## Contexte
Le texte brut produit par l'OCR contient souvent des artefacts (caractères parasites, espaces multiples, casse incohérente) et nécessite un traitement pour extraire des informations structurées : séparation titre/auteur, fusion des fragments de texte d'une même tranche, normalisation unicode.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS3 — point 2)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 6 — Post-traitement et enrichissement)
- Code : `src/postprocess.py`

Dépendances :
- Tâche 013 — Intégration OCR pipeline (doit être DONE)

## Objectif
Écrire `src/postprocess.py` avec les fonctions de nettoyage du texte brut OCR, de séparation titre/auteur par heuristiques, et de fusion des fragments de texte issus d'une même tranche.

## Règles attendues
- Texte en entrée : chaînes brutes issues de l'OCR.
- Normalisation unicode (NFC) systématique.
- Pas d'appels réseau dans ce module (le post-traitement est local).
- Les heuristiques de séparation titre/auteur doivent être documentées et configurables.
- Retourner des structures de données claires (dicts avec clés explicites).

## Évolutions proposées
- Fonction `clean_text(raw_text: str) -> str` : supprime les caractères parasites, normalise les espaces, applique la normalisation unicode NFC. Retourne le texte nettoyé.
- Fonction `merge_fragments(fragments: list[str]) -> str` : fusionne une liste de fragments de texte issus de la même tranche en une seule chaîne cohérente. Gère les coupures de mots en fin de ligne.
- Fonction `split_title_author(text: str) -> dict` : sépare le titre et l'auteur d'un texte de tranche par heuristiques (position, casse, mots-clés). Retourne `{"title": str, "author": str | None}`.
- Fonction `postprocess_spine(raw_texts: list[str]) -> dict` : orchestre merge_fragments → clean_text → split_title_author. Retourne `{"raw_text": str, "clean_text": str, "title": str, "author": str | None}`.

## Critères d'acceptation
- [ ] `clean_text` supprime les caractères parasites courants (ex : `\x00`, `|`, caractères de contrôle)
- [ ] `clean_text` normalise les espaces multiples en un seul espace
- [ ] `clean_text` applique la normalisation unicode NFC
- [ ] `merge_fragments` fusionne correctement les fragments avec gestion des coupures de mots
- [ ] `merge_fragments` retourne une chaîne vide pour une liste vide
- [ ] `split_title_author` sépare correctement les cas courants (ex : "LE PETIT PRINCE\nAntoine de Saint-Exupéry")
- [ ] `split_title_author` retourne `author: None` si un seul élément est détecté
- [ ] `postprocess_spine` orchestre correctement le pipeline de post-traitement
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords (texte vide, texte sans auteur, caractères spéciaux)
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/014-text-postprocessing` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/014-text-postprocessing` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS3] #014 RED: tests post-traitement texte OCR`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS3] #014 GREEN: post-traitement texte implémenté`.
- [ ] **Pull Request ouverte** vers `main` : `[WS3] #014 — Post-traitement texte`.
