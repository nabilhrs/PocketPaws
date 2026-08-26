from datetime import datetime

REVIVAL_CHARM_NAME = "Revival Charm"

def calculate_elapsed_seconds(last_updated_str):
    last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    
    delta = now - last_updated
    return delta.total_seconds()

def get_revival_charm_item_id(cursor):
    cursor.execute("SELECT item_id FROM items WHERE name = ?", (REVIVAL_CHARM_NAME,))
    row = cursor.fetchone()
    return row['item_id'] if row else None

def has_revival_charm(cursor, user_id, charm_item_id):
    if charm_item_id is None:
        return False
    cursor.execute(
        "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ? AND quantity > 0",
        (user_id, charm_item_id)
    )
    row = cursor.fetchone()
    return row is not None

def consume_revival_charm(cursor, user_id, charm_item_id):
    if charm_item_id is None:
        return
    cursor.execute(
        "SELECT inventory_id, quantity FROM inventory WHERE user_id = ? AND item_id = ?",
        (user_id, charm_item_id)
    )
    row = cursor.fetchone()
    if row is None:
        return
    new_qty = row['quantity'] - 1
    if new_qty > 0:
        cursor.execute("UPDATE inventory SET quantity = ? WHERE inventory_id = ?", (new_qty, row['inventory_id']))
    else:
        cursor.execute("DELETE FROM inventory WHERE inventory_id = ?", (row['inventory_id'],))

def process_pet_decay(pet, last_updated_str, cursor=None, user_id=None):
    """
    Applies time-based decay to the pet and checks for Revival Charms.
    """
    elapsed_seconds = calculate_elapsed_seconds(last_updated_str)
    
    game_time_factor = elapsed_seconds / 3600 

    charm_available = False
    charm_item_id = None
    if cursor is not None and user_id is not None:
        charm_item_id = get_revival_charm_item_id(cursor)
        charm_available = has_revival_charm(cursor, user_id, charm_item_id)

    pet.apply_decay(game_time_factor, has_revival_charm=charm_available)

    if getattr(pet, "revival_charm_consumed", False) and cursor is not None:
        consume_revival_charm(cursor, user_id, charm_item_id)
    
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")