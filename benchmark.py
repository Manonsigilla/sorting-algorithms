# benchmark.py
import time
import random
import tracemalloc
import math
from sorting import ALGORITHMS


def run_benchmark(algos: list[tuple], sizes: list[int]) -> dict:
    """
    Exécute le benchmark de tous les algorithmes sur différentes tailles.
    Mesure le temps d'exécution et la consommation mémoire.
    
    Args:
        algos: Liste de tuples (nom, fonction) des algorithmes à tester
        sizes: Liste des tailles de listes à tester
    
    Returns:
        Dictionnaire {algo_name: {size: {"time": time_ms, "memory": memory_mb}}}
    """
    results = {}
    
    for name, fn in algos:
        results[name] = {}
        
        for size in sizes:
            # Génère une liste aléatoire
            arr = [random.uniform(0, 1000) for _ in range(size)]
            
            # Commence le tracking mémoire
            tracemalloc.start()
            
            # Mesure le temps d'exécution précis
            start = time.perf_counter()
            fn(arr)
            elapsed = time.perf_counter() - start
            
            # Récupère la mémoire utilisée
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Convertir en MB
            memory_mb = peak / 1024 / 1024
            
            results[name][size] = {
                "time": elapsed * 1000,  # En millisecondes
                "memory": memory_mb
            }
    
    return results


def estimate_complexity(times: list[float], sizes: list[int]) -> str:
    """
    Estime la complexité asymptotique en comparant les temps mesurés
    aux courbes théoriques : O(n), O(n log n), O(n²), O(n³)
    
    Args:
        times: Liste des temps mesurés
        sizes: Liste des tailles correspondantes
    
    Returns:
        String décrivant la complexité estimée
    """
    if len(times) < 2:
        return "?"
    
    # Calcul des ratios pour chaque paire de points
    ratios_n = []
    ratios_nlogn = []
    ratios_n2 = []
    ratios_n3 = []
    
    for i in range(1, len(times)):
        if times[i-1] > 0 and sizes[i-1] > 0:
            time_ratio = times[i] / times[i-1]
            size_ratio = sizes[i] / sizes[i-1]
            
            # Calcul des ratios théoriques
            ratios_n.append(size_ratio)
            ratios_nlogn.append(size_ratio * math.log(sizes[i]) / math.log(sizes[i-1]))
            ratios_n2.append(size_ratio ** 2)
            ratios_n3.append(size_ratio ** 3)
    
    if not ratios_n:
        return "?"
    
    # Moyennes des ratios théoriques
    avg_n = sum(ratios_n) / len(ratios_n)
    avg_nlogn = sum(ratios_nlogn) / len(ratios_nlogn)
    avg_n2 = sum(ratios_n2) / len(ratios_n2)
    avg_n3 = sum(ratios_n3) / len(ratios_n3)
    
    # Calcul des erreurs pour chaque modèle
    errors = {}
    for i in range(1, len(times)):
        if times[i-1] > 0:
            time_ratio = times[i] / times[i-1]
            errors.setdefault("O(n)", []).append(abs(time_ratio - avg_n))
            errors.setdefault("O(n log n)", []).append(abs(time_ratio - avg_nlogn))
            errors.setdefault("O(n²)", []).append(abs(time_ratio - avg_n2))
            errors.setdefault("O(n³)", []).append(abs(time_ratio - avg_n3))
    
    # Le modèle avec la plus petite erreur moyenne est sélectionné
    best_model = min(errors, key=lambda x: sum(errors[x]) / len(errors[x]))
    
    return best_model

def print_benchmark_table(results: dict, sizes: list[int]):
    """
    Affiche un tableau formaté simple avec les résultats du benchmark.
    """
    col_w = 12
    
    # En-tête
    header = f"{'Algorithm':<15}" + "".join(f"| {str(s):<{col_w}}" for s in sizes)
    print("\n" + "=" * len(header))
    print(header)
    print("=" * len(header))
    
    # Lignes de données
    for name, timings in results.items():
        row = f"{name:<15}" + "".join(f"| {timings[s]['time']:>{col_w}.2f}ms" for s in sizes)
        print(row)
    
    print("=" * len(header) + "\n")

