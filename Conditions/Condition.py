from enum import Enum
from Log import ConditionLog


class Conditions(Enum):
    VALUE_CONDITION = 1
    PLAYER_CONDITION = 2
    CARD_TYPE_CONDITION = 3
    CARD_CONDITION = 4
    SELECTION_CONDITION = 5
    RANGE_CONDITION = 6
    CONTINUOUS_CONDITION = 7
    CHAIN_LINK_CONDITION = 8


class Condition:
    def __init__(self, effect):
        self.effect = effect
        self.condition_type = None

    @property
    def get_value(self, *args):
        return None

    def log(self):
        self.effect.log(ConditionLog(self))


class ValueCondition(Condition):
    def __init__(self, effect, value):
        super().__init__(effect)
        self.condition_type = Conditions.VALUE_CONDITION
        self.value = value

    def get_value(self):
        self.log()
        return self.value


class PlayerCondition(Condition):
    def __init__(self, effect, player=None):
        super().__init__(effect)
        self.condition_type = Conditions.PLAYER_CONDITION
        self.player = player

    def get_value(self):
        if self.player:
            return self.player

        return self.effect.card.owner.value


class AllCondition(Condition):
    def __init__(self, effect, location_condition, *args):
        super().__init__(effect)
        self.location_condition = location_condition
        self.conditions = args

    def get_value(self, simulator):
        cards = simulator.get_all_cards_in_locations(self.location_condition.get_value(simulator))
        filtered_cards = simulator.filter_cards(cards, self.conditions)

        return filtered_cards


class ActivateCondition(Condition):
    def __init__(self, effect, *args):
        super().__init__(effect)
        self.conditions = args

    def get_value(self, simulator):
        if not simulator.chain_link:
            return False

        if all(simulator.compare_card(self.effect.card, c) for c in self.conditions):
            return True

        return False


class ChainLinkCondition(Condition):
    def __init__(self, effect):
        super().__init__(effect)
        self.condition_type = Conditions.CHAIN_LINK_CONDITION

    def get_value(self, simulator):
        return simulator.chain_link[simulator.chain_link.index(self.effect.card)-1]


class CardTypeCondition(Condition):
    def __init__(self, effect, *args):
        super().__init__(effect)
        self.condition_type = Conditions.CARD_TYPE_CONDITION
        self.args = args


class CardCondition(Condition):
    def __init__(self, effect, *args):
        super().__init__(effect)
        self.condition_type = Conditions.CARD_CONDITION
        self.cards = args

    def get_value(self, simulator):
        if len(self.cards) == 1:
            if isinstance(self.cards[0], SelectionCondition):
                condition = self.cards[0].get_value(simulator)
                if isinstance(condition, tuple):
                    return condition
                self.log()
                return condition

            if isinstance(self.cards[0], ResultCondition):
                # Potentially add if False if returned
                self.log()
                return self.cards[0].get_value()[1].get_action_result()

        return self.cards


# Where selection is from, how many are being selected and what is being selected (types)
class SelectionCondition(Condition):
    def __init__(self, effect, location_condition, value, *args):
        super().__init__(effect)
        self.condition_type = Conditions.SELECTION_CONDITION
        self.location_condition = location_condition
        self.value = value
        self.conditions = args

    def get_value(self, simulator):
        cards = simulator.get_all_cards_in_locations(self.location_condition.get_value(simulator))
        filtered_cards = simulator.filter_cards(cards, self.conditions)

        # Change this to only use one method and do checking inside simulator
        if isinstance(self.value, ValueCondition):
            self.log()
            if not self.effect.choice:
                return "Selection", (filtered_cards, self.value)

            return self.effect.choice

        if isinstance(self.value, RangeCondition):
            self.log()
            return simulator.temp_get_range_selection(filtered_cards, self.value)

        return filtered_cards


# The locations(s) being chosen (Classes) from and if a player is given make it their locations
class LocationCondition(Condition):
    def __init__(self, effect, locations, player_condition=None):
        super().__init__(effect)
        self.condition_type = Conditions.SELECTION_CONDITION
        self.locations = locations
        self.player_condition = player_condition

    def get_value(self, simulator):
        locations = simulator.get_locations_from_types(self.locations)

        if self.player_condition:
            self.log()
            locations = [location for location in locations if location.owner.value == self.player_condition.get_value()]
        self.log()
        return locations


# The range being selected from
class RangeCondition(Condition):
    def __init__(self, effect, start, stop, step=1):
        super().__init__(effect)
        self.condition_type = Conditions.RANGE_CONDITION
        self.start = start
        self.end = stop
        self.step = step

    def get_value(self):
        self.log()
        return self.start, self.end, self.step


# Needs the action that it is getting a result from
class ResultCondition(Condition):
    def __init__(self, effect, action_type):
        super().__init__(effect)
        self.action_type = action_type

    def get_value(self):
        result = [result for result in self.effect.action_results if result[0] is True
                  and type(result[1]) is self.action_type][0]

        self.log()
        return result

"""simulator = "Bob"

class Card:
    def __init__(self):
        self.effect = None

card = Card()

a = Draw(simulator, PlayerCondition(card.effect), ValueCondition(card.effect, 2))"""


