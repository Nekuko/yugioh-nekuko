from Action import Draw, Target, Destroy, Return
from Conditions.Condition import PlayerCondition, ValueCondition, CardCondition, SelectionCondition, LocationCondition, \
    ResultCondition
from Field import Field
from Material import SynchroMaterial, LinkMaterial
from Monster import Monster, SynchroMonster, LinkMonster, EffectMonster, NormalMonster
from Player import Player
from Spell import Spell
from TargetSpecification import TargetSpecification
from Trap import Trap
from Zones import Hand, Deck, ExtraDeck

import openai
prompt = """
I want you to generate a machine-understandable representation of the effects of Yu-Gi-Oh cards given their text. The only text you will need to evaluate is the text given in quotation marks. Following the question marks will be the type of card in brackets. Do not give any other text aside from the translation and do not explain it.

Any text before a ";" is the cost of a card and must be the first item in the returned list.
If and is in a card it may have multiple effects and two effects with similar context may need to be generated. If a continous effect has an and both effects must have Continous surrounding them.

The actions are card can have, and what the action needs to be passed and in what order is as follows:
Target: CardCondition
Destroy: CardCondition
Return: CardCondition
Draw: PlayerCondition, ValueCondition
SpecialSummon: CardCondition
ChangeAttack: Integer, AllCondition
ChangeDefense: Integer, AllCondition
Continuous: The action that will be continuous

The part of the card that relates to that effect will be surrounded by the corresponding keyword in uppercase letters. For example, Draw(). A unique action Continuous only applies to Field Spells and Continuous Spells any effect that changes attack or defense will be surrounded in the Continuous action. Each action will require the simulator to be passed, as well as the conditions that the action needs to function. All actions need to be passed 'simulator' as their first parameter.

The conditions, and the order of their parameters are as follows:
AllCondition: LocationCondition
LocationCondition: list of location types
CardCondition: SelectionCondition or ResultCondition. (ResultCondition will be used if the effect has a cost and this CardCondition is in an effect after the cost)
SelectionCondition: LocationCondition
ValueCondition: Integer
PlayerCondition: only card.effect
ResultCondition: type(cost)

The different types are as follows: Monster, Spell, Trap, Field, Hand, Deck, Graveyard, Light, Dark.

The text "Target 1 Spell/Trap on the field; destroy that target" can be translated as follows:

[Target(simulator, CardCondition(card.effect, SelectionCondition(card.effect, LocationCondition(card.effect, [Field]), ValueCondition(card.effect, 1), [Spell, Trap])), Destroy(simulator, CardCondition(card.effect, ResultCondition(card.effect, type(cost)))))]

For the text "Target 1 monster on the field; return that target to the hand.", the machine-understandable representation is:

[Target(simulator, CardCondition(card.effect, SelectionCondition(card.effect, LocationCondition(card.effect, [Field]), ValueCondition(card.effect, 1), [Monster])), Return(simulator, CardCondition(card.effect, ResultCondition(card.effect, type(cost)))))].

"Draw 3 cards, then discard 2 cards." (Normal Spell)
"""


class CardTranslatorGPT:
    def __init__(self, simulator):
        self.simulator = simulator
        self.text = ""
        openai.api_key = ""
        self.model = "text-davinci-002"

    def response(self, prompt):
        return eval(openai.Completion.create(
            engine=self.model,
            prompt=prompt,
            max_tokens=2048
        ))


