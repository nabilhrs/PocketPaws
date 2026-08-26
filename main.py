import tkinter as tk
from database import initialize_database
from views.login_view import LoginView
from utils.sound_manager import SoundManager 

def main():
    initialize_database()
    
    SoundManager.init()
    
    root = tk.Tk()
    root.title("PocketPaws")
    root.geometry("450x800") 
    root.resizable(True, True) 
    
    app = LoginView(root)
    root.mainloop()

if __name__ == "__main__":
    main()