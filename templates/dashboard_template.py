import tkinter as tk
from tkinter import ttk
import os
import sys
from PIL import Image, ImageTk
from utils.sound_manager import SoundManager

# --- NEW: Helper function to find bundled images ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# ---------------------------------------------------

STAGE_PALETTES = {
    "dog": {
        "glow_outer": "#FFBF82", "glow_inner": "#FFC999", "wall": "#FFE8D6",
        "floor": "#FFD3B5", "shadow": "#965F3C", "sparkle": "#FFFFFF",
    },
    "cat": {
        "glow_outer": "#C8B4EB", "glow_inner": "#D8C7F0", "wall": "#E8DEF8",
        "floor": "#D5C7F0", "shadow": "#6E5A8C", "sparkle": "#FFFFFF",
    },
    "rabbit": {
        "glow_outer": "#AAE1C8", "glow_inner": "#C4EBD7", "wall": "#DEF5E8",
        "floor": "#C8EBD7", "shadow": "#5A8269", "sparkle": "#FFFFFF",
    },
    "dead": {
        "glow_outer": "#7A7A7A", "glow_inner": "#9E9E9E", "wall": "#E0E0E0",
        "floor": "#CCCCCC", "shadow": "#4D4D4D", "sparkle": "#B0B0B0",
    },
}

