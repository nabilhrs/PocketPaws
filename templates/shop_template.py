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
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# ---------------------------------------------------

class ShopTemplate:    
    def __init__(self, root, coins, pet_species, items, buy_callback, back_callback):
        self.root = root
        self.coins = coins
        self.pet_species = pet_species
        self.items = items
        self.buy_callback = buy_callback
        self.back_callback = back_callback
        
        self.bg_app = "#FFF7F0"       
        self.bg_card = "#FFFFFF"      
        self.text_main = "#4A3F3F"    
        self.text_muted = "#A89A9A"   
        self.card_border = "#FFE3D3"  
        
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_main = ("Segoe UI", 11, "bold")
        self.font_body = ("Segoe UI", 10)
        
        self.item_images = [] 
        
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.configure(bg=self.bg_app)
        self.build_scrollable_ui()

    def create_card(self, parent, pady=5):
        card = tk.Frame(parent, bg=self.bg_card, padx=15, pady=15, highlightbackground=self.card_border, highlightthickness=2)
        card.pack(fill="x", padx=15, pady=pady)
        return card

    def create_modern_button(self, parent, text, command, btn_color="#FFE5E5", hover_color="#FFB6C1", state="normal"):
        def button_action():
            try: SoundManager.play_click()
            except: pass
            command()
            
        btn = tk.Button(parent, text=text, command=button_action, bg=btn_color, fg=self.text_main, 
                        font=self.font_main, relief="flat", cursor="hand2", pady=8, state=state)
        
        def on_enter(e):
            if btn['state'] != 'disabled': e.widget['background'] = hover_color
        def on_leave(e):
            if btn['state'] != 'disabled': e.widget['background'] = btn_color
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

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

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.populate_content()

    def populate_content(self):
        header = tk.Frame(self.main_frame, bg=self.bg_app)
        header.pack(fill="x", padx=15, pady=(15, 10))
        tk.Label(header, text="Item Shop 🏪", font=self.font_title, bg=self.bg_app, fg=self.text_main).pack(side="left")
        tk.Label(header, text=f"{self.coins} 💰", font=self.font_title, bg=self.bg_app, fg="#F39C12").pack(side="right")

        if not self.pet_species:
            warning_card = self.create_card(self.main_frame)
            tk.Label(warning_card, text="Adopt a pet first to see tailored items!", font=self.font_main, bg=self.bg_card, fg="#D64545").pack(pady=5)

        if not self.items:
            empty_card = self.create_card(self.main_frame)
            tk.Label(empty_card, text="Nothing available right now.\nCheck back later!", font=self.font_main, bg=self.bg_card, fg=self.text_muted).pack(pady=20)
        else:
            for item in self.items:
                card = self.create_card(self.main_frame)
                card.columnconfigure(1, weight=1) 
                
                img_name = item['name'].lower().replace(" ", "_") + ".png"
                
                # --- NEW: Use resource_path() here ---
                img_path = resource_path(f"assets/images/items/{img_name}")
                # -------------------------------------
                
                icon_label = tk.Label(card, bg=self.bg_card)
                icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 15))
                
                try:
                    if os.path.exists(img_path):
                        img = Image.open(img_path).resize((50, 50), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        icon_label.config(image=photo)
                        self.item_images.append(photo)
                    else:
                        colors = {"food": "#E2F0CB", "toy": "#FFDEB4", "medicine": "#FFB7B2", "energy": "#C7CEEA", "charm": "#F3E5AB"}
                        bg_color = colors.get(item['type'], "#EEEEEE")
                        icon_label.config(text="📦", font=("Segoe UI", 24), bg=bg_color, width=3, height=1, relief="flat")
                except Exception:
                    pass
                
                header_text = f"{item['name']} ({item['type'].capitalize()})"
                tk.Label(card, text=header_text, font=self.font_main, bg=self.bg_card, fg=self.text_main, anchor="w").grid(row=0, column=1, sticky="w")
                tk.Label(card, text=item['description'], font=self.font_body, bg=self.bg_card, fg=self.text_muted, anchor="w", wraplength=200, justify="left").grid(row=1, column=1, sticky="w")
                
                can_afford = self.coins >= item['price']
                btn_state = "normal" if can_afford else "disabled"
                btn_bg = "#E2F0CB" if can_afford else "#F2F4F4"
                btn_hover = "#C5E1A5" if can_afford else "#F2F4F4"
                
                btn_text = f"{item['price']} 💰"
                btn = self.create_modern_button(card, btn_text, lambda i=item: self.buy_callback(i), btn_bg, btn_hover, state=btn_state)
                btn.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky="e")

        nav_card = tk.Frame(self.main_frame, bg=self.bg_app)
        nav_card.pack(fill="x", padx=15, pady=20)
        self.create_modern_button(nav_card, "Back to Dashboard", self.back_callback, "#FFFFFF", "#F2F4F4").pack(fill="x")