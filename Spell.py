from Card import Card


class Spell(Card):
    def __init__(self):
        super().__init__()
        self.effect = None
        self.is_set = False
        self.set_turn = -1
        self.spell_speed = 1
        self.other_type = None

    def get_json(self):
        return {"name": self.name.value, "id": str(self.password), "desc": self.text, "type": "spell",
                "position": "faceup" if not self.is_set else "set", "card_type": self.card_type,
                "other_type": self.other_type, "global_id": self.global_id}


class NormalSpell(Spell):
    def __init__(self):
        super().__init__()


class ContinuousSpell(Spell):
    def __init__(self):
        super().__init__()


class QuickPlaySpell(Spell):
    def __init__(self):
        super().__init__()
        self.spell_speed = 2


class RitualSpell(Spell):
    def __init__(self):
        super().__init__()


class FieldSpell(Spell):
    def __init__(self):
        super().__init__()


class EquipSpell(Spell):
    def __int__(self):
        super().__init__()
        self.card = None
