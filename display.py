import pygame
import threading
import queue
import time
import random

# Color constants
BLUE = (64, 164, 223)         # Neutral state
RED = (255, 69, 0)            # Active bar / Swapping
GREEN = (46, 139, 87)         # Final sorted position
BLACK = (30, 30, 30)          # Background
WHITE = (240, 240, 240)       # Borders
TEXT_COLOR = (200, 200, 200)  # Text

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
        # Only increment swaps if active_indices are provided (meaning a real sorting step occurred)
        if active_indices:
            self.swaps += 1

    def draw(self, surface, font):
        # Draw background and border
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

        # Draw texts
        title_surface = font.render(self.title, True, TEXT_COLOR)
        stats_surface = font.render(f"Swaps approx: {self.swaps}", True, TEXT_COLOR)
        surface.blit(title_surface, (self.rect.x + 10, self.rect.y + 10))
        surface.blit(stats_surface, (self.rect.x + 10, self.rect.y + 35))

        if not self.array:
            return

        # Calculate dimensions for the bars
        n = len(self.array)
        max_val = max(self.array) if n > 0 else 1
        bar_width = (self.rect.width - 20) / n
        max_height = self.rect.height - 80

        # Draw each bar
        for i, val in enumerate(self.array):
            height = (val / max_val) * max_height
            x = self.rect.x + 10 + i * bar_width
            y = self.rect.y + self.rect.height - 10 - height

            # Determine color based on current state
            color = BLUE
            if self.is_done:
                color = GREEN
            elif i in self.active_indices:
                color = RED

            bar_rect = pygame.Rect(x, y, max(1, bar_width - 1), height)
            pygame.draw.rect(surface, color, bar_rect)

def draw_legend(surface, font, width):
    """
    Draws a legend bar at the top of the window to explain colors.
    """
    legend_rect = pygame.Rect(0, 0, width, 40)
    pygame.draw.rect(surface, (20, 20, 20), legend_rect)
    pygame.draw.line(surface, WHITE, (0, 40), (width, 40), 2)
    
    items = [
        (BLUE, "Neutre"),
        (RED, "Actif / Deplacement"),
        (GREEN, "Termine (Trie)")
    ]
    
    x_offset = 20
    for color, text in items:
        # Draw color box
        pygame.draw.rect(surface, color, (x_offset, 10, 20, 20))
        # Draw description text
        text_surf = font.render(text, True, TEXT_COLOR)
        surface.blit(text_surf, (x_offset + 30, 10))
        x_offset += 250

def run_display(algos, arr, threaded=False):
    """
    Main entry point for the GUI, called by main.py.
    """
    pygame.init()
    window_width = 1200
    window_height = 800
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Visualisation des algorithmes de tri")
    font = pygame.font.SysFont("Arial", 18)

    # Generate a larger array if the default one is too small to see the animation properly
    if len(arr) < 20:
        arr = [random.uniform(10.0, 100.0) for _ in range(40)]

    # Legend reserves the top 40 pixels
    legend_height = 40

    # Grid layout calculation (e.g., 4 columns)
    grid_cols = 4
    grid_rows = (len(algos) + grid_cols - 1) // grid_cols
    cell_w = window_width // grid_cols
    cell_h = (window_height - legend_height) // max(1, grid_rows)

    views = {}
    ui_queue = queue.Queue()

    # Initialize all algorithm views
    for idx, (name, _) in enumerate(algos):
        col = idx % grid_cols
        row = idx // grid_cols
        # Offset Y axis by legend_height
        rect = (col * cell_w, legend_height + row * cell_h, cell_w, cell_h)
        views[name] = SorterView(rect, name.capitalize())
        views[name].update_state(arr.copy(), [])

    def sorting_worker(name, sort_func, array_copy, delay):
        """
        Worker function executed by each thread.
        """
        def callback(state, indices):
            # Send current state to the main Pygame thread
            ui_queue.put({"name": name, "state": state, "indices": indices, "done": False})
            time.sleep(delay)

        # Execute the sort and capture the returned sorted array (CRITICAL FIX)
        sorted_arr = sort_func(array_copy, callback)
        
        # Send the properly sorted array with done=True to turn it green
        ui_queue.put({"name": name, "state": sorted_arr, "indices": [], "done": True})

    # Adjust delay based on array size to keep animation enjoyable
    delay = 0.03

    # Start threads for all algorithms
    # We use threads in both cases here so the Pygame window doesn't freeze
    for name, sort_func in algos:
        t = threading.Thread(
            target=sorting_worker, 
            args=(name, sort_func, arr.copy(), delay),
            daemon=True
        )
        t.start()

    # Main Pygame Event Loop (Must run on main thread)
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Process all queued messages from sorting threads
        while not ui_queue.empty():
            try:
                msg = ui_queue.get_nowait()
                views[msg["name"]].update_state(msg["state"], msg["indices"], msg["done"])
            except queue.Empty:
                break

        # Render everything
        screen.fill(BLACK)
        draw_legend(screen, font, window_width)
        
        for view in views.values():
            view.draw(screen, font)
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()