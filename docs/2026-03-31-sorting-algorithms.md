# sorting-algorithms Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implémenter 7 algorithmes de tri avec CLI argparse, benchmarking matplotlib, GUI Pygame animée et multithreading.

**Architecture:** Pattern callback uniforme — chaque algo accepte un `callback(state, indices)` optionnel appelé à chaque échange, ce qui alimente la GUI et le bench sans couplage. La GUI lit des `queue.Queue` alimentées par des threads d'algos pour éviter les conflits Pygame/threading.

**Tech Stack:** Python 3.10+, Pygame 2.6+, Matplotlib 3.5+, pytest, threading, queue, argparse

---

## Fichiers à créer

| Fichier | Responsabilité |
|---|---|
| `sorting.py` | 7 algorithmes de tri avec callback |
| `main.py` | CLI argparse — point d'entrée |
| `benchmark.py` | Mesure des temps + graphiques matplotlib |
| `display.py` | GUI Pygame animée + multithreading |
| `tests/test_sorting.py` | Tests unitaires des 7 algos |
| `tests/test_benchmark.py` | Tests unitaires du benchmarking |
| `tests/test_main.py` | Tests de la CLI |
| `requirements.txt` | Dépendances |
| `README.md` | Documentation du projet |

---

## Task 1 : Setup du projet

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `sorting.py` (vide)
- Create: `main.py` (vide)
- Create: `benchmark.py` (vide)
- Create: `display.py` (vide)
- Create: `tests/__init__.py` (vide)

- [ ] **Step 1 : Initialiser le repo git**

```bash
cd /Users/louisvarennes/sorting-algorithms
git init
git checkout -b main
```

- [ ] **Step 2 : Créer `requirements.txt`**

```
pygame>=2.6.0
matplotlib>=3.5.0
numpy>=1.21.0
pytest>=7.0.0
```

- [ ] **Step 3 : Créer `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
venv/
benchmark.png
*.db
```

- [ ] **Step 4 : Créer les fichiers vides**

```bash
touch sorting.py main.py benchmark.py display.py
mkdir -p tests && touch tests/__init__.py
```

- [ ] **Step 5 : Installer les dépendances**

```bash
pip install -r requirements.txt
```

- [ ] **Step 6 : Premier commit**

```bash
git add requirements.txt .gitignore sorting.py main.py benchmark.py display.py tests/__init__.py
git commit -m "chore: setup initial project structure"
```

---

## Task 2 : Algorithmes simples (selection, bubble, insertion)

**Files:**
- Modify: `sorting.py`
- Create: `tests/test_sorting.py`

- [ ] **Step 1 : Écrire les tests paramétrés**

```python
# tests/test_sorting.py
import pytest
from sorting import selection_sort, bubble_sort, insertion_sort

SIMPLE_ALGOS = [selection_sort, bubble_sort, insertion_sort]

@pytest.mark.parametrize("sort_fn", SIMPLE_ALGOS)
def test_sorts_random_list(sort_fn):
    arr = [3.5, 1.2, 8.0, 4.0, 2.1]
    assert sort_fn(arr) == sorted(arr)

@pytest.mark.parametrize("sort_fn", SIMPLE_ALGOS)
def test_does_not_modify_input(sort_fn):
    arr = [3.5, 1.2, 8.0]
    original = arr.copy()
    sort_fn(arr)
    assert arr == original

@pytest.mark.parametrize("sort_fn", SIMPLE_ALGOS)
def test_empty_list(sort_fn):
    assert sort_fn([]) == []

@pytest.mark.parametrize("sort_fn", SIMPLE_ALGOS)
def test_single_element(sort_fn):
    assert sort_fn([42.0]) == [42.0]

@pytest.mark.parametrize("sort_fn", SIMPLE_ALGOS)
def test_reverse_sorted(sort_fn):
    arr = [5.0, 4.0, 3.0, 2.0, 1.0]
    assert sort_fn(arr) == [1.0, 2.0, 3.0, 4.0, 5.0]

@pytest.mark.parametrize("sort_fn", SIMPLE_ALGOS)
def test_callback_is_called(sort_fn):
    arr = [3.0, 1.0, 2.0]
    calls = []
    sort_fn(arr, callback=lambda state, idx: calls.append((state, idx)))
    assert len(calls) > 0

@pytest.mark.parametrize("sort_fn", SIMPLE_ALGOS)
def test_callback_receives_valid_args(sort_fn):
    arr = [3.0, 1.0, 2.0]
    def check(state, idx):
        assert isinstance(state, list)
        assert len(state) == len(arr)
        assert isinstance(idx, tuple) and len(idx) == 2
    sort_fn(arr, callback=check)
```

