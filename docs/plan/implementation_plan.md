# ShelfScan — Plan d'implémentation

## Vue d'ensemble

Le projet est découpé en **4 milestones** progressifs, chacun aboutissant à un livrable fonctionnel testable. En parallèle, le travail est organisé en **5 workstreams** correspondant aux grandes responsabilités techniques.

```
Semaine        S1              S2              S3              S4
            ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
Milestone   │  M1       │  │  M2       │  │  M3       │  │  M4       │
            │  Setup +  │  │  Pipeline │  │  Intégra- │  │  Polish + │
            │  Proto    │  │  complet  │  │  tion +   │  │  Soutenance│
            │           │  │           │  │  Éval     │  │           │
            └───────────┘  └───────────┘  └───────────┘  └───────────┘
```

---

## Workstreams

| ID  | Workstream                  | Responsable | Description courte                                      |
|-----|-----------------------------|-------------|---------------------------------------------------------|
| WS1 | Prétraitement & Segmentation| Membre 1    | De la photo brute aux tranches individuelles isolées     |
| WS2 | Détection & Orientation     | Membre 2    | Localisation des zones de texte et correction d'angle    |
| WS3 | OCR & Post-traitement       | Membre 3    | Reconnaissance de caractères et nettoyage du texte       |
| WS4 | Interface & Enrichissement  | Membre 4    | Démo Streamlit, appel API livres, export CSV/JSON        |
| WS5 | Évaluation & Présentation   | Tous        | Métriques, dataset de test, slides, répétition orale     |

---

## Milestone 1 — Setup & Prototype rapide

**Objectif** : avoir un environnement fonctionnel et un premier résultat end-to-end, même grossier, sur une seule image.

**Critère de validation** : une photo d'étagère entre dans le script, une liste de textes bruts en sort.

### WS1 — Prétraitement & Segmentation

- [ ] Créer le repo Git avec la structure de dossiers :
  ```
  shelfscan/
  ├── src/
  │   ├── preprocess.py
  │   ├── segment.py
  │   ├── detect_text.py
  │   ├── ocr.py
  │   ├── postprocess.py
  │   └── pipeline.py
  ├── data/
  │   ├── raw/            # photos brutes
  │   └── ground_truth/   # annotations manuelles
  ├── outputs/
  ├── notebooks/          # expérimentations
  ├── requirements.txt
  └── README.md
  ```
- [ ] Installer les dépendances (OpenCV, PaddleOCR, PyTorch, Streamlit).
- [ ] Écrire `preprocess.py` : chargement de l'image, redimensionnement, CLAHE sur le canal de luminance.
- [ ] Premier essai de segmentation naïve : Canny + HoughLinesP pour détecter les séparations verticales entre les livres.

### WS2 — Détection & Orientation

- [ ] Installer et tester CRAFT ou PaddleOCR en mode détection seule sur une image de tranche.
- [ ] Vérifier que les bounding boxes retournées sont cohérentes sur du texte vertical.

### WS3 — OCR & Post-traitement

- [ ] Tester PaddleOCR, TrOCR et Tesseract sur 3-4 crops manuels de tranches.
- [ ] Comparer qualitativement les sorties pour choisir le modèle principal.

### WS4 — Interface & Enrichissement

- [ ] Tester l'API Google Books / Open Library : envoyer un titre connu, vérifier le retour JSON.
- [ ] Scaffolder l'app Streamlit minimale (upload d'image + affichage).

### WS5 — Évaluation & Présentation

- [ ] Prendre 10 premières photos d'étagères variées.
- [ ] Annoter manuellement les titres visibles sur ces 10 photos (fichier CSV de ground truth).

---

## Milestone 2 — Pipeline complet fonctionnel

**Objectif** : le pipeline bout-en-bout tourne de manière automatisée sur n'importe quelle photo d'étagère.

**Critère de validation** : `pipeline.py` prend une image en entrée et produit un JSON contenant la liste des titres détectés.

### WS1 — Prétraitement & Segmentation