def compare_two_algos(algo1_name: str, algo1_fn, algo2_name: str, algo2_fn, sizes: list[int]) -> None:
    """
    Compare 1 vs 1 deux algorithmes de tri.
    Affiche temps, RAM et complexité dans le terminal.
    
    Args:
        algo1_name: Nom du premier algorithme
        algo1_fn: Fonction du premier algorithme
        algo2_name: Nom du deuxième algorithme
        algo2_fn: Fonction du deuxième algorithme
        sizes: Liste des tailles à tester
    """
    print(f"\n{'='*140}")
    print(f"Comparaison : {algo1_name} vs {algo2_name}")
    print(f"{'='*140}")
    print(f"{'Taille':<12} | {algo1_name:<15} Temps | RAM | {algo2_name:<15} Temps | RAM | Vainqueur")
    print(f"{'-'*140}")
    
    algo1_wins = 0
    algo2_wins = 0
    times1 = []
    times2 = []
    
    for size in sizes:
        arr = [random.uniform(0, 1000) for _ in range(size)]
        
        # Test algo 1
        arr1 = arr.copy()
        tracemalloc.start()
        start1 = time.perf_counter()
        algo1_fn(arr1)
        time1 = (time.perf_counter() - start1) * 1000
        _, peak1 = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        mem1 = peak1 / 1024 / 1024
        times1.append(time1)
        
        # Test algo 2
        arr2 = arr.copy()
        tracemalloc.start()
        start2 = time.perf_counter()
        algo2_fn(arr2)
        time2 = (time.perf_counter() - start2) * 1000
        _, peak2 = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        mem2 = peak2 / 1024 / 1024
        times2.append(time2)
        
        # Déterminer le vainqueur (basé sur le temps)
        if time1 < time2:
            winner = algo1_name
            algo1_wins += 1
        else:
            winner = algo2_name
            algo2_wins += 1
        
        print(f"{size:<12} | {algo1_name:<15} {time1:>7.2f}ms | {mem1:>6.2f}MB | {algo2_name:<15} {time2:>7.2f}ms | {mem2:>6.2f}MB | {winner}")
    
    print(f"{'-'*140}")
    
    # Estimation de complexité
    complexity1 = estimate_complexity(times1, sizes)
    complexity2 = estimate_complexity(times2, sizes)
    
    print(f"Complexité estimée : {algo1_name} ~ {complexity1:<12} | {algo2_name} ~ {complexity2:<12}")
    print(f"Score : {algo1_name} {algo1_wins}/{len(sizes)} | {algo2_name} {algo2_wins}/{len(sizes)}")
    print(f"{'='*140}\n")


def compare_all_algos(algos: list[tuple], sizes: list[int]) -> None:
    """
    Compare tous les algorithmes entre eux dans des tableaux.
    Affiche temps, RAM et complexité pour chaque algo.
    
    Args:
        algos: Liste de tuples (nom, fonction) des algorithmes à tester
        sizes: Liste des tailles à tester
    """
    results = run_benchmark(algos, sizes)
    
    print(f"\n{'='*180}")
    print(f"{'Comparaison complète - TEMPS (ms)':^180}")
    print(f"{'='*180}")
    
    # Tableau TEMPS
    header = f"{'Taille':<12}"
    for name, _ in algos:
        header += f" | {name:<15}"
    print(header)
    print(f"{'-'*180}")
    
    for size in sizes:
        row = f"{size:<12}"
        for name, _ in algos:
            row += f" | {results[name][size]['time']:<15.2f}ms"
        print(row)
    
    print(f"\n{'='*180}")
    print(f"{'Comparaison complète - RAM (MB)':^180}")
    print(f"{'='*180}")
    
    # Tableau RAM
    header = f"{'Taille':<12}"
    for name, _ in algos:
        header += f" | {name:<15}"
    print(header)
    print(f"{'-'*180}")
    
    for size in sizes:
        row = f"{size:<12}"
        for name, _ in algos:
            row += f" | {results[name][size]['memory']:<15.2f}MB"
        print(row)
    
    print(f"\n{'='*180}")
    print(f"{'Complexité asymptotique estimée':^180}")
    print(f"{'='*180}")
    
    # Calcul des complexités
    complexities = {}
    for name, _ in algos:
        times = [results[name][size]['time'] for size in sizes]
        complexities[name] = estimate_complexity(times, sizes)
    
    # Tableau complexité
    header = f"{'Algorithme':<20}"
    header += f" | {'Complexité':^30}"
    print(header)
    print(f"{'-'*180}")
    
    for name, _ in algos:
        print(f"{name:<20} | {complexities[name]:^30}")
    
    print(f"{'='*180}\n")
    
    # Résumé : quel algo est le plus rapide pour chaque taille
    print(f"{'Résumé - Algorithme le plus rapide par taille:':^180}")
    print(f"{'-'*180}")
    
    for size in sizes:
        fastest = min(algos, key=lambda x: results[x[0]][size]['time'])
        fastest_time = results[fastest[0]][size]['time']
        fastest_mem = results[fastest[0]][size]['memory']
        fastest_complexity = complexities[fastest[0]]
        print(f"  Taille {size:<6} → {fastest[0]:<15} ({fastest_time:.2f}ms, {fastest_mem:.2f}MB, {fastest_complexity})")
    
    print(f"{'='*180}\n")


