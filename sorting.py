# =============================================================================
# sorting.py — Implementation of 7 sorting algorithms
# =============================================================================
# Each function respects the same signature:
#   - arr      : list of real numbers to sort (never modified directly)
#   - callback : optional function called at each step
#                callback(state: list[float], indices: dict)
#                -> used to animate the GUI and measure steps
# =============================================================================

def selection_sort(arr: list[float], callback=None) -> list[float]:
    """
    Selection sort — O(n²)
    Finds the minimum element in the unsorted part and places it at the beginning.
    """
    arr = arr.copy()
    n = len(arr)

    for i in range(n):
        min_idx = i

        for j in range(i + 1, n):
            if callback:
                callback(arr.copy(), {"compare": [min_idx, j]})
                
            if arr[j] < arr[min_idx]:
                min_idx = j

        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            if callback:
                callback(arr.copy(), {"swap": [i, min_idx]})

    return arr


def bubble_sort(arr: list[float], callback=None) -> list[float]:
    """
    Bubble sort — O(n²), O(n) if already sorted
    Compares adjacent elements and swaps them if they are in the wrong order.
    Optimization: stops if a pass makes no swaps.
    """
    arr = arr.copy()
    n = len(arr)

    for i in range(n):
        swapped = False

        for j in range(n - i - 1):
            if callback:
                callback(arr.copy(), {"compare": [j, j + 1]})
                
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
                if callback:
                    callback(arr.copy(), {"swap": [j, j + 1]})

        if not swapped:
            break

    return arr


def insertion_sort(arr: list[float], callback=None) -> list[float]:
    """
    Insertion sort — O(n²) average, O(n) if already sorted
    Builds the sorted array one item at a time by inserting elements into their correct position.
    """
    arr = arr.copy()

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0:
            if callback:
                callback(arr.copy(), {"compare": [j, j + 1]})
                
            if arr[j] > key:
                arr[j + 1] = arr[j]
                if callback:
                    callback(arr.copy(), {"swap": [j + 1, j]})
                j -= 1
            else:
                break

        arr[j + 1] = key

    return arr


# =============================================================================
# Internal functions for merge sort (prefix _ = internal use only)
# =============================================================================

def _merge(arr, left, mid, right, callback):
    """Merges two sorted sublists into a single sorted list."""
    left_part = arr[left:mid + 1]
    right_part = arr[mid + 1:right + 1]
    i = j = 0
    k = left

    while i < len(left_part) and j < len(right_part):
        if callback:
            callback(arr.copy(), {"compare": [left + i, mid + 1 + j]})
            
        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        k += 1
        if callback:
            callback(arr.copy(), {"swap": [k - 1, k - 1]})

    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1
        if callback:
            callback(arr.copy(), {"swap": [k - 1, k - 1]})
            
    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1
        if callback:
            callback(arr.copy(), {"swap": [k - 1, k - 1]})


def _merge_sort_helper(arr, left, right, callback):
    """Recursively divides the list then merges."""
    if left < right:
        mid = (left + right) // 2
        _merge_sort_helper(arr, left, mid, callback)
        _merge_sort_helper(arr, mid + 1, right, callback)
        _merge(arr, left, mid, right, callback)


def merge_sort(arr: list[float], callback=None) -> list[float]:
    """
    Merge sort — O(n log n) in all cases
    Divides the list in two, sorts each half recursively,
    then merges the two sorted halves.
    """
    arr = arr.copy()
    _merge_sort_helper(arr, 0, len(arr) - 1, callback)
    return arr


# =============================================================================
# Internal functions for quick sort
# =============================================================================

def _partition(arr, low, high, callback):
    """
    Places the pivot at its correct position.
    Optimization: random pivot to avoid worst-case scenario on sorted lists.
    """
    import random
    rand_idx = random.randint(low, high)
    arr[rand_idx], arr[high] = arr[high], arr[rand_idx]

    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if callback:
            callback(arr.copy(), {"compare": [j, high]})
            
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            if callback:
                callback(arr.copy(), {"swap": [i, j]})

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    if callback:
        callback(arr.copy(), {"swap": [i + 1, high]})

    return i + 1


