class ModifiableAttribute:
    def __init__(self, original=None):
        self.original = original
        self.history = []

    @property
    def value(self):
        return 0

    def reset(self):
        pass


class Name(ModifiableAttribute):
    def __init__(self, original_name):
        super().__init__(original_name)

    @property
    def value(self):
        return self.original


class Attack(ModifiableAttribute):
    _minimum = 0

    def __init__(self, original_attack):
        super().__init__(original_attack)

    @property
    def value(self):
        if not self.history:
            return self.original

        history = self.history
        if False in self.history:
            history = self.history[:len(self.history)-self.history[::-1].index(False)]
        attack = self.original

        for event in history:
            attack += event[1]
        if attack < self._minimum:
            attack = self._minimum

        return attack


class Defense(ModifiableAttribute):
    _minimum = 0

    def __init__(self, original_defense):
        super().__init__(original_defense)

    @property
    def value(self):
        if not self.history:
            return self.original

        history = self.history
        if False in self.history:
            history = self.history[:len(self.history) - self.history[::-1].index(False)]
        defense = self.original

        for event in history:
            defense += event[1]

        if defense < self._minimum:
            defense = self._minimum

        return defense


class Level(ModifiableAttribute):
    _minimum = 1
    _maximum = 12

    def __init__(self, original_level):
        super().__init__(original_level)

    @property
    def value(self):
        return self.original


class Rank(ModifiableAttribute):
    _minimum = 1
    _maximum = 13

    def __init__(self, original_rank):
        super().__init__(original_rank)

    @property
    def value(self):
        return self.original


class LinkRating(ModifiableAttribute):
    _minimum = 1

    def __init__(self, original_link_rating):
        super().__init__(original_link_rating)

    @property
    def value(self):
        return self.original


class LinkArrows(ModifiableAttribute):
    def __init__(self, original_link_arrows):
        super().__init__(original_link_arrows)

    @property
    def value(self):
        return self.original


class Attribute(ModifiableAttribute):
    attributes = ['Dark', 'Divine', 'Earth', 'Fire', 'Light', 'Water', 'Wind']

    def __init__(self, original_attribute):
        super().__init__(original_attribute)

    @property
    def value(self):
        return self.original


class PendulumScale(ModifiableAttribute):
    _minimum = 0
    _maximum = 13

    def __init__(self, original_scale):
        super().__init__(original_scale)


class MonsterType(ModifiableAttribute):
    monster_types = ['Aqua', 'Beast', 'Beast-Warrior', 'Creator-God', 'Cyberse', 'Dinosaur', 'Divine-Beast',
                     'Dragon', 'Fairy', 'Fiend', 'Fish', 'Insect', 'Machine', 'Plant', 'Psychic', 'Pyro', 'Reptile',
                     'Rock', 'Sea Serpent', 'Spellcaster', 'Thunder', 'Warrior', 'Winged Beast', 'Wyrm', 'Zombie']

    def __init__(self, original_type):
        super().__init__(original_type)

    @property
    def value(self):
        return self.original


class Owner(ModifiableAttribute):
    def __init__(self, original_owner=None):
        super().__init__(original_owner)
        self.current_owner = original_owner

    @property
    def value(self):
        return self.original

