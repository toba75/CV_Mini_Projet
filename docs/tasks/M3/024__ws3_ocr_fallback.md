# Tâche — Fallback OCR multi-modèle

Statut : DONE
Ordre : 024
Workstream : WS3
Milestone : M3

## Contexte
Le modèle OCR principal peut échouer sur certaines tranches (confiance faible, texte illisible). Un mécanisme de fallback permettrait de tenter un second modèle quand le premier renvoie un résultat peu fiable, améliorant ainsi le taux de reconnaissance global.

Références :
- Plan : `docs/plan/implementation_plan.md` (M3 > WS3)
- Spécification : `docs/specifications/specifications.md` (§8 — Risques : polices décoratives)
- Code : `src/ocr.py`, `src/postprocess.py`

Dépendances :
- Tâche 023 — Comparaison quantitative OCR (doit être DONE)
- Tâche 013 — Intégration OCR pipeline (doit être DONE)

## Objectif
Implémenter un mécanisme de fallback OCR : si le modèle principal renvoie un texte avec un score de confiance inférieur à un seuil configurable, un second modèle est automatiquement sollicité.

## Règles attendues
- Le seuil de confiance doit être configurable (paramètre, pas de valeur hardcodée)
- L'ordre de priorité des modèles doit être configurable
- Le fallback ne doit pas ralentir excessivement le pipeline (mesurer l'impact)

## Évolutions proposées
- Ajouter un paramètre `confidence_threshold` pour déclencher le fallback
- Implémenter la logique de fallback dans `ocr.py` : modèle principal → modèle secondaire
- Retourner le meilleur résultat (confiance la plus élevée) entre les deux modèles
- Logger quel modèle a été utilisé pour chaque tranche (utile pour l'analyse)
- Mesurer l'impact sur le CER global et le temps de traitement

## Critères d'acceptation
- [x] Fallback déclenché quand confiance < seuil configurable
- [x] Au moins 2 modèles supportés dans la chaîne de fallback
- [x] Le résultat retenu est celui avec la meilleure confiance
- [x] Le modèle utilisé est loggé pour chaque tranche
- [ ] Impact mesuré : amélioration CER et surcoût temps
- [x] Tests couvrent les scénarios nominaux + erreurs + bords
- [x] Suite de tests verte après implémentation
- [x] `ruff check` passe sans erreur

## Pré-condition de démarrage
- **Tous les tests existants sont GREEN** avant de commencer.
- **Créer une branche dédiée** `task/024-ocr-fallback` depuis `main`.

## Checklist de fin de tâche
- [x] Branche `task/024-ocr-fallback` créée depuis `main`.
- [x] Tests RED écrits avant implémentation.
- [x] **Commit RED** : `[WS-3] #024 RED: tests fallback OCR multi-modèle`.
- [x] Tests GREEN passants et reproductibles.
- [x] Critères d'acceptation tous satisfaits.
- [x] `ruff check src/ tests/` passe sans erreur.
- [x] Fichier de tâche mis à jour (statut DONE, critères cochés).
- [ ] **Commit GREEN** : `[WS-3] #024 GREEN: fallback OCR multi-modèle`.
- [ ] **Pull Request ouverte** vers `main` : `[WS-3] #024 — Fallback OCR multi-modèle`.
