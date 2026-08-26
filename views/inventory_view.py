from tkinter import messagebox
from datetime import datetime
from database import get_connection
from utils.sound_manager import SoundManager
from models.item import FoodItem, ToyItem, MedicineItem, EnergyItem, CharmItem
from models.pet import DogPet, CatPet, RabbitPet, CustomPet
from templates.inventory_template import InventoryTemplate

class InventoryView:    
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.user_id = None
        self.pet_obj = None
        self.inventory_items = []
        
        self.load_data()
        
        has_pet = bool(self.pet_obj)
        self.template = InventoryTemplate(
            self.root,
            has_pet=has_pet,
            inventory_items=self.inventory_items,
            use_callback=self.handle_use_item,
            back_callback=self.go_back
        )

    def load_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (self.username,))
        user = cursor.fetchone()
        if user:
            self.user_id = user['user_id']
            
            cursor.execute("SELECT * FROM pets WHERE owner_id = ? ORDER BY pet_id DESC LIMIT 1", (self.user_id,))
            pet_row = cursor.fetchone()
            if pet_row:
                try:
                    cursor.execute("SELECT hunger_rate, happy_rate, energy_rate FROM species WHERE name = ?", (pet_row['species'],))
                    species_data = cursor.fetchone()
                except Exception:
                    species_data = None
                
                if species_data:
                    self.pet_obj = CustomPet(
                        pet_row['pet_id'], pet_row['name'], pet_row['species'], pet_row['owner_id'], pet_row['birth_time'],
                        species_data['hunger_rate'], species_data['happy_rate'], species_data['energy_rate']
                    )
                else:
                    if pet_row['species'] == 'Cat':
                        self.pet_obj = CatPet(pet_row['pet_id'], pet_row['name'], pet_row['species'], pet_row['owner_id'], pet_row['birth_time'])
                    elif pet_row['species'] == 'Rabbit':
                        self.pet_obj = RabbitPet(pet_row['pet_id'], pet_row['name'], pet_row['species'], pet_row['owner_id'], pet_row['birth_time'])
                    else:
                        self.pet_obj = DogPet(pet_row['pet_id'], pet_row['name'], pet_row['species'], pet_row['owner_id'], pet_row['birth_time'])
                
                self.pet_obj.hunger = pet_row['hunger']
                self.pet_obj.happiness = pet_row['happiness']
                self.pet_obj.energy = pet_row['energy']
                self.pet_obj.health = pet_row['health']
                self.pet_obj.status = pet_row['status']

            cursor.execute("""
                SELECT inv.inventory_id, inv.quantity, it.* FROM inventory inv
                JOIN items it ON inv.item_id = it.item_id
                WHERE inv.user_id = ? AND inv.quantity > 0
            """, (self.user_id,))
            self.inventory_items = cursor.fetchall()
            
        conn.close()

    def handle_use_item(self, row):
        if self.pet_obj.status == 'dead':
            try: SoundManager.play_error()
            except: pass
            messagebox.showerror("Error", "You cannot use items on a pet that has passed away.")
            return
            
        if row['type'] == 'food':
            item = FoodItem(row['item_id'], row['name'], row['price'], row['effect_value'], row['description'])
            try: SoundManager.play_eat()
            except: pass
        elif row['type'] == 'toy':
            item = ToyItem(row['item_id'], row['name'], row['price'], row['effect_value'], row['description'])
        elif row['type'] == 'medicine':
            item = MedicineItem(row['item_id'], row['name'], row['price'], row['effect_value'], row['description'])
        elif row['type'] == 'energy':
            item = EnergyItem(row['item_id'], row['name'], row['price'], row['effect_value'], row['description'])
        elif row['type'] == 'charm':
            item = CharmItem(row['item_id'], row['name'], row['price'], row['effect_value'], row['description'])
        else:
            return
            
        item.use(self.pet_obj)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE pets 
            SET hunger = ?, happiness = ?, energy = ?, health = ?, status = ?, last_updated = ?
            WHERE pet_id = ?
        """, (self.pet_obj.hunger, self.pet_obj.happiness, self.pet_obj.energy, 
              self.pet_obj.health, self.pet_obj.status, current_time, self.pet_obj.pet_id))
              
        new_qty = row['quantity'] - 1
        if new_qty > 0:
            cursor.execute("UPDATE inventory SET quantity = ? WHERE inventory_id = ?", (new_qty, row['inventory_id']))
        else:
            cursor.execute("DELETE FROM inventory WHERE inventory_id = ?", (row['inventory_id'],))
            
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"You used the {row['name']}!")
        
        InventoryView(self.root, self.username)

    def go_back(self):
        from views.dashboard_view import DashboardView
        DashboardView(self.root, self.username)