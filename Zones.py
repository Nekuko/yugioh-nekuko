import random

from ModifiableAttribute import Owner


class Zones:
    def __init__(self, zones, owner=None):
        self.zones = zones
        self.owner = Owner(owner)

    def __str__(self):
        cards = []
        for zone in self.zones:
            if zone.card:
                cards.append(zone.card)
        return f'{", ".join([str(card.name) for card in cards])}'

    def get_all_cards(self):
        return [zone.card for zone in self.zones if zone.card]

    def get_occupied_zones(self):
        return [zone for zone in self.zones if zone.card]

    def get_available_zones(self):
        return [zone for zone in self.zones if not zone.card]

    def get_zone_from_card_name(self, name):
        for zone in self.zones:
            if zone.card:
                if zone.card.name.value == name:
                    return zone

    def get_zone_from_card_id(self, global_id):
        for zone in self.zones:
            if zone.card:
                if zone.card.global_id == global_id:
                    return zone

    def get_json(self):
        return [zone.get_json() for zone in self.zones]

    def __iter__(self):
        return iter(self.zones)


class MainMonsterZones(Zones):
    def __init__(self, zones, owner=None):
        super().__init__(owner)
        self.zones = zones


class SpellTrapZones(Zones):
    def __init__(self, zones, owner=None):
        super().__init__(owner)
        self.zones = zones


class ExtraMonsterZones(Zones):
    def __init__(self, zones, owner=None):
        super().__init__(owner)
        self.zones = zones


class Zone:
    def __init__(self, owner):
        self.card = None
        self.owner = Owner(owner)

    def set_card(self, card):
        self.card = card
        self.assign_ownership()

    def assign_ownership(self):
        if self.card:
            self.card.owner.current_owner = self.owner.original

    def add_card(self, card):
        self.card = card
        self.assign_ownership()

    def pop_card(self):
        card = self.card
        self.card = None
        return card

    def get_json(self):
        if not self.card:
            return {}

        return self.card.get_json()


class MonsterZone(Zone):
    def __init__(self, owner):
        super().__init__(owner)

    def set_card(self, card):
        self.card = card
        self.assign_ownership()
        if not hasattr(self.card, "is_set"):
            return

        if hasattr(self.card, "defense_mode"):
            if self.card.is_set and not self.card.defense_mode:
                self.card.is_set = False
        else:
            if self.card.is_set:
                self.card.is_set = False


class SpellTrapZone(Zone):
    def __init__(self, owner):
        super().__init__(owner)

    def set_card(self, card):
        self.card = card
        self.assign_ownership()

        if hasattr(self.card, "defense_mode"):
            self.card.defense_mode = False
            if hasattr(self.card, "is_set"):
                self.card.is_set = False


class PendulumZone(SpellTrapZone):
    def __init__(self, owner):
        super().__init__(owner)


class FieldZone(Zone):
    def __init__(self, owner):
        super().__init__(owner)


class ExtraMonsterZone(MonsterZone):
    def __init__(self, owner):
        super().__init__(owner)


class Location:
    def __init__(self, owner):
        self.cards = []
        self.owner = Owner(owner)

    def get_json(self):
        lst = []
        for card in self.cards:
            json = card.get_json()
            json["index"] = self.cards.index(card)
            lst.append(json)
        return lst

    def add_card(self, card):
        card.is_set = False
        if hasattr(card, "defense_mode"):
            card.defense_mode = False

        if hasattr(card, "set_turn"):
            card.set_turn = -1

        self.cards.append(card)
        self.assign_ownership()

    def set_card(self, card, index):
        card.is_set = False
        if hasattr(card, "defense_mode"):
            card.defense_mode = False

        if not self.cards:
            self.add_card(card)
        else:
            self.cards[index] = card
        self.assign_ownership()

    def assign_ownership(self):
        for card in self.cards:
            card.owner.current_owner = self.owner

    def pop_card(self, index):
        return self.cards.pop(index)

    def __str__(self):
        return f'{", ".join([str(card.name) for card in self.cards])}'

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def populate(self, cards):
        self.cards = cards


class Graveyard(Location):
    def __init__(self, owner):
        super().__init__(owner)


class Banished(Location):
    def __init__(self, owner):
        super().__init__(owner)

    def add_card(self, card):
        if hasattr(card, "defense_mode"):
            card.defense_mode = False

        self.cards.append(card)
        self.assign_ownership()

    def set_card(self, card, index):
        if hasattr(card, "defense_mode"):
            card.defense_mode = False

        if not self.cards:
            self.add_card(card)
        else:
            self.cards[index] = card
        self.assign_ownership()


class Deck(Location):
    def __init__(self, owner):
        super().__init__(owner)

    @property
    def top_card(self):
        return self.cards[-1]

    @property
    def bottom_card(self):
        return self.cards[0]


class ExtraDeck(Location):
    def __init__(self, owner):
        super().__init__(owner)


class Hand(Location):
    def __init__(self, owner):
        super().__init__(owner)
