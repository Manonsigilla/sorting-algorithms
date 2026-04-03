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

> À compléter après avoir lancé `python main.py --algo all --bench`

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
