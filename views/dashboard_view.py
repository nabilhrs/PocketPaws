from datetime import datetime, timedelta
import random
from tkinter import messagebox
from database import get_connection
from utils.sound_manager import SoundManager

from models.pet import DogPet, CatPet, RabbitPet, CustomPet
from controllers.decay_engine import process_pet_decay
from templates.dashboard_template import DashboardTemplate

class DashboardView:    
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.user_id = None
        self.coins = 0
        self.pet_data = None
        self.pet_obj = None
        
        self.load_and_decay_pet()
        
        anim_state = self.get_anim_state()
        thought_text = self.get_pet_thought()
        
        callbacks = {
            'feed': self.action_feed,
            'play': self.action_play,
            'rest': self.action_rest,
            'adopt': self.adopt_pet,
            'inventory': self.open_inventory,
            'shop': self.open_shop,
            'memorial': self.open_memorial,
            'logout': self.logout,
            'debug': self.debug_fast_forward
        }
        
        self.template = DashboardTemplate(
            self.root, 
            self.username, 
            self.coins, 
            self.pet_data, 
            thought_text, 
            anim_state, 
            callbacks
        )

    def load_and_decay_pet(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, coins FROM users WHERE username = ?", (self.username,))
        user = cursor.fetchone()
        
        if user:
            self.user_id = user['user_id']
            self.coins = user['coins']
            
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
                
                new_timestamp = process_pet_decay(self.pet_obj, pet_row['last_updated'], cursor=cursor, user_id=self.user_id)
                
                cursor.execute("""
                    UPDATE pets 
                    SET hunger = ?, happiness = ?, energy = ?, health = ?, status = ?, last_updated = ?
                    WHERE pet_id = ?
                """, (self.pet_obj.hunger, self.pet_obj.happiness, self.pet_obj.energy, 
                      self.pet_obj.health, self.pet_obj.status, new_timestamp, self.pet_obj.pet_id))
                conn.commit()
                
                cursor.execute("SELECT * FROM pets WHERE pet_id = ?", (self.pet_obj.pet_id,))
                self.pet_data = cursor.fetchone()
                
        conn.close()

    def get_anim_state(self):
        if not self.pet_data: return "idle"
        status = self.pet_data['status'].lower()
        anim_map = {
            "healthy": "idle", "hungry": "hungry", "sad": "sad",
            "exhausted": "exhausted", "sick": "sick", "dead": "dead"
        }
        state = anim_map.get(status, "idle")
        if state == "idle" and self.pet_data['happiness'] > 80:
            return "happy"
        return state

    def get_pet_thought(self):
        if not self.pet_data: return ""
        if self.pet_data['status'] == 'dead': return "..."
        if self.pet_data['health'] < 100: return "I don't feel so good... medicine? 🤒"
        if self.pet_data['energy'] <= 20: return "So tired... let me sleep. 🥱"
        if self.pet_data['hunger'] <= 30: return "Starving! Need food! 🍗"
        if self.pet_data['happiness'] <= 30: return "I'm so lonely... play with me! 🪁"
        
        if self.pet_data['hunger'] > 80 and self.pet_data['happiness'] > 80 and self.pet_data['energy'] > 80:
            return "I feel AMAZING! ✨ (Coin find rate doubled!)"
            
        return "I love hanging out with you! 💖"

    def update_pet_db_and_refresh(self, coins_earned=0):
        self.template.cancel_animation()
        conn = get_connection()
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE pets 
            SET hunger = ?, happiness = ?, energy = ?, health = ?, status = ?, last_updated = ?
            WHERE pet_id = ?
        """, (self.pet_obj.hunger, self.pet_obj.happiness, self.pet_obj.energy, 
              self.pet_obj.health, self.pet_obj.status, current_time, self.pet_obj.pet_id))
              
        if coins_earned > 0:
            cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (coins_earned, self.user_id))
            
        conn.commit()
        conn.close()
        
        DashboardView(self.root, self.username)

    def action_feed(self):
        if self.pet_obj.hunger >= 100.0:
            SoundManager.play_error()
            messagebox.showinfo("Stuffed!", f"{self.pet_obj.name} is too full to eat right now.")
            return
        
        SoundManager.play_eat()
        self.pet_obj.hunger = min(100.0, self.pet_obj.hunger + 30)
        self.pet_obj.energy = max(0.0, self.pet_obj.energy - 5)
        self.pet_obj.health = min(100.0, self.pet_obj.health + 5) # Minor healing
        
        self.update_pet_db_and_refresh()

    def action_play(self):
        if self.pet_obj.energy < 15.0:
            SoundManager.play_error()
            messagebox.showwarning("Exhausted", f"{self.pet_obj.name} is too tired to play. Let them rest!")
            return
            
        SoundManager.play(f"{self.pet_obj.species.lower()}.wav")
        self.pet_obj.happiness = min(100.0, self.pet_obj.happiness + 20)
        self.pet_obj.hunger = max(0.0, self.pet_obj.hunger - 10) 
        self.pet_obj.energy = max(0.0, self.pet_obj.energy - 15)
        self.pet_obj.health = min(100.0, self.pet_obj.health + 2)
        
        coin_chance = 0.50 if (self.pet_obj.hunger > 80 and self.pet_obj.happiness > 80 and self.pet_obj.energy > 80) else 0.25 

        if random.random() < coin_chance: 
            SoundManager.play_coin()
            payout = random.randint(10, 25) 
            messagebox.showinfo("Treasure Found!", f"{self.pet_obj.name} had a great time and found {payout} Coins in the grass!")
            self.update_pet_db_and_refresh(coins_earned=payout)
        else:
            self.update_pet_db_and_refresh()

    def action_rest(self):
        if self.pet_obj.energy >= 100.0:
            messagebox.showinfo("Wide Awake", f"{self.pet_obj.name} is fully rested.")
            return

        SoundManager.play("sleep.wav", maxtime=5000)    
        self.template.trigger_sleep()
        
        self.root.after(5000, self.wake_up)

    def wake_up(self):
        self.pet_obj.energy = min(100.0, self.pet_obj.energy + 40)
        self.pet_obj.hunger = max(0.0, self.pet_obj.hunger - 15)
        self.pet_obj.health = min(100.0, self.pet_obj.health + 10) # Heavy healing
        self.update_pet_db_and_refresh()

    def debug_fast_forward(self):
        conn = get_connection()
        conn.execute("UPDATE pets SET last_updated = ? WHERE pet_id = ?", 
                     ((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), self.pet_obj.pet_id))
        conn.commit()
        conn.close()
        DashboardView(self.root, self.username)

    def adopt_pet(self):
        self.template.cancel_animation()
        from views.adopt_view import AdoptView
        AdoptView(self.root, self.username)
        
    def open_inventory(self):
        self.template.cancel_animation()
        from views.inventory_view import InventoryView
        InventoryView(self.root, self.username)

    def open_shop(self):
        self.template.cancel_animation()
        from views.shop_view import ShopView
        ShopView(self.root, self.username)
        
    def open_memorial(self):
        self.template.cancel_animation()
        from views.memorial_view import MemorialView
        MemorialView(self.root, self.username)

    def logout(self):
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            self.template.cancel_animation()
            from views.login_view import LoginView
            LoginView(self.root)