# sorting-algorithms

Projet scolaire — La Plateforme | Groupe de 3

Outil d'automatisation de tri de listes de nombres réels.
Implémente 8 algorithmes de tri avec visualisation animée et benchmarking.

---

## Algorithmes implémentés

| Algorithme | Complexité moyenne | Complexité pire cas | Mémoire supplémentaire |
| --- | --- | --- | --- |
| Tri par sélection | O(n²) | O(n²) | Non |
| Tri à bulles | O(n²) | O(n) si déjà trié | Non |
| Tri par insertion | O(n²) | O(n) si déjà trié | Non |
| Tri fusion | O(n log n) | O(n log n) | Oui |
| Tri rapide | O(n log n) | O(n²) | Non |
| Tri par tas | O(n log n) | O(n log n) | Non |
| Tri à peigne | O(n log n) | O(n²) | Non |
| **Timsort** | **O(n log n)** | **O(n log n)** | **Oui** |

---

## Améliorations apportées

- **Tri à bulles** : ajout d'un flag `swapped` — s'arrête dès qu'un passage ne fait aucun échange, ce qui le rend O(n) sur une liste déjà triée.
- **Tri rapide** : pivot aléatoire au lieu du dernier élément — réduit fortement le risque de tomber sur le pire cas O(n²) avec une liste déjà triée.
- **Affichage terminal** : l'input n'est affiché qu'une fois, les résultats sont alignés par algo.
- **Flag `--reverse`** : permet de trier dans l'ordre décroissant.

---

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
# Trier une liste dans le terminal
python main.py --algo bubble --list 3.5 1.2 8.0 4.0

# Trier avec tous les algos
python main.py --algo all --list 3.5 1.2 8.0 4.0

# Trier dans l'ordre décroissant
python main.py --algo quick --list 3.5 1.2 8.0 4.0 --reverse

# Lancer le benchmarking
python main.py --algo all --bench

# Visualisation animée (1 algo)
python main.py --algo quick --gui

# Visualisation animée (tous les algos, séquentiel)
python main.py --algo all --gui

