class Action:
    def __init__(self, simulator):
        self.simulator = simulator
        self.action_results = []
        self.complete = False

    def can_activate(self):
        return True

    def perform(self, *args):
        pass

    def get_action_result(self):
        return self.action_results


# Draw requires the player who is drawing and how many cards are being drawn
class Draw(Action):
    def __init__(self, simulator, player_condition, value_condition):
        super().__init__(simulator)
        self.player_condition = player_condition
        self.value_condition = value_condition
        self.drawn_cards = []

    def perform(self):
        player = self.player_condition.get_value()
        value = self.value_condition.get_value()
        hand = player.hand
        deck = player.deck

        for _ in range(value):
            card = deck.pop_card(-1)
            hand.add_card(card)
            self.drawn_cards.append(card)

        self.complete = True

        return True, self.get_action_result()

    def can_activate(self):
        player = self.player_condition.get_value()
        value = self.value_condition.get_value()

        # Not enough cards to draw
        if len(player.deck) - value < 0:
            return False

        # Game state doesn't prevent drawing
        return True, self

    def get_action_result(self):
        return self.drawn_cards


class Negate(Action):
    def __init__(self, simulator, chain_link_condition):
        super().__init__(simulator)
        self.chain_link_condition = chain_link_condition
        self.negated_cards = []

    def perform(self):
        card = self.chain_link_condition.get_value(self.simulator)
        card.effect.is_negated = True

        self.complete = True

        return True, self


# Discard requires the cards being discarded and who is discarding them (for checking if its legal)
class Discard(Action):
    def __init__(self, simulator, player_condition, cards_condition):
        super().__init__(simulator)
        self.player_condition = player_condition
        self.cards_condition = cards_condition
        self.discarded_cards = []

    def perform(self):
        cards = self.cards_condition.get_value(self.simulator)
        if isinstance(cards, tuple):
            return cards

        for card in cards:
            origin = self.simulator.find_card(card)
            self.simulator.move_card(origin, (card.owner.original.graveyard, -1))

        self.complete = True

        return True, self

    def can_activate(self):
        # Game state doesn't prevent discarding
        player = self.player_condition.get_value()
        cards = self.cards_condition.get_value(self.simulator)
        for card in cards:
            if card not in player.hand.cards:
                return False

        return True

    def get_action_result(self):
        return self.discarded_cards


# ChangeAttack needs the value to change by, and what cards will be changed
class ChangeAttack(Action):
    def __init__(self, simulator, value, cards_condition):
        super().__init__(simulator)
        self.cards_condition = cards_condition
        self.value = value
        self.affected_cards = []

    def perform(self):
        cards = self.cards_condition.get_value(self.simulator)

        for card in cards:
            if not hasattr(card, "attack"):
                continue

            if card.is_set:
                continue

            if any(event[0] is self for event in card.attack.history):
                continue

            card.attack.history.append((self, self.value))

        self.complete = True

        return True, self


# ChangeDefense needs the value to change by, and what cards will be changed
class ChangeDefense(Action):
    def __init__(self, simulator, value, cards_condition):
        super().__init__(simulator)
        self.cards_condition = cards_condition
        self.value = value
        self.affected_cards = []

    def perform(self):
        cards = self.cards_condition.get_value(self.simulator)

        for card in cards:
            if not hasattr(card, "defense"):
                continue

            if card.is_set:
                continue

            if any(event[0] is self for event in card.defense.history):
                continue

            card.defense.history.append((self, self.value))

        self.complete = True

        return True, self


# Continuous needs the action being applied
class Continuous(Action):
    def __init__(self, simulator, action):
        super().__init__(simulator)
        self.action = action

    def perform(self):
        self.action.perform()

        self.complete = True

        return True, self


# Set requires what is being set, where it is being set to and who is setting it
class Set(Action):
    def __init__(self, simulator, cards_condition, location_condition, player_condition):
        super().__init__(simulator)
        self.cards_condition = cards_condition
        self.location_condition = location_condition
        self.player_condition = player_condition
        self.set_cards = []

    def perform(self):
        cards = self.cards_condition.get_value(self.simulator)
        location = self.location_condition.get_value(self.simulator)
        # Do check for multiple cards
        for card in cards:
            self.simulator.set_card(card, location)

        self.complete = True

        return True, self


# Equip requires what is being equipped, where it is being equipped and who is equipping it
class Equip(Action):
    def __init__(self, simulator, cards_condition, location_condition, player_condition):
        super().__init__(simulator)
        self.cards_condition = cards_condition
        self.location_condition = location_condition
        self.player_condition = player_condition
        self.equipped_cards = []

    def perform(self):
        cards = self.cards_condition.get_value(self.simulator)
        location = self.location_condition.get_value(self.simulator)
        # Do check for multiple cards
        for card in cards:
            self.simulator.set_card(card, location)

        self.complete = True

        return True, self


# Destroy requires what is being destroyed
class Destroy(Action):
    def __init__(self, simulator, cards_condition, target_specification):
        super().__init__(simulator)
        self.cards_condition = cards_condition
        self.target_specification = target_specification
        self.destroyed_cards = []

    def perform(self):
        cards = self.cards_condition.get_value(self.simulator)
        for card in cards:
            origin = self.simulator.find_card(card)
            # add about target specifications (those targets / them)
            # add this
            # Check if card can be destroyed
            self.simulator.move_card(origin, (card.owner.original.graveyard, -1))

        self.complete = True

        return True, self

    def get_action_result(self):
        return self.destroyed_cards


# Return requires what is being returned and where it is being returned to
class Return(Action):
    def __init__(self, simulator, cards_condition, location_condition, target_specification):
        super().__init__(simulator)

        self.cards_condition = cards_condition
        self.location_condition = location_condition
        self.target_specification = target_specification
        self.returned_cards = []

    def perform(self):
        cards = self.cards_condition.get_value(self.simulator)
        location = self.location_condition.get_value(self.simulator)
        for card in cards:
            self.simulator.return_card(card, location)

        self.complete = True

        return True, self

    def get_action_result(self):
        return self.returned_cards


# Target requires the cards being targeted and who is targeting them
class Target(Action):
    def __init__(self, simulator, cards_condition):
        super().__init__(simulator)
        self.cards_condition = cards_condition
        self.targeted_cards = []

    def perform(self):
        cards = self.cards_condition.get_value(self.simulator)
        if isinstance(cards, tuple):
            return cards

        for card in cards:
            self.targeted_cards.append(card)

        self.complete = True

        return True, self

    def get_action_result(self):
        return self.targeted_cards


