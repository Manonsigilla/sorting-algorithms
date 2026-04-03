import pygame
import threading
import queue
import time
import random
import csv
import os
import psutil
from datetime import datetime

# =============================================================================
# Constants & Colors matching the provided mockups
# =============================================================================

BG_COLOR = (34, 34, 34)
CARD_BG = (51, 51, 51)
CARD_BORDER = (80, 80, 80)
BAR_COLOR_DEFAULT = (168, 209, 240)
BAR_COLOR_ACTIVE = (255, 100, 100)
BAR_COLOR_DONE = (76, 175, 80)

WHITE = (240, 240, 240)
TEXT_MUTED = (170, 170, 170)
BTN_BG = (45, 45, 45)
BTN_HOVER = (70, 70, 70)
BADGE_STABLE = (76, 175, 80)
BADGE_UNSTABLE = (244, 67, 54)

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# =============================================================================
# Algorithm Theoretical Data (for Summary Cards)
# =============================================================================

ALGO_METADATA = {
    "selection": {
        "name": "Tri par selection", "stable": False, 
        "avg": "O(n^2)", "mem": "O(1)", 
        "desc": "Trouve le minimum, le place en tete. Simple mais lent."
    },
    "bubble": {
        "name": "Tri a bulles", "stable": True, 
        "avg": "O(n^2)", "mem": "O(1)", 
        "desc": "Compare les voisins et remonte les grands elements."
    },
    "insertion": {
        "name": "Tri par insertion", "stable": True, 
        "avg": "O(n^2)", "mem": "O(1)", 
        "desc": "Insere chaque element a sa bonne place. Efficace sur donnees quasi-triees."
    },
    "merge": {
        "name": "Tri fusion", "stable": True, 
        "avg": "O(n log n)", "mem": "O(n)", 
        "desc": "Divise, trie recursivement, fusionne. Garantit O(n log n)."
    },
    "quick": {
        "name": "Tri rapide", "stable": False, 
        "avg": "O(n log n)", "mem": "O(log n)", 
        "desc": "Choisit un pivot, partitionne. Le plus rapide en pratique."
    },
    "heap": {
        "name": "Tri par tas", "stable": False, 
        "avg": "O(n log n)", "mem": "O(1)", 
        "desc": "Utilise une structure de tas binaire. Efficace en memoire."
    },
    "comb": {
        "name": "Tri a peigne", "stable": False, 
        "avg": "O(n log n)", "mem": "O(1)", 
        "desc": "Amelioration du tri a bulles avec un ecart decroissant."
    },
    "tim": {
        "name": "Timsort", "stable": True, 
        "avg": "O(n log n)", "mem": "O(n)", 
        "desc": "Hybride puissant (Insertion + Merge). Utilise par Python nativement."
    }
}

# =============================================================================
# UI Components
# =============================================================================

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.is_hovered = False

    def draw(self, surface):
        color = BTN_HOVER if self.is_hovered else BTN_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, CARD_BORDER, self.rect, 1, border_radius=6)
        
        txt_surf = self.font.render(self.text, True, WHITE)
        surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

class Slider:
    def __init__(self, x, y, w, h, values):
        self.rect = pygame.Rect(x, y, w, h)
        self.values = values
        self.index = 1
        self.dragging = False
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

    def get_speed_multiplier(self):
        return self.values[self.index]

    def draw(self, surface):
        lbl = self.font.render("Vitesse", True, TEXT_MUTED)
        surface.blit(lbl, (self.rect.x - 60, self.rect.centery - 8))
        
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 2, self.rect.width, 4)
        pygame.draw.rect(surface, CARD_BORDER, track_rect)
        
        ratio = self.index / max(1, len(self.values) - 1)
        knob_x = self.rect.x + ratio * self.rect.width
        pygame.draw.circle(surface, WHITE, (int(knob_x), self.rect.centery), 8)
        
        val_txt = self.font.render(f"x{self.values[self.index]}", True, WHITE)
        surface.blit(val_txt, (self.rect.right + 15, self.rect.centery - 8))

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(20, 20).collidepoint(pos):
                self.dragging = True
                self.update_from_pos(pos)
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_from_pos(pos)
            return True
        return False

    def update_from_pos(self, pos):
        rel_x = max(0, min(pos[0] - self.rect.x, self.rect.width))
        ratio = rel_x / self.rect.width
        self.index = round(ratio * (len(self.values) - 1))

