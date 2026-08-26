from tkinter import messagebox, simpledialog
import os
from database import get_connection
from templates.admin_template import AdminTemplate

class AdminView:    
    def __init__(self, root, username):
        self.root = root
        self.username = username
        
        self.root.geometry("1000x700")
        self.root.minsize(1000, 700)
        
        self.ensure_species_table()
        
        stats = self.fetch_stats()
        users = self.fetch_users()
        shop_items = self.fetch_shop_items()
        species_data = self.fetch_species()
        
        callbacks = {
            'logout': self.logout,
            'global_gift': self.global_gift_coins,
            'global_heal': self.global_heal_pets,
            'modify_coins': self.admin_modify_coins,
            'intervene': self.admin_heal_pet,
            'delete_user': self.admin_delete_user,
            'shop_add': self.add_shop_item,
            'shop_update': self.update_shop_item,
            'shop_delete': self.delete_shop_item,
            'species_add': self.add_species,
            'species_update': self.update_species,
            'species_delete': self.delete_species,
            'on_no_selection': lambda: messagebox.showwarning("Select Row", "Please select an item from the list first.")
        }
        
        self.template = AdminTemplate(self.root, self.username, stats, users, shop_items, species_data, callbacks)

    def ensure_species_table(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS species (
                            name TEXT PRIMARY KEY,
                            hunger_rate FLOAT,
                            happy_rate FLOAT,
                            energy_rate FLOAT
                          )''')
        cursor.execute("SELECT COUNT(*) as c FROM species")
        if cursor.fetchone()['c'] == 0:
            default_species = [
                ('Dog', 1.5, 2.5, 1.0),
                ('Cat', 2.0, 1.0, 1.5),
                ('Rabbit', 3.0, 1.5, 3.0)
            ]
            cursor.executemany("INSERT INTO species VALUES (?, ?, ?, ?)", default_species)
            conn.commit()
        conn.close()

    def fetch_species(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, hunger_rate, happy_rate, energy_rate FROM species")
        data = [(r['name'], r['hunger_rate'], r['happy_rate'], r['energy_rate']) for r in cursor.fetchall()]
        conn.close()
        return data

    def fetch_stats(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as c FROM users WHERE role = 'player'")
        players = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) as c FROM pets")
        pets = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) as c FROM pets WHERE status = 'dead'")
        dead = cursor.fetchone()['c']
        cursor.execute("SELECT SUM(coins) as c FROM users WHERE role = 'player'")
        economy = cursor.fetchone()['c'] or 0
        conn.close()
        
        return {
            "Total Registered Players:": players,
            "Total Pets Adopted:": pets,
            "Total Pets Deceased:": dead,
            "Total Coins in Economy:": f"{economy} 💰"
        }

    def fetch_users(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, u.coins, p.pet_id, p.name, p.species, p.health, p.status 
            FROM users u LEFT JOIN pets p ON u.user_id = p.owner_id
            WHERE u.role = 'player' ORDER BY u.username, p.pet_id DESC
        """)
        
        data = []
        for row in cursor.fetchall():
            pet_id = row['pet_id'] if row['pet_id'] else "-"
            pet_name = row['name'] if row['name'] else "No Pet"
            species = row['species'] if row['species'] else "-"
            health = f"{int(row['health'])}%" if row['health'] is not None else "-"
            status = row['status'].capitalize() if row['status'] else "-"
            data.append((row['username'], row['coins'], pet_id, pet_name, species, health, status))
        conn.close()
        return data

    def fetch_shop_items(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item_id, name, type, species, price, effect_value, description FROM items")
        data = [(r['item_id'], r['name'], r['type'].capitalize(), r['species'], r['price'], r['effect_value'], r['description']) for r in cursor.fetchall()]
        conn.close()
        return data

    def reload_view(self):
        AdminView(self.root, self.username)

    def global_gift_coins(self):
        if messagebox.askyesno("Confirm Global Gift", "Add 50 coins to every player's wallet?"):
            conn = get_connection()
            conn.execute("UPDATE users SET coins = coins + 50 WHERE role = 'player'")
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "50 coins distributed to all players!")
            self.reload_view()

    def global_heal_pets(self):
        if messagebox.askyesno("Confirm Global Heal", "Restore Health, Hunger, Energy, and Happiness to 100% for all LIVING pets?"):
            conn = get_connection()
            conn.execute("UPDATE pets SET health=100, hunger=100, happiness=100, energy=100, status='healthy' WHERE status != 'dead'")
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "All living pets have been fully restored!")
            self.reload_view()

    def admin_modify_coins(self, row_data):
        username = row_data[0]
        amount = simpledialog.askinteger("Modify Balance", f"Enter coin amount to ADD to {username}'s wallet:\n(Use negative numbers to remove coins)", parent=self.root)
        if amount is not None:
            conn = get_connection()
            conn.execute("UPDATE users SET coins = MAX(0, coins + ?) WHERE username = ?", (amount, username))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Adjusted {username}'s balance by {amount} coins.")
            self.reload_view()

    def admin_heal_pet(self, row_data):
        username, _, pet_id, pet_name, _, _, current_status = row_data
        if str(pet_id) == "-":
            messagebox.showwarning("No Pet", f"{username} does not own this pet.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        if current_status.lower() == 'dead':
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            user_id = cursor.fetchone()['user_id']
            cursor.execute("SELECT COUNT(*) as alive_count FROM pets WHERE owner_id = ? AND status != 'dead'", (user_id,))
            if cursor.fetchone()['alive_count'] > 0:
                messagebox.showerror("Revival Blocked", f"{username} already has an active, living pet.\nA player can only have one living pet at a time.")
                conn.close()
                return
            
        if messagebox.askyesno("Intervene", f"Restore {pet_name} to 100% Health, Energy, Hunger, and Happiness?"):
            cursor.execute("UPDATE pets SET health=100, hunger=100, happiness=100, energy=100, status='healthy' WHERE pet_id = ?", (pet_id,))
            conn.commit()
            messagebox.showinfo("Success", f"{pet_name} has been fully restored!")
            self.reload_view()
        conn.close()

    def admin_delete_user(self, row_data):
        username = row_data[0]
        confirm = simpledialog.askstring("Confirm Deletion", f"WARNING: You are about to wipe {username} entirely.\nType their username exactly to confirm:", parent=self.root)
        if confirm == username:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user:
                user_id = user['user_id']
                cursor.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM event_log WHERE pet_id IN (SELECT pet_id FROM pets WHERE owner_id = ?)", (user_id,))
                cursor.execute("DELETE FROM pets WHERE owner_id = ?", (user_id,))
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", f"User {username} has been wiped.")
            self.reload_view()

    def validate_shop_data(self, data):
        if not all([data['name'], data['price'], data['effect'], data['desc']]):
            messagebox.showerror("Error", "Please fill in all text fields.")
            return None
        try:
            return (data['name'].strip(), data['type'], data['species'], int(data['price']), float(data['effect']), data['desc'].strip())
        except ValueError:
            messagebox.showerror("Error", "Price must be a whole number, Effect must be a number.")
            return None

    def generate_placeholder_image(self, item_name):
        img_name = item_name.lower().replace(" ", "_") + ".png"
        folder_path = "assets/images/items"
        os.makedirs(folder_path, exist_ok=True)
        img_path = os.path.join(folder_path, img_name)
        
        if not os.path.exists(img_path):
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (150, 150), color="#E5E8E8")
                draw = ImageDraw.Draw(img)
                draw.rectangle([10, 10, 140, 140], outline="#BDC3C7", width=5)
                img.save(img_path)
            except: pass

    def add_shop_item(self, raw_data):
        valid_data = self.validate_shop_data(raw_data)
        if valid_data:
            conn = get_connection()
            conn.execute("INSERT INTO items (name, type, species, price, effect_value, description) VALUES (?, ?, ?, ?, ?, ?)", valid_data)
            conn.commit()
            conn.close()
            self.generate_placeholder_image(valid_data[0])
            messagebox.showinfo("Success", f"{valid_data[0]} has been added!")
            self.reload_view()

    def update_shop_item(self, item_id, raw_data):
        if not item_id: return self.callbacks['on_no_selection']()
        valid_data = self.validate_shop_data(raw_data)
        if valid_data:
            conn = get_connection()
            conn.execute("UPDATE items SET name=?, type=?, species=?, price=?, effect_value=?, description=? WHERE item_id=?", (*valid_data, item_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Item updated successfully!")
            self.reload_view()

    def delete_shop_item(self, item_id):
        if not item_id: return self.callbacks['on_no_selection']()
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this item?\nIt will also be permanently removed from all player backpacks."):
            conn = get_connection()
            conn.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))
            conn.execute("DELETE FROM items WHERE item_id = ?", (item_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Item has been removed from the game.")
            self.reload_view()

    def validate_species_data(self, data):
        if not all([data['name'], data['hunger_rate'], data['happy_rate'], data['energy_rate']]):
            messagebox.showerror("Error", "Please fill in all text fields.")
            return None
        try:
            return (data['name'].strip().capitalize(), float(data['hunger_rate']), float(data['happy_rate']), float(data['energy_rate']))
        except ValueError:
            messagebox.showerror("Error", "Rates must be numerical values.")
            return None

    def generate_species_placeholders(self, species_name):
        """Creates an asset folder and dummy graphics so the game doesn't crash when drawing new pets."""
        folder_path = f"assets/images/{species_name.lower()}"
        os.makedirs(folder_path, exist_ok=True)
        
        required_images = ["idle_1.png", "idle_2.png", "hungry_1.png", "hungry_2.png", 
                           "sad_1.png", "sad_2.png", "exhausted_1.png", "exhausted_2.png", 
                           "sick_1.png", "sick_2.png", "dead_1.png", "happy_1.png", "happy_2.png"]
                           
        try:
            from PIL import Image, ImageDraw, ImageFont
            for img_name in required_images:
                img_path = os.path.join(folder_path, img_name)
                if not os.path.exists(img_path):
                    img = Image.new('RGBA', (150, 150), color=(0,0,0,0))
                    draw = ImageDraw.Draw(img)
                    draw.ellipse([30, 30, 120, 120], fill="#D5DBDB", outline="#BDC3C7", width=5)
                    draw.ellipse([50, 60, 60, 70], fill="#2C3E50")
                    draw.ellipse([90, 60, 100, 70], fill="#2C3E50")
                    draw.arc([60, 80, 90, 100], start=0, end=180, fill="#2C3E50", width=4)
                    img.save(img_path)
        except: pass

    def add_species(self, raw_data):
        valid_data = self.validate_species_data(raw_data)
        if valid_data:
            conn = get_connection()
            try:
                conn.execute("INSERT INTO species (name, hunger_rate, happy_rate, energy_rate) VALUES (?, ?, ?, ?)", valid_data)
                conn.commit()
                self.generate_species_placeholders(valid_data[0])
                messagebox.showinfo("Success", f"The {valid_data[0]} species has been added!")
                self.reload_view()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to add species. It might already exist.\n{e}")
            finally:
                conn.close()

    def update_species(self, original_name, raw_data):
        if not original_name: return self.callbacks['on_no_selection']()
        valid_data = self.validate_species_data(raw_data)
        if valid_data:
            conn = get_connection()
            conn.execute("UPDATE species SET name=?, hunger_rate=?, happy_rate=?, energy_rate=? WHERE name=?", (*valid_data, original_name))
            conn.commit()
            conn.close()
            if original_name.lower() != valid_data[0].lower():
                self.generate_species_placeholders(valid_data[0])
            messagebox.showinfo("Success", "Species updated successfully!")
            self.reload_view()

    def delete_species(self, species_name):
        if not species_name: return self.callbacks['on_no_selection']()
        if species_name in ["Dog", "Cat", "Rabbit"]:
            messagebox.showerror("Protected Data", "You cannot delete the default base game species (Dog, Cat, Rabbit).")
            return
            
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {species_name}?\nPets of this species currently owned by players may bug out!"):
            conn = get_connection()
            conn.execute("DELETE FROM species WHERE name = ?", (species_name,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Species has been removed.")
            self.reload_view()

    def logout(self):
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            self.root.geometry("450x800")
            self.root.minsize(450, 800)
            from views.login_view import LoginView
            LoginView(self.root)