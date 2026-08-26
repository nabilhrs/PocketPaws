import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from utils.sound_manager import SoundManager

class InventoryTemplate:    
    def __init__(self, root, has_pet, inventory_items, use_callback, back_callback):
        self.root = root
        self.has_pet = has_pet
        self.inventory_items = inventory_items
        self.use_callback = use_callback
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
        tk.Label(header, text="Backpack 🎒", font=self.font_title, bg=self.bg_app, fg=self.text_main).pack(side="left")

        if not self.has_pet:
            warning_card = self.create_card(self.main_frame)
            tk.Label(warning_card, text="You need to adopt a pet to use items!", font=self.font_main, bg=self.bg_card, fg="#D64545").pack(pady=10)
        elif not self.inventory_items:
            empty_card = self.create_card(self.main_frame)
            tk.Label(empty_card, text="Your inventory is empty.\nGo to the shop!", font=self.font_main, bg=self.bg_card, fg=self.text_muted).pack(pady=20)
        else:
            for row in self.inventory_items:
                card = self.create_card(self.main_frame)
                card.columnconfigure(1, weight=1) 
                
                img_name = row['name'].lower().replace(" ", "_") + ".png"
                img_path = f"assets/images/items/{img_name}"
                
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
                        bg_color = colors.get(row['type'], "#EEEEEE")
                        icon_label.config(text="📦", font=("Segoe UI", 24), bg=bg_color, width=3, height=1, relief="flat")
                except Exception:
                    pass
                
                tk.Label(card, text=f"{row['name']} (x{row['quantity']})", font=self.font_main, bg=self.bg_card, fg=self.text_main, anchor="w").grid(row=0, column=1, sticky="w")
                tk.Label(card, text=row['description'], font=self.font_body, bg=self.bg_card, fg=self.text_muted, anchor="w", wraplength=180, justify="left").grid(row=1, column=1, sticky="w")
                
                if row['type'] == 'charm':
                    btn = tk.Button(card, text="Activates automatically", bg="#F2F4F4", fg=self.text_muted, font=("Segoe UI", 9, "italic"), relief="flat", state="disabled")
                    btn.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky="e")
                else:
                    btn = self.create_modern_button(card, "Use", lambda r=row: self.use_callback(r), "#FFDEB4", "#FFCBA4")
                    btn.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky="e")

        nav_card = tk.Frame(self.main_frame, bg=self.bg_app)
        nav_card.pack(fill="x", padx=15, pady=20)
        self.create_modern_button(nav_card, "Back to Dashboard", self.back_callback, "#FFFFFF", "#F2F4F4").pack(fill="x")