class MultiSelectDropdown:
    def __init__(self, x, y, w, h, options):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.selected = {options[0][0]}
        self.is_open = False
        self.font = pygame.font.SysFont("Arial", 16)
        self.item_h = 30

    def draw(self, surface):
        pygame.draw.rect(surface, BTN_BG, self.rect, border_radius=4)
        pygame.draw.rect(surface, CARD_BORDER, self.rect, 1, border_radius=4)
        
        if len(self.selected) == 1:
            txt = next(lbl for idx, lbl in self.options if idx in self.selected)
        else:
            txt = f"{len(self.selected)} algorithmes selectionnes"
            
        txt_surf = self.font.render(txt, True, WHITE)
        surface.blit(txt_surf, (self.rect.x + 15, self.rect.y + 8))
        
        pygame.draw.polygon(surface, TEXT_MUTED, [
            (self.rect.right - 20, self.rect.centery - 3),
            (self.rect.right - 10, self.rect.centery - 3),
            (self.rect.right - 15, self.rect.centery + 3)
        ])

        if self.is_open:
            drop_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.item_h)
            pygame.draw.rect(surface, CARD_BG, drop_rect)
            pygame.draw.rect(surface, CARD_BORDER, drop_rect, 1)
            
            for i, (idx, lbl) in enumerate(self.options):
                iy = drop_rect.y + i * self.item_h
                hover = pygame.Rect(drop_rect.x, iy, drop_rect.width, self.item_h).collidepoint(pygame.mouse.get_pos())
                if hover:
                    pygame.draw.rect(surface, BTN_HOVER, (drop_rect.x, iy, drop_rect.width, self.item_h))
                
                cb_rect = pygame.Rect(drop_rect.x + 10, iy + 8, 14, 14)
                pygame.draw.rect(surface, TEXT_MUTED, cb_rect, 1)
                if idx in self.selected:
                    pygame.draw.rect(surface, BAR_COLOR_DONE, cb_rect.inflate(-4, -4))
                
                surface.blit(self.font.render(lbl, True, WHITE), (cb_rect.right + 10, iy + 5))

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_open:
                for i, (idx, _) in enumerate(self.options):
                    item_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.item_h, self.rect.width, self.item_h)
                    if item_rect.collidepoint(pos):
                        if idx in self.selected:
                            if len(self.selected) > 1: self.selected.remove(idx)
                        else:
                            self.selected.add(idx)
                        return True
                self.is_open = False
                return True
            else:
                if self.rect.collidepoint(pos):
                    self.is_open = True
                    return True
        return False

# =============================================================================
# Algorithm View (Bar Chart)
# =============================================================================

class SorterView:
    def __init__(self, rect, algo_id):
        self.rect = pygame.Rect(rect)
        self.algo_id = algo_id
        self.name = ALGO_METADATA[algo_id]["name"]
        self.array = []
        self.active_indices = []
        self.is_done = False
        
        self.steps = 0
        self.swaps = 0
        self.time = 0.0
        self.cpu = 0.0

    def update_state(self, arr, indices, done, metrics):
        self.array = arr
        self.is_done = done
        
        # Safely handle dictionary, tuple, or list indices
        if isinstance(indices, dict):
            self.active_indices = indices.get("red", [])
        elif indices:
            self.active_indices = list(indices)
        else:
            self.active_indices = []

        if metrics:
            self.steps = metrics["steps"]
            self.swaps = metrics["swaps"]
            self.time = metrics["time"]
            self.cpu = metrics["cpu"]

    def draw(self, surface, font, small_font):
        pygame.draw.rect(surface, BG_COLOR, self.rect)
        
        header_txt = f"{self.name}   |   Comparaisons: {self.steps}   Echanges: {self.swaps}   Temps: {self.time:.2f}s   CPU: {self.cpu:.1f}%"
        h_surf = small_font.render(header_txt, True, TEXT_MUTED)
        surface.blit(h_surf, (self.rect.x, self.rect.y))
        
        if not self.array: return
        
        n = len(self.array)
        max_val = max(self.array) if n > 0 else 1
        bar_w = self.rect.width / n
        max_h = self.rect.height - 30
        
        for i, val in enumerate(self.array):
            h = (val / max_val) * max_h
            x = self.rect.x + i * bar_w
            y = self.rect.bottom - h
            
            color = BAR_COLOR_DONE if self.is_done else (BAR_COLOR_ACTIVE if i in self.active_indices else BAR_COLOR_DEFAULT)
            pygame.draw.rect(surface, color, (x, y, max(1, bar_w - 1), h))

