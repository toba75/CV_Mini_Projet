# ShelfScan — Inventaire de bibliothèque par reconnaissance visuelle

## 1. Contexte et problématique

Réaliser l'inventaire d'une bibliothèque personnelle ou professionnelle est une tâche fastidieuse lorsqu'elle est effectuée manuellement : il faut retirer chaque livre, noter le titre et l'auteur, puis le replacer. Pour une collection de plusieurs centaines d'ouvrages, cela représente plusieurs heures de travail.

**Problématique** : Comment automatiser l'inventaire d'une bibliothèque à partir de simples photographies des tranches de livres ?

**Objectif** : Développer une preuve de concept capable de prendre en entrée une photo d'étagère et de produire en sortie une liste structurée des ouvrages identifiés (titre, auteur, éditeur si possible).

---

## 2. Périmètre du projet

### 2.1 In scope (dans le périmètre)

- Photographies de tranches de livres prises dans des conditions raisonnables (éclairage correct, angle frontal ou légèrement incliné).
- Texte imprimé en caractères latins (français, anglais).
- Livres rangés verticalement sur une étagère.
- Sortie sous forme de liste structurée (CSV ou JSON).
- Enrichissement des résultats via une API de métadonnées bibliographiques (Google Books ou Open Library).

### 2.2 Out of scope (hors périmètre)

- Texte manuscrit ou en alphabets non latins.
- Livres empilés horizontalement ou en désordre.
- Reconnaissance en temps réel (flux vidéo continu).
- Application mobile complète (UI/UX avancée).

---

## 3. Architecture du pipeline

Le système repose sur un pipeline séquentiel en 6 étapes :

```
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  1. Entrée  │───▶│ 2. Prétraitement │───▶│ 3. Segmentation  │
│   (photo)   │    │    de l'image     │    │   des tranches   │
└─────────────┘    └──────────────────┘    └──────────────────┘
                                                    │
                                                    ▼
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  6. Post-   │◀───│ 5. Reconnais-    │◀───│ 4. Détection du  │
│  traitement │    │   sance (OCR)    │    │   texte (ROI)    │
└─────────────┘    └──────────────────┘    └──────────────────┘
       │
       ▼
┌─────────────────┐
│ 7. Inventaire   │
│ structuré (JSON)│
└─────────────────┘
```

### Étape 1 — Acquisition de l'image

- **Entrée** : photographie d'une étagère (JPEG/PNG).
- **Source** : appareil photo, smartphone ou webcam.
- **Résolution minimale recommandée** : 1920×1080 px.

### Étape 2 — Prétraitement

- Redimensionnement adaptatif pour normaliser la résolution d'entrée.
- Correction de perspective si l'image est prise en angle (transformation affine ou homographie via OpenCV).
- Amélioration du contraste (CLAHE — Contrast Limited Adaptive Histogram Equalization).
- Conversion en niveaux de gris si nécessaire pour certains traitements.

### Étape 3 — Segmentation des tranches

- **Objectif** : isoler chaque tranche de livre individuellement.
- **Méthode principale** : détection de lignes verticales par transformée de Hough sur les bords (Canny + HoughLinesP), puis découpage en bandes verticales.
- **Méthode alternative** : utilisation d'un modèle de détection d'objets (YOLOv8 fine-tuné) si la méthode par lignes se révèle insuffisante.

### Étape 4 — Détection des zones de texte

- **Objectif** : localiser les régions contenant du texte sur chaque tranche isolée.
- **Méthode** : CRAFT (Character Region Awareness for Text Detection) ou EAST (Efficient and Accurate Scene Text Detector).
- **Sortie** : bounding boxes orientées autour de chaque zone de texte.
- **Correction d'orientation** : rotation des zones détectées pour redresser le texte vertical ou incliné (estimation de l'angle via les bounding boxes ou la transformée de Hough).

### Étape 5 — Reconnaissance de caractères (OCR)

