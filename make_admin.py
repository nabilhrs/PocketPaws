"""Creates an admin account in the local PocketPaws save file.

Usage: python make_admin.py
"""
import getpass
import sqlite3
from database import get_db_path, initialize_database
from utils.security import hash_password


def create_admin():
    initialize_database()  # Make sure the tables exist on a fresh install

    username = input("Admin username: ").strip()
    password = getpass.getpass("Admin password: ")
    confirm = getpass.getpass("Confirm password: ")

    if not username or not password:
        print("Username and password are required.")
        return
    if password != confirm:
        print("Passwords do not match.")
        return
    if len(password) < 8:
        print("Admin password must be at least 8 characters long.")
        return

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, coins) VALUES (?, ?, 'admin', 0)",
            (username, hash_password(password))
        )
        conn.commit()
        print(f"Admin account '{username}' created.")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists.")
    finally:
        conn.close()


if __name__ == "__main__":
    create_admin()
