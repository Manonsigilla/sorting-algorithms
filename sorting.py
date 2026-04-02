# =============================================================================
# sorting.py — Implémentation des 7 algorithmes de tri
# =============================================================================
# Chaque fonction respecte la même signature :
#   - arr      : liste de nombres réels à trier (jamais modifiée)
#   - callback : fonction optionnelle appelée à chaque échange
#                callback(state: list[float], indices: tuple[int, int])
#                → utilisée pour animer la GUI et mesurer les étapes
# =============================================================================


def selection_sort(arr: list[float], callback=None) -> list[float]:
    """
    Tri par sélection — O(n²)
    À chaque tour, cherche le plus petit élément du reste
    et le place à sa position définitive.
    """
    arr = arr.copy()
    n = len(arr)

    for i in range(n):
        # On suppose que le minimum est à la position i
        min_idx = i

        # On cherche s'il existe un élément plus petit après i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j

        # Si on a trouvé un minimum plus loin, on échange
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            if callback:
                callback(arr.copy(), (i, min_idx))

    return arr


def bubble_sort(arr: list[float], callback=None) -> list[float]:
    """
    Tri à bulles — O(n²), O(n) si déjà trié
    Compare chaque paire de voisins et les échange si nécessaire.
    Les grands éléments "remontent" comme des bulles à chaque passage.
    Optimisation : s'arrête dès qu'un passage ne fait aucun échange.
    """
    arr = arr.copy()
    n = len(arr)

    for i in range(n):
        swapped = False  # Optimisation : détecte si la liste est déjà triée

        # À chaque tour, les i derniers éléments sont déjà triés
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
                if callback:
                    callback(arr.copy(), (j, j + 1))

        # Si aucun échange n'a eu lieu, la liste est triée
        if not swapped:
            break

    return arr


def insertion_sort(arr: list[float], callback=None) -> list[float]:
    """
    Tri par insertion — O(n²) en moyenne, O(n) si déjà trié
    Insère chaque élément à sa bonne place dans la partie déjà triée,
    comme on trie des cartes dans sa main.
    """
    arr = arr.copy()

    for i in range(1, len(arr)):
        key = arr[i]  # L'élément à insérer
        j = i - 1

        # Décale les éléments plus grands vers la droite pour faire de la place
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
            if callback:
                callback(arr.copy(), (j + 1, j + 2))

        # Place l'élément à sa bonne position
        arr[j + 1] = key

    return arr


# =============================================================================
# Fonctions internes pour merge sort (préfixe _ = usage interne uniquement)
# =============================================================================

def _merge(arr, left, mid, right, callback):
    """Fusionne deux sous-listes triées en une seule liste triée."""
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

    # Copie les éléments restants
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


def _merge_sort_helper(arr, left, right, callback):
    """Divise récursivement la liste puis fusionne."""
    if left < right:
        mid = (left + right) // 2
        _merge_sort_helper(arr, left, mid, callback)
        _merge_sort_helper(arr, mid + 1, right, callback)
        _merge(arr, left, mid, right, callback)


def merge_sort(arr: list[float], callback=None) -> list[float]:
    """
    Tri fusion — O(n log n) dans tous les cas
    Divise la liste en deux, trie chaque moitié récursivement,
    puis fusionne les deux moitiés triées.
    Utilise de la mémoire supplémentaire pour les sous-listes.
    """
    arr = arr.copy()
    _merge_sort_helper(arr, 0, len(arr) - 1, callback)
    return arr


# =============================================================================
# Fonctions internes pour quick sort
# =============================================================================

def _partition(arr, low, high, callback):
    """
    Place le pivot à sa position définitive.
    Tous les éléments à gauche sont plus petits, à droite plus grands.
    Optimisation : pivot aléatoire pour éviter le pire cas sur liste triée.
    """
    import random
    # Échange un élément aléatoire avec le dernier pour diversifier le pivot
    rand_idx = random.randint(low, high)
    arr[rand_idx], arr[high] = arr[high], arr[rand_idx]

    pivot = arr[high]  # Le pivot est maintenant à la dernière position
    i = low - 1        # Index du dernier élément plus petit que le pivot

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            if callback:
                callback(arr.copy(), (i, j))

    # Place le pivot à sa position définitive
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    if callback:
        callback(arr.copy(), (i + 1, high))

    return i + 1


def _quick_sort_helper(arr, low, high, callback):
    """Trie récursivement les deux parties autour du pivot."""
    if low < high:
        pivot_idx = _partition(arr, low, high, callback)
        _quick_sort_helper(arr, low, pivot_idx - 1, callback)
        _quick_sort_helper(arr, pivot_idx + 1, high, callback)


def quick_sort(arr: list[float], callback=None) -> list[float]:
    """
    Tri rapide — O(n log n) en moyenne, O(n²) dans le pire cas
    Choisit un pivot aléatoire, place les petits à gauche et les grands à droite,
    puis recommence récursivement sur chaque côté.
    Trie sur place, très rapide en pratique.
    Le pivot aléatoire réduit fortement le risque du pire cas.
    """
    arr = arr.copy()
    _quick_sort_helper(arr, 0, len(arr) - 1, callback)
    return arr


# =============================================================================
# Fonctions internes pour heap sort
# =============================================================================

