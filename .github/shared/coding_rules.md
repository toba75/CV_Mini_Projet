# Règles de code partagées — ShelfScan

> **Source de vérité unique** pour les règles de code appliquées par les skills `pr-reviewer` et `implementing-task`.
> Chaque agent doit lire ce fichier au début de son workflow.
>
> **Convention** : les sections sont numérotées `§R1` à `§R9` + `§GREP` pour référence croisée.

---

## §R1 — Strict code (no fallbacks)

- [ ] Aucun fallback silencieux (pattern `or []`, `or {}`, `or ""`, `or 0`, `value if value else default`).
- [ ] Aucun `except:` ou `except Exception:` trop large qui continue l'exécution.
- [ ] Aucun paramètre optionnel avec default implicite masquant une erreur.
- [ ] Validation explicite aux frontières (entrées utilisateur, fichiers image, données externes).
- [ ] Erreur explicite (`raise`) en cas d'entrée invalide ou manquante.

## §R2 — Pas de hardcoding

- [ ] Les seuils et paramètres configurables (ex : seuils Canny, confiance OCR, fuzzy matching) sont des constantes nommées ou paramètres de fonction, pas des valeurs magiques hardcodées.
- [ ] Les chemins de fichiers sont construits dynamiquement (pas de chemins absolus hardcodés).
- [ ] Les noms de modèles OCR et d'API utilisés sont configurables.

## §R3 — Reproductibilité

- [ ] Seeds fixées pour toute opération aléatoire (ex : augmentations de données, shuffles).
- [ ] Pas de legacy random API (`np.random.seed`, `random.seed` sans `seed` paramètre explicite). Utiliser `np.random.default_rng(seed)`.
- [ ] Résultats reproductibles sur relance avec les mêmes paramètres et données d'entrée.

## §R4 — Conventions image et données

- [ ] Images OpenCV en BGR — convertir en RGB avant tout modèle deep learning (`cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`).
- [ ] Ne jamais modifier en place une image d'entrée — travailler sur une copie (`img.copy()`).
- [ ] Vérifier les dimensions et types d'image aux frontières (`assert img.ndim == 3`, `assert img.dtype == np.uint8`).
- [ ] Float32 pour les tenseurs d'inférence. Float64 pour les métriques (CER, WER).
- [ ] Images normalisées en [0, 1] ou [-1, 1] selon les exigences du modèle, documentées explicitement.

## §R5 — Gestion des fichiers et I/O

- [ ] Tout `open()` utilise `with`. Les raccourcis `Path.read_text()` / `Path.write_text()` sont acceptés.
- [ ] Les répertoires de sortie (`outputs/`) sont créés avant usage (`mkdir(parents=True, exist_ok=True)`).
- [ ] Validation des extensions de fichier image (`.jpg`, `.jpeg`, `.png`) en entrée.
- [ ] Chemins de fichiers construits avec `pathlib.Path`, pas de concaténation de strings.

## §R6 — Anti-patterns Python / numpy

- [ ] **Mutable default arguments** : pas de `def f(x=[])` ni `def f(x={})`.
- [ ] **Boucles Python sur arrays numpy** : vectoriser les opérations sur les arrays. Utiliser les opérations numpy/OpenCV vectorisées plutôt que des boucles Python sur des pixels ou des régions.
- [ ] **Comparaison float avec ==** : pas de `==` sur des floats numpy. Utiliser `np.isclose`, `np.testing.assert_allclose`, ou `pytest.approx`.
- [ ] **Données désérialisées non validées** : après `json.loads()` ou lecture de fichier CSV, les valeurs sont validées avant utilisation.
- [ ] **open() sans context manager** : tout `open()` utilise `with`.
- [ ] **f-string ou format** : pas de `str + str` dans les messages d'erreur — utiliser f-string.

## §R7 — Qualité du code

- [ ] Nommage snake_case cohérent.
- [ ] Pas de code mort, commenté ou TODO orphelin.
- [ ] Pas de `print()` de debug restant — utiliser `logging` uniquement si nécessaire.
- [ ] Imports propres : pas d'imports inutilisés, pas d'imports `*`. Ordre isort (stdlib → third-party → local, séparés par des lignes vides).
- [ ] Aucune variable morte : chaque variable assignée est utilisée au moins une fois.
- [ ] Pas de fichiers générés ou temporaires inclus dans le versionning.
- [ ] **DRY** : pas de duplication de logique de prétraitement ou d'évaluation entre modules.