class CardTranslator:
    def __init__(self, simulator):
        self.simulator = simulator
        self.card = None
        self.key_terms_map = {"draw": DrawItem, "draws": DrawItem, "target": TargetItem, "destroy": DestroyItem, "return": ReturnItem}
        self.card_type_map = {"effect": EffectMonster, "normal": NormalMonster, "monster": Monster, "spell": Spell,
                              "trap": Trap, "spell/trap": [Spell, Trap]}
        self.zone_type_map = {"field": Field, "hand": Hand, "deck": Deck, "extra deck": ExtraDeck}

    def add_material(self, card):
        self.card = card
        if isinstance(card, SynchroMonster):
            return self._add_synchro()

        if isinstance(card, LinkMonster):
            return self._add_link()

    def _add_link(self):
        material = LinkMaterial()
        material.text = self.card.text.split("\n")[0]
        split_text = material.text.split()

        value, condition = split_text[0:2]
        if "+" in value:
            value = value[:-1]
            material.multiple = True
            material.value = int(value)

        material.condition = self.card_type_map[condition.lower()]

        self.card.material = material

        return self.card

    def _add_synchro(self):
        material = SynchroMaterial()
        material.text = self.card.text.split("\n")[0]
        split_text = material.text.split()
        tuner_index = split_text.index("Tuner")
        non_tuner_index = split_text.index("non-Tuner")
        tuner_text = split_text[:tuner_index]
        non_tuner_text = split_text[tuner_index+2:non_tuner_index]

        for text in tuner_text:
            if text[0].isdigit():
                material.tuner_count = text

        for text in non_tuner_text:
            if text[0].isdigit():
                if "+" in text:
                    material.non_tuner_count = text[:-1]
                    material.multiple_non_tuners = True
                else:
                    material.non_tuner_count = text

        self.card.material = material

        return self.card

    def add_effect(self, card):
        self.card = card
        actions = []
        cost_object = []
        effect_object = []
        converted = self.convert_text(self.card.text)

        for item in converted:
            text = item.split_text
            if isinstance(item, Cost):
                cost = self.key_terms_map[text[0].lower()](self)
                cost_object = cost.create(text[1:])

            if isinstance(item, Effect):
                effect = self.key_terms_map[text[0].lower()](self)
                if cost_object:
                    effect_object = effect.create(text[1:], cost_object)
                else:
                    effect_object = effect.create(text[1:])

        if cost_object:
            self.card.effect.costs.append(cost_object)

        self.card.effect.actions.append(effect_object)

        return self.card

    def convert_text(self, text):
        space_split = text.split()
        lst = []

        current_text = []
        for string in space_split:
            if string[-1] == ";":
                current_text.append(string[:-1])
                lst.append(Cost(current_text))
                current_text = []
                continue

            current_text.append(string)

        lst.append(Effect(current_text))
        return lst


class DrawItem:
    def __init__(self, translator):
        self.translator = translator
        self.action = Draw
        self.unneeded_words = ["your", "cards", "card"]
        self.structures = [[(str, Player), (int, int)], [(int, int)]]

    def create(self, text):
        text = [token for token in text if token not in self.unneeded_words]
        structure = [s for s in self.structures if len(text) == len(s)][0]
        simulator = self.translator.simulator
        card = self.translator.card

        effect = [simulator, None, None]
        for t, s in zip(text, structure):
            initial, final = s
            if t.isdigit():
                effect[2] = ValueCondition(card.effect, int(t))

            if initial is str and not t.isdigit():
                effect[1] = PlayerCondition(card.effect, simulator.non_turn_player)
        if None in effect:
            effect[1] = PlayerCondition(card.effect)

        return Draw(effect[0], effect[1], effect[2])


class DestroyItem:
    def __init__(self, translator):
        self.translator = translator
        self.action = Destroy
        self.structures = []
        self.unneeded_words = []

    def create(self, text, cost=None):
        simulator = self.translator.simulator
        text = [token for token in text if token not in self.unneeded_words]
        # structure = [s for s in self.structures if len(text) == len(s)][0]
        structure = []
        card = self.translator.card

        effect = []
        for t, s in zip(text, structure):
            initial, final = s

        return Destroy(simulator, CardCondition(card.effect, ResultCondition(card.effect, type(cost))),
                       TargetSpecification.THEM)


class ReturnItem:
    def __init__(self, translator):
        # Target takes a card condition
        self.translator = translator
        self.action = Return
        self.unneeded_words = ["to", "the"]

    def create(self, text, cost=None):
        text = [token for token in text if token not in self.unneeded_words]
        simulator = self.translator.simulator
        card = self.translator.card
        location = ""

        for string in text:
            lower_string = string.lower().replace(".", "")

            if lower_string in self.translator.zone_type_map:
                location = self.translator.zone_type_map[lower_string]
                if not isinstance(location, list):
                    location = [location]

        if cost:
            return Return(simulator, CardCondition(card.effect, ResultCondition(card.effect, type(cost))),
                          LocationCondition(card.effect, location, PlayerCondition(card.effect)),
                          TargetSpecification.THAT_TARGET)


class TargetItem:
    def __init__(self, translator):
        # Target takes a card condition
        self.translator = translator
        self.action = Target

    def create(self, text):
        simulator = self.translator.simulator
        card = self.translator.card
        value = -1
        conditions = []
        location = ""
        for string in text:
            if string.isdigit():
                value = int(string)

            lower_string = string.lower()

            if lower_string in self.translator.card_type_map:
                conditions = self.translator.card_type_map[lower_string]
                if not isinstance(conditions, list):
                    conditions = [conditions]

            elif lower_string in self.translator.zone_type_map:
                location = self.translator.zone_type_map[lower_string]
                if not isinstance(location, list):
                    location = [location]

        return Target(simulator, CardCondition(card.effect, SelectionCondition(card.effect,
                      LocationCondition(card.effect, location), ValueCondition(card.effect, value), *conditions)))


class Effect:
    def __init__(self, split_text):
        self.split_text = split_text


class Cost:
    def __init__(self, split_text):
        self.split_text = split_text

