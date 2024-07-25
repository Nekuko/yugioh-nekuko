from Zones import MonsterZone, PendulumZone, SpellTrapZone, FieldZone, Deck, ExtraDeck, Graveyard, Banished, \
    ExtraMonsterZone, ExtraMonsterZones, MainMonsterZones, SpellTrapZones


class Field:
    def __init__(self, player_1, player_2):
        self.fields = [player_1.field, player_2.field]
        self.extra_monster_zones = ExtraMonsterZones([ExtraMonsterZone(None), ExtraMonsterZone(None)])

    def find_card(self, card):
        for zone in self.extra_monster_zones.zones:
            if zone.card == card:
                return zone

        for field in self.fields:
            location = field.find_card(card)
            if location:
                return location

    def get_json(self):
        return {"fields": [field.get_json() for field in self.fields],
                "extra_monster_zones": self.extra_monster_zones.get_json()}


class PlayerField:
    def __init__(self, player):
        self.player = player
        self.monster_zones = MainMonsterZones([MonsterZone(self), MonsterZone(self), MonsterZone(self),
                                               MonsterZone(self), MonsterZone(self)], self)
        self.spell_trap_zones = SpellTrapZones([PendulumZone(self), SpellTrapZone(self), SpellTrapZone(self),
                                                SpellTrapZone(self), PendulumZone(self)], self)
        self.field_zone = FieldZone(self)
        self.deck = Deck(self)
        self.extra_deck = ExtraDeck(self)
        self.graveyard = Graveyard(self)
        self.banished = Banished(self)

    def get_json(self):
        return {"player": f"{'1' if self.player.player_1 else '2'}",
                "monster_zones": self.monster_zones.get_json(),
                "spell_trap_zones": self.spell_trap_zones.get_json(),
                "field_zone": self.field_zone.get_json(),
                "deck": self.deck.get_json(),
                "extra_deck": self.extra_deck.get_json(),
                "graveyard": self.graveyard.get_json(),
                "banished": self.banished.get_json()
                }

    def find_card(self, card):
        for zone in self.monster_zones.zones:
            if zone.card == card:
                return zone

        for zone in self.spell_trap_zones.zones:
            if zone.card == card:
                return zone

        if self.field_zone.card == card:
            return self.field_zone

        if card in self.deck.cards:
            return self.deck, self.deck.cards.index(card)

        if card in self.extra_deck.cards:
            return self.extra_deck, self.extra_deck.cards.index(card)

        if card in self.graveyard.cards:
            return self.graveyard, self.graveyard.cards.index(card)

        if card in self.banished.cards:
            return self.banished, self.banished.cards.index(card)