- [ ] **Step 2 : Vérifier que les tests échouent**

```bash
pytest tests/test_sorting.py -v
```

Attendu : `ImportError` (fonctions non définies)

- [ ] **Step 3 : Implémenter les 3 algorithmes dans `sorting.py`**

```python
# sorting.py

def selection_sort(arr: list[float], callback=None) -> list[float]:
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            if callback:
                callback(arr.copy(), (i, min_idx))
    return arr


def bubble_sort(arr: list[float], callback=None) -> list[float]:
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                if callback:
                    callback(arr.copy(), (j, j + 1))
    return arr


def insertion_sort(arr: list[float], callback=None) -> list[float]:
    arr = arr.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
            if callback:
                callback(arr.copy(), (j + 1, j + 2))
        arr[j + 1] = key
    return arr
```

- [ ] **Step 4 : Vérifier que les tests passent**

```bash
pytest tests/test_sorting.py -v
```

Attendu : 21 tests PASS

- [ ] **Step 5 : Commit**

```bash
git add sorting.py tests/test_sorting.py
git commit -m "feat: implement selection, bubble, insertion sort with callbacks"
```

---

## Task 3 : Algorithmes récursifs (merge, quick)

**Files:**
- Modify: `sorting.py`
- Modify: `tests/test_sorting.py`

- [ ] **Step 1 : Ajouter les tests pour merge et quick**

Ajouter à la fin de `tests/test_sorting.py` :

```python
from sorting import merge_sort, quick_sort

RECURSIVE_ALGOS = [merge_sort, quick_sort]

@pytest.mark.parametrize("sort_fn", RECURSIVE_ALGOS)
def test_recursive_sorts_random_list(sort_fn):
    arr = [3.5, 1.2, 8.0, 4.0, 2.1]
    assert sort_fn(arr) == sorted(arr)

@pytest.mark.parametrize("sort_fn", RECURSIVE_ALGOS)
def test_recursive_does_not_modify_input(sort_fn):
    arr = [3.5, 1.2, 8.0]
    original = arr.copy()
    sort_fn(arr)
    assert arr == original

@pytest.mark.parametrize("sort_fn", RECURSIVE_ALGOS)
def test_recursive_empty_list(sort_fn):
    assert sort_fn([]) == []

@pytest.mark.parametrize("sort_fn", RECURSIVE_ALGOS)
def test_recursive_callback_is_called(sort_fn):
    arr = [3.0, 1.0, 2.0]
    calls = []
    sort_fn(arr, callback=lambda state, idx: calls.append((state, idx)))
    assert len(calls) > 0
```

- [ ] **Step 2 : Vérifier que les nouveaux tests échouent**

```bash
pytest tests/test_sorting.py -v -k "recursive"
```

Attendu : `ImportError`

- [ ] **Step 3 : Implémenter merge_sort et quick_sort dans `sorting.py`**

Ajouter à la suite de `sorting.py` :

```python
def merge_sort(arr: list[float], callback=None) -> list[float]:
    arr = arr.copy()
    _merge_sort_helper(arr, 0, len(arr) - 1, callback)
    return arr


def _merge_sort_helper(arr, left, right, callback):
    if left < right:
        mid = (left + right) // 2
        _merge_sort_helper(arr, left, mid, callback)
        _merge_sort_helper(arr, mid + 1, right, callback)
        _merge(arr, left, mid, right, callback)


def _merge(arr, left, mid, right, callback):
    left_part = arr[left:mid + 1]
    right_part = arr[mid + 1:right + 1]
    i = j = 0
    k = left
    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        k += 1
        if callback:
            callback(arr.copy(), (left, right))
    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1
    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1
    if callback:
        callback(arr.copy(), (left, right))


def quick_sort(arr: list[float], callback=None) -> list[float]:
    arr = arr.copy()
    _quick_sort_helper(arr, 0, len(arr) - 1, callback)
    return arr


def _quick_sort_helper(arr, low, high, callback):
    if low < high:
        pivot_idx = _partition(arr, low, high, callback)
        _quick_sort_helper(arr, low, pivot_idx - 1, callback)
        _quick_sort_helper(arr, pivot_idx + 1, high, callback)


def _partition(arr, low, high, callback):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            if callback:
                callback(arr.copy(), (i, j))
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    if callback:
        callback(arr.copy(), (i + 1, high))
    return i + 1
```

