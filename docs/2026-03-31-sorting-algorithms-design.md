# Design — sorting-algorithms

**Date :** 2026-03-31
**Sujet :** Les Papyrus de Héron — La Plateforme
**Équipe :** 3 membres (chacun touche à tout)

---

## Contexte

Implémenter 7 algorithmes de tri en Python avec CLI, benchmarking, GUI animée (Pygame) et multithreading.

---

## Structure des fichiers

```
sorting-algorithms/
├── main.py        # Point d'entrée CLI (argparse)
├── sorting.py     # 7 algorithmes de tri avec callback optionnel
├── benchmark.py   # Mesure des temps d'exécution + graphiques matplotlib
├── display.py     # GUI Pygame animée
└── README.md
```

---

## sorting.py

### Signature commune

Chaque algorithme respecte la même signature :

```python
def bubble_sort(arr: list[float], callback=None) -> list[float]:
```

- `arr` : liste d'entrée, jamais modifiée (on travaille sur une copie interne)
- `callback(state: list[float], indices: tuple[int, int])` : appelé à chaque échange ou comparaison significative — alimente la GUI et le benchmarking
- Retourne la liste triée

### Algorithmes à implémenter

1. `selection_sort`
2. `bubble_sort`
3. `insertion_sort`
4. `merge_sort`
5. `quick_sort`
6. `heap_sort`
7. `comb_sort`

### Dictionnaire de dispatch

```python
ALGORITHMS = {
    "selection": selection_sort,
    "bubble":    bubble_sort,
    "insertion": insertion_sort,
    "merge":     merge_sort,
    "quick":     quick_sort,
    "heap":      heap_sort,
    "comb":      comb_sort,
}
```

La valeur spéciale `"all"` dans le CLI n'est pas une clé du dictionnaire — `main.py` la résout en `list(ALGORITHMS.values())` avant d'appeler les algos.

---

## main.py

### Usage CLI

```
python main.py --algo bubble --list 3.5 1.2 8 4
python main.py --algo all --bench
python main.py --algo bubble --gui
python main.py --algo all --gui --threads
```

### Comportement selon les flags

| Flags | Comportement |
|---|---|
| `--algo X --list ...` | Trie et affiche input + output dans le terminal |
| `--bench` | Lance le benchmarking (tous les algos, tailles croissantes) |
| `--gui` | Lance la GUI Pygame animée |
| `--threads` | Combiné avec `--algo all --gui`, chaque algo dans son propre thread |

### Sortie terminal minimale

```
Input  : [3.5, 1.2, 8.0, 4.0]
Output : [1.2, 3.5, 4.0, 8.0]
```

---

## benchmark.py

### Fonction principale

```python
def run_benchmark(algos: list, sizes: list[int]) -> dict:
    # retourne {algo_name: {size: time_seconds}}
```

- Tailles testées : `[100, 500, 1000, 5000, 10000]`
- Listes générées aléatoirement pour chaque taille
- Affichage tableau dans le terminal
- Graphique matplotlib : courbes temps/taille par algo (échelle log), exportable PNG

### Sortie terminal

```
Algorithm   | 100     | 1000    | 10000
------------|---------|---------|--------
bubble      | 0.001s  | 0.12s   | 12.3s
quick       | 0.0001s | 0.003s  | 0.04s
```

---

## display.py

### Layout

Fenêtre divisée en N panneaux (N = nombre d'algos lancés). Chaque panneau affiche :
- Nom de l'algorithme
- Barres verticales représentant les valeurs
- Barres comparées surlignées en rouge
- Statut : en cours / terminé

### Multithreading

Chaque algo tourne dans son propre `threading.Thread`. Les callbacks poussent les états dans une `queue.Queue` par panneau. Le thread Pygame principal (boucle d'événements) lit les queues et redessine — pas de conflit entre threads.

```python
# Thread algo
def run_algo(algo_fn, arr, q):
    algo_fn(arr, callback=lambda state, idx: q.put((state, idx)))

# Boucle Pygame (thread principal)
for panel, q in zip(panels, queues):
    if not q.empty():
        panel.update(*q.get())
```

---

## Rendu attendu (sujet)

- Repo GitHub public nommé `sorting-algorithms`
- Fichiers : `sorting.py`, `main.py`, `README.md`
- README : contexte du projet, description des algos, conclusion/observations sur les performances
