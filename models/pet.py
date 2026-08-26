from abc import ABC, abstractmethod

class Pet(ABC):
    def __init__(self, pet_id, name, species, owner_id, birth_time):
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.owner_id = owner_id
        self.birth_time = birth_time
        self.hunger = 100.0
        self.happiness = 100.0
        self.energy = 100.0
        self.health = 100.0
        self.status = "healthy"
        self.revival_charm_consumed = False

    @abstractmethod
    def decay_rate(self) -> dict:
        pass

    def apply_decay(self, elapsed_hours: float, has_revival_charm: bool = False):
        rates = self.decay_rate()
        
        self.hunger -= rates['hunger'] * elapsed_hours
        self.happiness -= rates['happiness'] * elapsed_hours
        self.energy -= rates['energy'] * elapsed_hours
        
        health_penalty = 0
        if self.hunger <= 0: health_penalty += 5 * elapsed_hours
        if self.happiness <= 0: health_penalty += 2 * elapsed_hours
        if self.energy <= 0: health_penalty += 1 * elapsed_hours

        self.hunger = max(0, min(100, self.hunger))
        self.happiness = max(0, min(100, self.happiness))
        self.energy = max(0, min(100, self.energy))
        
        self.update_health_from_neglect(health_penalty, has_revival_charm=has_revival_charm)

    def update_health_from_neglect(self, penalty: float = 0.0, has_revival_charm: bool = False):
        self.revival_charm_consumed = False

        if self.hunger <= 0 or self.happiness <= 0:
            self.health -= 5 
            
        self.health -= penalty
            
        if self.health <= 0:  
            if has_revival_charm:
                self.health = 30  
                self.status = "sick"  
                self.revival_charm_consumed = True
            else:
                self.status = "dead"
        elif self.health <= 20: 
            self.status = "sick"
        elif self.energy <= 20:
            self.status = "exhausted"
        elif self.hunger <= 30:
            self.status = "hungry"
        elif self.happiness <= 30:
            self.status = "sad"
        else:
            self.status = "healthy"

class DogPet(Pet):
    def decay_rate(self):
        return {'hunger': 0.8, 'happiness': 1.2, 'energy': 0.7}

class CatPet(Pet):
    def decay_rate(self):
        return {'hunger': 1.0, 'happiness': 0.5, 'energy': 0.8}

class RabbitPet(Pet):
    def decay_rate(self):
        return {'hunger': 1.2, 'happiness': 0.9, 'energy': 1.5}
    
class CustomPet(Pet):
    def __init__(self, pet_id, name, species, owner_id, birth_time, hunger_rate, happy_rate, energy_rate):
        super().__init__(pet_id, name, species, owner_id, birth_time)
        self._hunger_rate = hunger_rate
        self._happy_rate = happy_rate
        self._energy_rate = energy_rate

    def decay_rate(self):
        return {
            'hunger': self._hunger_rate,
            'happiness': self._happy_rate,
            'energy': self._energy_rate
        }