- [ ] **Step 4 : Vérifier que tous les tests passent**

```bash
pytest tests/test_sorting.py -v
```

Attendu : tous PASS

- [ ] **Step 5 : Commit**

```bash
git add sorting.py tests/test_sorting.py
git commit -m "feat: implement merge sort and quick sort with callbacks"
```

---

## Task 4 : Algorithmes avancés (heap, comb) + ALGORITHMS dict

**Files:**
- Modify: `sorting.py`
- Modify: `tests/test_sorting.py`

- [ ] **Step 1 : Ajouter les tests pour heap et comb**

Ajouter à la fin de `tests/test_sorting.py` :

```python
from sorting import heap_sort, comb_sort, ALGORITHMS

ADVANCED_ALGOS = [heap_sort, comb_sort]

@pytest.mark.parametrize("sort_fn", ADVANCED_ALGOS)
def test_advanced_sorts_random_list(sort_fn):
    arr = [3.5, 1.2, 8.0, 4.0, 2.1]
    assert sort_fn(arr) == sorted(arr)

@pytest.mark.parametrize("sort_fn", ADVANCED_ALGOS)
def test_advanced_does_not_modify_input(sort_fn):
    arr = [3.5, 1.2, 8.0]
    original = arr.copy()
    sort_fn(arr)
    assert arr == original

@pytest.mark.parametrize("sort_fn", ADVANCED_ALGOS)
def test_advanced_empty_list(sort_fn):
    assert sort_fn([]) == []

@pytest.mark.parametrize("sort_fn", ADVANCED_ALGOS)
def test_advanced_callback_is_called(sort_fn):
    arr = [3.0, 1.0, 2.0]
    calls = []
    sort_fn(arr, callback=lambda state, idx: calls.append((state, idx)))
    assert len(calls) > 0

def test_algorithms_dict_has_all_keys():
    expected = {"selection", "bubble", "insertion", "merge", "quick", "heap", "comb"}
    assert set(ALGORITHMS.keys()) == expected

def test_algorithms_dict_values_are_callable():
    for name, fn in ALGORITHMS.items():
        assert callable(fn), f"{name} n'est pas callable"
```

- [ ] **Step 2 : Vérifier que les nouveaux tests échouent**

```bash
pytest tests/test_sorting.py -v -k "advanced or algorithms_dict"
```

Attendu : `ImportError`

- [ ] **Step 3 : Implémenter heap_sort, comb_sort et ALGORITHMS dans `sorting.py`**

Ajouter à la fin de `sorting.py` :

```python
def heap_sort(arr: list[float], callback=None) -> list[float]:
    arr = arr.copy()
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        _heapify(arr, n, i, callback)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        if callback:
            callback(arr.copy(), (0, i))
        _heapify(arr, i, 0, callback)
    return arr


def _heapify(arr, n, i, callback):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2
    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        if callback:
            callback(arr.copy(), (i, largest))
        _heapify(arr, n, largest, callback)


def comb_sort(arr: list[float], callback=None) -> list[float]:
    arr = arr.copy()
    n = len(arr)
    gap = n
    shrink = 1.3
    sorted_ = False
    while not sorted_:
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_ = True
        i = 0
        while i + gap < n:
            if arr[i] > arr[i + gap]:
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                sorted_ = False
                if callback:
                    callback(arr.copy(), (i, i + gap))
            i += 1
    return arr


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

- [ ] **Step 4 : Vérifier que tous les tests passent**

```bash
pytest tests/test_sorting.py -v
```

Attendu : tous PASS (35+ tests)

- [ ] **Step 5 : Commit**

```bash
git add sorting.py tests/test_sorting.py
git commit -m "feat: implement heap sort, comb sort and ALGORITHMS registry"
```

---

## Task 5 : main.py — CLI argparse

**Files:**
- Modify: `main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1 : Écrire les tests CLI**

