from itertools import zip_longest

from Action import Continuous
from Effect.Conjunction import Conjunction
from Log import CostLog, ActionLog, ConjunctionLog


class Effect:
    def __init__(self, card):
        self.card = card
        self.activate_location = ""
        self.costs = []
        self.cost_conjunctions = []
        self.actions = []
        self.action_conjunctions = []
        self.activation_conditions = []
        self.is_negated = False
        self.can_cost_be_payed_move_this = False
        self.is_chainable = False
        self.is_condition_met_move_this = False
        self.action_results = []
        self.logging = []
        self.choice = []
        self.choices = 0

    def temp_print_log(self):
        for l in self.logging:
            print(l)

    def log(self, event):
        self.logging.append(event)

    def resolve(self, simulator):
        for cost, conjunction in zip_longest(self.costs, self.cost_conjunctions, fillvalue=Conjunction.NONE):
            if cost.complete:
                continue

            if conjunction is conjunction.NONE:
                result = cost.perform()
                if result[0] == "Selection":
                    return result

                self.action_results.append(result)
                self.log(CostLog(result))
                self.choice = []

            elif conjunction is conjunction.THEN:
                result = cost.perform()
                if result[0] == "Selection":
                    return result

                self.action_results.append(result)
                self.log(CostLog(result))
                self.log(ConjunctionLog(conjunction.THEN))
                self.choice = []
                continue

        if self.is_negated:
            return True, self

        for action, conjunction in zip_longest(self.actions, self.action_conjunctions, fillvalue=Conjunction.NONE):
            if conjunction is conjunction.NONE:
                if isinstance(action, Continuous):
                    simulator.continuous_effects.append(action)

                result = action.perform()
                self.action_results.append(result)
                self.log(ActionLog(result))

            elif conjunction is conjunction.THEN:
                if isinstance(action, Continuous):
                    simulator.continuous_effects.append(action)
                result = action.perform()
                self.action_results.append(result)
                self.log(ActionLog(result))
                self.log(ConjunctionLog(conjunction.THEN))
                continue

        return True, self

        # Then create the "destroy" effect of twin twisters (using "them") and add it all together for an entire effect
