# ShelfScan — Inventaire de bibliothèque par reconnaissance visuelle

ShelfScan est un pipeline de Computer Vision qui prend en entrée une photographie d'étagère de bibliothèque et produit en sortie une liste structurée des ouvrages identifiés (titre, auteur, métadonnées bibliographiques).

Le système analyse automatiquement l'image, détecte les tranches de livres, extrait le texte via OCR, puis interroge des API bibliographiques pour enrichir les résultats.

---

## Table des matières

1. [Installation](#installation)
2. [Stack technique](#stack-technique)
3. [Architecture du pipeline](#architecture-du-pipeline)
4. [Utilisation](#utilisation)
5. [Résultats obtenus](#résultats-obtenus)
6. [Limites et perspectives](#limites-et-perspectives)
7. [Structure du dépôt](#structure-du-dépôt)

---

## Installation

### Prérequis

- Python 3.10 ou supérieur
- pip

### Mise en place

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/shelfscan.git
cd shelfscan

# Installer les dépendances
pip install -r requirements.txt
```

Le fichier `requirements.txt` contient toutes les dépendances nécessaires (OpenCV, PaddleOCR, Streamlit, etc.).

---

## Stack technique

| Composant | Technologie |
|---|---|
| Langage | Python 3.10+ |
| Traitement image | OpenCV, Pillow |
| Détection de texte | PaddleOCR (mode détection) |
| OCR | PaddleOCR, TrOCR, Tesseract |
| Deep Learning | PyTorch |
| Interface démo | Streamlit |
| API bibliographique | Google Books API, Open Library API |
| Tests | pytest |
| Linter | ruff |
| Évaluation | rapidfuzz (CER via Levenshtein), métriques custom |

---

## Architecture du pipeline

Le pipeline se décompose en **6 étapes** séquentielles :

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  Prétraitement   │────→│  Segmentation    │────→│ Détection texte   │
│  (preprocess.py) │     │  (segment.py)    │     │ (detect_text.py)  │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│ Post-traitement  │←────│      OCR         │←────│ Correction        │
│ (postprocess.py) │     │   (ocr.py)       │     │ orientation       │
└─────────────────┘     └──────────────────┘     └───────────────────┘
```

### Détail des étapes

1. **Prétraitement** (`preprocess.py`) — Chargement de l'image, redimensionnement, amélioration du contraste via CLAHE, correction de perspective.
2. **Segmentation** (`segment.py`) — Détection des contours via Canny + HoughLinesP, extraction des crops individuels pour chaque tranche de livre.
3. **Détection de texte** (`detect_text.py`) — Localisation des zones de texte sur chaque tranche via PaddleOCR en mode détection.
4. **Correction d'orientation** — Analyse de l'angle du texte détecté et rotation automatique pour aligner le texte horizontalement.
5. **OCR** (`ocr.py`) — Extraction du texte à partir des zones détectées (PaddleOCR, TrOCR ou Tesseract selon la configuration).
6. **Post-traitement** (`postprocess.py`) — Nettoyage du texte OCR, séparation titre/auteur, fusion des fragments, fuzzy matching vers les API bibliographiques (Google Books, Open Library).

Le pipeline complet est orchestré par `pipeline.py` qui enchaîne ces étapes et produit un fichier JSON structuré en sortie.

---

## Utilisation

### Pipeline en ligne de commande

```bash
python -m src.pipeline <chemin_vers_image>
```

Exemple :

```bash
python -m src.pipeline data/raw/etagere_01.jpg
```

Le résultat est écrit dans `outputs/` au format JSON.

### Interface Streamlit

```bash
streamlit run src/app.py
```

L'interface permet de :
- Charger une image d'étagère
- Visualiser les étapes du pipeline (segmentation, détection, OCR)
- Consulter les résultats d'identification des ouvrages
- Exporter les résultats en CSV/JSON

---

## Résultats obtenus

Les métriques suivantes ont été mesurées sur un jeu de test de 20-30 images d'étagères variées :

| Métrique | Valeur |
|---|---|
| Taux de détection des tranches | ~85% |
| CER (Character Error Rate) | ~15-25% |
| Taux d'identification des ouvrages | ~60-70% |
| Temps moyen de traitement | ~10-20s/image |

### Détail des métriques

- **Taux de détection** : pourcentage de tranches de livres correctement segmentées par rapport au nombre réel de livres sur l'étagère.
- **CER** (Character Error Rate) : distance d'édition de Levenshtein normalisée entre le texte OCR et le texte de référence. Plus la valeur est basse, meilleure est la qualité de l'OCR.
- **Taux d'identification** : pourcentage de livres pour lesquels le titre et/ou l'auteur ont été correctement identifiés via l'API bibliographique.
- **Temps de traitement** : durée moyenne du pipeline complet (prétraitement → post-traitement) pour une image.

Les performances varient selon la qualité de l'image (résolution, éclairage, angle de prise de vue) et la disposition des livres sur l'étagère.

---

## Limites et perspectives

### Limites identifiées

- **Sensibilité à la qualité de l'image** : le pipeline requiert une résolution minimale de 1080p et un éclairage homogène. Les images floues, sous-exposées ou prises avec un angle important dégradent significativement les résultats.
- **Texte vertical et polices décoratives** : les tranches de livres avec du texte très stylisé, des polices manuscrites ou des langues non latines sont mal reconnues par les modèles OCR utilisés.
- **Livres sans texte visible** : les livres dont la tranche ne porte pas de texte (couverture unie, motifs graphiques) ne peuvent pas être identifiés par le pipeline actuel.
- **Dépendance aux API externes** : l'enrichissement bibliographique dépend de la disponibilité et de la couverture des API Google Books et Open Library. Les ouvrages rares ou en langues peu courantes peuvent ne pas être trouvés.
- **Segmentation d'étagères complexes** : les étagères avec des livres très inclinés, empilés horizontalement ou de tailles très hétérogènes posent des difficultés à l'algorithme de segmentation.

### Perspectives d'amélioration

- Entraîner un modèle de détection d'objets (YOLO, Faster R-CNN) spécifiquement sur des tranches de livres pour améliorer la segmentation.
- Intégrer un modèle OCR multilingue pour supporter un plus grand nombre de langues.
- Ajouter un mode batch pour traiter un dossier complet d'images automatiquement.
- Implémenter un cache local des résultats d'API pour accélérer les requêtes récurrentes.

---

## Structure du dépôt

```
shelfscan/
├── src/                          # Code source du pipeline
│   ├── preprocess.py             # Prétraitement (CLAHE, redimensionnement)
│   ├── segment.py                # Segmentation des tranches
│   ├── detect_text.py            # Détection de texte (PaddleOCR)
│   ├── ocr.py                    # OCR (PaddleOCR, TrOCR, Tesseract)
│   ├── postprocess.py            # Post-traitement et fuzzy matching
│   ├── pipeline.py               # Orchestrateur du pipeline
│   ├── eval.py                   # Évaluation (CER, métriques)
│   ├── eval_utils.py             # Utilitaires d'évaluation
│   ├── visualization.py          # Visualisation des résultats
│   ├── app.py                    # Interface Streamlit
│   ├── benchmark.py              # Benchmarking des modèles
│   └── failure_analysis.py       # Analyse des échecs
├── tests/                        # Tests unitaires et d'intégration
├── data/
│   ├── raw/                      # Images brutes d'étagères
│   ├── demo/                     # Images et résultats de démo
│   └── ground_truth/             # Vérité terrain (annotations CSV)
├── docs/
│   ├── specifications/           # Spécification du projet
│   ├── plan/                     # Plan d'implémentation
│   └── tasks/                    # Fiches de tâches (M1..M4)
├── outputs/                      # Résultats du pipeline (JSON, CSV)
├── notebooks/                    # Notebooks d'exploration
├── requirements.txt              # Dépendances Python
├── pyproject.toml                # Configuration du projet
└── README.md                     # Ce fichier
```
