# Tâche — Structurer la sortie JSON complète du pipeline

Statut : TODO
Ordre : 016
Workstream : WS4
Milestone : M2

## Contexte
Le pipeline doit produire une sortie JSON structurée contenant toutes les informations extraites : texte brut, texte nettoyé, titre, auteur, ISBN, score de confiance. Cette structure constitue le livrable principal du pipeline et le critère de validation du milestone M2.

Références :
- Plan : `docs/plan/implementation_plan.md` (section M2 > WS4 — point 2)
- Spécification : `docs/specifications/specifications.md` (§3 Étape 6 — Export final JSON/CSV, §2.1 Sortie structurée)
- Code : `src/pipeline.py`

Dépendances :
- Tâche 015 — Fuzzy matching (doit être DONE)
- Tâche 013 — Intégration OCR pipeline (doit être DONE)

## Objectif
Assembler le pipeline complet dans `src/pipeline.py` : image en entrée → JSON structuré en sortie. Définir le schéma de sortie JSON et implémenter la fonction d'orchestration qui chaîne toutes les étapes (prétraitement → segmentation → détection texte → orientation → OCR → post-traitement → matching → JSON).

## Règles attendues
- Le schéma JSON doit correspondre exactement à celui défini dans le plan d'implémentation.
- Le pipeline doit être appelable avec une seule fonction prenant un chemin d'image.
- Chaque livre dans la sortie doit avoir un `spine_id` unique (index 1-based).
- Gérer les erreurs gracieusement : si une étape échoue pour une tranche, la signaler dans le JSON sans bloquer les autres tranches.
- Export en fichier JSON et CSV.

## Évolutions proposées
- Fonction `run_pipeline(image_path: str | Path, ocr_engine: str = "paddleocr", output_dir: str | Path | None = None) -> dict` : orchestre le pipeline complet. Retourne le dict JSON structuré.
- Structure de sortie :
  ```json
  {
    "image": "photo_01.jpg",
    "num_spines_detected": 5,
    "processing_time_s": 12.3,
    "books": [
      {
        "spine_id": 1,
        "raw_text": "LE PETIT PRINCE Antoine de Saint-Exupéry",
        "title": "Le Petit Prince",
        "author": "Antoine de Saint-Exupéry",
        "isbn": "978-2-07-040850-4",
        "confidence": 0.92
      }
    ]
  }
  ```
- Fonction `export_json(result: dict, output_path: str | Path) -> Path` : écrit le résultat en fichier JSON.
- Fonction `export_csv(result: dict, output_path: str | Path) -> Path` : exporte la liste des livres en CSV (colonnes : spine_id, raw_text, title, author, isbn, confidence).

## Critères d'acceptation
- [ ] `run_pipeline` prend un chemin d'image et retourne un dict avec les clés `image`, `num_spines_detected`, `processing_time_s`, `books`
- [ ] Chaque élément de `books` contient les clés `spine_id`, `raw_text`, `title`, `author`, `isbn`, `confidence`
- [ ] `spine_id` est unique et 1-based
- [ ] `processing_time_s` reflète le temps réel de traitement
- [ ] `run_pipeline` lève `FileNotFoundError` si l'image n'existe pas
- [ ] `run_pipeline` lève `ValueError` si le fichier n'est pas une image valide
- [ ] Les erreurs sur une tranche individuelle n'empêchent pas le traitement des autres
- [ ] `export_json` produit un fichier JSON valide et lisible
- [ ] `export_csv` produit un fichier CSV avec les colonnes attendues
- [ ] Tests couvrent les scénarios nominaux + erreurs + bords (image invalide, aucune tranche détectée)
- [ ] Suite de tests verte après implémentation
- [ ] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/016-json-output-structure` depuis `main`.

## Checklist de fin de tâche
- [ ] Branche `task/016-json-output-structure` créée depuis `main`.
- [ ] Tests RED écrits avant implémentation.
- [ ] **Commit RED** : `[WS4] #016 RED: tests structure JSON sortie pipeline`.
- [ ] Tests GREEN passants et reproductibles.
- [ ] Critères d'acceptation tous satisfaits.
- [ ] `ruff check src/ tests/` passe sans erreur.
- [ ] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS4] #016 GREEN: pipeline complet avec sortie JSON`.
- [ ] **Pull Request ouverte** vers `main` : `[WS4] #016 — Structure JSON sortie`.
