from tkinter import messagebox
from database import get_connection
from utils.sound_manager import SoundManager
from templates.adopt_template import AdoptTemplate

class AdoptView:    
    def __init__(self, root, username):
        self.root = root
        self.username = username
        
        self.available_species = self.fetch_available_species()
        
        self.template = AdoptTemplate(
            self.root,
            available_species=self.available_species,
            adopt_callback=self.handle_adopt,
            back_callback=self.go_back
        )

    def fetch_available_species(self):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM species")
            species_list = [row['name'] for row in cursor.fetchall()]
        except Exception:
            species_list = ["Dog", "Cat", "Rabbit"] 
        conn.close()
        return species_list

    def handle_adopt(self):        
        pet_name = self.template.entry_name.get().strip()
        species = self.template.species_var.get()
        
        if not pet_name:
            messagebox.showerror("Error", "Please give your pet a name!")
            return
            
        if len(pet_name) > 15:
            messagebox.showerror("Error", "Pet name is too long! (Max 15 characters)")
            return

        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (self.username,))
        user = cursor.fetchone()
        
        if user:
            user_id = user['user_id']
            
            cursor.execute("""
                INSERT INTO pets (owner_id, name, species) 
                VALUES (?, ?, ?)
            """, (user_id, pet_name, species))
            
            conn.commit()
            
            try:
                SoundManager.play(f"{species.lower()}.wav")
            except Exception:
                pass 
            messagebox.showinfo("Success", f"You have successfully adopted {pet_name} the {species}!")
            self.go_back()
        
        conn.close()

    def go_back(self):
        """Navigate back to the main dashboard."""
        from views.dashboard_view import DashboardView
        DashboardView(self.root, self.username)