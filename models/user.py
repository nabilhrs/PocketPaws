class User:
    def __init__(self, user_id, username, role="player", coins=50):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.coins = coins

class Player(User):
    def __init__(self, user_id, username, coins=50):
        super().__init__(user_id, username, role="player", coins=coins)
        self.pets = []
        self.inventory = []

class Admin(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, role="admin", coins=0)