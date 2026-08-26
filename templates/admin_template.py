import tkinter as tk
from tkinter import ttk
from utils.sound_manager import SoundManager

class AdminTemplate:
    """PURE UI - Draws the multi-tabbed admin panel, Treeviews, and data entry forms."""
    
    def __init__(self, root, username, stats_data, users_data, shop_data, species_data, callbacks):
        self.root = root
        self.username = username
        self.stats_data = stats_data
        self.users_data = users_data
        self.shop_data = shop_data
        self.species_data = species_data
        self.callbacks = callbacks 
        
        self.bg_app = "#ECF0F1"       
        self.bg_card = "#FFFFFF"
        self.text_main = "#2C3E50"    
        self.text_muted = "#7F8C8D"
        self.card_border = "#BDC3C7"
        self.admin_accent = "#2980B9" 
        self.danger_color = "#E74C3C" 
        
        self.font_title = ("Segoe UI", 18, "bold")
        self.font_subtitle = ("Segoe UI", 12, "italic")
        self.font_main = ("Segoe UI", 11, "bold")
        self.font_body = ("Segoe UI", 10)
        
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.configure(bg=self.bg_app)
        self.setup_styles()
        self.build_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=self.bg_app, borderwidth=0)
        style.configure("TNotebook.Tab", background="#D5DBDB", foreground=self.text_main, font=self.font_main, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.bg_card)], foreground=[("selected", self.admin_accent)])

    def create_card(self, parent, pady=10):
        card = tk.Frame(parent, bg=self.bg_card, padx=20, pady=20, highlightbackground=self.card_border, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=pady)
        return card

    def create_modern_button(self, parent, text, command, btn_color="#D6EAF8", hover_color="#AED6F1", text_color=None):
        fg_color = text_color if text_color else self.text_main
        def button_action():
            try: SoundManager.play_click()
            except: pass
            command()
            
        btn = tk.Button(parent, text=text, command=button_action, bg=btn_color, fg=fg_color, font=self.font_main, relief="flat", cursor="hand2", pady=8, padx=10)
        btn.bind("<Enter>", lambda e: e.widget.config(background=hover_color) if btn['state'] != 'disabled' else None)
        btn.bind("<Leave>", lambda e: e.widget.config(background=btn_color) if btn['state'] != 'disabled' else None)
        return btn

    def build_ui(self):
        header_frame = tk.Frame(self.root, bg=self.bg_app)
        header_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        tk.Label(header_frame, text="Admin Control Panel ⚙️", font=self.font_title, bg=self.bg_app, fg=self.admin_accent).pack(side="left")
        self.create_modern_button(header_frame, "Log Out", self.callbacks['logout'], "#F2F4F4", "#E5E8E8").pack(side="right")
        tk.Label(self.root, text=f"Logged in as: {self.username}", font=self.font_subtitle, bg=self.bg_app, fg=self.text_muted).pack(anchor="w", padx=20)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        tab_stats = tk.Frame(notebook, bg=self.bg_app)
        tab_users = tk.Frame(notebook, bg=self.bg_app)
        tab_shop = tk.Frame(notebook, bg=self.bg_app)
        tab_species = tk.Frame(notebook, bg=self.bg_app)

        notebook.add(tab_stats, text="  📊 System Stats  ")
        notebook.add(tab_users, text="  👥 Users & Pets  ")
        notebook.add(tab_shop, text="  🏪 Shop Manager  ")
        notebook.add(tab_species, text="  🐕 Species Manager  ")

        self.build_stats_tab(tab_stats)
        self.build_users_tab(tab_users)
        self.build_shop_tab(tab_shop)
        self.build_species_tab(tab_species)

    def build_stats_tab(self, frame):
        card = self.create_card(frame)
        tk.Label(card, text="Global Server Data", font=self.font_title, bg=self.bg_card, fg=self.text_main).pack(pady=(0, 10))
        
        for label, value in self.stats_data.items():
            row = tk.Frame(card, bg=self.bg_card)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=self.font_main, bg=self.bg_card, fg=self.text_muted).pack(side="left")
            tk.Label(row, text=str(value), font=self.font_main, bg=self.bg_card, fg=self.text_main).pack(side="right")

        tk.Label(card, text="Global Actions (Affects All Users)", font=self.font_main, bg=self.bg_card, fg=self.text_main).pack(pady=(25, 10))
        btn_frame = tk.Frame(card, bg=self.bg_card)
        btn_frame.pack(fill="x")
        self.create_modern_button(btn_frame, "🎁 Gift 50 Coins to All", self.callbacks['global_gift'], "#D4EFDF", "#A9DFBF").pack(side="left", expand=True, fill="x", padx=5)
        self.create_modern_button(btn_frame, "💖 Heal All Living Pets", self.callbacks['global_heal'], "#D4EFDF", "#A9DFBF").pack(side="right", expand=True, fill="x", padx=5)

    def build_users_tab(self, frame):
        card = self.create_card(frame)
        tk.Label(card, text="Player Database & Moderation", font=self.font_title, bg=self.bg_card, fg=self.text_main).pack(pady=(0, 10))
        
        columns = ("User", "Coins", "Pet ID", "Pet Name", "Species", "Health", "Status")
        self.tree_users = ttk.Treeview(card, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree_users.heading(col, text=col)
            w = 50 if col in ("Coins", "Health", "Pet ID") else 90
            self.tree_users.column(col, anchor="center", width=w)
            
        self.tree_users.pack(fill="both", expand=True, pady=5)
        
        for row in self.users_data:
            self.tree_users.insert("", "end", values=row)
            
        btn_frame = tk.Frame(card, bg=self.bg_card)
        btn_frame.pack(fill="x", pady=5)
        
        def on_modify():
            selected = self.tree_users.selection()
            if selected: self.callbacks['modify_coins'](self.tree_users.item(selected[0])['values'])
            else: self.callbacks['on_no_selection']()

        def on_intervene():
            selected = self.tree_users.selection()
            if selected: self.callbacks['intervene'](self.tree_users.item(selected[0])['values'])
            else: self.callbacks['on_no_selection']()

        def on_delete():
            selected = self.tree_users.selection()
            if selected: self.callbacks['delete_user'](self.tree_users.item(selected[0])['values'])
            else: self.callbacks['on_no_selection']()

        self.create_modern_button(btn_frame, "💰 Modify Balance", on_modify, "#D4EFDF", "#A9DFBF").pack(side="left", padx=2)
        self.create_modern_button(btn_frame, "💖 Intervene", on_intervene, "#FCF3CF", "#F9E79F").pack(side="left", padx=2)
        self.create_modern_button(btn_frame, "🔨 Delete User", on_delete, "#FADBD8", "#F5B7B1", text_color=self.danger_color).pack(side="right", padx=2)

    def build_shop_tab(self, frame):
        table_card = tk.Frame(frame, bg=self.bg_card, padx=15, pady=10, highlightbackground=self.card_border, highlightthickness=1)
        table_card.pack(fill="both", expand=True, padx=20, pady=(10, 5))
        
        tk.Label(table_card, text="Shop Inventory Database", font=self.font_title, bg=self.bg_card, fg=self.text_main).pack(pady=(0, 5))
        
        columns = ("ID", "Name", "Type", "Species", "Price", "Effect", "Desc")
        self.tree_shop = ttk.Treeview(table_card, columns=columns, show="headings", height=5)
        for col in columns:
            self.tree_shop.heading(col, text=col)
            w = 30 if col == "ID" else 80 if col in ("Price", "Effect") else 100
            self.tree_shop.column(col, anchor="center", width=w)
        
        self.tree_shop.pack(fill="both", expand=True)
        self.tree_shop.bind("<<TreeviewSelect>>", self.on_shop_item_select)
        
        for item in self.shop_data:
            self.tree_shop.insert("", "end", values=item)
            
        form_card = tk.Frame(frame, bg=self.bg_card, padx=15, pady=15, highlightbackground=self.card_border, highlightthickness=1)
        form_card.pack(fill="x", padx=20, pady=(5, 10))
        
        self.selected_item_id = None
        form_grid = tk.Frame(form_card, bg=self.bg_card)
        form_grid.pack()
        
        tk.Label(form_grid, text="Name:", font=self.font_body, bg=self.bg_card).grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entry_item_name = tk.Entry(form_grid, width=20)
        self.entry_item_name.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(form_grid, text="Type:", font=self.font_body, bg=self.bg_card).grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.type_var = tk.StringVar(value="food")
        ttk.Combobox(form_grid, textvariable=self.type_var, values=["food", "toy", "medicine", "energy", "charm"], state="readonly", width=17).grid(row=0, column=3, padx=5, pady=2)
        
        tk.Label(form_grid, text="Price:", font=self.font_body, bg=self.bg_card).grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entry_item_price = tk.Entry(form_grid, width=20)
        self.entry_item_price.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Label(form_grid, text="Species:", font=self.font_body, bg=self.bg_card).grid(row=1, column=2, sticky="e", padx=5, pady=2)
        self.species_var = tk.StringVar(value="Any")
        ttk.Combobox(form_grid, textvariable=self.species_var, values=["Any", "Dog", "Cat", "Rabbit"], state="readonly", width=17).grid(row=1, column=3, padx=5, pady=2)
        
        tk.Label(form_grid, text="Effect:", font=self.font_body, bg=self.bg_card).grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.entry_item_effect = tk.Entry(form_grid, width=20)
        self.entry_item_effect.grid(row=2, column=1, padx=5, pady=2)
        
        tk.Label(form_grid, text="Desc:", font=self.font_body, bg=self.bg_card).grid(row=2, column=2, sticky="e", padx=5, pady=2)
        self.entry_item_desc = tk.Entry(form_grid, width=20)
        self.entry_item_desc.grid(row=2, column=3, padx=5, pady=2)
        
        def get_form_data():
            return {
                "name": self.entry_item_name.get(),
                "type": self.type_var.get(),
                "species": self.species_var.get(),
                "price": self.entry_item_price.get(),
                "effect": self.entry_item_effect.get(),
                "desc": self.entry_item_desc.get()
            }

        btn_frame = tk.Frame(form_card, bg=self.bg_card)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        self.create_modern_button(btn_frame, "➕ Add New", lambda: self.callbacks['shop_add'](get_form_data()), "#D4EFDF", "#A9DFBF").pack(side="left", expand=True, fill="x", padx=2)
        self.create_modern_button(btn_frame, "💾 Update Selected", lambda: self.callbacks['shop_update'](self.selected_item_id, get_form_data()), "#FCF3CF", "#F9E79F").pack(side="left", expand=True, fill="x", padx=2)
        self.create_modern_button(btn_frame, "🗑️ Delete Selected", lambda: self.callbacks['shop_delete'](self.selected_item_id), "#FADBD8", "#F5B7B1", text_color=self.danger_color).pack(side="left", expand=True, fill="x", padx=2)
        self.create_modern_button(btn_frame, "Clear Form", self.clear_shop_form, "#F2F4F4", "#E5E8E8").pack(side="right", padx=5)

    def on_shop_item_select(self, event):
        selected = self.tree_shop.selection()
        if not selected: return
        values = self.tree_shop.item(selected[0])['values']
        
        self.selected_item_id = values[0]
        self.entry_item_name.delete(0, tk.END)
        self.entry_item_name.insert(0, values[1])
        self.type_var.set(values[2].lower())
        self.species_var.set(values[3])
        self.entry_item_price.delete(0, tk.END)
        self.entry_item_price.insert(0, values[4])
        self.entry_item_effect.delete(0, tk.END)
        self.entry_item_effect.insert(0, values[5])
        self.entry_item_desc.delete(0, tk.END)
        self.entry_item_desc.insert(0, values[6])

    def clear_shop_form(self):
        self.selected_item_id = None
        self.entry_item_name.delete(0, tk.END)
        self.type_var.set("food")
        self.species_var.set("Any")
        self.entry_item_price.delete(0, tk.END)
        self.entry_item_effect.delete(0, tk.END)
        self.entry_item_desc.delete(0, tk.END)
        for item in self.tree_shop.selection():
            self.tree_shop.selection_remove(item)

    def build_species_tab(self, frame):
        table_card = tk.Frame(frame, bg=self.bg_card, padx=15, pady=10, highlightbackground=self.card_border, highlightthickness=1)
        table_card.pack(fill="both", expand=True, padx=20, pady=(10, 5))
        
        tk.Label(table_card, text="Adoptable Species Database", font=self.font_title, bg=self.bg_card, fg=self.text_main).pack(pady=(0, 5))
        
        columns = ("Species Name", "Hunger Decay Rate", "Happiness Decay Rate", "Energy Decay Rate")
        self.tree_species = ttk.Treeview(table_card, columns=columns, show="headings", height=5)
        for col in columns:
            self.tree_species.heading(col, text=col)
            self.tree_species.column(col, anchor="center", width=120)
        
        self.tree_species.pack(fill="both", expand=True)
        self.tree_species.bind("<<TreeviewSelect>>", self.on_species_select)
        
        for item in self.species_data:
            self.tree_species.insert("", "end", values=item)
            
        form_card = tk.Frame(frame, bg=self.bg_card, padx=15, pady=15, highlightbackground=self.card_border, highlightthickness=1)
        form_card.pack(fill="x", padx=20, pady=(5, 10))
        
        self.selected_species_name = None
        form_grid = tk.Frame(form_card, bg=self.bg_card)
        form_grid.pack()
        
        tk.Label(form_grid, text="Species Name:", font=self.font_body, bg=self.bg_card).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_species_name = tk.Entry(form_grid, width=20)
        self.entry_species_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_grid, text="Hunger Rate:", font=self.font_body, bg=self.bg_card).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.entry_hunger_rate = tk.Entry(form_grid, width=20)
        self.entry_hunger_rate.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_grid, text="Happy Rate:", font=self.font_body, bg=self.bg_card).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_happy_rate = tk.Entry(form_grid, width=20)
        self.entry_happy_rate.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_grid, text="Energy Rate:", font=self.font_body, bg=self.bg_card).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_energy_rate = tk.Entry(form_grid, width=20)
        self.entry_energy_rate.grid(row=1, column=3, padx=5, pady=5)
        
        def get_species_data():
            return {
                "name": self.entry_species_name.get(),
                "hunger_rate": self.entry_hunger_rate.get(),
                "happy_rate": self.entry_happy_rate.get(),
                "energy_rate": self.entry_energy_rate.get()
            }

        btn_frame = tk.Frame(form_card, bg=self.bg_card)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        self.create_modern_button(btn_frame, "➕ Add New Species", lambda: self.callbacks['species_add'](get_species_data()), "#D4EFDF", "#A9DFBF").pack(side="left", expand=True, fill="x", padx=2)
        self.create_modern_button(btn_frame, "💾 Update Selected", lambda: self.callbacks['species_update'](self.selected_species_name, get_species_data()), "#FCF3CF", "#F9E79F").pack(side="left", expand=True, fill="x", padx=2)
        self.create_modern_button(btn_frame, "🗑️ Delete Selected", lambda: self.callbacks['species_delete'](self.selected_species_name), "#FADBD8", "#F5B7B1", text_color=self.danger_color).pack(side="left", expand=True, fill="x", padx=2)
        self.create_modern_button(btn_frame, "Clear Form", self.clear_species_form, "#F2F4F4", "#E5E8E8").pack(side="right", padx=5)

    def on_species_select(self, event):
        selected = self.tree_species.selection()
        if not selected: return
        values = self.tree_species.item(selected[0])['values']
        
        self.selected_species_name = values[0]
        self.entry_species_name.delete(0, tk.END)
        self.entry_species_name.insert(0, values[0])
        self.entry_hunger_rate.delete(0, tk.END)
        self.entry_hunger_rate.insert(0, values[1])
        self.entry_happy_rate.delete(0, tk.END)
        self.entry_happy_rate.insert(0, values[2])
        self.entry_energy_rate.delete(0, tk.END)
        self.entry_energy_rate.insert(0, values[3])

    def clear_species_form(self):
        self.selected_species_name = None
        self.entry_species_name.delete(0, tk.END)
        self.entry_hunger_rate.delete(0, tk.END)
        self.entry_happy_rate.delete(0, tk.END)
        self.entry_energy_rate.delete(0, tk.END)
        for item in self.tree_species.selection():
            self.tree_species.selection_remove(item)