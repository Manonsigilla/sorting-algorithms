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
# Modern Egyptian Theme (Night & Gold Glassmorphism)
# =============================================================================

# Gradients & Background
BG_TOP = (15, 20, 35)                 # Midnight Lapis Blue
BG_BOTTOM = (5, 5, 10)                # Deep dark
GLASS_BG = (30, 40, 60, 160)          # Translucent dark blue for panels
GLASS_BORDER = (212, 175, 55, 100)    # Translucent Gold for borders
GLASS_HOVER = (212, 175, 55, 160)      # Gold tint on hover

# Colors
WHITE = (240, 240, 240)
COLOR_PAPYRUS = (235, 222, 190)       # Main Text (Soft beige)
COLOR_PAPYRUS_MUTED = (160, 150, 130) # Secondary Text
COLOR_LAPIS = (38, 120, 180)          # Default Bar
COLOR_CARNELIAN = (227, 66, 52)       # Active/Swap
COLOR_GOLD = (212, 175, 55)           # Sorted / Accents
BADGE_STABLE = (46, 204, 113)         # Emerald Green
BADGE_UNSTABLE = (231, 76, 60)        # Alizarin Crimson
SUCCESS_GREEN = (30, 130, 70, 230)    # For toast notification

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# =============================================================================
# Algorithm Theoretical Data
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
# Audio Manager
# =============================================================================

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds_dir = "sounds"
        if not os.path.exists(self.sounds_dir): 
            os.makedirs(self.sounds_dir)
            
        self.snd_swap = self.load_sound("swap.wav")
        self.snd_finish = self.load_sound("finish.wav")
        
        self.bg_music_loaded = False
        bg_path = os.path.join(self.sounds_dir, "egyptian_bg.ogg")
        if os.path.exists(bg_path):
            try:
                pygame.mixer.music.load(bg_path)
                pygame.mixer.music.set_volume(0.3)
                self.bg_music_loaded = True
            except Exception: pass

    def load_sound(self, filename):
        path = os.path.join(self.sounds_dir, filename)
        if os.path.exists(path):
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(0.5)
                return snd
            except Exception: return None
        return None

    def play_bg_music(self):
        if self.bg_music_loaded and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

    def stop_bg_music(self):
        if self.bg_music_loaded: pygame.mixer.music.stop()

    def play_swap(self):
        if self.snd_swap: self.snd_swap.play()

    def play_finish(self):
        if self.snd_finish: self.snd_finish.play()

# =============================================================================
# Graphical Helpers (Glassmorphism, 3D & Gradients)
# =============================================================================

def create_bg_gradient(w, h):
    """Pre-calculates the background gradient to save CPU."""
    bg = pygame.Surface((w, h))
    for y in range(h):
        ratio = y / h
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        pygame.draw.line(bg, (r, g, b), (0, y), (w, y))
    return bg

def draw_glass_panel(surface, rect, radius=8, hover=False):
    """Draws a translucent panel with a shiny border."""
    panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    bg_color = GLASS_HOVER if hover else GLASS_BG
    pygame.draw.rect(panel, bg_color, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, GLASS_BORDER, panel.get_rect(), 1, border_radius=radius)
    surface.blit(panel, rect.topleft)

# =============================================================================
# UI Components
# =============================================================================

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont("Garamond, Times New Roman", 18, bold=True)
        self.is_hovered = False

    def draw(self, surface):
        # Base panel for 3D effect
        panel = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        bg_color = (60, 80, 110, 220) if self.is_hovered else (40, 55, 80, 200)
        
        pygame.draw.rect(panel, bg_color, panel.get_rect(), border_radius=6)
        
        # 3D Highlights (Top shine, Bottom shadow)
        pygame.draw.line(panel, (255, 255, 255, 60), (4, 1), (self.rect.w - 5, 1), 2)
        pygame.draw.line(panel, (0, 0, 0, 120), (4, self.rect.h - 2), (self.rect.w - 5, self.rect.h - 2), 2)
        
        # Golden border
        pygame.draw.rect(panel, COLOR_GOLD, panel.get_rect(), 1, border_radius=6)
        surface.blit(panel, self.rect.topleft)
        
        # Text
        txt_color = COLOR_GOLD if self.is_hovered else COLOR_PAPYRUS
        txt_surf = self.font.render(self.text, True, txt_color)
        surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered: return True
        return False

