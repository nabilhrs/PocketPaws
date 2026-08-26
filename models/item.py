class Item:
    def __init__(self, item_id, name, price, effect_value, description):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.effect_value = effect_value
        self.description = description

    def use(self, pet):
        pass

class FoodItem(Item):
    def use(self, pet):
        pet.hunger = min(100.0, pet.hunger + self.effect_value)
        pet.happiness = min(100.0, pet.happiness + 5)
        pet.update_health_from_neglect()

class ToyItem(Item):
    def use(self, pet):
        pet.happiness = min(100.0, pet.happiness + self.effect_value)
        pet.update_health_from_neglect()

class MedicineItem(Item):
    def use(self, pet):
        pet.health = min(100.0, pet.health + self.effect_value)
        pet.update_health_from_neglect()

class EnergyItem(Item):
    def use(self, pet):
        pet.energy = min(100.0, pet.energy + self.effect_value)
        pet.update_health_from_neglect()

class CharmItem(Item):
    def use(self, pet):
        pass