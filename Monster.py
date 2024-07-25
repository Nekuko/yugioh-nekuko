from Card import Card


class Monster(Card):
    def __init__(self):
        super().__init__()
        self.attack = None
        self.attribute = None
        self.monster_type = None
        self.is_tuner = False
        self.attack_count = 1

    def get_battle_value(self):
        if self.defense_mode:
            return self.defense.value
        return self.attack.value

    def can_attack(self):
        if self.defense_mode or self.attack_count <= 0:
            return False

        return True

    def get_json(self):
        mode = "attack"
        if self.is_set:
            mode = "set"
        elif self.defense_mode:
            mode = "defense"

        return {"name": self.name.value, "id": str(self.password), "desc": self.text,
                "type": "monster", "position": mode, "attack": self.attack.value, "defense": self.defense.value,
                "card_type": self.card_type, "monster_type": self.monster_type.value, "attribute": self.attribute.value,
                "level": self.level.value, "attacks": self.attack_count, "global_id": self.global_id}


class NormalMonster(Monster):
    def __init__(self):
        super().__init__()
        self.defense = None
        self.level = None
        self.lore = ""
        self.defense_mode = False
        self.is_set = False


class EffectMonster(Monster):
    def __init__(self):
        super().__init__()
        self.effect = None
        self.defense = None
        self.level = None
        self.defense_mode = False
        self.is_set = False


class RitualMonster(Monster):
    def __init__(self):
        super().__init__()
        self.defense = None
        self.level = None
        self.defense_mode = False
        self.effect = None
        self.is_set = False


class FusionMonster(Monster):
    def __init__(self):
        super().__init__()
        self.defense = None
        self.level = None
        self.defense_mode = False
        self.effect = None
        self.is_set = False
        self.material = []


class SynchroMonster(Monster):
    def __init__(self):
        super().__init__()
        self.defense = None
        self.level = None
        self.defense_mode = False
        self.effect = None
        self.is_set = False
        self.material = []


class XyzMonster(Monster):
    def __init__(self):
        super().__init__()
        self.defense = None
        self.rank = None
        self.material = []
        self.defense_mode = False
        self.effect = None
        self.is_set = False
        self.material = []
        self.xyz_material = []

    def get_json(self):
        mode = "attack"
        if self.is_set:
            mode = "set"
        elif self.defense_mode:
            mode = "defense"

        return {"name": self.name.value, "id": str(self.password), "desc": self.text,
                "type": "xyz_monster", "position": mode, "attack": self.attack.value, "defense": self.defense.value,
                "card_type": self.card_type, "monster_type": self.monster_type.value, "attribute": self.attribute.value,
                "rank": self.rank.value, "attacks": self.attack_count, "global_id": self.global_id}


class LinkMonster(Monster):
    def __init__(self):
        super().__init__()
        self.link_rating = None
        self.link_arrows = []
        self.effect = None
        self.material = []

    def get_battle_value(self):
        return self.attack.value

    def can_attack(self):
        return not self.attack_count == 0

    def get_json(self):
        return {"name": self.name.value, "id": str(self.password), "desc": self.text, "type": "link_monster",
                "position": "attack", "attack": self.attack.value, "link_rating": self.link_rating.value,
                "card_type": self.card_type, "monster_type": self.monster_type.value, "attribute": self.attribute.value,
                "link_arrows": "apple", "attacks": self.attack_count, "global_id": self.global_id}


class PendulumMonster(Monster):
    def __init__(self):
        super().__init__()
        self.effect = None
        self.pendulum_scale = 0
        self.defense_mode = False
        self.effect = None
        self.is_set = False


class NormalPendulumMonster(NormalMonster, PendulumMonster):
    pass


class EffectPendulumMonster(EffectMonster, PendulumMonster):
    pass


class RitualPendulumMonster(RitualMonster, PendulumMonster):
    pass


class FusionPendulumMonster(FusionMonster, PendulumMonster):
    pass


class SynchroPendulumMonster(SynchroMonster, PendulumMonster):
    pass


class XyzPendulumMonster(XyzMonster, PendulumMonster):
    pass
