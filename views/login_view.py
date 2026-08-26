from tkinter import messagebox
import hashlib
from database import get_connection
from utils.sound_manager import SoundManager
from templates.login_template import LoginTemplate

class LoginView:    
    def __init__(self, root):
        self.root = root
        
        self.template = LoginTemplate(
            self.root, 
            login_callback=self.login, 
            register_callback=self.go_to_register
        )

    def hash_password(self, password):
        """Simple SHA-256 hashing for the database."""
        return hashlib.sha256(password.encode()).hexdigest()

    def go_to_register(self):
        from views.register_view import RegisterView
        RegisterView(self.root)

    def login(self):
        username = self.template.entry_username.get().strip()
        password = self.template.entry_password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        hashed_pw = self.hash_password(password)
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()

        if user:
            SoundManager.play("intro.wav")
            
            if user['role'] == 'admin':
                from views.admin_view import AdminView
                AdminView(self.root, username)
            else:
                from views.dashboard_view import DashboardView
                DashboardView(self.root, username)
        else:
            messagebox.showerror("Error", "Invalid username or password.")