def benchmark_summary(algos: list[tuple], sizes: list[int]) -> None:
    """
    Affiche un résumé complet du benchmark avec statistiques temps, RAM et complexité.
    
    Args:
        algos: Liste de tuples (nom, fonction) des algorithmes à tester
        sizes: Liste des tailles à tester
    """
    results = run_benchmark(algos, sizes)
    
    print(f"\n{'='*160}")
    print(f"{'RÉSUMÉ DU BENCHMARK':^160}")
    print(f"{'='*160}")
    
    # Tableau de comparaison TEMPS
    print(f"\n{'TEMPS D\'EXÉCUTION (ms)':^160}")
    print(f"{'-'*160}")
    header = f"{'Algorithme':<15}"
    for size in sizes:
        header += f" | {size:<12}"
    print(header)
    print(f"{'-'*160}")
    
    for name, _ in algos:
        row = f"{name:<15}"
        for size in sizes:
            row += f" | {results[name][size]['time']:<12.2f}ms"
        print(row)
    
    # Tableau de comparaison RAM
    print(f"\n{'CONSOMMATION MÉMOIRE (MB)':^160}")
    print(f"{'-'*160}")
    header = f"{'Algorithme':<15}"
    for size in sizes:
        header += f" | {size:<12}"
    print(header)
    print(f"{'-'*160}")
    
    for name, _ in algos:
        row = f"{name:<15}"
        for size in sizes:
            row += f" | {results[name][size]['memory']:<12.2f}MB"
        print(row)
    
    # Tableau de complexité asymptotique
    print(f"\n{'COMPLEXITÉ ASYMPTOTIQUE':^160}")
    print(f"{'-'*160}")
    
    for name, _ in algos:
        times = [results[name][size]['time'] for size in sizes]
        complexity = estimate_complexity(times, sizes)
        print(f"{name:<15} → {complexity}")
    
    # Statistiques détaillées par algorithme
    print(f"\n{'='*160}")
    print(f"{'Statistiques détaillées par algorithme':^160}")
    print(f"{'='*160}\n")
    
    for name, _ in algos:
        times = [results[name][size]['time'] for size in sizes]
        mems = [results[name][size]['memory'] for size in sizes]
        complexity = estimate_complexity(times, sizes)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        avg_mem = sum(mems) / len(mems)
        min_mem = min(mems)
        max_mem = max(mems)
        
        print(f"{name}")
        print(f"     Temps moyen  : {avg_time:.2f}ms")
        print(f"     Temps min    : {min_time:.2f}ms (taille {sizes[times.index(min_time)]})")
        print(f"     Temps max    : {max_time:.2f}ms (taille {sizes[times.index(max_time)]})")
        print(f"     RAM moyen    : {avg_mem:.2f}MB")
        print(f"     RAM min      : {min_mem:.2f}MB (taille {sizes[mems.index(min_mem)]})")
        print(f"     RAM max      : {max_mem:.2f}MB (taille {sizes[mems.index(max_mem)]})")
        print(f"     Complexité   : {complexity}")
        print()
    
    print(f"{'='*160}\n")


if __name__ == "__main__":
    # Exemple d'utilisation
    sizes = [100, 500, 1000, 5000]
    
    # Récupérer les algos
    algos = list(ALGORITHMS.items())
    
    # Comparaison complète
    compare_all_algos(algos, sizes)
    
    # Résumé avec statistiques
    benchmark_summary(algos, sizes)
    
    # Comparaison 1 vs 1
    compare_two_algos("bubble", ALGORITHMS["bubble"], "quick", ALGORITHMS["quick"], sizes)

    