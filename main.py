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
    """
    Définit et parse les arguments de la ligne de commande.
    argparse gère automatiquement l'affichage de l'aide (--help)
    et les erreurs si un argument obligatoire est manquant.
    """
    parser = argparse.ArgumentParser(description="Outil de tri — Les Papyrus de Héron")

    # Argument obligatoire : nom de l'algo ou "all" pour les exécuter tous
    parser.add_argument(
        "--algo",
        required=True,
        choices=list(ALGORITHMS.keys()) + ["all"],
        help="Algorithme à utiliser (ou 'all' pour tous)",
    )
    # nargs="+" signifie "un ou plusieurs valeurs" → retourne une liste
    parser.add_argument(
        "--list",
        dest="numbers",
        nargs="+",
        type=float,
        help="Liste de nombres réels à trier",
    )
    # action="store_true" → True si le flag est présent, False sinon
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Trier dans l'ordre décroissant",
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
    """
    Convertit le nom d'algo en liste de (nom, fonction).
    "all" est une valeur spéciale qui retourne les 7 algos.
    Sinon on retourne uniquement l'algo demandé.
    """
    if algo_name == "all":
        return list(ALGORITHMS.items())
    return [(algo_name, ALGORITHMS[algo_name])]


def main():
    args = parse_args()
    algos = resolve_algos(args.algo)

    # --- Mode benchmark ---
    # Importé ici (et non en haut du fichier) pour ne pas charger
    # matplotlib si on ne l'utilise pas
    if args.bench:
        from benchmark import run_benchmark, print_benchmark_table, plot_benchmark
        sizes = [100, 500, 1000, 5000, 10000]
        results = run_benchmark(algos, sizes)
        print_benchmark_table(results, sizes)
        plot_benchmark(results, sizes)
        return

    # --- Mode GUI ---
    # Même principe : Pygame n'est chargé que si --gui est passé
    if args.gui:
        from display import run_display
        # Liste par défaut si l'utilisateur ne passe pas --list
        arr = args.numbers or [5.0, 3.0, 8.0, 1.0, 9.0, 2.0, 7.0, 4.0, 6.0]
        run_display(algos, arr, threaded=args.threads)
        return

    # --- Mode terminal (comportement minimal requis par le sujet) ---
    if args.numbers:
        print(f"\nInput  : {args.numbers}\n")
        for name, sort_fn in algos:
            try:
                result = sort_fn(args.numbers)
                if args.reverse:
                    result = result[::-1]  # Inverse le résultat pour l'ordre décroissant
                print(f"[{name:<10}] : {result}")
            except Exception as e:
                print(f"[{name:<10}] : Erreur — {e}")
    else:
        print("Erreur : --list requis sans --bench ni --gui")


if __name__ == "__main__":
    main()
