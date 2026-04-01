# =============================================================================
# main.py — Point d'entrée de l'outil de tri
# =============================================================================
# Usage :
#   python main.py --algo bubble --list 3.5 1.2 8.0 4.0
#   python main.py --algo all --list 3.5 1.2 8.0 4.0
#   python main.py --algo all --bench
#   python main.py --algo bubble --gui
#   python main.py --algo all --gui --threads
# =============================================================================

import argparse
from sorting import ALGORITHMS


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
        help="Lancer la visualisation Pygame animée",
    )
    parser.add_argument(
        "--threads",
        action="store_true",
        help="Exécuter les algos en parallèle (requiert --algo all --gui)",
    )

    return parser.parse_args()


def resolve_algos(algo_name: str) -> list[tuple]:
    """Retourne la liste des (nom, fonction) à exécuter."""
    if algo_name == "all":
        return list(ALGORITHMS.items())
    return [(algo_name, ALGORITHMS[algo_name])]


def main():
    args = parse_args()
    algos = resolve_algos(args.algo)

    # --- Mode benchmark ---
    if args.bench:
        from benchmark import run_benchmark, print_benchmark_table, plot_benchmark
        sizes = [100, 500, 1000, 5000, 10000]
        results = run_benchmark(algos, sizes)
        print_benchmark_table(results, sizes)
        plot_benchmark(results, sizes)
        return

    # --- Mode GUI ---
    if args.gui:
        from display import run_display
        arr = args.numbers or [5.0, 3.0, 8.0, 1.0, 9.0, 2.0, 7.0, 4.0, 6.0]
        run_display(algos, arr, threaded=args.threads)
        return

    # --- Mode terminal (comportement minimal requis) ---
    if args.numbers:
        print(f"Input  : {args.numbers}")
        for name, sort_fn in algos:
            result = sort_fn(args.numbers)
            print(f"[{name}] : {result}")
    else:
        print("Erreur : --list requis sans --bench ni --gui")


if __name__ == "__main__":
    main()
