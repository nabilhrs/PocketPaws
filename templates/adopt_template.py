import tkinter as tk
from tkinter import ttk
from utils.sound_manager import SoundManager

class AdoptTemplate:    
    def __init__(self, root, available_species, adopt_callback, back_callback):
        self.root = root
        self.available_species = available_species
        self.adopt_callback = adopt_callback
        self.back_callback = back_callback
        
        self.bg_app = "#FFF7F0"
        self.bg_card = "#FFFFFF"
        self.text_main = "#4A3F3F"
        self.text_muted = "#A89A9A"
        self.card_border = "#FFE3D3"
        
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_main = ("Segoe UI", 11, "bold")
        self.font_body = ("Segoe UI", 11)
        
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.configure(bg=self.bg_app)
        self.build_ui()

    def create_card(self, parent, pady=10):
        card = tk.Frame(parent, bg=self.bg_card, padx=30, pady=30, highlightbackground=self.card_border, highlightthickness=2)
        card.pack(padx=30, pady=pady, fill="x")
        return card

    def create_modern_button(self, parent, text, command, btn_color="#FFE5E5", hover_color="#FFB6C1"):
        def button_action():
            try: SoundManager.play_click()
            except: pass
            command()
            
        btn = tk.Button(parent, text=text, command=button_action, bg=btn_color, fg=self.text_main, 
                        font=self.font_main, relief="flat", cursor="hand2", pady=8)
        
        def on_enter(e):
            if btn['state'] != 'disabled': e.widget['background'] = hover_color
        def on_leave(e):
            if btn['state'] != 'disabled': e.widget['background'] = btn_color
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def build_ui(self):
        tk.Label(self.root, text="Adopt a Pet 🐾", font=self.font_title, bg=self.bg_app, fg=self.text_main).pack(pady=(40, 10))
        tk.Label(self.root, text="Give a loving home to a new friend!", font=("Segoe UI", 10, "italic"), bg=self.bg_app, fg=self.text_muted).pack(pady=(0, 20))

        card = self.create_card(self.root)

        tk.Label(card, text="Pet's Name:", font=self.font_main, bg=self.bg_card, fg=self.text_main).pack(anchor="w", pady=(0, 5))
        self.entry_name = tk.Entry(card, font=self.font_body, bg="#F8F9F9", fg=self.text_main, relief="flat", highlightbackground=self.card_border, highlightthickness=1)
        self.entry_name.pack(fill="x", pady=(0, 20), ipady=5)

        tk.Label(card, text="Select Species:", font=self.font_main, bg=self.bg_card, fg=self.text_main).pack(anchor="w", pady=(0, 5))
        
        default_val = self.available_species[0] if self.available_species else "Dog"
        self.species_var = tk.StringVar(value=default_val)
        style = ttk.Style()
        style.configure("TCombobox", padding=5)
        
        self.combo_species = ttk.Combobox(card, textvariable=self.species_var, values=self.available_species, state="readonly", font=self.font_body)
        self.combo_species.pack(fill="x", pady=(0, 30))

        self.create_modern_button(card, "Adopt Now 💖", self.adopt_callback, "#D4EFDF", "#A9DFBF").pack(fill="x", pady=(0, 15))
        self.create_modern_button(card, "⬅️ Back", self.back_callback, "#F2F4F4", "#E5E8E8").pack(fill="x")