- **Objectif** : transcrire le texte contenu dans chaque zone détectée.
- **Méthodes envisagées** (à comparer lors de la phase d'expérimentation) :
  - **PaddleOCR** : pipeline complet (détection + reconnaissance), bon support multilingue, léger.
  - **TrOCR** (Microsoft) : modèle Transformer encoder-decoder pré-entraîné, performant sur le scene text.
  - **Tesseract 5** : OCR open-source classique, utilisable comme baseline de comparaison.
- **Sortie** : texte brut pour chaque tranche.

### Étape 6 — Post-traitement et enrichissement

- Nettoyage du texte brut : suppression des artefacts, normalisation des espaces et de la casse.
- Heuristiques de séparation titre / auteur / éditeur (position sur la tranche, taille de police relative).
- Requête vers une API bibliographique (Google Books API ou Open Library API) pour :
  - Corriger les erreurs OCR par fuzzy matching sur les titres connus.
  - Récupérer les métadonnées complètes (auteur, ISBN, année, couverture).
- Export final au format JSON ou CSV.

---

## 4. Stack technique

| Composant            | Technologie                          |
|----------------------|--------------------------------------|
| Langage              | Python 3.10+                         |
| Traitement d'image   | OpenCV, Pillow                       |
| Détection de texte   | CRAFT ou PaddleOCR                   |
| Reconnaissance OCR   | PaddleOCR / TrOCR / Tesseract        |
| Deep Learning        | PyTorch                              |
| API bibliographique  | Google Books API ou Open Library API  |
| Interface démo       | Streamlit ou Gradio                   |
| Gestion des données  | Pandas                               |

---

## 5. Données

### 5.1 Dataset de développement

- **Constitution manuelle** : 20 à 30 photographies d'étagères prises dans des conditions variées (éclairage, angle, densité de livres).
- **Annotation** : pour chaque photo, relevé manuel des titres visibles servant de ground truth pour le calcul des métriques.

### 5.2 Modèles pré-entraînés

- Aucun entraînement from scratch n'est prévu. Le projet repose sur le **transfer learning** et l'utilisation de modèles pré-entraînés (CRAFT, PaddleOCR, TrOCR).
- Un fine-tuning léger pourra être envisagé sur TrOCR si les résultats initiaux sont insuffisants.

---

## 6. Métriques d'évaluation

| Métrique                     | Description                                                        | Cible       |
|-----------------------------|--------------------------------------------------------------------|-------------|
| **Taux de détection**        | % de livres correctement segmentés sur l'étagère                   | ≥ 80%       |
| **CER** (Character Error Rate) | Taux d'erreur au niveau caractère sur le texte reconnu            | ≤ 20%       |
| **Taux d'identification**    | % de livres pour lesquels le titre correct est retrouvé via l'API  | ≥ 60%       |
| **Temps de traitement**      | Durée totale du pipeline pour une image                            | < 30s       |

Le CER sera calculé en comparant le texte OCR brut au ground truth annoté manuellement, en utilisant la distance d'édition de Levenshtein (conformément à la métrique vue en cours).

---

## 7. Démonstration

La démo prendra la forme d'une interface web simple (Streamlit ou Gradio) permettant :

1. **Upload** d'une photo d'étagère.
2. **Visualisation** du pipeline étape par étape :
   - Image originale → image prétraitée → tranches segmentées (bounding boxes colorées) → zones de texte détectées → texte reconnu.
3. **Affichage** de l'inventaire final sous forme de tableau (titre, auteur, confiance OCR).
4. **Export** du résultat en CSV.

---

## 8. Risques identifiés et mitigations

| Risque                                            | Impact | Mitigation                                                         |
|---------------------------------------------------|--------|--------------------------------------------------------------------|
| Texte vertical ou fortement incliné               | Élevé  | Correction d'angle automatique + rotation des crops                |
| Polices décoratives / dorées difficilement lisibles| Élevé  | Prétraitement de contraste, fallback sur le fuzzy matching API     |
| Tranches très fines (< 1 cm)                      | Moyen  | Résolution d'entrée élevée, signalement des tranches non lisibles  |
| Reflets ou ombres sur les tranches                 | Moyen  | CLAHE + consignes de prise de photo dans le README                 |
| API bibliographique indisponible ou limitée        | Faible | Mode dégradé : affichage du texte brut sans enrichissement         |

---

## 9. Livrables

1. **Diapositives de présentation** (~10 slides, 20 minutes).
2. **Code source** du pipeline et de l'interface de démonstration.
3. **README** décrivant :
   - L'installation et les dépendances.
   - La stack technique.
   - Les instructions pour reproduire la démo.
   - Les résultats obtenus et les limites identifiées.
4. **Fichier de résultats** : exemples d'images traitées avec l'inventaire généré.

---

## 10. Répartition indicative du travail (groupe de 3-4)

| Membre   | Responsabilité principale                              |
|----------|--------------------------------------------------------|
| Membre 1 | Prétraitement + segmentation des tranches              |
| Membre 2 | Détection de texte + correction d'orientation          |
| Membre 3 | OCR (comparaison des modèles) + post-traitement        |
| Membre 4 | Interface démo (Streamlit) + enrichissement API + slides|

---

## 11. Liens avec le cours

| Concept du cours                          | Application dans le projet                          |
|-------------------------------------------|-----------------------------------------------------|
| Architectures CNN (séance 2)              | Backbone des modèles de détection (CRAFT, EAST)     |
| Vision Transformers (séance 4)            | TrOCR pour la reconnaissance de texte               |
| Transfer learning                         | Utilisation de modèles pré-entraînés, fine-tuning   |
| OCR : détection et reconnaissance (séance 3) | Cœur du pipeline (étapes 4 et 5)                 |
| Métriques CER / WER (séance 3)           | Évaluation quantitative des résultats               |
| Prétraitements OCR (séance 3)            | Étape 2 du pipeline (contraste, perspective, deskew) |
| Post-traitements OCR (séance 3)          | Étape 6 (nettoyage, fuzzy matching, API)             |
