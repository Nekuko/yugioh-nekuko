from Action import Action
from Exceptions import InvalidActionException


class SetSpellTrap(Action):
    def __init__(self, simulator):
        super().__init__(simulator)

    def perform(self, card, target):
        origin = self.simulator.find_card(card)
        if not self.can_perform(origin, target):
            raise InvalidActionException

        card.face_down = True
        self.simulator.move_card(origin, target)

    def can_perform(self, origin, target):
        # add about card itself
        # add about game state restriction
        if not origin:
            return False

        if target.card:
            return False

        return True