```python
# tests/test_main.py
import pytest
from unittest.mock import patch
from main import main


def run_main(args):
    with patch("sys.argv", ["main.py"] + args):
        main()


def test_cli_sorts_and_prints(capsys):
    run_main(["--algo", "bubble", "--list", "3.0", "1.0", "2.0"])
    out = capsys.readouterr().out
    assert "Input" in out
    assert "Output" in out
    assert "1.0" in out


def test_cli_all_algos_sorts(capsys):
    run_main(["--algo", "all", "--list", "3.0", "1.0", "2.0"])
    out = capsys.readouterr().out
    # all affiche le résultat du premier algo
    assert "Output" in out


def test_cli_missing_list_shows_error(capsys):
    run_main(["--algo", "bubble"])
    out = capsys.readouterr().out
    assert "Erreur" in out or "requis" in out
```

- [ ] **Step 2 : Vérifier que les tests échouent**

```bash
pytest tests/test_main.py -v
```

Attendu : `ImportError` ou erreurs

- [ ] **Step 3 : Implémenter `main.py`**

```python
# main.py
import argparse
from sorting import ALGORITHMS


BENCH_SIZES = [100, 500, 1000, 5000, 10000]


def parse_args():
    parser = argparse.ArgumentParser(description="Outil de tri — Les Papyrus de Héron")
    parser.add_argument(
        "--algo",
        required=True,
        choices=list(ALGORITHMS.keys()) + ["all"],
        help="Algorithme à utiliser (ou 'all' pour tous)",
    )
    parser.add_argument(
        "--list",
        dest="numbers",
        nargs="+",
        type=float,
        help="Liste de nombres réels à trier",
    )
    parser.add_argument(
        "--bench",
        action="store_true",
        help="Lancer le benchmarking sur toutes les tailles",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Lancer la visualisation Pygame",
    )
    parser.add_argument(
        "--threads",
        action="store_true",
        help="Exécuter les algos en parallèle (requiert --algo all --gui)",
    )
    return parser.parse_args()


def resolve_algos(algo_name: str) -> list[tuple[str, callable]]:
    if algo_name == "all":
        return list(ALGORITHMS.items())
    return [(algo_name, ALGORITHMS[algo_name])]


def main():
    args = parse_args()
    algos = resolve_algos(args.algo)

    if args.bench:
        from benchmark import run_benchmark, print_benchmark_table, plot_benchmark
        results = run_benchmark(algos, BENCH_SIZES)
        print_benchmark_table(results, BENCH_SIZES)
        plot_benchmark(results, BENCH_SIZES)
        return

    if args.gui:
        from display import run_display
        arr = args.numbers or [5.0, 3.0, 8.0, 1.0, 9.0, 2.0, 7.0, 4.0, 6.0]
        run_display(algos, arr, threaded=args.threads)
        return

    if args.numbers:
        print(f"Input  : {args.numbers}")
        _, sort_fn = algos[0]
        result = sort_fn(args.numbers)
        print(f"Output : {result}")
    else:
        print("Erreur : --list requis sans --bench ni --gui")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4 : Vérifier que les tests passent**

```bash
pytest tests/test_main.py -v
```

Attendu : tous PASS

- [ ] **Step 5 : Tester manuellement la CLI**

```bash
python main.py --algo bubble --list 3.5 1.2 8.0 4.0
```

Attendu :
```
Input  : [3.5, 1.2, 8.0, 4.0]
Output : [1.2, 3.5, 4.0, 8.0]
```

- [ ] **Step 6 : Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: implement CLI with argparse"
```

---

## Task 6 : benchmark.py — mesure des temps + matplotlib

**Files:**
- Modify: `benchmark.py`
- Create: `tests/test_benchmark.py`

- [ ] **Step 1 : Écrire les tests de benchmark**

```python
# tests/test_benchmark.py
from benchmark import run_benchmark
from sorting import ALGORITHMS


def test_run_benchmark_returns_correct_structure():
    algos = [("bubble", ALGORITHMS["bubble"])]
    sizes = [10, 50]
    results = run_benchmark(algos, sizes)
    assert "bubble" in results
    assert 10 in results["bubble"]
    assert 50 in results["bubble"]


def test_run_benchmark_times_are_non_negative():
    algos = [("selection", ALGORITHMS["selection"])]
    sizes = [100]
    results = run_benchmark(algos, sizes)
    assert results["selection"][100] >= 0


def test_run_benchmark_all_algos():
    algos = list(ALGORITHMS.items())
    sizes = [10]
    results = run_benchmark(algos, sizes)
    assert set(results.keys()) == set(ALGORITHMS.keys())
```