class PetStage:
    def __init__(self, parent, bg_color, size=200):
        self.size = size
        self.canvas = tk.Canvas(parent, width=size, height=size, bg=bg_color, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.pet_image_item = None
        self._backdrop_ids = []

    def render_backdrop(self, species: str):
        for item_id in self._backdrop_ids:
            self.canvas.delete(item_id)
        self._backdrop_ids = []

        p = STAGE_PALETTES.get(species, STAGE_PALETTES["dog"])
        c = self.canvas
        cx, cy = self.size // 2, self.size // 2

        self._backdrop_ids.append(c.create_oval(cx - 95, cy - 95, cx + 95, cy + 95, fill=p["glow_outer"], outline="", stipple="gray12"))
        self._backdrop_ids.append(c.create_oval(cx - 70, cy - 70, cx + 70, cy + 70, fill=p["glow_inner"], outline="", stipple="gray25"))
        self._backdrop_ids.append(c.create_rectangle(15, 15, self.size - 15, self.size - 60, fill=p["wall"], outline=""))
        self._backdrop_ids.append(c.create_oval(20, self.size - 82, self.size - 20, self.size - 28, fill=p["floor"], outline=""))
        self._backdrop_ids.append(c.create_oval(cx - 48, self.size - 58, cx + 48, self.size - 30, fill=p["shadow"], outline="", stipple="gray50"))
        
        for sx, sy in [(32, 32), (self.size - 46, 46), (self.size - 36, 82)]:
            self._backdrop_ids.append(c.create_oval(sx, sy, sx + 8, sy + 8, fill=p["sparkle"], outline=""))

        if self.pet_image_item is not None:
            for item_id in self._backdrop_ids:
                c.tag_lower(item_id, self.pet_image_item)

    def draw_pet(self, photo_image):
        cx, cy = self.size // 2, self.size // 2 - 5
        if self.pet_image_item is None:
            self.pet_image_item = self.canvas.create_image(cx, cy, image=photo_image)
        else:
            self.canvas.itemconfig(self.pet_image_item, image=photo_image)
        self.canvas.image_ref = photo_image

class DashboardTemplate:    
    def __init__(self, root, username, coins, pet_data, thought_text, anim_state, callbacks):
        self.root = root
        self.username = username
        self.coins = coins
        self.pet_data = pet_data
        self.thought_text = thought_text
        self.anim_state = anim_state
        self.callbacks = callbacks
        
        self.animation_frames = []
        self.current_frame_index = 0
        self.animation_loop_id = None
        self.stage = None
        
        self.bg_app = "#FFF7F0"
        self.bg_card = "#FFFFFF"
        self.text_main = "#4A3F3F"
        self.text_muted = "#A89A9A"
        self.accent_color = "#FF9A9E"
        self.card_border = "#FFE3D3"

        self.status_healthy_bg = "#D4F4DD"
        self.status_healthy_fg = "#2F9E5C"
        self.status_alert_bg = "#FFD9D9"
        self.status_alert_fg = "#D64545"
        
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_subtitle = ("Segoe UI", 12, "italic")
        self.font_main = ("Segoe UI", 11, "bold")
        self.font_body = ("Segoe UI", 10)
        
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.configure(bg=self.bg_app)
        self.setup_progressbar_styles()
        self.build_scrollable_ui()

    def setup_progressbar_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        bar_configs = {
            "Health.Horizontal.TProgressbar": "#FF6B6B",
            "Hunger.Horizontal.TProgressbar": "#FFA94D",
            "Happiness.Horizontal.TProgressbar": "#69DB7C",
            "Energy.Horizontal.TProgressbar": "#74C0FC",
            "Alert.Horizontal.TProgressbar": "#FF6B6B",
        }
        for style_name, color in bar_configs.items():
            style.configure(style_name, troughcolor="#F1ECE7", background=color, bordercolor="#F1ECE7", 
                            lightcolor=color, darkcolor=color, thickness=18)

    def create_card(self, parent, pady=10):
        card = tk.Frame(parent, bg=self.bg_card, padx=20, pady=20, highlightbackground=self.card_border, highlightthickness=2)
        card.pack(fill="x", padx=15, pady=pady)
        return card

    def create_modern_button(self, parent, text, command, btn_color="#FFE5E5", hover_color="#FFB6C1"):
        def button_action():
            if btn['state'] != 'disabled':
                SoundManager.play_click()
                command()
        btn = tk.Button(parent, text=text, command=button_action, bg=btn_color, fg=self.text_main, 
                        font=self.font_main, relief="flat", cursor="hand2", pady=8)
        
        btn.bind("<Enter>", lambda e: e.widget.config(bg=hover_color) if btn['state'] != 'disabled' else None)
        btn.bind("<Leave>", lambda e: e.widget.config(bg=btn_color) if btn['state'] != 'disabled' else None)
        return btn

    def create_status_badge(self, parent, text, healthy=True):
        bg = self.status_healthy_bg if healthy else self.status_alert_bg
        fg = self.status_healthy_fg if healthy else self.status_alert_fg
        badge = tk.Label(parent, text=f"  ●  {text}  ", font=("Segoe UI", 9, "bold"), bg=bg, fg=fg, padx=4, pady=3)
        badge.pack(pady=(2, 10))
        return badge

    def build_scrollable_ui(self):
        self.canvas = tk.Canvas(self.root, bg=self.bg_app, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.main_frame = tk.Frame(self.canvas, bg=self.bg_app)
        
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        def configure_canvas_width(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind("<Configure>", configure_canvas_width)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        self.populate_content()

    def populate_content(self):
        header = tk.Frame(self.main_frame, bg=self.bg_app)
        header.pack(fill="x", padx=15, pady=(15, 0))
        tk.Label(header, text=f"Welcome, {self.username}", font=self.font_title, bg=self.bg_app, fg=self.text_main).pack(side="left")
        tk.Label(header, text=f"{self.coins} 💰", font=self.font_title, bg=self.bg_app, fg="#F39C12").pack(side="right")

        if self.pet_data:
            self.build_profile_card()
            self.build_vitals_card()
            if self.pet_data['status'] != 'dead':
                self.build_actions_card()
            else:
                death_card = self.create_card(self.main_frame)
                tk.Label(death_card, text="Your pet has passed away... 🪦", font=self.font_title, bg=self.bg_card, fg="#E74C3C").pack(pady=10)
                self.create_modern_button(death_card, "Adopt a New Pet", self.callbacks['adopt'], "#FFB7B2", "#FF9A9E").pack(fill="x")
        else:
            no_pet_card = self.create_card(self.main_frame)
            tk.Label(no_pet_card, text="You don't have a pet yet! 🥚", font=self.font_title, bg=self.bg_card, fg=self.text_main).pack(pady=20)
            self.create_modern_button(no_pet_card, "Adopt a Pet", self.callbacks['adopt'], "#E2F0CB", "#C5E1A5").pack(fill="x", pady=10)

        nav_card = tk.Frame(self.main_frame, bg=self.bg_app)
        nav_card.pack(fill="x", padx=15, pady=15)
        self.create_modern_button(nav_card, "🎒 Inventory", self.callbacks['inventory'], "#FFFFFF", "#F2F4F4").grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        self.create_modern_button(nav_card, "🏪 Shop", self.callbacks['shop'], "#FFFFFF", "#F2F4F4").grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        self.create_modern_button(nav_card, "🕊️ Memorial", self.callbacks['memorial'], "#FFFFFF", "#F2F4F4").grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        self.create_modern_button(nav_card, "Log Out", self.callbacks['logout'], "#FFFFFF", "#F2F4F4").grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        nav_card.grid_columnconfigure(0, weight=1)
        nav_card.grid_columnconfigure(1, weight=1)

        if self.pet_data and self.pet_data['status'] != 'dead':
            self.btn_debug = tk.Button(self.main_frame, text="[DEBUG] Fast Forward 24h", command=self.callbacks['debug'], bg=self.bg_app, fg=self.text_muted, relief="flat", font=self.font_body)
            self.btn_debug.pack(pady=20)

    def build_profile_card(self):
        profile_card = self.create_card(self.main_frame)
        tk.Label(profile_card, text=f"{self.pet_data['name']} the {self.pet_data['species']}", font=self.font_title, bg=self.bg_card, fg=self.text_main).pack()
        self.create_status_badge(profile_card, self.pet_data['status'].capitalize(), healthy=(self.pet_data['status'] == "healthy"))
        
        species = self.pet_data['species'].lower()
        self.animation_frames = []
        base_dir = f"assets/images/{species}"
        frames_to_load = 1 if self.anim_state == "dead" else 2
        
        for i in range(1, frames_to_load + 1): 
            # --- NEW: Use resource_path() here ---
            image_path = resource_path(f"{base_dir}/{self.anim_state}_{i}.png")
            if not os.path.exists(image_path):
                alt_path = f"{base_dir}/sick_1.png" if self.anim_state == "dead" else f"{base_dir}/idle_{i}.png"
                image_path = resource_path(alt_path)
            # -------------------------------------
                
            try:
                if os.path.exists(image_path):
                    img = Image.open(image_path).resize((150, 150), Image.Resampling.LANCZOS)
                    self.animation_frames.append(ImageTk.PhotoImage(img))
            except: pass
        
        self.stage = PetStage(profile_card, bg_color=self.bg_card)
        self.stage.render_backdrop("dead" if self.pet_data['status'] == "dead" else species)

        if self.animation_frames:
            self.stage.draw_pet(self.animation_frames[0])
            self.animate_pet()
        else:
            tk.Label(profile_card, text="( No Image )", width=20, height=5, bg="#F2F4F4").pack(pady=10)
        
        self.lbl_thought = tk.Label(profile_card, text=f'"{self.thought_text}"', font=self.font_subtitle, bg="#F8F9F9", fg=self.text_main, pady=10)
        if self.pet_data['status'] != 'dead':
            self.lbl_thought.pack(fill="x", pady=(5,0))

    def build_vitals_card(self):
        vitals_card = self.create_card(self.main_frame, pady=5)
        tk.Label(vitals_card, text="Vitals", font=self.font_main, bg=self.bg_card, fg=self.text_muted).pack(anchor="w", pady=(0, 10))
        grid_frame = tk.Frame(vitals_card, bg=self.bg_card)
        grid_frame.pack(fill="x")

        stats = [
            ("Health 💖", self.pet_data['health'], "Health.Horizontal.TProgressbar"),
            ("Hunger 🍖", self.pet_data['hunger'], "Hunger.Horizontal.TProgressbar"),
            ("Happiness 🎾", self.pet_data['happiness'], "Happiness.Horizontal.TProgressbar"),
            ("Energy ⚡", self.pet_data['energy'], "Energy.Horizontal.TProgressbar")
        ]
        for i, (label_text, value, style_name) in enumerate(stats):
            tk.Label(grid_frame, text=label_text, font=self.font_body, bg=self.bg_card, fg=self.text_main).grid(row=i, column=0, sticky="w", pady=2)
            effective_style = "Alert.Horizontal.TProgressbar" if value <= 20 else style_name
            bar = ttk.Progressbar(grid_frame, length=200, mode='determinate', style=effective_style)
            bar['value'] = value
            bar.grid(row=i, column=1, sticky="e", pady=2, padx=(10, 0))

    def build_actions_card(self):
        action_card = self.create_card(self.main_frame, pady=5)
        tk.Label(action_card, text="Interactions", font=self.font_main, bg=self.bg_card, fg=self.text_muted).pack(anchor="w", pady=(0, 10))
        
        self.btn_feed = self.create_modern_button(action_card, "Feed 🍱 (+30 Hunger, -5 Energy)", self.callbacks['feed'], "#E2F0CB", "#C5E1A5")
        self.btn_feed.pack(fill="x", pady=4)
        self.btn_play = self.create_modern_button(action_card, "Play 🪁 (+20 Happy, -15 Energy) [Find Coins!]", self.callbacks['play'], "#FFDEB4", "#FFCBA4")
        self.btn_play.pack(fill="x", pady=4)
        self.btn_rest = self.create_modern_button(action_card, "Rest 💤 (+40 Energy, -15 Hunger)", self.callbacks['rest'], "#C7CEEA", "#A8B4E5")
        self.btn_rest.pack(fill="x", pady=4)

    def animate_pet(self):
        if len(self.animation_frames) > 1:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
            self.stage.draw_pet(self.animation_frames[self.current_frame_index])
        self.animation_loop_id = self.root.after(500, self.animate_pet)

    def cancel_animation(self):
        if self.animation_loop_id:
            self.root.after_cancel(self.animation_loop_id)
            self.animation_loop_id = None

    def trigger_sleep(self):
        self.cancel_animation()
        self.lbl_thought.config(text='💭 "Zzz... 💤"', bg="#EAEDED")
        self.btn_feed.config(state="disabled", text="Shh... Sleeping", bg="#F2F4F4")
        self.btn_play.config(state="disabled", text="Shh... Sleeping", bg="#F2F4F4")
        self.btn_rest.config(state="disabled", text="Sleeping... ⏳", bg="#F2F4F4")
        if hasattr(self, 'btn_debug'): self.btn_debug.config(state="disabled")

        species = self.pet_data['species'].lower()
        
        # --- NEW: Use resource_path() here ---
        sleep_path = resource_path(f"assets/images/{species}/exhausted_2.png")
        if not os.path.exists(sleep_path):
            sleep_path = resource_path(f"assets/images/{species}/idle_2.png")
        # -------------------------------------
        
        try:
            if os.path.exists(sleep_path):
                img = Image.open(sleep_path).resize((150, 150), Image.Resampling.LANCZOS)
                self.sleep_photo = ImageTk.PhotoImage(img) # Save reference
                self.stage.draw_pet(self.sleep_photo)
        except Exception as e:
            print(f"[Image load failed] Sleep sprite: {e}")