## §R8 — Cohérence intermodule

Vérifier que les changements ne créent pas de divergence avec les modules existants.

- [ ] **Signatures et types de retour** : les fonctions/classes modifiées respectent les signatures attendues par les modules appelants.
- [ ] **Format de sortie du pipeline** : les bounding boxes, crops et textes OCR respectent les formats définis entre modules (`preprocess.py` → `segment.py` → `detect_text.py` → `ocr.py` → `postprocess.py`).
- [ ] **Structures de données partagées** : le format JSON de sortie est cohérent entre `postprocess.py` et l'interface Streamlit.
- [ ] **Cohérence des métriques** : CER et taux de détection calculés de manière identique dans `eval.py` et la démo Streamlit.

Une incohérence intermodule est **bloquante** — elle provoque des bugs silencieux à l'intégration.

## §R9 — Bonnes pratiques Computer Vision / OCR

- [ ] **CLAHE appliqué sur le bon canal** : CLAHE s'applique sur le canal L (espace LAB) ou sur l'image en niveaux de gris, pas sur les canaux RGB.
- [ ] **Transformée de Hough calibrée** : les paramètres `threshold`, `minLineLength`, `maxLineGap` sont documentés et justifiés.
- [ ] **CER calculé correctement** : via distance d'édition de Levenshtein normalisée par la longueur de la référence (pas du candidat).
- [ ] **Bounding boxes cohérentes** : les coordonnées sont en format `(x, y, w, h)` ou `(x1, y1, x2, y2)` de manière uniforme dans tout le code.
- [ ] **Résolution d'entrée vérifiée** : alerter si la résolution est inférieure à 1080p recommandée.
- [ ] **Orientation du texte** : les tranches de livres ont souvent du texte vertical — la rotation doit être appliquée avant OCR.
- [ ] **Normalisation du texte** : normalisation unicode (NFC) appliquée sur toutes les sorties OCR avant comparaison.
- [ ] **Fuzzy matching justifié** : le seuil de similarité minimal pour le fuzzy matching vers l'API bibliographique est documenté et configurable.

---

## §GREP — Commandes de scan automatisé

> Commandes à exécuter sur les fichiers modifiés pour preuve factuelle.

```bash
# Initialisation des variables
CHANGED=$(git diff --name-only main...HEAD | grep '\.py$')
CHANGED_SRC=$(echo "$CHANGED" | grep '^src/')
CHANGED_TEST=$(echo "$CHANGED" | grep '^tests/')

# §R1 — Fallbacks silencieux
grep -n ' or \[\]\| or {}\| or ""\| or 0\b\| if .* else ' $CHANGED_SRC

# §R1 — Except trop large
grep -n 'except:$\|except Exception:' $CHANGED_SRC

# §R7 — Print résiduel
grep -n 'print(' $CHANGED_SRC

# §R3 — Legacy random API
grep -n 'np\.random\.seed\|random\.seed' $CHANGED

# §R7 — TODO/FIXME orphelins
grep -n 'TODO\|FIXME\|HACK\|XXX' $CHANGED

# §R5 — Chemins hardcodés OS-spécifiques (tests)
grep -n '/tmp\|/var/tmp\|C:\\' $CHANGED_TEST

# §R6 — Mutable default arguments
grep -n 'def .*=\[\]\|def .*={}' $CHANGED

# §R4 — Images modifiées en place (sans copy)
grep -n 'img\s*=' $CHANGED_SRC | grep -v '\.copy()\|cv2\.\|np\.'

# §R9 — CER calculé sans normalisation
grep -n 'editdistance\|Levenshtein' $CHANGED_SRC

# §R4 — BGR/RGB non converti
grep -n 'COLOR_BGR2RGB\|COLOR_RGB2BGR' $CHANGED_SRC
```

**Pour chaque match** : analyser en contexte (lire les lignes autour) et classer :
- **BLOQUANT** si c'est un vrai problème
- **WARNING** si risque potentiel
- **Faux positif** si le pattern est utilisé correctement (noter dans le rapport)

**Si aucun match** pour un pattern → noter « 0 occurrences (grep exécuté) » dans le rapport comme preuve d'exécution.