class Slider:
    def __init__(self, x, y, w, h, values):
        self.rect = pygame.Rect(x, y, w, h)
        self.values = values
        self.index = 1
        self.dragging = False
        self.font = pygame.font.SysFont("Garamond, Times New Roman", 16, bold=True)

    def get_speed_multiplier(self):
        return self.values[self.index]

    def draw(self, surface):
        lbl = self.font.render("Vitesse", True, COLOR_PAPYRUS_MUTED)
        surface.blit(lbl, (self.rect.x - 60, self.rect.centery - 10))
        
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 2, self.rect.width, 4)
        pygame.draw.rect(surface, (50, 50, 70), track_rect, border_radius=2)
        pygame.draw.rect(surface, COLOR_GOLD, (self.rect.x, self.rect.centery - 2, self.rect.width * (self.index / max(1, len(self.values)-1)), 4), border_radius=2)
        
        ratio = self.index / max(1, len(self.values) - 1)
        knob_x = self.rect.x + ratio * self.rect.width
        
        # Shiny Knob
        pygame.draw.circle(surface, COLOR_GOLD, (int(knob_x), self.rect.centery), 8)
        pygame.draw.circle(surface, BG_TOP, (int(knob_x), self.rect.centery), 4)
        
        val_txt = self.font.render(f"x{self.values[self.index]}", True, COLOR_GOLD)
        surface.blit(val_txt, (self.rect.right + 15, self.rect.centery - 10))

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
        self.font = pygame.font.SysFont("Garamond, Times New Roman", 18)
        self.item_h = 32

    def draw(self, surface):
        is_hover = self.rect.collidepoint(pygame.mouse.get_pos())
        
        # Base button panel with 3D effect
        btn_panel = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        bg_color = (60, 80, 110, 220) if is_hover else (40, 55, 80, 200)
        pygame.draw.rect(btn_panel, bg_color, btn_panel.get_rect(), border_radius=6)
        pygame.draw.line(btn_panel, (255, 255, 255, 60), (4, 1), (self.rect.w - 5, 1), 2)
        pygame.draw.rect(btn_panel, COLOR_GOLD, btn_panel.get_rect(), 1, border_radius=6)
        surface.blit(btn_panel, self.rect.topleft)
        
        if len(self.selected) == 1:
            txt = next(lbl for idx, lbl in self.options if idx in self.selected)
        else:
            txt = f"{len(self.selected)} manuscrits choisis"
            
        surface.blit(self.font.render(txt, True, COLOR_PAPYRUS), (self.rect.x + 15, self.rect.y + 8))
        
        # Chevron indicator (▼ or ▲)
        chevron_color = COLOR_GOLD if is_hover else COLOR_PAPYRUS_MUTED
        if self.is_open:
            pts = [(self.rect.right - 20, self.rect.centery + 3), (self.rect.right - 10, self.rect.centery + 3), (self.rect.right - 15, self.rect.centery - 3)]
        else:
            pts = [(self.rect.right - 20, self.rect.centery - 3), (self.rect.right - 10, self.rect.centery - 3), (self.rect.right - 15, self.rect.centery + 3)]
        pygame.draw.polygon(surface, chevron_color, pts)

        # High Opacity Dropdown List
        if self.is_open:
            drop_h = len(self.options) * self.item_h
            drop_rect = pygame.Rect(self.rect.x, self.rect.bottom + 2, self.rect.width, drop_h)
            
            panel = pygame.Surface((drop_rect.w, drop_rect.h), pygame.SRCALPHA)
            # Highly opaque dark blue background to hide background charts completely
            pygame.draw.rect(panel, (*BG_TOP, 250), panel.get_rect(), border_radius=6)
            
            m_pos = pygame.mouse.get_pos()
            for i, (idx, lbl) in enumerate(self.options):
                iy = i * self.item_h
                hover_rect = pygame.Rect(drop_rect.x, drop_rect.y + iy, drop_rect.w, self.item_h)
                
                if hover_rect.collidepoint(m_pos):
                    pygame.draw.rect(panel, GLASS_HOVER, (0, iy, drop_rect.w, self.item_h))
                
                # Checkbox
                cb_rect = pygame.Rect(10, iy + 8, 14, 14)
                pygame.draw.rect(panel, COLOR_PAPYRUS_MUTED, cb_rect, 1, border_radius=3)
                if idx in self.selected:
                    pygame.draw.rect(panel, COLOR_GOLD, cb_rect.inflate(-4, -4), border_radius=2)
                
                panel.blit(self.font.render(lbl, True, COLOR_PAPYRUS), (cb_rect.right + 10, iy + 6))
                
            pygame.draw.rect(panel, COLOR_GOLD, panel.get_rect(), 1, border_radius=6)
            surface.blit(panel, drop_rect.topleft)

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_open:
                drop_rect = pygame.Rect(self.rect.x, self.rect.bottom + 2, self.rect.width, len(self.options) * self.item_h)
                if drop_rect.collidepoint(pos):
                    rel_y = pos[1] - drop_rect.y
                    idx_clicked = self.options[rel_y // self.item_h][0]
                    if idx_clicked in self.selected:
                        if len(self.selected) > 1: self.selected.remove(idx_clicked)
                    else:
                        self.selected.add(idx_clicked)
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
        
        if isinstance(indices, dict):
            # Picks "swap" indices if they exist, otherwise picks "compare"
            self.active_indices = indices.get("swap", indices.get("compare", []))
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
        draw_glass_panel(surface, self.rect, radius=8)
        
        header_txt = f"{self.name}   |   Comp: {self.steps}   Ech: {self.swaps}   Tps: {self.time:.2f}s"
        h_surf = small_font.render(header_txt, True, COLOR_PAPYRUS_MUTED)
        surface.blit(h_surf, (self.rect.x + 10, self.rect.y + 10))
        
        if not self.array: return
        
        n = len(self.array)
        max_val = max(self.array) if n > 0 else 1
        bar_w = (self.rect.width - 20) / n
        max_h = self.rect.height - 40
        
        for i, val in enumerate(self.array):
            h = (val / max_val) * max_h
            x = self.rect.x + 10 + i * bar_w
            y = self.rect.bottom - h - 10
            
            color = COLOR_GOLD if self.is_done else (COLOR_CARNELIAN if i in self.active_indices else COLOR_LAPIS)
            
            bar_rect = pygame.Rect(x, y, max(1, bar_w - 2), h)
            pygame.draw.rect(surface, color, bar_rect, border_radius=2)
            
            # Glass highlight on bars
            highlight = pygame.Surface((bar_rect.w, bar_rect.h), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 255, 40), (0, 0, bar_rect.w/2, bar_rect.h), border_radius=2)
            surface.blit(highlight, bar_rect.topleft)

