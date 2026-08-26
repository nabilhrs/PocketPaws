from datetime import datetime
import random
from database import get_connection

# Import the new UI template
from templates.memorial_template import MemorialTemplate

class MemorialView:    
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.deceased_pets_data = []
        
        # 1. Fetch and process the data
        self.prepare_data()
        
        # 2. Initialize the Template with the formatted data
        self.template = MemorialTemplate(
            self.root,
            pets_data=self.deceased_pets_data,
            back_callback=self.go_back
        )

    def prepare_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (self.username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return
            
        user_id = user['user_id']
        
        cursor.execute("SELECT * FROM pets WHERE owner_id = ? AND status = 'dead' ORDER BY last_updated DESC", (user_id,))
        raw_pets = cursor.fetchall()
        conn.close()

        epitaphs = [
            "Always in our hearts.",
            "A good pet, gone too soon.",
            "Playing in the endless fields now.",
            "Rest peacefully, little one.",
            "Forever chasing butterflies."
        ]

        for pet in raw_pets:
            birth = datetime.strptime(pet['birth_time'], "%Y-%m-%d %H:%M:%S")
            death = datetime.strptime(pet['last_updated'], "%Y-%m-%d %H:%M:%S")
            time_lived = death - birth
            
            days = time_lived.days
            hours, remainder = divmod(time_lived.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                duration_str = f"{days} Days, {hours} Hours"
            elif hours > 0:
                duration_str = f"{hours} Hours, {minutes} Minutes"
            else:
                duration_str = f"{max(1, minutes)} Minutes"
                
            cause = "Old Age / Unknown"
            if pet['hunger'] <= 0: cause = "Starvation 🍖"
            elif pet['happiness'] <= 0: cause = "Broken Heart 💔"
            elif pet['energy'] <= 0: cause = "Exhaustion 💤"
            elif pet['health'] <= 0: cause = "Illness 🤒"
            
            self.deceased_pets_data.append({
                'name': pet['name'],
                'species': pet['species'],
                'duration': duration_str,
                'cause': cause,
                'date': pet['last_updated'][:10],
                'quote': random.choice(epitaphs)
            })

    def go_back(self):
        """Navigate back to the main dashboard."""
        from views.dashboard_view import DashboardView
        DashboardView(self.root, self.username)