import tkinter as tk
from utils.sound_manager import SoundManager

class RegisterTemplate:    
    def __init__(self, root, register_callback, back_callback):
        self.root = root
        self.register_callback = register_callback
        self.back_callback = back_callback
        
        self.bg_app = "#FFF7F0"
        self.bg_card = "#FFFFFF"
        self.text_main = "#4A3F3F"
        self.card_border = "#FFE3D3"
        
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_main = ("Segoe UI", 11, "bold")
        self.font_body = ("Segoe UI", 11)
        
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.configure(bg=self.bg_app)
        self.build_ui()

    def create_card(self, parent, pady=10):
        card = tk.Frame(parent, bg=self.bg_card, padx=30, pady=35, highlightbackground=self.card_border, highlightthickness=2)
        card.pack(padx=30, pady=pady)
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
        tk.Label(self.root, text="Create an Account", font=self.font_title, bg=self.bg_app, fg=self.text_main).pack(pady=(40, 10))

        card = self.create_card(self.root)

        tk.Label(card, text="Username:", font=self.font_main, bg=self.bg_card, fg=self.text_main).pack(anchor="w", pady=(0, 5))
        self.entry_username = tk.Entry(card, font=self.font_body, bg="#F8F9F9", fg=self.text_main, relief="flat", highlightbackground=self.card_border, highlightthickness=1)
        self.entry_username.pack(fill="x", pady=(0, 15), ipady=5)

        tk.Label(card, text="Password:", font=self.font_main, bg=self.bg_card, fg=self.text_main).pack(anchor="w", pady=(0, 5))
        self.entry_password = tk.Entry(card, show="●", font=self.font_body, bg="#F8F9F9", fg=self.text_main, relief="flat", highlightbackground=self.card_border, highlightthickness=1)
        self.entry_password.pack(fill="x", pady=(0, 15), ipady=5)

        tk.Label(card, text="Confirm Password:", font=self.font_main, bg=self.bg_card, fg=self.text_main).pack(anchor="w", pady=(0, 5))
        self.entry_confirm = tk.Entry(card, show="●", font=self.font_body, bg="#F8F9F9", fg=self.text_main, relief="flat", highlightbackground=self.card_border, highlightthickness=1)
        self.entry_confirm.pack(fill="x", pady=(0, 25), ipady=5)

        self.create_modern_button(card, "Register 🎉", self.register_callback, "#D4EFDF", "#A9DFBF").pack(fill="x", pady=(0, 15))
        self.create_modern_button(card, "⬅️ Back to Login", self.back_callback, "#F2F4F4", "#E5E8E8").pack(fill="x")