# =============================================================================
# Main Application
# =============================================================================

class SortApp:
    def __init__(self, algos, base_array):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Les Papyrus de Heron - Visualisation")
        
        self.scroll_y = 0
        self.max_scroll = 0
        self.is_fullscreen = False
        
        self.font_title = pygame.font.SysFont("Garamond, Times New Roman", 28, bold=True)
        self.font = pygame.font.SysFont("Garamond, Times New Roman", 20, bold=True)
        self.font_small = pygame.font.SysFont("Garamond, Times New Roman", 15)
        
        self.bg_surface = create_bg_gradient(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.audio = AudioManager()
        
        self.algos_dict = dict(algos)
        self.base_array = base_array if len(base_array) >= 10 else [random.uniform(10.0, 100.0) for _ in range(40)]
        
        self.state = "MENU"
        self.ui_queue = queue.Queue()
        self.threads = []
        self.run_results = []
        self.finished_algos = set()
        
        self.is_paused = False
        self.step_event = threading.Event()
        self.step_event.set()

        self.reports_dir = "rapports_analyse"
        
        # Toast Notification
        self.toast_msg = ""
        self.toast_end_time = 0

        self.setup_ui()
        self.init_views()
        self.audio.play_bg_music()

    def setup_ui(self):
        opts = [(k, ALGO_METADATA[k]["name"]) for k in self.algos_dict.keys()]
        self.dropdown = MultiSelectDropdown(20, 20, 350, 40, opts)
        
        self.btn_run = Button(20, 75, 110, 36, "Lancer")
        self.btn_step = Button(140, 75, 110, 36, "Etape")
        self.btn_shuffle = Button(260, 75, 110, 36, "Melanger")
        
        self.slider = Slider(450, 93, 150, 20, [1, 3, 5, 10, 20, 50, 100])
        self.btn_summary = Button(WINDOW_WIDTH - 180, 75, 160, 36, "Voir les Resultats")

        self.btn_back = Button(20, 20, 120, 36, "Retour")
        self.btn_csv = Button(150, 20, 140, 36, "Exporter CSV")
        self.btn_pdf = Button(300, 20, 140, 36, "Exporter PDF")

    def show_toast(self, msg, duration=3.0):
        self.toast_msg = msg
        self.toast_end_time = time.time() + duration

    def draw_toast(self):
        if time.time() < self.toast_end_time and self.toast_msg:
            txt_surf = self.font_small.render(self.toast_msg, True, COLOR_PAPYRUS)
            pad_x, pad_y = 20, 10
            rect = pygame.Rect(0, 0, txt_surf.get_width() + pad_x*2, txt_surf.get_height() + pad_y*2)
            rect.midbottom = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)
            
            panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(panel, SUCCESS_GREEN, panel.get_rect(), border_radius=15)
            pygame.draw.rect(panel, COLOR_GOLD, panel.get_rect(), 1, border_radius=15)
            
            self.screen.blit(panel, rect.topleft)
            self.screen.blit(txt_surf, (rect.x + pad_x, rect.y + pad_y))

    def ensure_report_dir(self):
        if not os.path.exists(self.reports_dir): os.makedirs(self.reports_dir)

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
        steps, swaps = 0, 0
        start_time = time.perf_counter()
        
        process = psutil.Process(os.getpid())
        process.cpu_percent() 

        def callback(state, indices):
            nonlocal steps, swaps
            steps += 1
            
            # Only count as a swap if it's actually a swap action
            if isinstance(indices, dict) and "swap" in indices:
                swaps += 1
            elif isinstance(indices, tuple) or isinstance(indices, list):
                swaps += 1
            
            self.step_event.wait()
            
            metrics = {"steps": steps, "swaps": swaps, "time": time.perf_counter() - start_time, "cpu": process.cpu_percent()}
            
            # Sound is only played on swaps
            play_sound = "swap" if (isinstance(indices, dict) and "swap" in indices) else None
            self.ui_queue.put({"id": algo_id, "state": state, "indices": indices, "done": False, "metrics": metrics, "sound": play_sound})
            
            delay = 0.05 / self.slider.get_speed_multiplier()
            
            if self.is_paused: self.step_event.clear()
            else: time.sleep(delay)

        sorted_data = sort_func(data, callback)
        total_time = time.perf_counter() - start_time
        final_cpu = process.cpu_percent()
        final_metrics = {"steps": steps, "swaps": swaps, "time": total_time, "cpu": final_cpu}
        
        self.ui_queue.put({"id": algo_id, "state": sorted_data, "indices": [], "done": True, "metrics": final_metrics, "sound": "finish"})
        
        self.run_results.append({
            "id": algo_id, "name": ALGO_METADATA[algo_id]["name"],
            "time": total_time, "steps": steps, "swaps": swaps, "cpu": final_cpu
        })

    def start_sorting(self, step_mode=False):
        self.state = "RUNNING"
        self.run_results = []
        self.finished_algos = set()
        self.is_paused = step_mode
        if step_mode: self.step_event.clear()
        else: self.step_event.set()

        self.init_views()
        self.threads = []
        
        for view in self.views:
            t = threading.Thread(target=self.worker_thread, args=(view.algo_id, self.algos_dict[view.algo_id], self.base_array.copy()), daemon=True)
            self.threads.append(t)
            t.start()

    def _export_csv(self):
        self.ensure_report_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.reports_dir, f"heron_analyse_{timestamp}.csv")
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Algorithme", "Temps (s)", "Etapes", "Echanges", "CPU (%)", "Stabilite"])
            for r in self.run_results:
                stable_str = "Oui" if ALGO_METADATA[r["id"]]["stable"] else "Non"
                writer.writerow([r["name"], f"{r['time']:.4f}", r["steps"], r["swaps"], f"{r['cpu']:.1f}", stable_str])
        
        self.show_toast(f"CSV sauvegarde avec succes !")

    def _export_pdf(self):
        self.ensure_report_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.reports_dir, f"heron_analyse_{timestamp}.pdf")

        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(11, 5))
        ax.axis("tight")
        ax.axis("off")

        cols = ["Algorithme", "Temps (s)", "Etapes", "Echanges", "CPU (%)", "Complexite Moy", "Stabilite"]
        data = []
        best_algo, best_time = "", float('inf')

        for r in self.run_results:
            stable_str = "Stable" if ALGO_METADATA[r["id"]]["stable"] else "Non stable"
            data.append([
                r["name"], f"{r['time']:.4f}", str(r["steps"]), str(r["swaps"]), 
                f"{r['cpu']:.1f}", ALGO_METADATA[r["id"]]["avg"], stable_str
            ])
            if r["time"] < best_time:
                best_time, best_algo = r["time"], r["name"]

        table = ax.table(cellText=data, colLabels=cols, loc="center", cellLoc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        plt.title("Les Papyrus de Heron - Analytique des Tris", fontsize=16, pad=20, fontname='serif')
        conclusion = f"Conclusion :\nParmi les manuscrits testes, {best_algo} a ete le plus vif avec un temps de {best_time:.4f}s."
        plt.figtext(0.1, 0.05, conclusion, fontsize=12, ha="left", color="#3b2b20", fontname='serif')
        plt.subplots_adjust(bottom=0.25)

        plt.savefig(filepath, format="pdf", bbox_inches="tight")
        plt.close(fig)
        self.show_toast(f"PDF sauvegarde avec succes !")

    def draw_summary(self):
        self.screen.blit(self.bg_surface, (0, 0))
        
        card_w, card_h, gap = 360, 220, 20
        win_w, win_h = self.screen.get_size()
        
        # Calculer le nombre de colonnes dynamiquement
        cols = max(1, (win_w - 40 + gap) // (card_w + gap))
        rows = (len(self.run_results) + cols - 1) // cols
        
        # Calculer la limite du scroll
        total_content_height = 130 + rows * (card_h + gap)
        self.max_scroll = max(0, total_content_height - win_h + 50)
        
        # Appliquer le scroll aux boutons
        self.btn_back.rect.topleft = (20, 20 - self.scroll_y)
        self.btn_csv.rect.topleft = (150, 20 - self.scroll_y)
        self.btn_pdf.rect.topleft = (300, 20 - self.scroll_y)
        
        self.btn_back.draw(self.screen)
        self.btn_csv.draw(self.screen)
        self.btn_pdf.draw(self.screen)
        
        title = self.font_title.render("Les Papyrus de Heron - Decryptage", True, COLOR_GOLD)
        self.screen.blit(title, (20, 80 - self.scroll_y))
        
        start_x, start_y = 20, 130 - self.scroll_y
        
        for i, res in enumerate(self.run_results):
            x = start_x + (i % cols) * (card_w + gap)
            y = start_y + (i // cols) * (card_h + gap)
            
            meta = ALGO_METADATA[res["id"]]
            
            draw_glass_panel(self.screen, pygame.Rect(x, y, card_w, card_h), radius=10)
            
            # Using soft papyrus color instead of gold for titles
            self.screen.blit(self.font.render(meta["name"], True, COLOR_PAPYRUS), (x + 15, y + 15))
            
            badge_c = BADGE_STABLE if meta["stable"] else BADGE_UNSTABLE
            badge_txt = "Stable" if meta["stable"] else "Instable"
            b_surf = self.font_small.render(badge_txt, True, WHITE)
            b_rect = pygame.Rect(x + card_w - b_surf.get_width() - 25, y + 15, b_surf.get_width() + 10, 24)
            
            b_bg = pygame.Surface((b_rect.w, b_rect.h), pygame.SRCALPHA)
            pygame.draw.rect(b_bg, (*badge_c, 150), b_bg.get_rect(), border_radius=12)
            pygame.draw.rect(b_bg, badge_c, b_bg.get_rect(), 1, border_radius=12)
            self.screen.blit(b_bg, b_rect.topleft)
            self.screen.blit(b_surf, (b_rect.x + 5, b_rect.y + 3))
            
            m_y = y + 55
            metrics = [
                ("Temps execution", f"{res['time']:.4f} s"),
                ("Nombre d'etapes", f"{res['steps']}"),
                ("CPU utilise", f"{res['cpu']:.1f} %")
            ]
            for lbl, val in metrics:
                self.screen.blit(self.font_small.render(lbl, True, COLOR_PAPYRUS_MUTED), (x + 15, m_y))
                self.screen.blit(self.font_small.render(val, True, COLOR_PAPYRUS), (x + 140, m_y))
                m_y += 22
                
            pygame.draw.line(self.screen, GLASS_BORDER, (x + 15, m_y + 5), (x + card_w - 15, m_y + 5))
            
            t_y = m_y + 15
            self.screen.blit(self.font_small.render(f"Mem: {meta['mem']} | Moy: {meta['avg']}", True, COLOR_PAPYRUS_MUTED), (x + 15, t_y))
            
            desc_words = meta['desc'].split(" ")
            line, ly = "", t_y + 22
            for w in desc_words:
                if self.font_small.size(line + w)[0] > card_w - 30:
                    self.screen.blit(self.font_small.render(line, True, COLOR_PAPYRUS), (x + 15, ly))
                    line, ly = w + " ", ly + 18
                else:
                    line += w + " "
            self.screen.blit(self.font_small.render(line, True, COLOR_PAPYRUS), (x + 15, ly))
            
        self.draw_toast()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Gestion du plein écran (Touche F11)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    global WINDOW_WIDTH, WINDOW_HEIGHT
                    self.is_fullscreen = not self.is_fullscreen
                    if self.is_fullscreen:
                        info = pygame.display.Info()
                        WINDOW_WIDTH, WINDOW_HEIGHT = info.current_w, info.current_h
                        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
                    else:
                        WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
                        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                    
                    self.bg_surface = create_bg_gradient(WINDOW_WIDTH, WINDOW_HEIGHT)
                    self.init_views()

                # Gestion de la redimension de la fenêtre à la souris
                if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                    WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                    self.bg_surface = create_bg_gradient(WINDOW_WIDTH, WINDOW_HEIGHT)
                    self.init_views()

                # Gestion de la molette de souris (Scroll)
                if event.type == pygame.MOUSEWHEEL and self.state == "SUMMARY":
                    self.scroll_y -= event.y * 40
                    self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
                
                if self.state in ["MENU", "RUNNING"]:
                    if self.dropdown.handle_event(event, pos):
                        if not self.dropdown.is_open and self.state == "MENU": self.init_views()
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
                            self.scroll_y = 0
                            self.state = "MENU"
                        elif self.btn_csv.is_hovered: self._export_csv()
                        elif self.btn_pdf.is_hovered: self._export_pdf()

            while not self.ui_queue.empty():
                try:
                    msg = self.ui_queue.get_nowait()
                    
                    if msg.get("sound") == "swap" and not self.is_paused:
                        if random.random() < 0.2: self.audio.play_swap()
                    elif msg.get("sound") == "finish" and msg["id"] not in self.finished_algos:
                        self.audio.play_finish()
                        self.finished_algos.add(msg["id"])

                    for view in self.views:
                        if view.algo_id == msg["id"]:
                            view.update_state(msg["state"], msg["indices"], msg["done"], msg.get("metrics"))
                except queue.Empty: break

            if self.state == "RUNNING" and all(not t.is_alive() for t in self.threads):
                self.state = "MENU"

            if self.state == "SUMMARY":
                self.draw_summary()
            else:
                self.screen.blit(self.bg_surface, (0, 0))
                for view in self.views: view.draw(self.screen, self.font, self.font_small)
                
                self.btn_run.draw(self.screen)
                self.btn_step.draw(self.screen)
                self.btn_shuffle.draw(self.screen)
                self.slider.draw(self.screen)
                
                if self.state == "MENU" and len(self.run_results) > 0:
                    self.btn_summary.draw(self.screen)
                
                self.dropdown.draw(self.screen)
                self.draw_toast()

            pygame.display.flip()
            clock.tick(60)

        self.audio.stop_bg_music()
        pygame.quit()

def run_display(algos, arr, threaded=False):
    app = SortApp(algos, arr)
    app.run()