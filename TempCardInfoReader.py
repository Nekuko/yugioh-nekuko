import pandas as pd

from ModifiableAttribute import Attack, Attribute, MonsterType, Defense, Level, LinkRating, LinkArrows, PendulumScale, \
    Rank, Name
from Monster import NormalMonster, EffectMonster, RitualMonster, XyzMonster, SynchroMonster, FusionMonster, \
    LinkMonster, NormalPendulumMonster, EffectPendulumMonster, FusionPendulumMonster, SynchroPendulumMonster, \
    RitualPendulumMonster, XyzPendulumMonster, Token

from Spell import NormalSpell, FieldSpell, EquipSpell, ContinuousSpell, QuickPlaySpell, RitualSpell, Spell
from Trap import NormalTrap, CounterTrap, ContinuousTrap, Trap

df = pd.read_csv('cards.csv')
name = 'Blue-Eyes White Dragon'


def get_card_class(card_data):
    card_type_dict = {'normal': NormalMonster, 'effect': EffectMonster, 'ritual': RitualMonster,
                      'fusion': FusionMonster, 'synchro': SynchroMonster, 'xyz': XyzMonster,
                      'link': LinkMonster, 'normal_pendulum': NormalPendulumMonster,
                      'effect_pendulum': EffectPendulumMonster, 'ritual_pendulum': RitualPendulumMonster,
                      'fusion_pendulum': FusionPendulumMonster, 'synchro_pendulum': SynchroPendulumMonster,
                      'xyz_pendulum': XyzPendulumMonster, 'spell': 'Spell', 'trap': 'Trap', 'token': Token}

    frame_type = card_data['frameType'].values[0]

    card = card_type_dict[frame_type]

    if not isinstance(card, str):
        return card

    race = card_data['race'].values[0]

    if card == 'Spell':
        spell_type_dict = {'Normal': NormalSpell, 'Field': FieldSpell, 'Equip': EquipSpell, 'Continuous':
                           ContinuousSpell, 'Quick-Play': QuickPlaySpell, 'Ritual': RitualSpell}

        return spell_type_dict[race]

    if card == 'Trap':
        trap_type_dict = {'Normal': NormalTrap, 'Continuous': ContinuousTrap, 'Counter': CounterTrap}

        return trap_type_dict[race]


def load_monster_data(card_object, card_data):
    card_type = card_data['type'].values[0]
    desc = card_data['desc'].values[0]

    card_object.attack = Attack(card_data['atk'].values[0])
    card_object.monster_type = MonsterType(card_data['race'].values[0])
    card_object.attribute = Attribute(card_data['attribute'].values[0])

    if 'Tuner' in card_type:
        card_object.is_tuner = True

    if 'Spirit' in card_type:
        card_object.is_spirit = True

    if 'Gemini' in card_type:
        card_object.is_gemini = True

    if 'Toon' in card_type:
        card_object.is_toon = True

    if 'Flip' in card_type:
        card_object.is_flip = True

    if 'Pendulum' in card_type:
        card_object.pendulum_scale = PendulumScale(card_data['scale'].values[0])

    if 'Normal' in card_type:
        card_object.lore = desc
        card_object.defense = Defense(card_data['def'].values[0])
        card_object.level = Level(card_data['level'].values[0])

        return card_object

    card_object.effect = desc

    if 'XYZ' in card_type:
        card_object.rank = Rank(card_data['rank'].values[0])
        return card_object

    if 'Link' in card_type:
        card_object.link_rating = LinkRating(card_data['linkval'].values[0])
        card_object.link_arrows = LinkArrows(card_data['linkmarkers'].values[0])
        return card_object

    card_object.defense = Defense(card_data['def'].values[0])

    return card_object


def data_to_object(card_data):
    card_object = get_card_class(card_data)()

    card_object.password = card_data['id']
    card_object.name = Name(card_data['name'].values[0])

    if isinstance(card_object, Spell) or isinstance(card_object, Trap):
        card_object.effect = card_data['desc'].values[0]

        return card_object

    return load_monster_data(card_object, card_data)

a = data_to_object(df.loc[df['name'] == name])
print(a.name)
