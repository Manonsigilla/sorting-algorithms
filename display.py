import pygame
import threading
import queue
import time

# Constantes de couleurs demandées
BLUE = (64, 164, 223)         # Neutre
ORANGE = (255, 165, 0)        # Comparaison en cours
RED = (255, 69, 0)            # Barre active / déplacement
MINT_GREEN = (152, 255, 152)   # Minimum (sélection) / Pivot (rapide)
PURPLE = (147, 112, 219)      # Pivot secondaire
GREEN = (46, 139, 87)         # Position définitive (trié)
BLACK = (30, 30, 30)
WHITE = (240, 240, 240)
TEXT_COLOR = (200, 200, 200)

class SorterView:
    def __init__(self, rect, title):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.array = []
        self.active_indices = []
        self.is_done = False
        self.swaps = 0

    def update_state(self, array, active_indices, is_done=False):
        self.array = array
        self.active_indices = active_indices
        self.is_done = is_done
        self.swaps += 1

    def draw(self, surface, font):
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

        # Affichage du titre et des statistiques
        title_surface = font.render(self.title, True, TEXT_COLOR)
        stats_surface = font.render(f"Swaps approx: {self.swaps}", True, TEXT_COLOR)
        surface.blit(title_surface, (self.rect.x + 10, self.rect.y + 10))
        surface.blit(stats_surface, (self.rect.x + 10, self.rect.y + 35))

        if not self.array:
            return

        n = len(self.array)
        max_val = max(self.array) if n > 0 else 1
        bar_width = (self.rect.width - 20) / n
        max_height = self.rect.height - 80

        # Dessin des barres
        for i, val in enumerate(self.array):
            height = (val / max_val) * max_height
            x = self.rect.x + 10 + i * bar_width
            y = self.rect.y + self.rect.height - 10 - height

            color = BLUE
            if self.is_done:
                color = GREEN
            elif i in self.active_indices:
                color = RED

            bar_rect = pygame.Rect(x, y, max(1, bar_width - 1), height)
            pygame.draw.rect(surface, color, bar_rect)

def run_display(algos, arr, threaded=False):
    """
    Point d'entrée pour l'interface graphique appelé par main.py.
    algos : liste de tuples (nom_algo, fonction_de_tri)
    arr : la liste de nombres à trier
    threaded : booléen pour savoir si on parallélise l'exécution
    """
    pygame.init()
    window_width = 1200
    window_height = 800
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Visualisation des algorithmes de tri")
    font = pygame.font.SysFont("Arial", 18)

    # Configuration de la grille (ex: 4 colonnes pour 8 algos = 2 lignes)
    grid_cols = 4
    grid_rows = (len(algos) + grid_cols - 1) // grid_cols
    cell_w = window_width // grid_cols
    cell_h = window_height // max(1, grid_rows)

    views = {}
    ui_queue = queue.Queue()

    # Initialisation des vues
    for idx, (name, _) in enumerate(algos):
        col = idx % grid_cols
        row = idx // grid_cols
        rect = (col * cell_w, row * cell_h, cell_w, cell_h)
        views[name] = SorterView(rect, name.capitalize())
        views[name].update_state(arr.copy(), [])

    def sorting_worker(name, sort_func, array_copy, delay=0.05):
        """Fonction exécutée par le thread pour chaque algorithme"""
        def callback(state, indices):
            ui_queue.put({"name": name, "state": state, "indices": indices, "done": False})
            time.sleep(delay)

        sort_func(array_copy, callback)
        ui_queue.put({"name": name, "state": array_copy, "indices": [], "done": True})

    # Lancement des threads
    if threaded:
        for name, sort_func in algos:
            t = threading.Thread(
                target=sorting_worker, 
                args=(name, sort_func, arr.copy(), 0.05),
                daemon=True
            )
            t.start()
    else:
        # Version non-parallélisée (séquentielle) demandée par ton main.py possiblement
        # Pour faire simple ici, on lance un thread à la fois ou on laisse tout dans des threads
        # mais on ajuste pour respecter ton drapeau "threaded" si besoin.
        # Ici on les lance tous en parallèle quoi qu'il arrive si c'est le but de la GUI.
        for name, sort_func in algos:
            t = threading.Thread(target=sorting_worker, args=(name, sort_func, arr.copy(), 0.05), daemon=True)
            t.start()

    # Boucle principale Pygame (tourne sur le Thread Principal)
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Récupération des messages de la file d'attente
        while not ui_queue.empty():
            try:
                msg = ui_queue.get_nowait()
                views[msg["name"]].update_state(msg["state"], msg["indices"], msg["done"])
            except queue.Empty:
                break

        # Dessin à l'écran
        screen.fill(BLACK)
        for view in views.values():
            view.draw(screen, font)
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()