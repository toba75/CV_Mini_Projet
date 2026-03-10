---
marp: true
theme: default
paginate: true
---

# ShelfScan

## Inventaire de bibliothèque par reconnaissance visuelle

**Projet de Computer Vision — 2025-2026**

---

## Problématique et motivation

- Les bibliothèques gèrent des milliers d'ouvrages : inventaire manuel long et coûteux
- Objectif : **automatiser l'inventaire** à partir d'une simple photo d'étagère
- Entrée : une photographie d'étagère
- Sortie : une liste structurée (titre, auteur, métadonnées bibliographiques)

**Cas d'usage** : bibliothécaires, collectionneurs, librairies d'occasion

---

## État de l'art

### Reconnaissance de texte en scène (Scene Text Recognition)

- **Détection** : CRAFT, EAST, PaddleOCR (DB-Net)
- **Reconnaissance** : CRNN, TrOCR (Transformer), PaddleOCR (SVTR)
- **Bout en bout** : PaddleOCR, EasyOCR, Google Vision API

### Méthodes du cours appliquées

- Filtrage et amélioration de contraste (CLAHE)
- Détection de contours (Canny + transformée de Hough)
- Segmentation par analyse de lignes verticales
- Correction de perspective et d'orientation

---

## Architecture du pipeline

6 étapes séquentielles :

```
Image → Prétraitement → Segmentation → Détection texte
         → Correction orientation → OCR → Post-traitement → JSON
```

| Étape | Module | Rôle |
|---|---|---|
| 1 | `preprocess.py` | CLAHE, redimensionnement, correction perspective |
| 2 | `segment.py` | Canny + HoughLinesP → crops par tranche |
| 3 | `detect_text.py` | PaddleOCR détection → bounding boxes |
| 4 | `detect_text.py` | Correction d'angle automatique |
| 5 | `ocr.py` | Extraction texte (PaddleOCR / TrOCR / Tesseract) |
| 6 | `postprocess.py` | Nettoyage, fuzzy matching API bibliographique |

---

## Prétraitement et segmentation

### Prétraitement (`preprocess.py`)

- Chargement et redimensionnement (max 1920px de large) via OpenCV
- **CLAHE** sur canal L (espace LAB) pour améliorer le contraste
- Correction de perspective disponible (détection de quadrilatère), appliquée si nécessaire

### Segmentation (`segment.py`)

- Conversion en niveaux de gris + filtre Canny
- **Transformée de Hough** (HoughLinesP) → lignes verticales
- Filtrage et fusion des lignes proches
- Extraction des crops individuels pour chaque tranche de livre

---

## Détection de texte et correction d'orientation

### Détection (`detect_text.py`)

- **PaddleOCR** en mode détection seule (DB-Net)
- Produit des bounding boxes orientées pour chaque zone de texte
- Filtrage par score de confiance (seuil configurable)

### Correction d'orientation

- Analyse de l'angle médian des bounding boxes détectées
- Rotation automatique selon l'angle médian détecté pour aligner le texte horizontalement
- Gestion du texte incliné ou vertical sur les tranches de livres
- Indispensable avant l'étape OCR pour maximiser la qualité de reconnaissance

---

## Reconnaissance OCR — Comparaison des modèles

| Modèle | Type | Forces | Faiblesses |
|---|---|---|---|
| **PaddleOCR** | SVTR (CNN + Transformer) | Rapide, bon sur texte imprimé | Moins bon sur polices décoratives |
| **TrOCR** | Transformer pur (encoder-decoder) | Excellent sur texte complexe | Plus lent, requiert GPU |
| **Tesseract** | LSTM classique | Léger, multilingue | Sensible au bruit, moins précis |

### Choix retenu

- **PaddleOCR** comme modèle principal (meilleur compromis vitesse/précision)
- TrOCR en alternative pour les cas difficiles
- Tesseract comme baseline de référence

---

## Post-traitement et enrichissement API

### Nettoyage du texte OCR (`postprocess.py`)

- Normalisation Unicode (NFC)
- Suppression des caractères parasites et espaces superflus
- Séparation titre / auteur par heuristiques
- Fusion des fragments de texte provenant de la même tranche

### Enrichissement bibliographique

- **Fuzzy matching** (ratio de similarité ≥ 60%) vers les API :
  - Google Books API
  - Open Library API
- Récupération des métadonnées : titre complet, auteur, ISBN, éditeur
- Export structuré en JSON et CSV

---

## Résultats quantitatifs

### Métriques sur le jeu de test (15 images d'étagères)

| Métrique | Valeur |
|---|---|
| Taux de détection des tranches | ~85 % |
| CER (Character Error Rate) | ~20 % |
| Taux d'identification des ouvrages | ~65 % |
| Temps moyen de traitement | ~15 s/image |

### Cas d'échec identifiés

- Images floues ou sous-exposées → CER dégradé
- Polices très décoratives ou manuscrites → reconnaissance faible
- Livres sans texte visible sur la tranche → non identifiables
- Étagères très encombrées → segmentation imprécise

---

## Démo live — Conclusion et perspectives

### Démo

- Interface **Streamlit** : chargement d'image, visualisation des étapes, résultats interactifs
- Pipeline complet en ~15 secondes par image

### Limites

- Sensibilité à la qualité de l'image (résolution, éclairage, angle)
- Texte vertical et polices décoratives restent difficiles
- Dépendance aux API externes pour l'enrichissement

### Perspectives d'amélioration

- Détection par deep learning (YOLO / Faster R-CNN) pour la segmentation
- OCR multilingue pour supporter davantage de langues
- Mode batch pour traiter des dossiers complets
- Cache local des résultats API

**Merci — Questions ?**
