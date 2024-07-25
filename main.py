import random

from Action import Discard, Target, Destroy
from Actions.SetSpellTrap import SetSpellTrap
from Card import Card
from Conditions.Condition import SelectionCondition, PlayerCondition, CardCondition, ValueCondition, LocationCondition, \
    RangeCondition, ResultCondition
from Effect.Conjunction import Conjunction
from Effect.Cost import Cost
from Effect.Effect import Effect
from Field import Field
from ModifiableAttribute import Owner
from Simulator import Simulator
from Spell import Spell
from Summon import Summons
from TargetSpecification import TargetSpecification
from Trap import Trap
from Zones import Hand

sim = Simulator()
sim.start()

obelisk = sim.card_builder.name_to_object('Obelisk the Tormentor')
obelisk.owner = Owner(sim.player_1)
sim.player_1.monster_zones.zones[0].card = obelisk

slifer = sim.card_builder.name_to_object('Slifer the Sky Dragon')
slifer.owner = Owner(sim.player_1)
sim.player_1.monster_zones.zones[1].card = slifer

avram = sim.card_builder.name_to_object('Mekk-Knight Avram')
avram.owner = Owner(sim.player_1)
sim.player_1.hand.cards.append(avram)

cyber_dragon = sim.card_builder.name_to_object('Cyber Dragon')
cyber_dragon.owner = Owner(sim.player_1)
sim.player_1.hand.cards.append(cyber_dragon)

blue_eyes = sim.card_builder.name_to_object('Blue-Eyes White Dragon')
blue_eyes.owner = Owner(sim.player_1)
sim.player_1.hand.cards.append(blue_eyes)

print([card.name.value for card in sim.get_all_summonable_cards()])
print('Hand:', sim.player_1.hand)
print('Graveyard:', sim.player_1.graveyard)
print('Field', [card.name.value for card in sim.player_1.monster_zones.get_all_cards()])

sim.summon_cards([blue_eyes], [sim.player_1.monster_zones.zones[4]], [Summons.NORMAL], [obelisk, slifer])

print([card.name.value for card in sim.get_all_summonable_cards()])
print('Hand:', sim.player_1.hand)
print('Graveyard:', sim.player_1.graveyard)
print('Field', [card.name.value for card in sim.player_1.monster_zones.get_all_cards()])





# Discard 1 card, then target up to 2 Spell/Traps on the field; destroy them

"""

Monsters
set monsters can be flip summoned to face up attack

monsters can be changed to defense (if not link)
create get_battle_value function to get attack / defense
defense mosnters can be changed to attack
if monster battled in main 2 it cannot change position

"""

"""

tt = sim.card_builder.name_to_object('Twin Twisters')
spell = sim.card_builder.name_to_object('Card of Demise')
spell.owner = Owner(sim.player_2)
spell_2 = sim.card_builder.name_to_object('Upstart Goblin')
spell_2.owner = Owner(sim.player_2)
sim.player_2.field.spell_trap_zones.zones[0].card = spell
sim.player_2.field.spell_trap_zones.zones[1].card = spell_2
tt.owner = Owner(sim.player_1)

twin_twister_cost = Cost(Discard(sim, PlayerCondition(tt.effect), CardCondition(tt.effect, SelectionCondition(tt.effect,
                         LocationCondition(tt.effect, [Hand]), ValueCondition(tt.effect, 1)))))

twin_twister_cost_2 = Cost(Target(sim, CardCondition(tt.effect, SelectionCondition(tt.effect,
                           LocationCondition(tt.effect, [Field]), RangeCondition(tt.effect, 1, 2), Spell, Trap))))

twin_twister_effect = Destroy(sim, CardCondition(tt.effect, ResultCondition(tt.effect, Target)),
                              TargetSpecification.THEM)


tt.effect.costs.append(twin_twister_cost)
tt.effect.costs.append(twin_twister_cost_2)
tt.effect.actions.append(twin_twister_effect)
tt.effect.cost_conjunctions.append(Conjunction.THEN)

for x in range(3):
    a = sim.card_builder.name_to_object('Block Dragon')
    a.owner = Owner(sim.player_1)
    sim.player_1.hand.cards.append(a)

print(f'Player 1 Hand: {sim.player_1.hand}')
print(f'Player 1 Graveyard: {sim.player_1.graveyard}')
print(f'Player 2 Graveyard: {sim.player_2.graveyard}')
for zone in sim.player_2.field.spell_trap_zones.zones:
    print(zone.card)

sim.activate_card(tt)

print(f'Player 1 Hand: {sim.player_1.hand}')
print(f'Player 1 Graveyard: {sim.player_1.graveyard}')
print(f'Player 2 Graveyard: {sim.player_2.graveyard}')
for zone in sim.player_2.field.spell_trap_zones.zones:
    print(zone.card)"""


print("-------------------------")
for log in sim.log:
    print(log)
print("Done")
