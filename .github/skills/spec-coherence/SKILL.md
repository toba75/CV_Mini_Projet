---
name: spec-coherence
description: "Vérifie la cohérence intrinsèque des spécifications ShelfScan : terminologie, références croisées, contrats I/O du pipeline, métriques. Produit un rapport structuré. À utiliser quand l'utilisateur demande « vérifie la cohérence de la spec », « audit des spécifications »."
argument-hint: "[spec: docs/specifications/specifications.md] [fix: false|true]"
---

# Agent Skill — Vérification de cohérence de la spécification (ShelfScan)

## Objectif

Auditer la **cohérence intrinsèque** de la spécification ShelfScan (`docs/specifications/specifications.md`). Détecter les contradictions internes, ambiguïtés, références cassées et incohérences de pipeline — **sans consulter le code ni les tests**.

## Phase A — Analyse de cohérence intrinsèque

### Périmètre de lecture

Lire **intégralement** `docs/specifications/specifications.md`.

### Axes d'analyse

#### A1. Cohérence terminologique
- [ ] Les étapes du pipeline sont-elles nommées de manière cohérente (« prétraitement » vs « preprocessing », etc.) ?
- [ ] Les modèles OCR sont-ils désignés avec les mêmes noms (PaddleOCR, TrOCR, Tesseract) partout ?
- [ ] Les métriques (CER, WER, taux de détection) sont-elles définies et utilisées de manière cohérente ?

#### A2. Cohérence des références croisées
- [ ] Chaque référence à une étape du pipeline existe-t-elle réellement ?
- [ ] Les sections citant d'autres sections pointent-elles vers le bon contenu ?

#### A3. Cohérence du flux de données (pipeline I/O)
- [ ] Les sorties de l'étape N sont-elles compatibles avec les entrées de l'étape N+1 ?
  - Prétraitement → Segmentation : format image, type numpy ?
  - Segmentation → Détection de texte : format des crops (liste d'images) ?
  - Détection → OCR : format des bounding boxes ?
  - OCR → Post-traitement : format du texte brut par tranche ?
  - Post-traitement → Inventaire JSON : structure du dictionnaire ?
- [ ] Les types de données sont-ils cohérents aux frontières (uint8, float32, liste de strings) ?

#### A4. Cohérence des métriques
- [ ] La définition du CER (distance de Levenshtein / longueur de référence) est-elle cohérente partout ?
- [ ] Les cibles de métriques (≥ 80%, ≤ 20%, ≥ 60%, < 30s) sont-elles référencées de manière cohérente ?
- [ ] La procédure d'évaluation est-elle décrite de manière cohérente entre la section métriques et la section dataset ?

#### A5. Cohérence du périmètre (In scope / Out of scope)
- [ ] Les fonctionnalités décrites dans les étapes du pipeline sont-elles cohérentes avec le périmètre défini en §2 ?
- [ ] Les risques identifiés correspondent-ils aux limitations définies en Out of scope ?

#### A6. Cohérence de la stack technique
- [ ] Les modèles listés dans la stack sont-ils ceux utilisés dans les descriptions des étapes ?
- [ ] Pas de technologie citée dans les étapes mais absente de la stack, ou vice-versa ?

#### A7. Cohérence structurelle
- [ ] Toutes les sections annoncées sont-elles présentes ?
- [ ] La numérotation des étapes du pipeline est-elle séquentielle et cohérente ?

---

### Sortie de la Phase A

Créer `docs/review_coherence_spec/NNNN_spec_coherence.md` :

```markdown
# Revue de cohérence — Spécification ShelfScan

**Date** : YYYY-MM-DD
**Document audité** : `docs/specifications/specifications.md`
**Verdict** : ✅ COHÉRENT | ⚠️ INCOHÉRENCES MINEURES | ❌ INCOHÉRENCES STRUCTURELLES

---

## Résumé exécutif

<2-3 phrases synthèse>

| Axe | Incohérences | BLOQUANT | WARNING | MINEUR |
|---|---|---|---|---|
| A1. Terminologie | N | n | n | n |
| A2. Références | N | n | n | n |
| A3. Flux I/O | N | n | n | n |
| A4. Métriques | N | n | n | n |
| A5. Périmètre | N | n | n | n |
| A6. Stack | N | n | n | n |
| A7. Structure | N | n | n | n |
| **Total** | **N** | **n** | **n** | **n** |

---

## Incohérences détectées

### I-1. <titre court>

- **Axe** : A1|...|A7
- **Sévérité** : BLOQUANT|WARNING|MINEUR
- **Localisation** : §X ↔ §Y
- **Description** : <description factuelle>
- **Recommandation** : <correction suggérée>

---

## Matrice flux I/O (A3)

| Étape source | Sortie décrite | Étape cible | Entrée attendue | Compatible ? |
|---|---|---|---|---|
| Prétraitement | image RGB float32 | Segmentation | image numpy | ✅/❌ |
| Segmentation | liste de crops | Détection | liste d'images | ✅/❌ |
| Détection | bounding boxes | OCR | regions orientées | ✅/❌ |
| OCR | texte brut par tranche | Post-traitement | string | ✅/❌ |
| Post-traitement | dict structuré | JSON output | format JSON | ✅/❌ |

---

## Conclusion

<verdict final>
```

## Phase B — Correction des incohérences (optionnelle)

> Activée uniquement si l'utilisateur passe `fix: true`.

### Workflow

1. Lire le rapport Phase A, créer les TODOs par sévérité (BLOQUANT → WARNING → MINEUR).
2. Pour chaque incohérence : lire les sections, déterminer la correction, appliquer.
3. **Principe du moindre changement** : modifier le minimum de texte nécessaire.
4. Après toutes corrections, relancer la Phase A. **Garde-fou** : 3 itérations max.

## Principes

1. **Document analysé en isolation** : la spec est analysée sans consulter le code.
2. **Factuel** : chaque incohérence cite les passages exacts qui se contredisent.
3. **Exhaustivité par axe** : chaque axe A1–A7 est couvert, même si aucune incohérence n'est trouvée.