def _heapify(arr, n, i, callback):
    """
    Maintient la propriété du tas à partir du nœud i.
    Dans un tas, chaque parent est plus grand que ses enfants.
    """
    largest = i
    left = 2 * i + 1   # Enfant gauche
    right = 2 * i + 2  # Enfant droit

    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right

    # Si le plus grand n'est pas le parent, on échange et on continue
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        if callback:
            callback(arr.copy(), (i, largest))
        _heapify(arr, n, largest, callback)


def heap_sort(arr: list[float], callback=None) -> list[float]:
    """
    Tri par tas — O(n log n) dans tous les cas
    Construit un tas (le plus grand élément est toujours au sommet),
    puis extrait les éléments un par un en les plaçant à la fin.
    Trie sur place, sans mémoire supplémentaire.
    """
    arr = arr.copy()
    n = len(arr)

    # Construction du tas (de bas en haut)
    for i in range(n // 2 - 1, -1, -1):
        _heapify(arr, n, i, callback)

    # Extraction des éléments du tas un par un
    for i in range(n - 1, 0, -1):
        # Le sommet (plus grand) va à la fin
        arr[0], arr[i] = arr[i], arr[0]
        if callback:
            callback(arr.copy(), (0, i))
        # On reconstruit le tas sur la partie restante
        _heapify(arr, i, 0, callback)

    return arr


def comb_sort(arr: list[float], callback=None) -> list[float]:
    """
    Tri à peigne — O(n log n) en moyenne, O(n²) dans le pire cas
    Amélioration du tri à bulles : compare des éléments éloignés
    puis réduit progressivement l'écart (gap) jusqu'à 1.
    Beaucoup plus rapide que le tri à bulles en pratique.
    """
    arr = arr.copy()
    n = len(arr)
    gap = n          # Écart initial = taille de la liste
    shrink = 1.3     # Facteur de réduction de l'écart (valeur optimale connue)
    sorted_ = False

    while not sorted_:
        # Réduction de l'écart
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_ = True  # On suppose que c'est trié, un échange prouvera le contraire

        i = 0
        while i + gap < n:
            if arr[i] > arr[i + gap]:
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                sorted_ = False  # Un échange a eu lieu, pas encore trié
                if callback:
                    callback(arr.copy(), (i, i + gap))
            i += 1

    return arr


# =============================================================================
# Timsort — implémentation manuelle
# =============================================================================
# Timsort est l'algorithme utilisé nativement par Python (sorted(), list.sort()).
# Créé en 2002 par Tim Peters, il est aussi utilisé par Java, Android et Swift.
#
# Principe : divise la liste en petits blocs appelés "runs" (séquences naturellement
# triées), les complète avec du tri par insertion, puis les fusionne comme merge sort.
# Il exploite le fait que les données réelles sont souvent partiellement triées.
# =============================================================================

# Taille minimale d'un run — valeur classique entre 32 et 64
# En dessous, le tri par insertion est plus rapide que de diviser davantage
MIN_RUN = 32


def _insertion_sort_run(arr, left, right, callback):
    """
    Tri par insertion sur le sous-tableau arr[left:right+1].
    Utilisé par Timsort pour trier les petits runs.
    """
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
            if callback:
                callback(arr.copy(), (j + 1, j + 2))
        arr[j + 1] = key


def _merge_runs(arr, left, mid, right, callback):
    """
    Fusionne deux runs triés : arr[left:mid+1] et arr[mid+1:right+1].
    Même logique que _merge() du tri fusion.
    """
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


def tim_sort(arr: list[float], callback=None) -> list[float]:
    """
    Timsort — O(n log n) en moyenne et dans le pire cas, O(n) si déjà trié
    Algorithme hybride utilisé nativement par Python (sorted()), Java et Android.
    Créé en 2002 par Tim Peters.

    Étape 1 : découpe la liste en "runs" de taille MIN_RUN et trie chacun
              avec le tri par insertion (très efficace sur les petits blocs).
    Étape 2 : fusionne les runs deux par deux comme le tri fusion,
              en doublant la taille à chaque tour.

    Sa force : exploite les séquences déjà triées dans les données réelles,
    ce qui le rend imbattable en pratique sur des données du monde réel.
    """
    arr = arr.copy()
    n = len(arr)

    # --- Étape 1 : trier chaque run avec le tri par insertion ---
    for start in range(0, n, MIN_RUN):
        end = min(start + MIN_RUN - 1, n - 1)
        _insertion_sort_run(arr, start, end, callback)

    # --- Étape 2 : fusionner les runs en doublant la taille à chaque tour ---
    size = MIN_RUN
    while size < n:
        for left in range(0, n, size * 2):
            mid = min(left + size - 1, n - 1)
            right = min(left + size * 2 - 1, n - 1)

            # On ne fusionne que s'il y a bien deux runs à fusionner
            if mid < right:
                _merge_runs(arr, left, mid, right, callback)

        size *= 2  # On double la taille des blocs à chaque passage

    return arr


# =============================================================================
# Dictionnaire de dispatch — permet d'accéder aux algos par leur nom (string)
# Utilisé par main.py : ALGORITHMS["bubble"](ma_liste)
# =============================================================================

ALGORITHMS = {
    "selection": selection_sort,
    "bubble":    bubble_sort,
    "insertion": insertion_sort,
    "merge":     merge_sort,
    "quick":     quick_sort,
    "heap":      heap_sort,
    "comb":      comb_sort,
    "tim":       tim_sort,
}