# =============================================================================
# Main Application
# =============================================================================

class SortApp:
    def __init__(self, algos, base_array):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Visualisation des algorithmes de tri")
        
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 14)
        
        self.algos_dict = dict(algos)
        self.base_array = base_array if len(base_array) >= 10 else [random.uniform(10.0, 100.0) for _ in range(40)]
        
        self.state = "MENU"
        self.ui_queue = queue.Queue()
        self.threads = []
        self.run_results = []
        
        self.is_paused = False
        self.step_event = threading.Event()
        self.step_event.set()

        # Define export directory
        self.reports_dir = "rapports_analyse"

        self.setup_ui()
        self.init_views()

    def setup_ui(self):
        opts = [(k, ALGO_METADATA[k]["name"]) for k in self.algos_dict.keys()]
        self.dropdown = MultiSelectDropdown(20, 20, 400, 36, opts)
        
        self.btn_run = Button(20, 70, 100, 36, "Lancer")
        self.btn_step = Button(130, 70, 100, 36, "Etape")
        self.btn_shuffle = Button(240, 70, 100, 36, "Melanger")
        
        self.slider = Slider(450, 88, 150, 20, [1, 3, 5, 10, 20, 50, 100])
        self.btn_summary = Button(WINDOW_WIDTH - 150, 70, 130, 36, "Voir Resultats")

        # Summary UI
        self.btn_back = Button(20, 20, 100, 36, "Retour")
        self.btn_csv = Button(130, 20, 130, 36, "Exporter CSV")
        self.btn_pdf = Button(270, 20, 130, 36, "Exporter PDF")

    def ensure_report_dir(self):
        """Creates the export directory if it doesn't exist."""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def init_views(self):
        self.views = []
        selected = list(self.dropdown.selected)
        if not selected: return

        cols = min(2, len(selected)) if len(selected) > 1 else 1
        rows = (len(selected) + cols - 1) // cols
        
        cell_w = (WINDOW_WIDTH - 40 - (cols - 1) * 20) // cols
        cell_h = (WINDOW_HEIGHT - 160 - (rows - 1) * 30) // rows

        for i, algo_id in enumerate(selected):
            c = i % cols
            r = i // cols
            rect = (20 + c * (cell_w + 20), 140 + r * (cell_h + 30), cell_w, cell_h)
            view = SorterView(rect, algo_id)
            view.update_state(self.base_array.copy(), [], False, None)
            self.views.append(view)

    def worker_thread(self, algo_id, sort_func, data):
        steps = 0
        swaps = 0
        start_time = time.perf_counter()
        
        process = psutil.Process(os.getpid())
        process.cpu_percent() 

        def callback(state, indices):
            nonlocal steps, swaps
            steps += 1
            if indices: swaps += 1
            
            self.step_event.wait()
            
            cur_time = time.perf_counter() - start_time
            cur_cpu = process.cpu_percent()
            metrics = {"steps": steps, "swaps": swaps, "time": cur_time, "cpu": cur_cpu}
            
            self.ui_queue.put({"id": algo_id, "state": state, "indices": indices, "done": False, "metrics": metrics})
            
            delay = 0.05 / self.slider.get_speed_multiplier()
            
            if self.is_paused:
                self.step_event.clear()
            else:
                time.sleep(delay)

        sorted_data = sort_func(data, callback)
        total_time = time.perf_counter() - start_time
        final_cpu = process.cpu_percent()
        final_metrics = {"steps": steps, "swaps": swaps, "time": total_time, "cpu": final_cpu}
        
        self.ui_queue.put({"id": algo_id, "state": sorted_data, "indices": [], "done": True, "metrics": final_metrics})
        
        self.run_results.append({
            "id": algo_id,
            "name": ALGO_METADATA[algo_id]["name"],
            "time": total_time,
            "steps": steps,
            "swaps": swaps,
            "cpu": final_cpu
        })

    def start_sorting(self, step_mode=False):
        self.state = "RUNNING"
        self.run_results = []
        self.is_paused = step_mode
        if step_mode: self.step_event.clear()
        else: self.step_event.set()

        self.init_views()
        self.threads = []
        
        for view in self.views:
            t = threading.Thread(
                target=self.worker_thread,
                args=(view.algo_id, self.algos_dict[view.algo_id], self.base_array.copy()),
                daemon=True
            )
            self.threads.append(t)
            t.start()

    def _export_csv(self):
        self.ensure_report_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.reports_dir, f"sorting_analytics_{timestamp}.csv")
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Algorithme", "Temps (s)", "Etapes", "Echanges", "CPU (%)", "Stabilite"])
            for r in self.run_results:
                stable_str = "Oui" if ALGO_METADATA[r["id"]]["stable"] else "Non"
                writer.writerow([r["name"], f"{r['time']:.4f}", r["steps"], r["swaps"], f"{r['cpu']:.1f}", stable_str])
        print(f"[OK] CSV exporte : {filename}")

    def _export_pdf(self):
        self.ensure_report_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.reports_dir, f"sorting_analytics_{timestamp}.pdf")

        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(11, 5))
        ax.axis("tight")
        ax.axis("off")

        cols = ["Algorithme", "Temps (s)", "Etapes", "Echanges", "CPU (%)", "Complexite Moy", "Stabilite"]
        data = []
        best_algo = ""
        best_time = float('inf')

        for r in self.run_results:
            stable_str = "Stable" if ALGO_METADATA[r["id"]]["stable"] else "Non stable"
            data.append([
                r["name"], f"{r['time']:.4f}", str(r["steps"]), str(r["swaps"]), 
                f"{r['cpu']:.1f}", ALGO_METADATA[r["id"]]["avg"], stable_str
            ])
            
            # Find the best time for the conclusion
            if r["time"] < best_time:
                best_time = r["time"]
                best_algo = r["name"]

        table = ax.table(cellText=data, colLabels=cols, loc="center", cellLoc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        plt.title("Analytique et Comparaison des Algorithmes de Tri", fontsize=14, pad=20)
        
        # Add dynamic conclusion below table
        conclusion = f"Conclusion :\nParmi les algorithmes testes, {best_algo} a ete le plus rapide avec un temps de {best_time:.4f}s."
        plt.figtext(0.1, 0.05, conclusion, fontsize=11, ha="left", color="#333333")
        plt.subplots_adjust(bottom=0.25) # Make room for text at the bottom

        plt.savefig(filepath, format="pdf", bbox_inches="tight")
        plt.close(fig)
        print(f"[OK] PDF exporte : {filepath}")

    def draw_summary(self):
        self.screen.fill(BG_COLOR)
        
        self.btn_back.draw(self.screen)
        self.btn_csv.draw(self.screen)
        self.btn_pdf.draw(self.screen)
        
        title = self.font.render("Algorithmes de tri - Resultats du benchmark", True, WHITE)
        self.screen.blit(title, (20, 80))
        
        card_w, card_h, gap = 360, 190, 20
        start_x, start_y = 20, 130
        
        for i, res in enumerate(self.run_results):
            x = start_x + (i % 3) * (card_w + gap)
            y = start_y + (i // 3) * (card_h + gap)
            
            meta = ALGO_METADATA[res["id"]]
            
            pygame.draw.rect(self.screen, CARD_BG, (x, y, card_w, card_h), border_radius=8)
            pygame.draw.rect(self.screen, CARD_BORDER, (x, y, card_w, card_h), 1, border_radius=8)
            
            self.screen.blit(self.font.render(meta["name"], True, WHITE), (x + 15, y + 15))
            
            badge_c = BADGE_STABLE if meta["stable"] else BADGE_UNSTABLE
            badge_txt = "Stable" if meta["stable"] else "Non stable"
            b_surf = self.font_small.render(badge_txt, True, badge_c)
            b_rect = pygame.Rect(x + card_w - b_surf.get_width() - 25, y + 15, b_surf.get_width() + 10, 24)
            pygame.draw.rect(self.screen, badge_c, b_rect, 1, border_radius=12)
            self.screen.blit(b_surf, (b_rect.x + 5, b_rect.y + 3))
            
            m_y = y + 50
            metrics = [
                ("Temps execution", f"{res['time']:.4f} s"),
                ("Nombre d'etapes", f"{res['steps']}"),
                ("CPU utilise", f"{res['cpu']:.1f} %")
            ]
            for lbl, val in metrics:
                self.screen.blit(self.font_small.render(lbl, True, TEXT_MUTED), (x + 15, m_y))
                self.screen.blit(self.font_small.render(val, True, WHITE), (x + 140, m_y))
                m_y += 22
                
            pygame.draw.line(self.screen, CARD_BORDER, (x + 15, m_y + 5), (x + card_w - 15, m_y + 5))
            
            t_y = m_y + 15
            self.screen.blit(self.font_small.render(f"Memoire: {meta['mem']} | Moyenne: {meta['avg']}", True, TEXT_MUTED), (x + 15, t_y))
            
            desc_words = meta['desc'].split(" ")
            line, ly = "", t_y + 22
            for w in desc_words:
                if self.font_small.size(line + w)[0] > card_w - 30:
                    self.screen.blit(self.font_small.render(line, True, WHITE), (x + 15, ly))
                    line, ly = w + " ", ly + 18
                else:
                    line += w + " "
            self.screen.blit(self.font_small.render(line, True, WHITE), (x + 15, ly))

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.state in ["MENU", "RUNNING"]:
                    if self.dropdown.handle_event(event, pos):
                        if not self.dropdown.is_open and self.state == "MENU":
                            self.init_views()
                        continue
                    
                    if not self.dropdown.is_open:
                        self.slider.handle_event(event, pos)
                        self.btn_run.handle_event(event, pos)
                        self.btn_step.handle_event(event, pos)
                        self.btn_shuffle.handle_event(event, pos)
                        self.btn_summary.handle_event(event, pos)
                        
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if self.btn_shuffle.is_hovered and self.state == "MENU":
                                random.shuffle(self.base_array)
                                self.init_views()
                            elif self.btn_run.is_hovered:
                                if self.state == "RUNNING" and self.is_paused:
                                    self.is_paused = False
                                    self.step_event.set()
                                elif self.state == "MENU":
                                    self.start_sorting(step_mode=False)
                            elif self.btn_step.is_hovered:
                                if self.state == "MENU":
                                    self.start_sorting(step_mode=True)
                                elif self.state == "RUNNING":
                                    self.is_paused = True
                                    self.step_event.set()
                            elif self.btn_summary.is_hovered and len(self.run_results) > 0:
                                self.state = "SUMMARY"

                elif self.state == "SUMMARY":
                    self.btn_back.handle_event(event, pos)
                    self.btn_csv.handle_event(event, pos)
                    self.btn_pdf.handle_event(event, pos)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.btn_back.is_hovered:
                            self.run_results = []
                            self.state = "MENU"
                        elif self.btn_csv.is_hovered:
                            self._export_csv()
                        elif self.btn_pdf.is_hovered:
                            self._export_pdf()

            while not self.ui_queue.empty():
                try:
                    msg = self.ui_queue.get_nowait()
                    for view in self.views:
                        if view.algo_id == msg["id"]:
                            view.update_state(msg["state"], msg["indices"], msg["done"], msg.get("metrics"))
                except queue.Empty:
                    break

            if self.state == "RUNNING" and all(not t.is_alive() for t in self.threads):
                self.state = "MENU"

            if self.state == "SUMMARY":
                self.draw_summary()
            else:
                self.screen.fill(BG_COLOR)
                for view in self.views: view.draw(self.screen, self.font, self.font_small)
                
                self.btn_run.draw(self.screen)
                self.btn_step.draw(self.screen)
                self.btn_shuffle.draw(self.screen)
                self.slider.draw(self.screen)
                
                if self.state == "MENU" and len(self.run_results) > 0:
                    self.btn_summary.draw(self.screen)
                
                self.dropdown.draw(self.screen) 

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

def run_display(algos, arr, threaded=False):
    app = SortApp(algos, arr)
    app.run()