from Action import ChangeAttack, Continuous
from CardBuilder import CardBuilder
from CardTranslator import CardTranslator
from Field import Field
from Log import EffectLog, PhaseLog, TributeLog, SummonLog
from ModifiableAttribute import Owner, ModifiableAttribute
from Monster import Monster, FusionMonster, XyzMonster, SynchroMonster, LinkMonster, PendulumMonster
from Phase import DrawPhase, MainPhase1, StandbyPhase, BattlePhase, MainPhase2, EndPhase, Phase, Phases
from Player import Player
from Spell import NormalSpell, Spell, QuickPlaySpell, FieldSpell
from Summon import Summons, NormalSummon, FlipSummon, SpecialSummon
from Trap import Trap
from YDKReader import YDKReader
from Zones import Location, Zone, Deck, ExtraDeck, FieldZone, ExtraMonsterZone, Hand, SpellTrapZone, MonsterZone
from itertools import chain, combinations


class Simulator:
    def __init__(self):
        self.turn_player = None
        self.turn_number = 0
        self.player_1 = None
        self.player_2 = None
        self.field = None
        self.phases = []
        self.current_phase = Phases.NONE
        self.summons = []
        self.card_builder = CardBuilder(self)
        self.card_translator = CardTranslator(self)
        self.log = []
        self.choice = {}
        self.action_choice = {}
        self.chain_link = []
        self.is_resolving = False
        self.chain_choice = {}
        self.summoning_card = None
        self.summoning_zone = None
        self.current_material = []
        self.summon_position = None
        self.continuous_effects = []

    def start(self):
        self._populate()

    def get_json(self):
        json = self.field.get_json()
        json["turn"] = self.turn_number
        json["turn_player"] = 1 if self.turn_player is self.player_1 else 2
        json["players"] = [player.get_json() for player in [self.player_1, self.player_2]]
        json["phase"] = str(self.current_phase)
        json["hands"] = [hand.get_json() for hand in [self.player_1.hand, self.player_2.hand]]
        json["summonable"] = [(card[0], card[1].get_json()) for card in self.get_all_summonable_cards()]
        json["activatable"] = [card.get_json() for card in self.get_all_activatable_cards()]
        json["settable"] = [card.get_json() for card in self.get_all_settable_cards()]
        json["attackers"] = [card.get_json() for card in self.get_all_attackers()]
        self.get_all_link_arrow_zones()

        return json

    @property
    def non_turn_player(self):
        return [player for player in [self.player_1, self.player_2] if player is not self.turn_player][0]

    def apply_continuous(self):
        for continuous in self.continuous_effects:
            continuous.perform()

    def remove_continuous(self, effect):
        for card in self.get_all_cards_in_locations(self.get_all_locations()):
            for action in effect.actions:
                if isinstance(action, Continuous):
                    action = action.action
                    if isinstance(action, ChangeAttack):
                        if hasattr(card, "attack"):
                            updated_history = []
                            for event in card.attack.history:
                                if event[0] is not action:
                                    updated_history.append(event)
                            card.attack.history = updated_history

                        elif hasattr(card, "defense"):
                            updated_history = []
                            for event in card.defense.history:
                                if event[0] is not action:
                                    updated_history.append(event)
                            card.defense.history = updated_history

        for action in effect.actions:
            if action in self.continuous_effects:
                self.continuous_effects.remove(action)

        self.apply_continuous()

    def manage_move(self, data):
        origin, origin_card = data["origin"]
        origin = self.get_zone_from_code(origin)
        if issubclass(type(origin), Location):
            origin = (origin, origin_card["index"])

        target = data["target"]
        target = self.get_zone_from_code(target)

        if issubclass(type(target), Location):
            target = (target, -1)

        success, result = self.move_card(origin, target)

        if not success:
            return {"error": result}

        return result.get_json()

    def manage_position(self, data):
        position, card, location = data
        location = self.get_zone_from_code(location)
        if issubclass(type(location), Location):
            return {"error": "Cards in Locations cannot changed position"}

        card = location.card
        updated_card = self.change_card_position(card, position)

        return updated_card.get_json()

    def manage_phase(self, data):
        if data == "Next Turn":
            self.next_turn()
            return {"phase": str(self.current_phase)}
        else:
            phase = self.get_phase_by_string(data)
            if isinstance(phase, BattlePhase) and self.turn_number == 1:
                return {"phase": str(phase)}

            self.set_phase(phase.phase_type)

        return {"phase": str(phase)}

    def manage_link_summon(self, data):
        all_combinations = self.get_link_combinations(self.summoning_card)

        if "choice" in data:
            if isinstance(data["choice"], dict):
                card = self.get_card_by_id(data["choice"]["global_id"])
                self.current_material.append(card)

            else:
                self.summoning_zone = self.get_zone_from_code(data["choice"])

        all_material = False
        for combination in all_combinations:
            if all(material in combination for material in self.current_material) and \
                    len(combination) == len(self.current_material):
                all_material = True

        if not all_material:
            self.choice = {"original": "link"}

            applicable_combinations = []
            for combination in all_combinations:
                if all(material in combination for material in self.current_material):
                    applicable_combinations.append(combination)

            cards = []
            for combination in applicable_combinations:
                for card in combination:
                    if card not in self.current_material:
                        cards.append(card)

            return {"choice": {"material": [card.get_json() for card in cards]}}

        if not self.summoning_zone:
            self.choice = {"original": "link"}
            zones = [self.get_code_from_zone(zone) for zone in self.turn_player.monster_zones.get_available_zones()]
            for material in self.current_material:
                zones.append(self.get_code_from_zone(self.turn_player.monster_zones.get_zone_from_card_id(
                    material.global_id)))

            zones.extend([self.get_code_from_zone(zone) for zone in
                          self.get_available_extra_monster_zones(self.turn_player)])

            self.choice = {"original": "synchro"}
            return {"choice": {"zones": zones}}

        self.summoning_card.defense_mode = not self.summon_position

        success, result = self.summon_cards([self.summoning_card], [Summons.LINK], [self.summoning_zone],
                                            self.current_material)
        self.current_material = []
        self.summoning_zone = None
        self.summoning_card = None
        self.choice = {}

        return result.get_json()

    def manage_synchro_summon(self, data):
        all_combinations = self.get_synchro_tuner_combinations(self.summoning_card)
        all_tuners = []
        for combination in all_combinations:
            for card in combination:
                if card.is_tuner:
                    all_tuners.append(card)

        all_tuners = list(set(all_tuners))

        all_non_tuners = []
        for combination in all_combinations:
            for card in combination:
                if not card.is_tuner:
                    all_non_tuners.append(card)

        all_non_tuners = list(set(all_non_tuners))

        if "choice" in data:
            if isinstance(data["choice"], dict):
                card = self.get_card_by_id(data["choice"]["global_id"])
                self.current_material.append(card)

            else:
                self.summoning_zone = self.get_zone_from_code(data["choice"])

        if not self.current_material:
            self.choice = {"original": "synchro"}
            return {"choice": {"material": [card.get_json() for card in all_tuners]}}

        if len(self.current_material) == 1:
            self.choice = {"original": "synchro"}
            return {"choice": {"material": [card.get_json() for card in all_non_tuners]}}

        all_material = False
        for combination in all_combinations:
            if all(material in combination for material in self.current_material) and \
                    len(combination) == len(self.current_material):
                all_material = True

        if not all_material:
            self.choice = {"original": "synchro"}

            applicable_combinations = []
            for combination in all_combinations:
                if all(material in combination for material in self.current_material):
                    applicable_combinations.append(combination)

            cards = []
            for combination in applicable_combinations:
                for card in combination:
                    if card not in self.current_material:
                        cards.append(card)

            return {"choice": {"material": [card.get_json() for card in cards]}}

        if not self.summoning_zone:
            self.choice = {"original": "synchro"}
            zones = [self.get_code_from_zone(zone) for zone in self.turn_player.monster_zones.get_available_zones()]
            for material in self.current_material:
                zones.append(self.get_code_from_zone(self.turn_player.monster_zones.get_zone_from_card_id(
                    material.global_id)))

            zones.extend([self.get_code_from_zone(zone) for zone in
                          self.get_available_extra_monster_zones(self.turn_player)])

            self.choice = {"original": "synchro"}
            return {"choice": {"zones": zones}}

        self.summoning_card.defense_mode = not self.summon_position

        success, result = self.summon_cards([self.summoning_card], [Summons.SYNCHRO], [self.summoning_zone],
                                            self.current_material)
        self.current_material = []
        self.summoning_zone = None
        self.summoning_card = None
        self.summon_position = None
        self.choice = {}

        return result.get_json()

    def manage_extra_summon(self, data):
        card, zone, materials = None, None, None

        if not self.summoning_card:
            self.summoning_card = self.get_card_by_id(data["card"]["global_id"])
            self.summon_position = data["position"]

        if isinstance(self.summoning_card, SynchroMonster):
            return self.manage_synchro_summon(data)

        if isinstance(self.summoning_card, LinkMonster):
            return self.manage_synchro_summon(data)

        self.choice = {}

    def get_card_by_id(self, global_id):
        for card in self.get_all_cards_in_locations(self.get_all_locations()):
            if card.global_id == global_id:
                return card

    def get_available_extra_monster_zones(self, player):
        zones = []
        cards = self.get_all_cards_in_locations(self.field.extra_monster_zones)
        if any([player is card.owner.value for card in cards]):
            return []

        for zone in self.field.extra_monster_zones:
            if not zone.card:
                zones.append(zone)

        return zones

    def manage_summon(self, data):
        card, zone, tribute, is_set = None, None, None, None

        if self.choice:
            if "zones" in self.choice["info"].keys():
                card, zone, tribute = self.choice["old"]["card"], self.choice["old"]["zone"], \
                    self.choice["old"]["tributes"]

                zone = data

            if "material" in self.choice["info"].keys():
                card, zone, tribute = self.choice["old"]["card"], self.choice["old"]["zone"], \
                    self.choice["old"]["tributes"]

                tribute = data

            is_set = self.choice["old"]["set"]

        else:
            card, zone, tribute, is_set = data["card"], data["zone"], data["tributes"], data["set"]

        if not issubclass(type(card), Monster):
            card = self.get_card_by_id(card["global_id"])

        if card.level.value <= 4:
            if not zone:
                self.choice = {"original": "summon", "old": data,
                               "info": {"zones": [self.get_code_from_zone(zone) for zone in
                                                  self.turn_player.monster_zones.get_available_zones()]}}

                return {"choice": {"zones": [self.get_code_from_zone(zone) for zone in
                                             self.turn_player.monster_zones.get_available_zones()]}}

            summons = [Summons.NORMAL]
            if is_set:
                summons.append(Summons.SET)

            success, result = self.summon_cards([card], summons, [self.get_zone_from_code(zone)])
            self.choice = {}

        elif card.level.value <= 6:
            if not tribute:
                self.choice = {"original": "summon", "old": {"card": card, "zone": zone, "tributes": tribute,
                                                             "set": is_set},
                               "info": {"material": [card.get_json() for card in
                                                     self.turn_player.monster_zones.get_all_cards()]}}

                return {"choice": {"material": [card.get_json() for card in
                                                self.turn_player.monster_zones.get_all_cards()], "count": 0}}

            if not zone:
                tribute = tribute[0]["choice"]
                self.choice = {"original": "summon", "old": {"card": card, "zone": zone, "tributes": tribute,
                                                             "set": is_set},
                               "info": {"zones": [self.get_code_from_zone(zone) for zone in
                                                  self.turn_player.monster_zones.get_available_zones()]}}
                tribute_zone = self.get_code_from_zone(self.turn_player.monster_zones.get_zone_from_card_name(
                    tribute["name"]))

                self.choice["info"]["zones"].append(tribute_zone)

                return {"choice": {"zones": self.choice["info"]["zones"]}}

            summons = [Summons.TRIBUTE]
            if is_set:
                summons.append(Summons.SET)

            success, result = self.summon_cards([card], summons, [self.get_zone_from_code(zone)],
                                                [self.turn_player.monster_zones.get_zone_from_card_name(
                                                    tribute["name"]).card])
            self.choice = {}
        else:
            if not tribute or len(tribute) == 1:
                material = [card.get_json() for card in self.turn_player.monster_zones.get_all_cards()]
                if len(tribute) == 1:
                    material.remove(tribute[0]["choice"])
                self.choice = {"original": "summon", "old": {"card": card, "zone": zone, "tributes": tribute,
                                                             "set": is_set},
                               "info": {"material": material}}

                return {"choice": {"material": material, "count": 1 if not tribute else 0}}

            if not zone:
                tribute = [t["choice"] for t in tribute]
                self.choice = {"original": "summon", "old": {"card": card, "zone": zone, "tributes": tribute,
                                                             "set": is_set},
                               "info": {"zones": [self.get_code_from_zone(zone) for zone in
                                                  self.turn_player.monster_zones.get_available_zones()]}}
                tribute_zones = [self.get_code_from_zone(self.turn_player.monster_zones.get_zone_from_card_name(
                    t["name"])) for t in tribute]

                self.choice["info"]["zones"].extend(tribute_zones)

                return {"choice": {"zones": self.choice["info"]["zones"]}}

            summons = [Summons.TRIBUTE]
            if is_set:
                summons.append(Summons.SET)

            success, result = self.summon_cards([card], summons, [self.get_zone_from_code(zone)],
                                                [self.turn_player.monster_zones.get_zone_from_card_name(
                                                    t["name"]).card for t in tribute])
            self.choice = {}
        return result.get_json()

    def manage_activate(self, data):
        card, zone = None, None
        if self.chain_link and self.chain_choice:
            if data["chain_choice"] == "end":
                self.is_resolving = True
            else:
                choices = self.chain_choice["choice"]["chain"]
                for choice in choices:
                    if choice["data"].global_id == data["chain_choice"]["global_id"]:
                        card = choice

            self.choice = {}

        elif self.action_choice:
            card, zone = self.choice

            choice = None
            for c in self.action_choice["choice"]["action"]:
                if c["data"].global_id == data["content"][0]["action_choice"]["global_id"]:
                    choice = c["data"]

            card.effect.choice.append(choice)

            success, result = None, None
            for card in self.chain_link[::-1]:
                success, result = self.activate_card(card)

                if success == "Selection":
                    self.action_choice = {"choice": {"action": [{"data": card}
                                                                for x, card in enumerate(result[0])],
                                                     "count": result[1].get_value(), "game": self.get_json()}}

                    self.choice = (card, zone)
                    self.chain_choice = {}

                    return {"choice": {"action": [{"data": card.get_json()}
                                                  for x, card in enumerate(result[0])],
                                       "count": result[1].get_value(), "game": self.get_json()}}
            self.choice = {}
            self.chain_link = []
            self.chain_choice = {}
            self.action_choice = {}
            self.is_resolving = False
            return result.get_json()

        elif self.choice:
            if "zones" in self.choice["info"].keys():
                if "card" in self.choice["old"].keys():
                    card, zone = self.choice["old"]["card"], self.choice["old"]["zone"]
                    zone = data

                else:
                    card = self.choice["old"]["chain_choice"]
                    zone = data["choice"]

        else:
            card, zone = data["card"], data["zone"]

        if card:
            if card["other_type"] == "Field":
                zone = self.get_code_from_zone(self.turn_player.field_zone)

        if not zone and not self.is_resolving:
            self.choice = {"original": "activate", "old": data,
                           "info": {"zones": [self.get_code_from_zone(zone) for zone in
                                              self.turn_player.spell_trap_zones.get_available_zones()]}}

            self.chain_choice = {}

            return {"choice": {"zones": [self.get_code_from_zone(zone) for zone in
                                         self.turn_player.spell_trap_zones.get_available_zones()]}}

        if not self.is_resolving:
            zone_obj = self.get_zone_from_code(zone)
            card = self.get_card_by_id(card["global_id"])

            if self.find_card(card) is not zone_obj:
                self.move_card(self.find_card(card), zone_obj)

            if card not in self.chain_link:
                self.chain_link.append(card)

            self.choice = {"original": "activate", "old": data}

            chain_data = self.manage_chains(data)

            if chain_data:
                return chain_data

        self.is_resolving = True
        success, result = None, None
        for card in self.chain_link[::-1]:
            if isinstance(card, FieldSpell):
                success, result = self.activate_card(card, False)
            else:
                success, result = self.activate_card(card)

            if success == "Selection":
                self.action_choice = {"choice": {"action": [{"data": card} for x, card in enumerate(result[0])],
                                                 "count": result[1].get_value(), "game": self.get_json()}}

                self.choice = (card, zone)
                self.chain_choice = {}

                return {"choice": {"action": [{"data": card.get_json()}
                                              for x, card in enumerate(result[0])],
                                   "count": result[1].get_value(), "game": self.get_json()}}

        self.choice = {}
        self.chain_link = []
        self.chain_choice = {}
        self.action_choice = {}
        self.is_resolving = False
        return result.get_json()

    def manage_chains(self, data):
        chainable = self.get_all_chainable_cards()

        if not chainable:
            self.chain_choice = {}
            return

        if self.chain_link:
            last_player = self.chain_link[-1].owner.value
            only_other_player = [card for card in chainable if card.owner.value is not last_player]

            # Other player has no chainable cards
            if len(only_other_player) != 0:
                chainable = only_other_player

        self.chain_choice = {
            "choice": {"chain": [{"data": card, "id": x} for x, card in enumerate(chainable)],
                       "game": self.get_json()}}

        data = {"choice": {"chain": [{"data": card.get_json(), "id": x} for x, card in enumerate(chainable)],
                           "game": self.get_json()}}

        data["choice"]["chain"].append({"end": True})
        return data

    def manage_set(self, data):
        card, zone = None, None
        if self.choice:
            if "zones" in self.choice["info"].keys():
                card, zone = self.choice["old"]["card"], self.choice["old"]["zone"]

                zone = data

        else:
            card, zone = data["card"], data["zone"]

        if not zone:
            self.choice = {"original": "set", "old": data,
                           "info": {"zones": [self.get_code_from_zone(zone) for zone in
                                              self.turn_player.spell_trap_zones.get_available_zones()]}}

            return {"choice": {"zones": [self.get_code_from_zone(zone) for zone in
                                         self.turn_player.spell_trap_zones.get_available_zones()]}}

        if zone == "FZ":
            zone = self.get_code_from_zone(self.turn_player.field_zone)

        card = self.get_card_by_id(card["global_id"])

        success, result = self.set_card(card, self.get_zone_from_code(zone))
        self.choice = {}

        return result.get_json()

    def next_turn(self):
        self.turn_player = [player for player in [self.player_1, self.player_2] if player is not self.turn_player][0]
        self.turn_player.normal_summon_count = 1
        self.non_turn_player.normal_summon_count = 0
        self.turn_number += 1
        self.set_phase()
        self.draw_as_game(1, [self.turn_player])

    def manage_attack(self, data):
        card, target = None, None

        if self.choice:
            if "target" in self.choice["info"].keys():
                card, target = self.choice["old"]["card"], self.choice["old"]["target"]

                target = data

        else:
            card, target = data["card"], data["target"]

        if not target:
            self.choice = {"original": "attack", "old": data,
                           "info": {"target": [obj.get_json() for obj in self.get_attackable_objects()]}}

            return {"choice": {"target": [obj.get_json() for obj in self.get_attackable_objects()]}}

        card = self.get_card_by_id(card["global_id"])
        if "player" in target:
            target = self.non_turn_player
        else:
            target = self.get_card_by_id(target["global_id"])

        success, result = self.attack(card, target)
        self.choice = {}

        return result.get_json()

    def manage_request(self, data):
        json = {}
        request = data["content"]

        if "error" in json:
            return json

        if self.action_choice:
            json = self.manage_activate(data)

        elif self.choice:
            original = self.choice["original"]
            if original == "summon":
                if type(request) is list:
                    json = self.manage_summon(request)
                else:
                    json = self.manage_summon(request["choice"])

            if original == "activate":
                if self.chain_link:
                    json = self.manage_activate(request)
                else:
                    json = self.manage_activate(request["choice"])

            if original == "attack":
                json = self.manage_attack(request["choice"])

            if original == "set":
                json = self.manage_set(request["choice"])

            if original == "synchro":
                json = self.manage_synchro_summon(request)

        elif "move" in request:
            json = self.manage_move(request["move"])

        elif "position" in request:
            json = self.manage_position(request["position"])

        elif "phase" in request:
            json = self.manage_phase(request["phase"])

        elif "perform_summon" in request:
            json = self.manage_summon(request["perform_summon"])

        elif "extra_summon" in request:
            json = self.manage_extra_summon(request["extra_summon"])

        elif "activate" in request:
            json = self.manage_activate(request["activate"])

        elif "attack" in request:
            json = self.manage_attack(request["attack"])

        elif "set" in request:
            json = self.manage_set(request["set"])

        if "error" in json:
            return json

        self.apply_continuous()

        return {"201": self.get_json(), "data": json}

    @staticmethod
    def change_card_position(card, position):
        if issubclass(type(card), Monster):
            if position == "attack":
                card.is_set = False
                card.defense_mode = False
            elif position == "defense":
                card.defense_mode = True
                card.is_set = False
            else:
                card.is_set = True
                card.defense_mode = True
        else:
            if position == "faceup":
                card.is_set = False
            else:
                card.is_set = True

        return card

    def direct_attack(self, card, player):
        attacker_value = card.get_battle_value()
        self.change_lp(player, -attacker_value)
        card.attack_count -= 1

        return True, card

    def attack(self, card, target):
        if isinstance(target, Player):
            return self.direct_attack(card, target)

        # At "Before damage calculation" face-down monsters are flipped face up
        if not isinstance(target, LinkMonster):
            if target.is_set:
                self.change_card_position(target, "defense")

        # Perform damage calculation
        attacker_value = card.get_battle_value()
        target_value = target.get_battle_value()
        result = attacker_value - target_value

        # Attacking monster has more attack
        if result > 0:
            if not isinstance(target, LinkMonster):
                if not target.defense_mode:
                    self.change_lp(self.non_turn_player, -result)

        # Defending monster has more attack
        elif result < 0:
            self.change_lp(self.turn_player, result)

        # After damage calculation
        # End of damage step

        # Defending monster is destroyed
        if result > 0:
            self.move_card(self.find_card(target), (self.non_turn_player.graveyard, -1))

        elif result < 0:
            if not isinstance(target, LinkMonster):
                if not target.defense_mode:
                    self.move_card(self.find_card(card), (self.turn_player.graveyard, -1))

        card.attack_count -= 1

        return True, card

    @staticmethod
    def change_lp(player, value):
        player.lp += value

    def get_code_from_zone(self, zone):
        zones = {"p1H": self.player_1.hand, "p2H": self.player_2.hand,
                 "p1D": self.player_1.deck, "p2D": self.player_2.deck,
                 "p1ED": self.player_1.extra_deck, "p2ED": self.player_2.extra_deck,
                 "p1GY": self.player_1.graveyard, "p2GY": self.player_2.graveyard,
                 "p1BZ": self.player_1.banished, "p2BZ": self.player_2.banished,
                 "p1FZ": self.player_1.field_zone, "p2FZ": self.player_2.field_zone,
                 "p1MMZ1": self.player_1.monster_zones.zones[0], "p1STZ1": self.player_1.spell_trap_zones.zones[0],
                 "p1MMZ2": self.player_1.monster_zones.zones[1], "p1STZ2": self.player_1.spell_trap_zones.zones[1],
                 "p1MMZ3": self.player_1.monster_zones.zones[2], "p1STZ3": self.player_1.spell_trap_zones.zones[2],
                 "p1MMZ4": self.player_1.monster_zones.zones[3], "p1STZ4": self.player_1.spell_trap_zones.zones[3],
                 "p1MMZ5": self.player_1.monster_zones.zones[4], "p1STZ5": self.player_1.spell_trap_zones.zones[4],
                 "p2MMZ1": self.player_2.monster_zones.zones[0], "p2STZ1": self.player_2.spell_trap_zones.zones[0],
                 "p2MMZ2": self.player_2.monster_zones.zones[1], "p2STZ2": self.player_2.spell_trap_zones.zones[1],
                 "p2MMZ3": self.player_2.monster_zones.zones[2], "p2STZ3": self.player_2.spell_trap_zones.zones[2],
                 "p2MMZ4": self.player_2.monster_zones.zones[3], "p2STZ4": self.player_2.spell_trap_zones.zones[3],
                 "p2MMZ5": self.player_2.monster_zones.zones[4], "p2STZ5": self.player_2.spell_trap_zones.zones[4],
                 "EMZ1": self.field.extra_monster_zones.zones[0], "EMZ2": self.field.extra_monster_zones.zones[1]
                 }
        return list(zones.keys())[list(zones.values()).index(zone)]

    def get_zone_from_code(self, code):
        return {"p1H": self.player_1.hand, "p2H": self.player_2.hand,
                "p1D": self.player_1.deck, "p2D": self.player_2.deck,
                "p1ED": self.player_1.extra_deck, "p2ED": self.player_2.extra_deck,
                "p1GY": self.player_1.graveyard, "p2GY": self.player_2.graveyard,
                "p1BZ": self.player_1.banished, "p2BZ": self.player_2.banished,
                "p1FZ": self.player_1.field_zone, "p2FZ": self.player_2.field_zone,
                "p1MMZ1": self.player_1.monster_zones.zones[0], "p1STZ1": self.player_1.spell_trap_zones.zones[0],
                "p1MMZ2": self.player_1.monster_zones.zones[1], "p1STZ2": self.player_1.spell_trap_zones.zones[1],
                "p1MMZ3": self.player_1.monster_zones.zones[2], "p1STZ3": self.player_1.spell_trap_zones.zones[2],
                "p1MMZ4": self.player_1.monster_zones.zones[3], "p1STZ4": self.player_1.spell_trap_zones.zones[3],
                "p1MMZ5": self.player_1.monster_zones.zones[4], "p1STZ5": self.player_1.spell_trap_zones.zones[4],
                "p2MMZ1": self.player_2.monster_zones.zones[0], "p2STZ1": self.player_2.spell_trap_zones.zones[0],
                "p2MMZ2": self.player_2.monster_zones.zones[1], "p2STZ2": self.player_2.spell_trap_zones.zones[1],
                "p2MMZ3": self.player_2.monster_zones.zones[2], "p2STZ3": self.player_2.spell_trap_zones.zones[2],
                "p2MMZ4": self.player_2.monster_zones.zones[3], "p2STZ4": self.player_2.spell_trap_zones.zones[3],
                "p2MMZ5": self.player_2.monster_zones.zones[4], "p2STZ5": self.player_2.spell_trap_zones.zones[4],
                "EMZ1": self.field.extra_monster_zones.zones[0], "EMZ2": self.field.extra_monster_zones.zones[1]
                }[code]

    def find_card(self, card):
        for player in [self.player_1, self.player_2]:
            for i, hand_card in enumerate(player.hand.cards):
                if hand_card == card:
                    return player.hand, i

        return self.field.find_card(card)

    def assign_original_ownership(self):
        for player in [self.player_1, self.player_2]:
            for card in player.deck.cards:
                card.owner = Owner(player)

            for card in player.extra_deck.cards:
                card.owner = Owner(player)

    def log_event(self, event):
        if type(event) is list:
            self.log.extend(event)
        else:
            self.log.append(event)

    def get_attackable_objects(self):
        # Cards can only be attacked in the Battle Phase
        if self.current_phase is not self.get_phase(Phases.BATTLE):
            return []
        cards = []

        # If the Non-Turn Player has no Monsters they can be attacked directly
        if len(self.non_turn_player.monster_zones.get_available_zones()) == 5:
            return [self.non_turn_player]

        # All cards in Non-Turn Player's Main Monster Zones
        for card in self.get_all_cards_in_locations(
                [self.non_turn_player.monster_zones, self.field.extra_monster_zones]):
            if card.owner.value is self.non_turn_player:
                cards.append(card)

        return cards

    def get_all_attackers(self):
        # Cards can only attack in the Battle Phase
        if self.current_phase is not self.get_phase(Phases.BATTLE):
            return []
        cards = []
        # Main Monster Zones
        for card in self.get_all_cards_in_locations([self.turn_player.monster_zones]):
            # Cards must be able to attack
            if not hasattr(card, "can_attack"):
                continue

            if not card.can_attack or card.attack_count == 0:
                continue

            cards.append(card)

        for card in [card for card in self.get_all_cards_in_locations([self.field.extra_monster_zones])
                     if card.owner.value is self.turn_player]:
            if not hasattr(card, "can_attack"):
                continue

            if not card.can_attack or card.attack_count == 0:
                continue

            cards.append(card)

        return cards

    def get_all_chainable_cards(self):
        cards = []
        for card in self.get_all_cards_in_locations(self.get_all_locations()):
            if self.chain_link:
                if card in self.chain_link:
                    # Cards cannot be activated multiple times in same chain
                    # (This is incorrect as some cards have multiple effects)
                    continue

                spell_speed = 1
                if not isinstance(card, Monster):
                    spell_speed = card.spell_speed

                if spell_speed == 1:
                    continue

                if spell_speed < self.chain_link[-1].spell_speed:
                    # Only cards with an equal or higher spell speed can chain to a card
                    continue

            # Check if action actually creates a chain link
            if not self.check_can_activate(card):
                # Card must be able to be activated
                continue

            cards.append(card)

        return cards

    def get_all_activatable_cards(self):
        cards = []

        # Turn Player Hand
        for player in [self.player_1, self.player_2]:
            hand = player.hand.cards
            spell_trap_zones = self.get_all_cards_in_locations(
                [self.player_1.spell_trap_zones, self.player_2.spell_trap_zones])
            all_cards = hand + spell_trap_zones

            for card in all_cards:
                if not self.check_can_activate(card):
                    # Card must be able to be activated
                    continue
                # Add about checking if its legal to activate
                cards.append(card)

        return cards

    def get_all_summonable_cards(self):
        cards = []

        # Cannot Normal or Tribute summon outside the Main Phase(s)
        if self.current_phase not in [self.get_phase(Phases.MAIN_1), self.get_phase(Phases.MAIN_2)]:
            return []

        # Do effect summons later
        if self.turn_player.normal_summon_count == 0:
            # Player can only normal summon once per turn
            return []

        hand = self.turn_player.hand
        extra = self.turn_player.extra_deck

        for card in hand:
            if any(isinstance(card, card_type) for card_type in [Spell, Trap]):
                # Spell / Traps cannot be summoned
                continue

            # Level 1-4 doesnt need a tribute
            if card.level.value in [1, 2, 3, 4]:
                if not self.turn_player.monster_zones.get_available_zones():
                    # Player must have a zone to summon to
                    return []
                cards.append(("normal", card))

            # Level 5-6 needs 1 tribute
            if card.level.value in [5, 6]:
                # Change this to make it better
                if len(self.turn_player.monster_zones.get_available_zones()) != 5:
                    cards.append(("tribute", card))

            # Level 7+ needs 2 tributes
            if card.level.value > 6:
                # Change this to make it better
                if len(self.turn_player.monster_zones.get_available_zones()) < 4:
                    cards.append(("tribute", card))

        for card in extra:
            # Synchro Summon
            if isinstance(card, SynchroMonster):
                if self.check_can_synchro_summon(card):
                    cards.append(("synchro", card))

        return cards

    def get_synchro_combinations(self, card):
        minimum = card.material.non_tuner_count
        maximum = minimum
        multiple_non_tuners = card.material.multiple_non_tuners
        all_monsters = self.get_all_cards_in_locations([self.turn_player.monster_zones])
        all_monsters.extend([extra_monster for extra_monster in
                             self.get_all_cards_in_locations([self.field.extra_monster_zones])
                             if extra_monster.owner.value is self.turn_player])

        all_non_tuners = [monster for monster in all_monsters if not monster.is_tuner and hasattr(monster, "level")]

        if multiple_non_tuners:
            maximum = len(all_non_tuners)

        all_combinations = []
        for r in range(maximum + 1):
            for combination in combinations(all_non_tuners, r):
                all_combinations.append(combination)

        all_combinations = [combination for combination in all_combinations if combination and all(combination)]

        return all_combinations

    def get_synchro_tuner_combinations(self, card):
        level = card.level.value
        minimum = card.material.non_tuner_count
        maximum = minimum
        multiple_non_tuners = card.material.multiple_non_tuners
        all_monsters = self.get_all_cards_in_locations([self.turn_player.monster_zones])
        all_monsters.extend([extra_monster for extra_monster in
                             self.get_all_cards_in_locations([self.field.extra_monster_zones])
                             if extra_monster.owner.value is self.turn_player])

        all_tuners = [monster for monster in all_monsters if monster.is_tuner and hasattr(monster, "level")]
        all_non_tuners = [monster for monster in all_monsters if not monster.is_tuner and hasattr(monster, "level")]

        if multiple_non_tuners:
            maximum = len(all_non_tuners)

        all_combinations = []
        for r in range(maximum + 1):
            for combination in combinations(all_non_tuners, r):
                all_combinations.append(combination)

        all_combinations = [combination for combination in all_combinations if combination and all(combination)]

        tuner_combinations = []
        for tuner in all_tuners:
            tuner_level = tuner.level.value
            required_level = level - tuner_level

            for combination in all_combinations:
                if sum([card.level.value for card in combination]) == required_level:
                    tuner_combinations.append((tuner,) + combination)

        return tuner_combinations

    def get_link_combinations(self, card):
        pass

    def get_all_link_arrow_zones(self, exclusions=None):
        all_cards = self.get_all_cards_in_locations([self.player_1.monster_zones, self.player_1.monster_zones,
                                                     self.field.extra_monster_zones])

        all_links = list(set([card for card in all_cards if isinstance(card, LinkMonster)]))

        zones = []

        for link in all_links:
            zone = self.find_card(link)
            owner = link.owner.value

            if type(zone) is MonsterZone:
                zone_group = zone.owner.value.monster_zones
                zone_index = zone_group.zones.index(zone)
                if "Left" in link.link_arrows.value:
                    if zone_index != 0:
                        zones.append(zone_group.zones[zone_index - 1])

                if "Right" in link.link_arrows.value:
                    if zone_index != 4:
                        zones.append(zone_group.zones[zone_index + 1])

            if isinstance(zone, ExtraMonsterZone):
                for direction in link.link_arrows.value:
                    if direction in ["Left", "Right"]:
                        continue

                    if owner is self.player_1:
                        # Left Extra Monster Zone
                        if self.field.extra_monster_zones.zones.index(zone) == 0:
                            if direction == "Top-Left":
                                zones.append(self.player_2.monster_zones.zones[4])

                            if direction == "Top":
                                zones.append(self.player_2.monster_zones.zones[3])

                            if direction == "Top-Right":
                                zones.append(self.player_2.monster_zones.zones[2])

                            if direction == "Bottom-Right":
                                zones.append(self.player_1.monster_zones.zones[2])

                            if direction == "Bottom":
                                zones.append(self.player_1.monster_zones.zones[1])

                            if direction == "Bottom-Left":
                                zones.append(self.player_1.monster_zones.zones[0])

                        # Right Extra Monster Zone
                        else:
                            if direction == "Top-Left":
                                zones.append(self.player_2.monster_zones.zones[2])

                            if direction == "Top":
                                zones.append(self.player_2.monster_zones.zones[1])

                            if direction == "Top-Right":
                                zones.append(self.player_2.monster_zones.zones[0])

                            if direction == "Bottom-Right":
                                zones.append(self.player_1.monster_zones.zones[4])

                            if direction == "Bottom":
                                zones.append(self.player_1.monster_zones.zones[3])

                            if direction == "Bottom-Left":
                                zones.append(self.player_1.monster_zones.zones[2])

                    else:
                        # Left Extra Monster Zone
                        if self.field.extra_monster_zones.index(zone) == 0:
                            if direction == "Top-Left":
                                zones.append(self.player_1.monster_zones.zones[2])

                            if direction == "Top":
                                zones.append(self.player_1.monster_zones.zones[1])

                            if direction == "Top-Right":
                                zones.append(self.player_1.monster_zones.zones[0])

                            if direction == "Bottom-Right":
                                zones.append(self.player_2.monster_zones.zones[4])

                            if direction == "Bottom":
                                zones.append(self.player_2.monster_zones.zones[3])

                            if direction == "Bottom-Left":
                                zones.append(self.player_2.monster_zones.zones[2])

                        # Right Extra Monster Zone
                        else:
                            if direction == "Top-Left":
                                zones.append(self.player_1.monster_zones.zones[4])

                            if direction == "Top":
                                zones.append(self.player_1.monster_zones.zones[3])

                            if direction == "Top-Right":
                                zones.append(self.player_1.monster_zones.zones[2])

                            if direction == "Bottom-Right":
                                zones.append(self.player_2.monster_zones.zones[2])

                            if direction == "Bottom":
                                zones.append(self.player_2.monster_zones.zones[1])

                            if direction == "Bottom-Left":
                                zones.append(self.player_2.monster_zones.zones[0])

        return zones

    def check_can_link_summon(self, card):
        pass

    def check_can_synchro_summon(self, card):
        level = card.level.value
        all_monsters = self.get_all_cards_in_locations([self.turn_player.monster_zones])
        all_tuners = [monster for monster in all_monsters if monster.is_tuner and hasattr(monster, "level")]
        all_combinations = self.get_synchro_combinations(card)

        for tuner in all_tuners:
            tuner_level = tuner.level.value
            required_level = level - tuner_level

            # Synchro summons must have more than one monster
            if required_level == 0:
                continue

            for combination in all_combinations:
                if sum([card.level.value for card in combination]) == required_level:
                    return True

        return False

    def summon_cards(self, cards, summon_types, locations=None, materials=None):
        summon = None
        result = None
        # Normal summon
        if Summons.NORMAL in summon_types or Summons.TRIBUTE in summon_types:
            # Normal summon 1-4
            if not materials:
                summon = NormalSummon(cards, locations, [], summon_types)
            # Tribute summon 5+
            else:
                summon = NormalSummon(cards, locations, materials, summon_types)

            # Send materials to graveyard first
            materials = summon.materials
            if materials:
                for material in materials:
                    self.log_event(TributeLog(material))
                    self.move_card(self.find_card(material), (self.turn_player.graveyard, -1))

            pairs = summon.get_card_location_pairs()
            for card, location in pairs:
                summon.set_card_positions()
                self.log_event(SummonLog(summon))
                result = self.move_card(self.find_card(card), location)

            self.turn_player.normal_summon_count -= 1

            return result

        elif Summons.FLIP in summon_types:
            summon = FlipSummon(cards)
            summon.set_card_positions()
            self.log_event(SummonLog(summon))

        elif Summons.SYNCHRO in summon_types:
            summon = SpecialSummon(cards, locations, materials, summon_types)

            # Send materials to graveyard first
            materials = summon.materials
            if materials:
                for material in materials:
                    self.move_card(self.find_card(material), (self.turn_player.graveyard, -1))

            pairs = summon.get_card_location_pairs()
            for card, location in pairs:
                result = self.move_card(self.find_card(card), location)

            return result

    def activate_card(self, card, gy=True):
        result = card.effect.resolve(self)

        if result[0] == "Selection":
            return result

        self.log_event(EffectLog(card.effect))
        self.log_event(card.effect.logging)

        # Change this
        if gy:
            self.move_card(self.find_card(card), (card.owner.original.graveyard, -1))

        return True, card

    def get_all_settable_cards(self):
        cards = []
        hand = self.turn_player.hand
        if self.current_phase.phase_type not in [Phases.MAIN_1, Phases.MAIN_2]:
            return []

        for card in hand:
            if isinstance(card, Spell) or isinstance(card, Trap):
                if type(card) is FieldSpell:
                    cards.append(card)

                elif len(self.turn_player.spell_trap_zones.get_available_zones()) != 0:
                    cards.append(card)
        return cards

    def get_settable_zones(self, card):
        # Add check if zone is disabled
        if isinstance(card, Spell) or isinstance(card, Trap):
            if type(card) is FieldSpell:
                return [self.turn_player.field_zone]

            return self.turn_player.spell_trap_zones.get_available_zones()

        else:
            # Monsters
            pass

    def set_card(self, card, zone):
        if isinstance(card, Spell) or isinstance(card, Trap):
            card.is_set = True
            card.set_turn = self.turn_number

        origin = self.find_card(card)
        if isinstance(card, FieldSpell) and zone.card:
            self.move_card(zone, (card.owner.value.graveyard, -1))

        success, result = self.move_card(origin, zone)

        return success, result

    def check_can_activate(self, card):
        # check specific game state conditions (runick fountain) activatable
        card_location = self.find_card(card)
        if isinstance(card_location, tuple):
            card_location = card_location[0]
        player = card.owner.value
        current_phase = self.get_current_phase()

        if any(isinstance(card, card_type) for card_type in [Monster]):
            # Skip Monsters
            return False

        if player is not self.turn_player and isinstance(card_location, Hand):
            # Only the Turn Player can activate Spells from Hand (This is wrong because of Runick Fountain)
            return False

        if not self.turn_player.spell_trap_zones.get_available_zones() and isinstance(card_location, Hand):
            # Player must have a zone to activate to if playing from the hand
            return False

        if type(card_location) not in [Hand, SpellTrapZone]:
            # Card must be in the Hand or SpellTrapZones to activate (Change this)
            return False

        if not card.effect.actions:
            # Skip any card without an effect
            return False

        # Only Quick-Play Spells and set Traps can be Activated outside the Main Phase
        if self.current_phase not in [self.get_phase(Phases.MAIN_1), self.get_phase(Phases.MAIN_2)] and \
                (not isinstance(card, QuickPlaySpell) and not isinstance(card, Trap)):
            return False

        if isinstance(card, Trap):
            if not card.is_set or card.set_turn == self.turn_number:
                # Traps must be set for at least 1 turn before activation
                return False

        if isinstance(card, Spell):
            if isinstance(card, QuickPlaySpell):
                if card.is_set and card.set_turn == self.turn_number:
                    # Quick-play spells cannot be activated the turn they are set
                    return False

        return True

    def draw_as_game(self, value, players=None):
        if not players:
            players = [self.player_1, self.player_2]

        for player in players:
            for _ in range(value):
                card = player.deck.pop_card(-1)
                player.hand.add_card(card)

    @staticmethod
    def get_all_cards_in_locations(locations):
        all_cards = []
        for location in locations:
            if isinstance(location, Location):
                all_cards.extend(location.cards)

            elif isinstance(location, Zone):
                all_cards.append(location.card)

            else:
                all_cards.extend(location.get_all_cards())
        return [card for card in all_cards if card]

    # List of cards and args of attributes to check against
    def filter_cards(self, cards, conditions):
        if not conditions:
            return cards

        filtered_cards = []

        for condition in conditions:
            if type(condition) is list:
                for card in cards:
                    if all(self.compare_card(card, c) for c in condition):
                        filtered_cards.append(card)
            else:
                for card in cards:
                    if self.compare_card(card, condition):
                        filtered_cards.append(card)

        return list(set(filtered_cards))

    # Card and attribute to check against
    def compare_card(self, card, attribute):
        if issubclass(type(card), attribute):
            return True

        if isinstance(attribute, ModifiableAttribute):
            return True

        return False

    def temp_get_range_selection(self, cards, condition):
        selected_cards = []
        start, end, step = condition.get_value()
        for x in range(start - 1, end, step):
            print(cards)
            i = int(input("Index: "))
            selected_cards.append(cards[i])
            cards.pop(i)

            # update this if there are no targets remaining
            if x != end - 1:
                i = str(input("Another? Y/N: "))
                if i.upper() == "N":
                    break

        return selected_cards

    def get_all_locations(self):
        all_locations = [self.field.extra_monster_zones]
        for player in [self.player_1, self.player_2]:
            all_locations.append(player.hand)
            all_locations.append(player.field.monster_zones)
            all_locations.append(player.field.spell_trap_zones)
            all_locations.append(player.field.field_zone)
            all_locations.append(player.field.deck)
            all_locations.append(player.field.extra_deck)
            all_locations.append(player.field.graveyard)
            all_locations.append(player.field.banished)

        return all_locations

    def get_field_locations(self):
        field_locations = [self.field.extra_monster_zones]
        for player in [self.player_1, self.player_2]:
            field_locations.append(player.field.monster_zones)
            field_locations.append(player.field.spell_trap_zones)
            field_locations.append(player.field.field_zone)

        return field_locations

    def get_locations_from_types(self, types):
        # make this better
        if "Hand" in types:
            return [self.player_1.hand, self.player_2.hand]

        if Field in types:
            return self.get_field_locations()
        all_locations = self.get_all_locations()

        locations = []
        for location in all_locations:
            if type(location) in types:
                locations.append(location)

        return locations

    @staticmethod
    def check_can_move(card, location):
        if isinstance(location, Deck):
            if type(card) in [FusionMonster, SynchroMonster, XyzMonster, LinkMonster]:
                return False, "Extra Deck Monsters cannot go in the Main Deck"

        if isinstance(location, ExtraDeck):
            if type(card) not in [FusionMonster, SynchroMonster, XyzMonster, LinkMonster, PendulumMonster]:
                return False, "Main Deck cards (excl. Pendulum Monsters) cannot go in the Extra Deck"

        if isinstance(location, FieldZone):
            if type(card) is not FieldSpell:
                return False, "Only Field Spell cards can go in the Field Zone"

        if isinstance(location, ExtraMonsterZone):
            if type(card) not in [FusionMonster, SynchroMonster, XyzMonster, LinkMonster, PendulumMonster]:
                return False, "Main Deck cards (excl. Pendulum Monsters) cannot go in the Extra Monster Zone"

        if isinstance(location, Hand):
            if type(card) in [FusionMonster, SynchroMonster, XyzMonster, LinkMonster, PendulumMonster]:
                return False, "Extra Deck cards cannot go in the Hand"

        return True, "ok"

    def return_card(self, card, location):
        origin = self.find_card(card)
        player = card.owner.original
        if type(location) == list:
            location = location[0]
        if self.check_can_move(card, location)[0]:
            self.move_card(origin, (location, -1))
        else:
            if type(card) in [FusionMonster, SynchroMonster, XyzMonster, LinkMonster]:
                self.move_card(origin, (player.extra_deck, -1))

    # Move card from one location/zone to another location/zone
    def move_card(self, origin, target):
        origin_index = target_index = None

        if isinstance(origin, tuple):
            origin, origin_index = origin

        if isinstance(target, tuple):
            target, target_index = target

        # Origin is a Zone
        if origin_index is None:
            if origin.card:
                if hasattr(origin.card, "effect") and type(origin.card.effect) is not str:
                    if origin.card.effect:
                        for action in origin.card.effect.actions:
                            if isinstance(action, Continuous):
                                self.remove_continuous(origin.card.effect)

                if hasattr(origin.card, "attack"):
                    origin.card.attack.history = []

                if hasattr(origin.card, "defense"):
                    origin.card.attack.history = []

            # Target is a Zone
            if not target_index:
                if target.card:
                    if target.card.effect:
                        for action in target.card.effect.actions:
                            if isinstance(action, Continuous):
                                self.remove_continuous(target.card.effect)

                    if hasattr(target.card, "attack"):
                        target.card.attack.history = []

                    if hasattr(origin.card, "defense"):
                        origin.card.attack.history = []

                if target.card:
                    if target.card.effect:
                        for action in target.card.effect.actions:
                            if isinstance(action, Continuous):
                                self.remove_continuous(target.card.effect)

                    if hasattr(target.card, "attack"):
                        target.card.attack.history = []

                    if hasattr(origin.card, "defense"):
                        origin.card.attack.history = []

                # Monsters cannot go in Field Zone
                if isinstance(target, FieldZone):
                    result = self.check_can_move(origin.card, target)
                    if not result[0]:
                        return result

                # Main Deck Monsters, Spells and Traps cannot go in the Extra Monster Zone
                elif isinstance(target, ExtraMonsterZone):
                    result = self.check_can_move(origin.card, target)
                    if not result[0]:
                        return result

                target.set_card(origin.pop_card())
                return True, target.card

            # Target is a Location
            else:
                # Target is Deck or Extra Deck
                if isinstance(target, Deck) or isinstance(target, ExtraDeck) or isinstance(target, Hand):
                    result = self.check_can_move(origin.card, target)
                    if not result[0]:
                        return result

                if target_index == -1:
                    target.add_card(origin.pop_card())
                    return True, target.cards[-1]
                else:
                    target.set_card(origin.pop_card(), target_index)
                    return True, target.cards[target_index]

        # Origin is a Location
        else:
            # Target is a Zone
            if not target_index:
                if target.card:
                    if target.card.effect:
                        for action in target.card.effect.actions:
                            if isinstance(action, Continuous):
                                self.remove_continuous(target.card.effect)

                    if hasattr(target.card, "attack"):
                        target.card.attack.history = []

                    if hasattr(origin.card, "defense"):
                        origin.card.attack.history = []

                if isinstance(target, FieldZone):
                    result = self.check_can_move(origin.cards[origin_index], target)
                    if not result[0]:
                        return result

                # Main Deck Monsters, Spells and Traps cannot go in the Extra Monster Zone
                elif isinstance(target, ExtraMonsterZone):
                    result = self.check_can_move(origin.cards[origin_index], target)
                    if not result[0]:
                        return result

                target.set_card(origin.pop_card(origin_index))
                return True, target.card

            # Target is a Location
            else:
                if isinstance(target, Deck) or isinstance(target, ExtraDeck) or isinstance(target, Hand):
                    result = self.check_can_move(origin.cards[origin_index], target)
                    if not result[0]:
                        return result

                if target_index == -1:
                    target.add_card(origin.pop_card(origin_index))
                    return True, target.cards[-1]
                else:
                    target.set_card(origin.pop_card(origin_index), target_index)
                    return True, target.cards[target_index]

    def import_deck(self, file_path):
        main, extra, side = YDKReader.convert(file_path)

        return self.card_builder.build_deck(main), self.card_builder.build_deck(extra)

    def get_phase(self, phase):
        for p in self.phases:
            if p.phase_type == phase:
                return p

    def get_phase_by_string(self, phase):
        for p in self.phases:
            if str(p) == phase:
                return p

    def set_phase(self, phase=Phases.DRAW):
        self.current_phase = self.get_phase(phase)
        self.log_event(PhaseLog(self.current_phase))

    def get_current_phase(self):
        return self.get_phase(self.current_phase)

    def next_phase(self):
        if self.current_phase.phase_type == Phases.DRAW:
            self.current_phase = self.get_phase(Phases.STANDBY)

        elif self.current_phase.phase_type == Phases.STANDBY:
            self.current_phase = self.get_phase(Phases.MAIN_1)

        elif self.current_phase.phase_type == Phases.MAIN_1:
            self.current_phase = self.get_phase(Phases.BATTLE)

        elif self.current_phase.phase_type == Phases.BATTLE:
            self.current_phase = self.get_phase(Phases.MAIN_2)

        elif self.current_phase.phase_type == Phases.MAIN_2:
            self.current_phase = self.get_phase(Phases.END)

        elif self.current_phase.phase_type == Phases.END:
            self.current_phase = self.get_phase(Phases.DRAW)

    def _populate(self):
        self.player_1 = Player(True)
        self.player_2 = Player(False)
        self.turn_player = self.player_1
        self.turn_player.normal_summon_count = 1
        self.player_2.normal_summon_count = 0

        self.turn_number += 1
        self.phases = [DrawPhase(self), StandbyPhase(self), MainPhase1(self), BattlePhase(self),
                       MainPhase2(self), EndPhase(self)]

        self.current_phase = self.get_phase(Phases.DRAW)

        self.field = Field(self.player_1, self.player_2)

        main, extra = self.import_deck('Sim Deck.ydk')

        self.player_1.deck.populate(main)
        self.player_1.extra_deck.populate(extra)

        main, extra = self.import_deck('Sim Deck.ydk')

        self.player_2.deck.populate(main)
        self.player_2.extra_deck.populate(extra)

        self.assign_original_ownership()

        self.player_1.deck.shuffle()
        self.player_2.deck.shuffle()

        self.draw_as_game(5)
