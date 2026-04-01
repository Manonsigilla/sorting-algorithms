# sorting-algorithms

Projet scolaire — La Plateforme | Groupe de 3

Outil d'automatisation de tri de listes de nombres réels.
Implémente 7 algorithmes de tri avec visualisation animée et benchmarking.

---

## Algorithmes implémentés

| Algorithme | Complexité moyenne | Complexité pire cas | Mémoire supplémentaire |
|---|---|---|---|
| Tri par sélection | O(n²) | O(n²) | Non |
| Tri à bulles | O(n²) | O(n²) | Non |
| Tri par insertion | O(n²) | O(n) si déjà trié | Non |
| Tri fusion | O(n log n) | O(n log n) | Oui |
| Tri rapide | O(n log n) | O(n²) | Non |
| Tri par tas | O(n log n) | O(n log n) | Non |
| Tri à peigne | O(n log n) | O(n²) | Non |

---

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
# Trier une liste dans le terminal
python main.py --algo bubble --list 3.5 1.2 8.0 4.0

# Lancer le benchmarking (tous les algos)
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

> À compléter après avoir lancé le benchmark

---

## Conclusion

> À compléter — quel algo est le plus rapide et pourquoi ?
