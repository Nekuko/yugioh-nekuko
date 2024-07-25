import pandas as pd

from Action import Draw, Continuous, ChangeAttack, ChangeDefense, Negate, Destroy
from Conditions.Condition import ValueCondition, PlayerCondition, CardCondition, AllCondition, LocationCondition, \
    ActivateCondition, ChainLinkCondition, ResultCondition
from Effect.Effect import Effect
from Field import Field
from ModifiableAttribute import Attack, Attribute, MonsterType, Defense, Level, LinkRating, LinkArrows, PendulumScale, \
    Rank, Name
from Monster import NormalMonster, EffectMonster, RitualMonster, XyzMonster, SynchroMonster, FusionMonster, \
    LinkMonster, NormalPendulumMonster, EffectPendulumMonster, FusionPendulumMonster, SynchroPendulumMonster, \
    RitualPendulumMonster, XyzPendulumMonster, Monster

from Spell import NormalSpell, FieldSpell, EquipSpell, ContinuousSpell, QuickPlaySpell, RitualSpell, Spell
from TargetSpecification import TargetSpecification
from Trap import NormalTrap, CounterTrap, ContinuousTrap, Trap


class CardBuilder:
    def __init__(self, simulator):
        self.simulator = simulator
        self.current_id = 0
        self.df = pd.read_csv('cards.csv')
        self.card_type_dict = {'normal': NormalMonster, 'effect': EffectMonster, 'ritual': RitualMonster,
                               'fusion': FusionMonster, 'synchro': SynchroMonster, 'xyz': XyzMonster,
                               'link': LinkMonster, 'spell': 'Spell', 'trap': 'Trap'}

    def assign_id(self, card):
        card.global_id = self.current_id
        self.current_id += 1

    def build_deck(self, deck):
        return [self.passcode_to_object(card) for card in deck]

    def passcode_to_object(self, passcode):
        return self.name_to_object(self.df.loc[self.df['id'] == int(passcode)]['name'].values[0])

    def name_to_object(self, name):
        card_data = self.df.loc[self.df['name'] == name]
        card_object = self._get_card_class(card_data)()

        self.assign_id(card_object)

        card_object.password = str(card_data['id'].values[0]).zfill(8)
        card_object.name = Name(card_data['name'].values[0])
        card_object.text = card_data['desc'].values[0]
        card_object.card_type = card_data['type'].values[0]

        if isinstance(card_object, Spell) or isinstance(card_object, Trap):
            card_object.other_type = card_data['race'].values[0]
            card_object.effect = Effect(card_object)

            if str(card_object.name.value) in ['Pot of Greed', "Mystical Space Typhoon", "Compulsory Evacuation Device"]:
                card_object = self.simulator.card_translator.add_effect(card_object)
                print(card_object)

            if str(card_object.name) in ["Luminous Spark"]:
                card_object.effect.actions.append(Continuous(self.simulator, ChangeAttack(self.simulator, 500,
                                                                                          AllCondition(
                                                                                              card_object.effect,
                                                                                              LocationCondition(
                                                                                                  card_object.effect,
                                                                                                  [Field])))))

                card_object.effect.actions.append(Continuous(self.simulator, ChangeDefense(self.simulator, -400,
                                                                                           AllCondition(
                                                                                               card_object.effect,
                                                                                               LocationCondition(
                                                                                                   card_object.effect,
                                                                                                   [Field])))))

            if str(card_object.name) in ["Dark Bribe"]:
                card_object.effect.activation_conditions.append(ActivateCondition(self.simulator, Spell, Trap))
                card_object.effect.actions.append(Draw(self.simulator, PlayerCondition(card_object.effect,
                                                                                       self.simulator.non_turn_player),
                                                       ValueCondition(card_object.effect, 1)))
                card_object.effect.actions.append(Negate(self.simulator, ChainLinkCondition(card_object.effect)))
                """card_object.effect.actions.append(Destroy(self.simulator, CardCondition(card_object.effect,
                                                                                        ResultCondition(
                                                                                            card_object.effect,
                                                                                            type(
                                                                                                card_object.effect.
                                                                                                costs[0]))),
                                                          TargetSpecification.THEM))"""

            return card_object

        return self._load_monster_data(card_object, card_data)

    def _load_monster_data(self, card_object, card_data):
        card_type = card_data['type'].values[0]
        desc = card_data['desc'].values[0]

        card_object.attack = Attack(card_data['atk'].values[0])
        card_object.monster_type = MonsterType(card_data['race'].values[0])
        card_object.attribute = Attribute(card_data['attribute'].values[0])

        if "Synchro" in card_type:
            card_object = self.simulator.card_translator.add_material(card_object)

        if 'Tuner' in card_type:
            card_object.is_tuner = True

        if 'Normal' in card_type:
            card_object.lore = desc
            card_object.defense = Defense(card_data['def'].values[0])
            card_object.level = Level(card_data['level'].values[0])

            return card_object

        card_object.effect = desc

        if 'XYZ' in card_type:
            card_object.defense = Defense(card_data['def'].values[0])
            card_object.rank = Rank(card_data['level'].values[0])
            return card_object

        if 'Link' in card_type:
            card_object = self.simulator.card_translator.add_material(card_object)
            card_object.link_rating = LinkRating(card_data['linkval'].values[0])
            card_object.link_arrows = LinkArrows(card_data['linkmarkers'].values[0].replace("[", "").replace("]", "").
                                                 replace("'", "").split(", "))
            return card_object

        card_object.defense = Defense(card_data['def'].values[0])
        card_object.level = Level(card_data['level'].values[0])

        return card_object

    def _get_card_class(self, card_data):
        frame_type = card_data['frameType'].values[0]

        card = self.card_type_dict[frame_type]

        if not isinstance(card, str):
            return card

        race = card_data['race'].values[0]

        if card == 'Spell':
            spell_type_dict = {'Normal': NormalSpell, 'Field': FieldSpell, 'Equip': EquipSpell,
                               'Continuous': ContinuousSpell, 'Quick-Play': QuickPlaySpell, 'Ritual': RitualSpell}

            return spell_type_dict[race]

        if card == 'Trap':
            trap_type_dict = {'Normal': NormalTrap, 'Continuous': ContinuousTrap, 'Counter': CounterTrap}

            return trap_type_dict[race]