- [ ] **Step 2 : Vérifier que les tests échouent**

```bash
pytest tests/test_benchmark.py -v
```

Attendu : `ImportError`

- [ ] **Step 3 : Implémenter `benchmark.py`**

```python
# benchmark.py
import time
import random


def run_benchmark(algos: list[tuple], sizes: list[int]) -> dict:
    """
    Retourne {algo_name: {size: time_seconds}}
    """
    results = {}
    for name, fn in algos:
        results[name] = {}
        for size in sizes:
            arr = [random.uniform(0, 1000) for _ in range(size)]
            start = time.perf_counter()
            fn(arr)
            elapsed = time.perf_counter() - start
            results[name][size] = elapsed
    return results


def print_benchmark_table(results: dict, sizes: list[int]):
    col_w = 10
    header = f"{'Algorithm':<14}" + "".join(f"| {str(s):<{col_w}}" for s in sizes)
    print(header)
    print("-" * len(header))
    for name, timings in results.items():
        row = f"{name:<14}" + "".join(f"| {timings[s]:.5f}s  " for s in sizes)
        print(row)


def plot_benchmark(results: dict, sizes: list[int], output_path: str = "benchmark.png"):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))
    for name, timings in results.items():
        ax.plot(sizes, [timings[s] for s in sizes], marker="o", label=name)
    ax.set_xlabel("Taille de la liste")
    ax.set_ylabel("Temps (secondes)")
    ax.set_title("Comparaison des algorithmes de tri")
    ax.set_yscale("log")
    ax.legend()
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()
    print(f"Graphique sauvegardé : {output_path}")
```

- [ ] **Step 4 : Vérifier que les tests passent**

```bash
pytest tests/test_benchmark.py -v
```

Attendu : tous PASS

- [ ] **Step 5 : Tester manuellement**

```bash
python main.py --algo all --bench
```

Attendu : tableau dans le terminal + fenêtre matplotlib + fichier `benchmark.png`

- [ ] **Step 6 : Commit**

```bash
git add benchmark.py tests/test_benchmark.py
git commit -m "feat: implement benchmarking with matplotlib visualization"
```

---

## Task 7 : display.py — GUI Pygame panneau unique

**Files:**
- Modify: `display.py`

*Note : la GUI n'est pas testée automatiquement — validation manuelle.*

- [ ] **Step 1 : Implémenter `display.py`**

```python
# display.py
import pygame
import threading
import queue
from typing import Callable

WIDTH = 1200
HEIGHT = 600
FPS = 60
BG_COLOR = (20, 20, 30)
BAR_COLOR = (100, 149, 237)
HIGHLIGHT_COLOR = (220, 50, 50)
DONE_COLOR = (50, 200, 100)
TEXT_COLOR = (255, 255, 255)


class SortPanel:
    def __init__(self, name: str, arr: list[float], x: int, y: int, w: int, h: int):
        self.name = name
        self.arr = arr.copy()
        self.highlighted = (-1, -1)
        self.done = False
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def update(self, state: list[float], indices: tuple[int, int]):
        self.arr = state
        self.highlighted = indices

    def mark_done(self):
        self.done = True
        self.highlighted = (-1, -1)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        pygame.draw.rect(surface, (30, 30, 40), (self.x, self.y, self.w, self.h))
        n = len(self.arr)
        if n == 0:
            return
        max_val = max(self.arr)
        bar_w = self.w / n
        bar_area_h = self.h - 30

        for i, val in enumerate(self.arr):
            bar_h = int((val / max_val) * bar_area_h)
            bx = self.x + int(i * bar_w)
            by = self.y + self.h - bar_h
            if self.done:
                color = DONE_COLOR
            elif i in self.highlighted:
                color = HIGHLIGHT_COLOR
            else:
                color = BAR_COLOR
            pygame.draw.rect(surface, color, (bx, by, max(1, int(bar_w) - 1), bar_h))

        status = "DONE" if self.done else "en cours..."
        label = font.render(f"{self.name} — {status}", True, TEXT_COLOR)
        surface.blit(label, (self.x + 5, self.y + 5))


def run_display(algos: list[tuple[str, Callable]], arr: list[float], threaded: bool = False):
    pygame.init()
    n = len(algos)
    panel_w = WIDTH // n
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sorting Algorithms Visualizer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    queues = [queue.Queue() for _ in algos]
    panels = [
        SortPanel(name, arr, i * panel_w, 0, panel_w, HEIGHT)
        for i, (name, _) in enumerate(algos)
    ]

    def run_algo(fn, q):
        fn(arr, callback=lambda state, idx: q.put(("update", state, idx)))
        q.put(("done", None, None))

    threads = [
        threading.Thread(target=run_algo, args=(fn, queues[i]), daemon=True)
        for i, (_, fn) in enumerate(algos)
    ]

    if threaded:
        for t in threads:
            t.start()
    else:
        threads[0].start()

    sequential_idx = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        for i, (panel, q) in enumerate(zip(panels, queues)):
            while not q.empty():
                msg = q.get_nowait()
                if msg[0] == "update":
                    panel.update(msg[1], msg[2])
                elif msg[0] == "done":
                    panel.mark_done()
                    if not threaded and sequential_idx < n - 1:
                        sequential_idx += 1
                        threads[sequential_idx].start()

        screen.fill(BG_COLOR)
        for panel in panels:
            panel.draw(screen, font)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
```

