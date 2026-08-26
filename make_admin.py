import sqlite3
import hashlib
from database import get_db_path  # Imports the safe path we set up

def create_admin():
    username = "admin"
    password = "adminpassword"
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    # Use the imported function to find the right database!
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role, coins) VALUES (?, ?, 'admin', 0)", (username, hashed_pw))
        conn.commit()
        print("Admin account created! Username: admin | Password: adminpassword")
    except sqlite3.IntegrityError:
        print("Admin account already exists!")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin()