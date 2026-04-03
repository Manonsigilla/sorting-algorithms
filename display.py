import pygame
import threading
import queue
import time
import random

# Color constants requested by the colleague
BLUE = (64, 164, 223)         # Neutral
ORANGE = (255, 165, 0)        # Comparing
RED = (255, 69, 0)            # Active / Swapping
MINT_GREEN = (152, 255, 152)  # Minimum / Pivot
PURPLE = (147, 112, 219)      # Pivot 2 (Quick Sort)
GREEN = (46, 139, 87)         # Sorted
BLACK = (30, 30, 30)
WHITE = (240, 240, 240)
TEXT_COLOR = (200, 200, 200)

class SorterView:
    def __init__(self, rect, title):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.array = []
        self.colored_indices = {}
        self.is_done = False
        self.swaps = 0

    def update_state(self, array, indices, is_done=False):
        """
        Updates the internal state. 
        Supports both the old tuple format from sorting.py (defaults to RED)
        and a new dictionary format to support multiple colors.
        """
        self.array = array
        self.is_done = is_done
        
        # Initialize color lists
        self.colored_indices = {
            RED: [],
            ORANGE: [],
            MINT_GREEN: [],
            PURPLE: []
        }
        
        # Check if colleagues updated sorting.py to send specific colors
        if isinstance(indices, dict):
            if "red" in indices: self.colored_indices[RED] = indices["red"]
            if "orange" in indices: self.colored_indices[ORANGE] = indices["orange"]
            if "mint" in indices: self.colored_indices[MINT_GREEN] = indices["mint"]
            if "purple" in indices: self.colored_indices[PURPLE] = indices["purple"]
            
            if "red" in indices and indices["red"]:
                self.swaps += 1
        else:
            # Fallback to the current sorting.py behavior
            self.colored_indices[RED] = list(indices)
            if indices:
                self.swaps += 1

    def draw(self, surface, font):
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

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

        for i, val in enumerate(self.array):
            height = (val / max_val) * max_height
            x = self.rect.x + 10 + i * bar_width
            y = self.rect.y + self.rect.height - 10 - height

            color = BLUE
            if self.is_done:
                color = GREEN
            else:
                # Apply the specific color if the index is active
                for c_rgb, idx_list in self.colored_indices.items():
                    if i in idx_list:
                        color = c_rgb
                        break

            bar_rect = pygame.Rect(x, y, max(1, bar_width - 1), height)
            pygame.draw.rect(surface, color, bar_rect)

def draw_legend(surface, font, width):
    """
    Draws the full legend bar matching the README specifications.
    """
    legend_rect = pygame.Rect(0, 0, width, 50)
    pygame.draw.rect(surface, (20, 20, 20), legend_rect)
    pygame.draw.line(surface, WHITE, (0, 50), (width, 50), 2)
    
    # Legend data
    items_top = [
        (BLUE, "Neutre"),
        (ORANGE, "Comparaison"),
        (RED, "Deplacement")
    ]
    items_bottom = [
        (MINT_GREEN, "Minimum / Pivot"),
        (PURPLE, "Pivot secondaire"),
        (GREEN, "Position triee")
    ]
    
    # Draw top row
    x_offset = 20
    for color, text in items_top:
        pygame.draw.rect(surface, color, (x_offset, 5, 15, 15))
        text_surf = font.render(text, True, TEXT_COLOR)
        surface.blit(text_surf, (x_offset + 25, 3))
        x_offset += 250
        
    # Draw bottom row
    x_offset = 20
    for color, text in items_bottom:
        pygame.draw.rect(surface, color, (x_offset, 25, 15, 15))
        text_surf = font.render(text, True, TEXT_COLOR)
        surface.blit(text_surf, (x_offset + 25, 23))
        x_offset += 250

def run_display(algos, arr, threaded=False):
    pygame.init()
    window_width = 1200
    window_height = 800
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Visualisation des algorithmes de tri")
    font = pygame.font.SysFont("Arial", 18)

    # Ensure array is large enough for a good visualization
    if len(arr) < 20:
        arr = [random.uniform(10.0, 100.0) for _ in range(40)]

    legend_height = 50
    grid_cols = 4
    grid_rows = (len(algos) + grid_cols - 1) // grid_cols
    cell_w = window_width // grid_cols
    cell_h = (window_height - legend_height) // max(1, grid_rows)

    views = {}
    ui_queue = queue.Queue()

    for idx, (name, _) in enumerate(algos):
        col = idx % grid_cols
        row = idx // grid_cols
        rect = (col * cell_w, legend_height + row * cell_h, cell_w, cell_h)
        views[name] = SorterView(rect, name.capitalize())
        views[name].update_state(arr.copy(), [])

    def sorting_worker(name, sort_func, array_copy, delay):
        def callback(state, indices):
            ui_queue.put({"name": name, "state": state, "indices": indices, "done": False})
            time.sleep(delay)

        sorted_arr = sort_func(array_copy, callback)
        ui_queue.put({"name": name, "state": sorted_arr, "indices": [], "done": True})

    delay = 0.03
    for name, sort_func in algos:
        t = threading.Thread(
            target=sorting_worker, 
            args=(name, sort_func, arr.copy(), delay),
            daemon=True
        )
        t.start()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        while not ui_queue.empty():
            try:
                msg = ui_queue.get_nowait()
                views[msg["name"]].update_state(msg["state"], msg["indices"], msg["done"])
            except queue.Empty:
                break

        screen.fill(BLACK)
        draw_legend(screen, font, window_width)
        
        for view in views.values():
            view.draw(screen, font)
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()