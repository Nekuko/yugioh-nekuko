from enum import Enum


class Summons(Enum):
    NORMAL = 1
    TRIBUTE = 3
    SPECIAL = 2
    RITUAL = 4
    FUSION = 5
    SYNCHRO = 6
    XYZ = 7
    PENDULUM = 8
    LINK = 9
    SET = 10
    FLIP = 11
    NONE = 12


class Summon:
    def __init__(self, cards, locations, additional_types=None):
        self.cards = cards
        self.locations = locations
        self.summon_types = [Summons.NONE]
        if additional_types:
            for additional_type in additional_types:
                if additional_type in self.summon_types:
                    continue
                self.summon_types.append(additional_type)

    def get_card_location_pairs(self):
        return zip(self.cards, self.locations)


class NormalSummon(Summon):
    def __init__(self, cards, locations, materials=None, additional_types=None):
        super().__init__(cards, locations)
        self.materials = materials
        self.summon_types = [Summons.NORMAL]
        if additional_types:
            for additional_type in additional_types:
                if additional_type in self.summon_types:
                    continue
                self.summon_types.append(additional_type)

    def set_card_positions(self):
        for card in self.cards:
            if Summons.SET in self.summon_types:
                card.defense_mode = True
                card.is_set = True
            else:
                card.defense_mode = False
                card.is_set = False


class FlipSummon(Summon):
    def __init__(self, cards, locations=None):
        super().__init__(cards, locations)
        self.summon_types = [Summons.FLIP]

    def set_card_positions(self):
        for card in self.cards:
            card.defense_mode = False
            card.is_set = False


class SpecialSummon(Summon):
    def __init__(self, cards, locations, materials=None, additional_types=None):
        super().__init__(cards, locations, materials)
        self.materials = materials
        self.summon_types = [Summons.SPECIAL]
        if additional_types:
            for additional_type in additional_types:
                if additional_type in self.summon_types:
                    continue
                self.summon_types.append(additional_type)
