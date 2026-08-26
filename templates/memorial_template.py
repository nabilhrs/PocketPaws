import tkinter as tk
from tkinter import ttk
from utils.sound_manager import SoundManager

class MemorialTemplate:    
    def __init__(self, root, pets_data, back_callback):
        self.root = root
        self.pets_data = pets_data
        self.back_callback = back_callback
        
        self.bg_app = "#FFF7F0"
        self.bg_card = "#FFFFFF"
        self.text_main = "#4A3F3F"
        self.text_muted = "#A89A9A"
        self.card_border = "#FFE3D3"
        
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_subtitle = ("Segoe UI", 12, "italic")
        self.font_main = ("Segoe UI", 12, "bold")
        self.font_body = ("Segoe UI", 10)
        self.accent_color = "#FF9A9E"
        
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.configure(bg=self.bg_app)
        self.build_scrollable_ui()

    def create_card(self, parent, pady=10):
        card = tk.Frame(parent, bg=self.bg_card, padx=20, pady=15, highlightbackground=self.card_border, highlightthickness=2)
        card.pack(fill="x", pady=pady)
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

    def build_scrollable_ui(self):
        tk.Label(self.root, text="Pet Memorial 🕊️", font=self.font_title, bg=self.bg_app, fg=self.text_main).pack(pady=(25, 5))
        tk.Label(self.root, text="Gone but not forgotten...", font=self.font_subtitle, bg=self.bg_app, fg=self.text_muted).pack(pady=(0, 15))
        
        self.canvas = tk.Canvas(self.root, bg=self.bg_app, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.main_frame = tk.Frame(self.canvas, bg=self.bg_app)
        
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        def configure_canvas_width(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind("<Configure>", configure_canvas_width)

        self.canvas.pack(side="top", fill="both", expand=True, padx=20)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.populate_content()

    def populate_content(self):
        if not self.pets_data:
            card = self.create_card(self.main_frame)
            tk.Label(card, text="You have no deceased pets. Great job! 💖", fg="#2F9E5C", bg=self.bg_card, font=self.font_main).pack(pady=20)
        else:
            for pet in self.pets_data:
                pet_card = self.create_card(self.main_frame, pady=5)
                
                header_text = f"{pet['name']} the {pet['species']} 🪦"
                tk.Label(pet_card, text=header_text, font=self.font_main, bg=self.bg_card, fg=self.text_main).pack(anchor="w")
                
                details = f"Lived for: {pet['duration']}\nCause of passing: {pet['cause']}\nDate: {pet['date']}"
                tk.Label(pet_card, text=details, justify="left", font=self.font_body, bg=self.bg_card, fg=self.text_muted).pack(anchor="w", pady=(5,5))
                
                tk.Label(pet_card, text=f'"{pet["quote"]}"', font=self.font_subtitle, bg=self.bg_card, fg=self.accent_color).pack(anchor="w")

        btn_frame = tk.Frame(self.root, bg=self.bg_app)
        btn_frame.pack(fill="x", padx=40, pady=20)
        self.create_modern_button(btn_frame, "Back to Dashboard", self.back_callback, "#FFFFFF", "#F2F4F4").pack(fill="x")