# Visualisation animée (tous les algos, en parallèle)
python main.py --algo all --gui --threads
```

---

## Observations sur les performances

Après avoir lancé les différents benchmarks (`--bench`, `--bench-compare`, `--bench-summary`, `--bench-1v1`), on observe clairement la différence de comportement entre les algorithmes en `O(n²)` et ceux en `O(n log n)`.

### 1. Algorithmes en O(n²)

Les algorithmes naïfs (sélection, bulles, insertion, peigne) deviennent rapidement impraticables lorsque la taille de la liste augmente :

- Pour des tailles de l’ordre de 100 à 500, les temps restent raisonnables.
- Au‑delà de quelques milliers d’éléments, les temps d’exécution explosent et les écarts entre `O(n²)` et `O(n log n)` deviennent très visibles.
- Le **tri à bulles optimisé** s’en sort nettement mieux sur des listes déjà triées ou presque triées grâce au flag `swapped`, où il se comporte en pratique comme un algorithme en `O(n)`.

### 2. Algorithmes en O(n log n)

Les algorithmes plus avancés (fusion, rapide, tas, peigne en pratique, timsort) montrent une montée en charge beaucoup plus progressive :

- **Tri rapide (quick sort)** est souvent le plus rapide sur des données aléatoires grâce au pivot aléatoire, tout en gardant un coût mémoire très faible (tri en place).
- **Tri fusion (merge sort)** est légèrement plus lent que quick sort, mais reste très stable et prévisible, au prix d’une consommation mémoire supplémentaire.
- **Tri par tas (heap sort)** est globalement compétitif, avec des performances proches de `O(n log n)` dans tous les cas, sans allocation de mémoire supplémentaire significative.
- **Timsort** est particulièrement performant sur des données partiellement triées : il profite des *runs* déjà ordonnés et réduit drastiquement le nombre d’opérations nécessaires.

### 3. Temps vs mémoire

Les mesures de consommation mémoire montrent que :

- Les algorithmes en place (sélection, bulles, insertion, rapide, tas, peigne) ont une empreinte mémoire faible et assez similaire.
- Les algorithmes basés sur des fusions (`merge sort`, `timsort`) consomment plus de mémoire à cause des tableaux temporaires, mais cette consommation reste maîtrisée pour les tailles testées dans le cadre du projet.

### 4. Synthèse générale

- Pour de **petites tailles**, la différence entre les algos est peu visible, et les surcoûts des algorithmes avancés peuvent même parfois les rendre légèrement plus lents.
- Pour des **tailles moyennes à grandes**, les algorithmes en `O(n log n)` dominent clairement, surtout `quick sort`, `heap sort` et `timsort`.
- En conditions réelles (données souvent partiellement triées), **timsort** est l’algorithme le plus adapté et confirme pourquoi il est utilisé dans les bibliothèques standard des langages modernes.

---

## Benchmarking et comparaisons

Le projet intègre un module de **benchmark avancé** (`benchmark.py`) qui permet de mesurer :

- Le **temps d’exécution** de chaque algorithme (en millisecondes)
- La **consommation mémoire** maximale pendant le tri (en Mo)
- Une **estimation automatique de la complexité asymptotique** (en comparant les courbes mesurées aux modèles théoriques `O(n)`, `O(n log n)`, `O(n²)`, `O(n³)`)

### Modes de benchmark disponibles

1. **Benchmark simple (tous les algos vs différentes tailles)**  
   Affiche un tableau temps/tailles et, selon l’implémentation choisie, peut générer un graphique matplotlib :

   ```bash
   python main.py --algo all --bench
   ```

2. **Comparaison complète de tous les algorithmes**  
   Compare tous les algos entre eux sur plusieurs tailles, pour le temps **et** la mémoire, puis estime la complexité de chacun :

   ```bash
   python main.py --algo all --bench-compare
   ```

3. **Résumé statistique global**  
   Affiche un résumé synthétique avec temps moyen/min/max, mémoire moyenne/min/max et complexité estimée pour chaque algorithme :

   ```bash
   python main.py --algo all --bench-summary
   ```

4. **Duel 1 vs 1 entre deux algorithmes**  
   Compare deux algos choisis (temps, RAM, complexité estimée, score de victoires) :

   ```bash
   python main.py --algo all --bench-1v1 bubble quick
   ```

   Tu peux remplacer `bubble` et `quick` par n’importe quel nom présent dans `ALGORITHMS` (par exemple `selection`, `merge`, `heap`, `tim`, etc.).

### Tailles et métriques

Par défaut, les comparaisons utilisent des tailles croissantes du type :

- `100`, `500`, `1000`, `5000`, `10000`

Pour chaque paire *(algorithme, taille)*, le benchmark :

- génère une liste de flottants aléatoires,
- exécute l’algorithme sur cette liste,
- mesure le **temps** avec `time.perf_counter()`,
- suit la **mémoire** avec `tracemalloc`,
- stocke les résultats dans une structure du type :

```python
{
  "bubble": {
    100:  {"time": 0.45, "memory": 0.80},
    500:  {"time": 5.32, "memory": 1.10},
    1000: {"time": 22.15, "memory": 1.45},
    # ...
  },
  # ...
}
```

Ces outils permettent de **visualiser concrètement** l’écart entre les algorithmes en `O(n²)` et ceux en `O(n log n)`, aussi bien en temps qu’en consommation mémoire, et de vérifier expérimentalement les complexités théoriques vues en cours.

---

## Aspect Visuel et Multithreading (Pygame)

Afin d'apporter un aspect visuel à l'efficacité des algorithmes de tri, une interface graphique a été développée en utilisant **Pygame**.
L'exécution de l'interface utilise le **multithreading** : l'interface tourne sur le thread principal pour rester fluide, tandis que chaque algorithme s'exécute sur son propre thread, permettant d'observer les comparaisons simultanément (parallélisation).

Pour bien comprendre ce qui se passe à l'écran, la longueur des barres encode la valeur (plus c'est grand, plus c'est haut) et un code couleur spécifique a été mis en place :

- **Bleu** : État neutre de l'élément.
- **Orange** : Barres actuellement comparées.
- **Rouge** : Barre active ou en cours de déplacement (swap).
- **Vert menthe** : Minimum trouvé (dans le tri par sélection) ou pivot actuel (tri rapide).
- **Violet** : Pivot secondaire (tri rapide).
- **Vert** : Position définitivement triée de l'élément.

Les compteurs en haut de chaque algorithme permettent de visualiser concrètement pourquoi des algorithmes en *O(n log n)* sont plus performants que ceux en *O(n²)* en comptant le nombre d'étapes nécessaires.

---

## Conclusion

Au-delà des 7 algorithmes imposés par le sujet, nous avons implémenté le **Timsort** — l'algorithme utilisé nativement par Python (`sorted()`), Java, Android et Swift. Créé en 2002 par Tim Peters, il est un hybride entre le tri par insertion et le tri fusion.

Sa force réside dans l'exploitation des séquences déjà partiellement triées dans les données réelles : il découpe la liste en petits blocs (appelés *runs*), les trie avec le tri par insertion, puis les fusionne. Cela lui permet d'atteindre O(n) sur une liste presque triée, tout en garantissant O(n log n) dans le pire cas.

C'est l'algorithme qui surpasserait tous les autres de ce projet en conditions réelles — ce qui explique pourquoi il est devenu le standard dans les langages modernes.
