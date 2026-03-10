# Notes de présentation — ShelfScan

Ce document contient les notes de l'orateur pour la soutenance, avec les réponses préparées aux questions probables du jury.

---

## Question 1 : « Pourquoi ce modèle OCR plutôt qu'un autre ? »

Nous avons comparé trois modèles OCR : PaddleOCR, TrOCR et Tesseract.

**PaddleOCR** a été retenu comme modèle principal pour les raisons suivantes :
- **Meilleur compromis vitesse/précision** : il traite une image en quelques secondes sur CPU, contre 10-15 secondes pour TrOCR.
- **Architecture moderne** (SVTR — Scene Visual Transformer for Text Recognition) : combine CNN pour l'extraction de features et Transformer pour la séquence de caractères.
- **Pipeline intégré** : PaddleOCR fournit à la fois la détection (DB-Net) et la reconnaissance, ce qui simplifie l'intégration.
- **Bon support multilingue** : modèles pré-entraînés pour le français et d'autres langues latines.

TrOCR (Microsoft) offre une meilleure précision sur les textes complexes grâce à son architecture Transformer pure (encoder-decoder), mais il est significativement plus lent et requiert un GPU pour un temps de réponse acceptable.

Tesseract, bien que léger et historiquement mature, obtient des résultats nettement inférieurs sur du texte en scène (images de tranches de livres avec bruit, angles, polices variées). Il reste utile comme baseline de comparaison.

---

## Question 2 : « Comment gérez-vous le texte vertical ? »

Le texte vertical est un défi majeur sur les tranches de livres. Notre approche :

1. **Détection des bounding boxes orientées** : PaddleOCR en mode détection produit des boîtes englobantes avec un angle. Les tranches de livres ont souvent du texte à 90° (vertical, de bas en haut ou de haut en bas).

2. **Analyse de l'angle médian** : nous calculons l'angle médian de toutes les bounding boxes détectées sur une tranche. Si cet angle dépasse un seuil de 2°, nous appliquons une rotation proportionnelle de l'image avant l'OCR.

3. **Rotation automatique** : le module `detect_text.py` corrige l'orientation en appliquant une rotation inverse pour ramener le texte à l'horizontale. Cela améliore significativement le CER sur les tranches à texte vertical.

4. **Cas limites** : pour les tranches avec du texte à des angles intermédiaires (oblique), nous appliquons une rotation fine basée sur l'angle exact détecté. Les cas de texte mixte (certains mots horizontaux, d'autres verticaux) restent difficiles et représentent une des limites actuelles.

---

## Question 3 : « Quelles sont les limites ? »

Les principales limites identifiées sont :

1. **Qualité de l'image d'entrée** : le pipeline nécessite une résolution minimale de 1080p et un éclairage relativement homogène. Les images floues, très sombres ou prises avec un angle de plus de ~30° par rapport à l'étagère dégradent fortement les résultats.

2. **Polices décoratives et manuscrites** : les modèles OCR sont entraînés principalement sur du texte imprimé standard. Les polices très stylisées, les logos et le texte manuscrit sont souvent mal reconnus (CER > 50 % dans ces cas).

3. **Segmentation d'étagères complexes** : l'algorithme basé sur Hough (lignes verticales) suppose des livres droits et alignés. Les livres très inclinés, empilés horizontalement, ou les étagères avec des objets décoratifs intercalés créent des erreurs de segmentation.

4. **Dépendance aux API externes** : l'enrichissement bibliographique requiert un accès réseau et dépend de la couverture des API Google Books et Open Library. Les ouvrages rares, auto-édités ou en langues peu courantes peuvent ne pas être trouvés.

5. **Livres sans texte sur la tranche** : environ 10-15 % des livres ont une tranche sans texte lisible (couverture unie, motif graphique). Ces livres ne peuvent pas être identifiés par notre approche actuelle.

6. **Performance** : ~15 secondes par image est acceptable pour un usage interactif, mais insuffisant pour du traitement massif en production.

---

## Question 4 : « Comment améliorer les résultats ? »

Plusieurs pistes d'amélioration ont été identifiées :

### Court terme (réalisable rapidement)
- **Fine-tuning du modèle OCR** sur un corpus de tranches de livres français pour améliorer la reconnaissance des polices courantes en édition.
- **Augmentation du jeu de données** d'évaluation (actuellement 15 images) pour des métriques plus robustes.
- **Optimisation des seuils** de segmentation et de détection par grid search sur le jeu de validation.

### Moyen terme
- **Remplacer Hough par un modèle de détection d'objets** (YOLO, Faster R-CNN) entraîné spécifiquement sur des tranches de livres. Cela améliorerait la segmentation sur les cas complexes (livres inclinés, empilés).
- **Intégrer un modèle OCR multilingue** plus performant pour supporter les langues non latines (arabe, chinois, japonais).
- **Cache local des résultats API** pour accélérer les requêtes récurrentes et réduire la dépendance réseau.

### Long terme
- **Mode batch automatisé** pour traiter des bibliothèques entières (dossiers d'images).
- **Apprentissage actif** : utiliser les corrections manuelles de l'utilisateur dans l'interface Streamlit pour améliorer progressivement le modèle.
- **Reconnaissance par la couverture** : compléter l'approche OCR par une reconnaissance visuelle de la couverture (image matching) pour les livres sans texte lisible sur la tranche.

---

## Notes générales pour la présentation

### Timing recommandé (~20 minutes)
- Diapositive 1 (Titre) : 30 secondes
- Diapositive 2 (Problématique) : 2 minutes
- Diapositive 3 (État de l'art) : 2 minutes
- Diapositive 4 (Architecture) : 2 minutes
- Diapositive 5 (Prétraitement) : 2 minutes
- Diapositive 6 (Détection) : 2 minutes
- Diapositive 7 (OCR) : 2-3 minutes
- Diapositive 8 (Post-traitement) : 2 minutes
- Diapositive 9 (Résultats) : 2-3 minutes
- Diapositive 10 (Démo + Conclusion) : 3 minutes

### Points clés à souligner
- L'approche modulaire du pipeline (chaque étape testable indépendamment)
- Le cycle TDD suivi tout au long du développement
- La comparaison objective des modèles OCR avec des métriques quantitatives
- L'interface Streamlit qui rend le projet accessible et démontrable
