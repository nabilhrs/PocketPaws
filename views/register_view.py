import hashlib
from tkinter import messagebox
from database import get_connection
from templates.register_template import RegisterTemplate

class RegisterView:    
    def __init__(self, root):
        self.root = root
        
        self.template = RegisterTemplate(
            self.root,
            register_callback=self.handle_register,
            back_callback=self.go_back
        )

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def go_back(self):
        from views.login_view import LoginView
        LoginView(self.root)

    def handle_register(self):        
        username = self.template.entry_username.get().strip()
        password = self.template.entry_password.get().strip()
        confirm = self.template.entry_confirm.get().strip()
        
        if not username or not password or not confirm:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters long.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists. Please choose another.")
            conn.close()
            return
            
        hashed_pw = self.hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Registration successful! You can now log in.")
        self.go_back()