- [ ] Implémenter la correction de perspective automatique (détection des contours de l'étagère → homographie).
- [ ] Affiner la segmentation des tranches :
  - Filtrer les lignes parasites (trop courtes, trop inclinées).
  - Gérer les cas où deux livres n'ont pas de séparation visible (fallback sur la largeur moyenne).
- [ ] Produire des crops individuels propres pour chaque tranche détectée.

### WS2 — Détection & Orientation

- [ ] Intégrer la détection de texte dans le pipeline (`detect_text.py`).
- [ ] Implémenter la correction d'orientation automatique :
  - Estimer l'angle dominant des bounding boxes.
  - Appliquer une rotation pour redresser le texte.
- [ ] Gérer les cas multi-lignes (titre sur plusieurs lignes d'une même tranche).

### WS3 — OCR & Post-traitement

- [ ] Intégrer le modèle OCR choisi dans `ocr.py`.
- [ ] Écrire `postprocess.py` :
  - Nettoyage du texte (caractères parasites, normalisation unicode).
  - Heuristique de séparation titre / auteur (position verticale, taille relative du texte).
  - Fusion des fragments de texte d'une même tranche en une seule chaîne.

### WS4 — Interface & Enrichissement

- [ ] Implémenter le fuzzy matching : pour chaque texte OCR, chercher le meilleur candidat via l'API livres (utiliser `rapidfuzz` ou `fuzzywuzzy` pour scorer les résultats).
- [ ] Structurer la sortie JSON :
  ```json
  {
    "image": "photo_01.jpg",
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

### WS5 — Évaluation & Présentation

- [ ] Compléter le dataset : atteindre 20-30 photos annotées.
- [ ] Écrire le script de calcul des métriques (`eval.py`) :
  - Taux de détection des tranches (livres trouvés / livres réels).
  - CER moyen sur le texte brut.
  - Taux d'identification (titres correctement matchés via l'API).

---

## Milestone 3 — Intégration, évaluation et optimisation

**Objectif** : l'interface de démo est fonctionnelle, les métriques sont calculées, les cas limites sont traités.

**Critère de validation** : démo jouable de bout en bout dans Streamlit avec affichage des résultats et des métriques.

### WS1 — Prétraitement & Segmentation

- [ ] Traiter les cas limites : étagères partiellement vides, objets non-livres, livres très fins.
- [ ] Ajouter une visualisation des tranches segmentées (bounding boxes colorées sur l'image originale).

### WS2 — Détection & Orientation

- [ ] Optimiser les seuils de détection pour réduire les faux positifs (texte sur les décorations, logos d'éditeur).
- [ ] Tester sur les cas difficiles : texte en arc de cercle, texte très petit, polices fantaisie.

### WS3 — OCR & Post-traitement

- [ ] Comparer quantitativement les modèles OCR sur le dataset annoté (CER par modèle).
- [ ] Implémenter un fallback : si le modèle principal renvoie un texte avec confiance < seuil, tenter un second modèle.
- [ ] Envisager un fine-tuning léger de TrOCR sur quelques crops de tranches si le CER reste trop élevé.

### WS4 — Interface & Enrichissement

- [ ] Finaliser l'interface Streamlit :
  - Vue étape par étape (onglets : Original → Prétraitement → Segmentation → OCR → Inventaire).
  - Tableau interactif des résultats avec score de confiance.
  - Bouton d'export CSV.
- [ ] Ajouter un mode "correction manuelle" : l'utilisateur peut éditer un titre mal reconnu.

### WS5 — Évaluation & Présentation

- [ ] Lancer l'évaluation complète sur tout le dataset.
- [ ] Produire un tableau de résultats :
  | Métrique               | Résultat obtenu | Cible   |
  |------------------------|-----------------|---------|
  | Taux de détection      | ??%             | ≥ 80%   |
  | CER moyen              | ??%             | ≤ 20%   |
  | Taux d'identification  | ??%             | ≥ 60%   |
  | Temps moyen / image    | ??s             | < 30s   |
- [ ] Identifier les 3-5 cas d'échec les plus fréquents pour la discussion en soutenance.

---

## Milestone 4 — Finalisation et soutenance

**Objectif** : tout est prêt pour la présentation orale de 20 minutes.

**Critère de validation** : répétition générale réussie en ≤ 20 min, tous les livrables sont prêts.

### WS1 / WS2 / WS3 — Code

- [ ] Nettoyage du code : suppression du code mort, commentaires, docstrings.
- [ ] Vérifier que `pip install -r requirements.txt` + `python pipeline.py` fonctionne sur une machine propre.

### WS4 — Interface & Enrichissement

- [ ] Préparer 3-4 images de démo fiables (résultats connus et bons) pour la soutenance.
- [ ] S'assurer que la démo tourne en < 30s par image sur un laptop standard.

### WS5 — Évaluation & Présentation

- [ ] Rédiger le README final :
  - Installation.
  - Architecture du pipeline (avec schéma).
  - Stack technique.
  - Comment reproduire la démo.
  - Résultats et limites.
- [ ] Créer les slides (~10 diapositives) :
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
- [ ] Répétition orale (2 passages minimum) :
  - Vérifier le timing (20 min max).
  - Préparer les réponses aux questions probables :
    - "Pourquoi ce modèle OCR plutôt qu'un autre ?"
    - "Comment gérez-vous le texte vertical ?"
    - "Quelles sont les limites ?"
    - "Comment améliorer les résultats ?"

---

## Matrice Milestones × Workstreams

|                      | M1 — Setup & Proto | M2 — Pipeline complet | M3 — Intégration & Éval | M4 — Finalisation |
|----------------------|:-------------------:|:---------------------:|:------------------------:|:-----------------:|
| **WS1** Prétraitement|        ██░░         |        ████           |          ██              |        █          |
| **WS2** Détection    |        █░░░         |        ████           |          ██              |        █          |
| **WS3** OCR          |        ██░░         |        ████           |          ███             |        █          |
| **WS4** Interface    |        █░░░         |        ███            |          ████            |        ██         |
| **WS5** Éval & Prés. |        ██░░         |        ██             |          ███             |        ████       |

**Légende** : █ = charge relative de travail sur la période.
