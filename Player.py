from Field import PlayerField
from Zones import Hand


class Player:
    def __init__(self, player_1):
        self.player_1 = player_1
        self.lp = 8000
        self.normal_summon_count = 1
        self.game_conditions = []
        self.field = PlayerField(self)
        self.hand = Hand(self)

    def get_json(self):
        return {"player": 1 if self.player_1 else 2, "lp": self.lp, "normal_summon_count": self.normal_summon_count}

    @property
    def deck(self):
        return self.field.deck

    @property
    def extra_deck(self):
        return self.field.extra_deck

    @property
    def graveyard(self):
        return self.field.graveyard

    @property
    def monster_zones(self):
        return self.field.monster_zones

    @property
    def spell_trap_zones(self):
        return self.field.spell_trap_zones

    @property
    def field_zone(self):
        return self.field.field_zone

    @property
    def banished(self):
        return self.field.banished

