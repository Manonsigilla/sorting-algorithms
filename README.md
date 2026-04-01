# sorting-algorithms

Projet scolaire — La Plateforme | Groupe de 3

Outil d'automatisation de tri de listes de nombres réels.
Implémente 7 algorithmes de tri avec visualisation animée et benchmarking.

---

## Algorithmes implémentés

| Algorithme | Complexité moyenne | Complexité pire cas | Mémoire supplémentaire |
|---|---|---|---|
| Tri par sélection | O(n²) | O(n²) | Non |
| Tri à bulles | O(n²) | O(n) si déjà trié | Non |
| Tri par insertion | O(n²) | O(n) si déjà trié | Non |
| Tri fusion | O(n log n) | O(n log n) | Oui |
| Tri rapide | O(n log n) | O(n²) | Non |
| Tri par tas | O(n log n) | O(n log n) | Non |
| Tri à peigne | O(n log n) | O(n²) | Non |

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

## Conclusion

> À compléter — quel algo est le plus rapide et pourquoi ?
