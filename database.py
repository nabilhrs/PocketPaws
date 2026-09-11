import sqlite3
import os
from utils.security import hash_password

# --- NEW: Safe Directory Handling ---
def get_db_path():
    """Returns a safe, permanent path for the database."""
    home_dir = os.path.expanduser("~")
    app_dir = os.path.join(home_dir, "PocketPaws")
    
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
        
    return os.path.join(app_dir, "pet_simulator.db")

DB_NAME = get_db_path()
DEMO_ADMIN_PASSWORD = "admin123"  # Documented demo login (see README)
# ------------------------------------

def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    """Creates the necessary tables based on the project schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Species Table 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS species (
            name TEXT PRIMARY KEY,
            hunger_rate REAL NOT NULL,
            happy_rate REAL NOT NULL,
            energy_rate REAL NOT NULL
        )
    ''')

    # 2. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('player','admin')) NOT NULL DEFAULT 'player',
            coins INTEGER DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Pets Table 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            hunger REAL DEFAULT 100,
            happiness REAL DEFAULT 100,
            energy REAL DEFAULT 100,
            health REAL DEFAULT 100,
            status TEXT DEFAULT 'healthy', 
            birth_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(user_id),
            FOREIGN KEY (species) REFERENCES species(name)
        )
    ''')

    # 4. Items Table 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('food','toy','medicine','energy','charm')) NOT NULL,
            species TEXT NOT NULL DEFAULT 'Any',
            price INTEGER NOT NULL,
            effect_value REAL NOT NULL,
            description TEXT
        )
    ''')

    # 5. Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(item_id)
        )
    ''')
    
    # 6. Event Log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            event_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(pet_id)
        )
    ''')

    cursor.execute("SELECT COUNT(*) as count FROM species")
    if cursor.fetchone()['count'] == 0:
        default_species = [
            ("Dog", 2.0, 1.5, 1.0),
            ("Cat", 1.5, 1.0, 1.5),
            ("Rabbit", 2.5, 2.0, 1.0)
        ]
        cursor.executemany("""
            INSERT INTO species (name, hunger_rate, happy_rate, energy_rate) 
            VALUES (?, ?, ?, ?)
        """, default_species)
        print("Default species injected!")

    # Demo admin so the admin portal can be tried straight away; the credentials
    # are listed in the README. Set POCKETPAWS_ADMIN_PASSWORD to use your own.
    admin_password = os.environ.get("POCKETPAWS_ADMIN_PASSWORD", DEMO_ADMIN_PASSWORD)
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, coins)
            VALUES (?, ?, ?, ?)
        """, ("admin", hash_password(admin_password), "admin", 9999))
        print("Default admin account created!")

    conn.commit()
    conn.close()
    
    migrate_items_table_if_needed()
    print("Database initialized successfully.")

def migrate_items_table_if_needed():
    """
    Rebuilds the items table from scratch if it detects the old schema, 
    preserving any rows that still fit the new shape.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(items)")
    columns = [row['name'] for row in cursor.fetchall()]

    if 'species' in columns:
        conn.close()
        return  

    print("Old items table schema detected -- migrating to add 'species' column...")

    cursor.execute("SELECT name, type, price, effect_value, description FROM items")
    old_rows = cursor.fetchall()

    cursor.execute("ALTER TABLE items RENAME TO items_old")
    cursor.execute('''
        CREATE TABLE items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('food','toy','medicine','energy','charm')) NOT NULL,
            species TEXT NOT NULL DEFAULT 'Any',
            price INTEGER NOT NULL,
            effect_value REAL NOT NULL,
            description TEXT
        )
    ''')

    for row in old_rows:
        cursor.execute('''
            INSERT INTO items (name, type, species, price, effect_value, description)
            VALUES (?, ?, 'Any', ?, ?, ?)
        ''', (row['name'], row['type'], row['price'], row['effect_value'], row['description']))

    cursor.execute("DROP TABLE items_old")
    conn.commit()
    conn.close()
    print("Migration complete. Old items were preserved with species='Any'.")

if __name__ == "__main__":
    initialize_database()