def _quick_sort_helper(arr, low, high, callback):
    """Recursively sorts both parts around the pivot."""
    if low < high:
        pivot_idx = _partition(arr, low, high, callback)
        _quick_sort_helper(arr, low, pivot_idx - 1, callback)
        _quick_sort_helper(arr, pivot_idx + 1, high, callback)


def quick_sort(arr: list[float], callback=None) -> list[float]:
    """
    Quick sort — O(n log n) average, O(n²) worst case
    Chooses a random pivot, places smaller elements to the left, larger to the right.
    """
    arr = arr.copy()
    _quick_sort_helper(arr, 0, len(arr) - 1, callback)
    return arr


# =============================================================================
# Internal functions for heap sort
# =============================================================================

def _heapify(arr, n, i, callback):
    """Maintains the max-heap property starting from node i."""
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n:
        if callback:
            callback(arr.copy(), {"compare": [left, largest]})
        if arr[left] > arr[largest]:
            largest = left

    if right < n:
        if callback:
            callback(arr.copy(), {"compare": [right, largest]})
        if arr[right] > arr[largest]:
            largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        if callback:
            callback(arr.copy(), {"swap": [i, largest]})
        _heapify(arr, n, largest, callback)


def heap_sort(arr: list[float], callback=None) -> list[float]:
    """
    Heap sort — O(n log n) in all cases
    Builds a max-heap, then extracts elements one by one to the end.
    """
    arr = arr.copy()
    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        _heapify(arr, n, i, callback)

    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        if callback:
            callback(arr.copy(), {"swap": [0, i]})
        _heapify(arr, i, 0, callback)

    return arr


def comb_sort(arr: list[float], callback=None) -> list[float]:
    """
    Comb sort — O(n log n) average, O(n²) worst case
    Improves bubble sort by comparing elements far apart,
    then gradually reducing the gap.
    """
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
            if callback:
                callback(arr.copy(), {"compare": [i, i + gap]})
                
            if arr[i] > arr[i + gap]:
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                sorted_ = False
                if callback:
                    callback(arr.copy(), {"swap": [i, i + gap]})
            i += 1

    return arr


# =============================================================================
# Timsort — manual implementation
# =============================================================================
MIN_RUN = 32

def _insertion_sort_run(arr, left, right, callback):
    """Insertion sort applied to a small run for Timsort."""
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left:
            if callback:
                callback(arr.copy(), {"compare": [j, j + 1]})
            if arr[j] > key:
                arr[j + 1] = arr[j]
                if callback:
                    callback(arr.copy(), {"swap": [j + 1, j]})
                j -= 1
            else:
                break
        arr[j + 1] = key


def _merge_runs(arr, left, mid, right, callback):
    """Merges two sorted runs. Same logic as merge sort."""
    left_part = arr[left:mid + 1]
    right_part = arr[mid + 1:right + 1]
    i = j = 0
    k = left

    while i < len(left_part) and j < len(right_part):
        if callback:
            callback(arr.copy(), {"compare": [left + i, mid + 1 + j]})
            
        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        k += 1
        if callback:
            callback(arr.copy(), {"swap": [k - 1, k - 1]})

    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1
        if callback:
            callback(arr.copy(), {"swap": [k - 1, k - 1]})
            
    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1
        if callback:
            callback(arr.copy(), {"swap": [k - 1, k - 1]})


def tim_sort(arr: list[float], callback=None) -> list[float]:
    """
    Timsort — O(n log n) average and worst case, O(n) if already sorted
    Hybrid algorithm natively used by Python (sorted()), Java and Android.
    """
    arr = arr.copy()
    n = len(arr)

    for start in range(0, n, MIN_RUN):
        end = min(start + MIN_RUN - 1, n - 1)
        _insertion_sort_run(arr, start, end, callback)

    size = MIN_RUN
    while size < n:
        for left in range(0, n, size * 2):
            mid = min(left + size - 1, n - 1)
            right = min(left + size * 2 - 1, n - 1)

            if mid < right:
                _merge_runs(arr, left, mid, right, callback)

        size *= 2

    return arr


# =============================================================================
# Dispatch dictionary
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