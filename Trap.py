from Card import Card


class Trap(Card):
    def __init__(self):
        super().__init__()
        self.effect = None
        self.is_set = False
        self.set_turn = -1
        self.spell_speed = 2
        self.other_type = None

    def get_json(self):
        return {"name": self.name.value, "id": str(self.password), "desc": self.text,
                "type": "trap", "position": "faceup" if not self.is_set else "set", "card_type": self.card_type,
                "other_type": self.other_type, "global_id": self.global_id}


class NormalTrap(Trap):
    def __init__(self):
        super().__init__()


class ContinuousTrap(Trap):
    def __init__(self):
        super().__init__()


class CounterTrap(Trap):
    def __init__(self):
        super().__init__()
        self.spell_speed = 3

