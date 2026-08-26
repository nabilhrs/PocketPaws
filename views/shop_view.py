from tkinter import messagebox
from database import get_connection
from utils.sound_manager import SoundManager
from templates.shop_template import ShopTemplate

class ShopView:    
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.user_id = None
        self.coins = 0
        self.items = []
        self.pet_species = None
        
        self.seed_items_if_empty()
        self.load_data()
        
        self.template = ShopTemplate(
            self.root, 
            coins=self.coins, 
            pet_species=self.pet_species, 
            items=self.items, 
            buy_callback=self.handle_buy, 
            back_callback=self.go_back
        )

    def seed_items_if_empty(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM items")
        if cursor.fetchone()['count'] == 0:
            default_items = [
                ("Meaty Chew", "food", "Dog", 15, 40, "Restores 40 Hunger, +5 Happiness"),
                ("Tuna Treat", "food", "Cat", 15, 40, "Restores 40 Hunger, +5 Happiness"),
                ("Carrot Stick", "food", "Rabbit", 15, 40, "Restores 40 Hunger, +5 Happiness"),
                ("Squeaky Bone", "toy", "Dog", 15, 35, "Restores 35 Happiness (No Energy cost)"),
                ("Yarn Ball", "toy", "Cat", 15, 35, "Restores 35 Happiness (No Energy cost)"),
                ("Willow Ball", "toy", "Rabbit", 15, 35, "Restores 35 Happiness (No Energy cost)"),
                ("Antibiotics", "medicine", "Any", 25, 60, "Cures sickness and restores 60 Health"),
                ("Energy Drink", "energy", "Any", 20, 50, "Instantly restores 50 Energy"),
                ("Revival Charm", "charm", "Any", 50, 30, "Prevents death automatically. Single use.")
            ]
            cursor.executemany("""
                INSERT INTO items (name, type, species, price, effect_value, description) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, default_items)
            conn.commit()
        conn.close()

    def load_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, coins FROM users WHERE username = ?", (self.username,))
        user = cursor.fetchone()
        if user:
            self.user_id = user['user_id']
            self.coins = user['coins']
            
            cursor.execute("SELECT species FROM pets WHERE owner_id = ? ORDER BY pet_id DESC LIMIT 1", (self.user_id,))
            pet_row = cursor.fetchone()
            if pet_row:
                self.pet_species = pet_row['species']
            
            if self.pet_species:
                cursor.execute("SELECT * FROM items WHERE species = ? OR species = 'Any'", (self.pet_species,))
            else:
                cursor.execute("SELECT * FROM items")
                
            self.items = cursor.fetchall()
            
        conn.close()

    def handle_buy(self, item):
        if self.coins < item['price']:
            SoundManager.play_error()
            messagebox.showerror("Error", "You don't have enough coins for this!")
            return
            
        SoundManager.play_coin()
        conn = get_connection()
        cursor = conn.cursor()
        
        new_balance = self.coins - item['price']
        cursor.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, self.user_id))
        
        cursor.execute("SELECT inventory_id FROM inventory WHERE user_id = ? AND item_id = ?", (self.user_id, item['item_id']))
        existing_item = cursor.fetchone()
        
        if existing_item:
            cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE inventory_id = ?", (existing_item['inventory_id'],))
        else:
            cursor.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, 1)", (self.user_id, item['item_id']))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"You bought {item['name']}!")
        
        ShopView(self.root, self.username)

    def go_back(self):
        from views.dashboard_view import DashboardView
        DashboardView(self.root, self.username)