- [ ] **Step 2 : Tester manuellement — 1 algo**

```bash
python main.py --algo bubble --list 5 3 8 1 9 2 7 4 6 --gui
```

Attendu : fenêtre Pygame avec barres animées, barres rouges sur les éléments comparés, barres vertes en fin de tri.

- [ ] **Step 3 : Tester manuellement — séquentiel, tous les algos**

```bash
python main.py --algo all --list 5 3 8 1 9 2 7 4 6 --gui
```

Attendu : 7 panneaux, les algos s'exécutent l'un après l'autre.

- [ ] **Step 4 : Tester manuellement — multithreading**

```bash
python main.py --algo all --list 5 3 8 1 9 2 7 4 6 --gui --threads
```

Attendu : 7 panneaux, tous les algos s'exécutent simultanément.

- [ ] **Step 5 : Commit**

```bash
git add display.py
git commit -m "feat: implement Pygame animated GUI with multithreading support"
```

---

## Task 8 : README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1 : Écrire le README**

```markdown
# sorting-algorithms

Projet scolaire — La Plateforme | Groupe de 3

Outil d'automatisation de tri de listes de nombres réels.
Implémente 7 algorithmes de tri avec visualisation animée et benchmarking.

## Algorithmes implémentés

| Algorithme | Complexité moyenne | Complexité pire cas | Stable |
|---|---|---|---|
| Tri par sélection | O(n²) | O(n²) | Non |
| Tri à bulles | O(n²) | O(n²) | Oui |
| Tri par insertion | O(n²) | O(n²) | Oui |
| Tri fusion | O(n log n) | O(n log n) | Oui |
| Tri rapide | O(n log n) | O(n²) | Non |
| Tri par tas | O(n log n) | O(n log n) | Non |
| Tri à peigne | O(n log n) | O(n²) | Non |

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
# Trier une liste dans le terminal
python main.py --algo bubble --list 3.5 1.2 8.0 4.0

# Lancer le benchmarking
python main.py --algo all --bench

# Visualisation animée (1 algo)
python main.py --algo quick --gui

# Visualisation animée (tous les algos, séquentiel)
python main.py --algo all --gui

# Visualisation animée (tous les algos, en parallèle)
python main.py --algo all --gui --threads
```

## Observations sur les performances

[À compléter après avoir lancé le benchmark — noter les temps mesurés et comparer]

## Conclusion

[À compléter — quel algo est le plus rapide ? Pourquoi ?]
```

- [ ] **Step 2 : Commit final**

```bash
git add README.md
git commit -m "docs: add README with usage and algorithm table"
```

---

## Récapitulatif des commandes de test

```bash
# Tous les tests unitaires
pytest tests/ -v

# Tests sorting uniquement
pytest tests/test_sorting.py -v

# Tests benchmark uniquement
pytest tests/test_benchmark.py -v

# Tests CLI uniquement
pytest tests/test_main.py -v
```
