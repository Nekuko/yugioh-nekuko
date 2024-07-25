from enum import Enum

from Spell import QuickPlaySpell, Spell
from Trap import Trap


class Phase:
    def __init__(self, simulator):
        self.simulator = simulator
        self.normal_summon_phase = False
        self.phase_type = Phases.NONE
        self.activatable_types = [QuickPlaySpell, Trap]

    def __str__(self):
        return {Phases.NONE: "None", Phases.DRAW: "Draw Phase", Phases.STANDBY: "Standby Phase",
                Phases.MAIN_1: "Main Phase 1", Phases.BATTLE: "Battle Phase", Phases.MAIN_2: "Main Phase 2",
                Phases.END: "End Phase"}[self.phase_type]


class DrawPhase(Phase):
    def __init__(self, simulator):
        super().__init__(simulator)
        self.phase_type = Phases.DRAW


class StandbyPhase(Phase):
    def __init__(self, simulator):
        super().__init__(simulator)
        self.phase_type = Phases.STANDBY


class MainPhase1(Phase):
    def __init__(self, simulator):
        super().__init__(simulator)
        self.normal_summon_phase = True
        self.phase_type = Phases.MAIN_1
        self.activatable_types = [Spell, Trap]


class BattlePhase(Phase):
    def __init__(self, simulator):
        super().__init__(simulator)
        self.phase_type = Phases.BATTLE


class MainPhase2(Phase):
    def __init__(self, simulator):
        super().__init__(simulator)
        self.normal_summon_phase = True
        self.phase_type = Phases.MAIN_2
        self.activatable_types = [Spell, Trap]


class EndPhase(Phase):
    def __init__(self, simulator):
        super().__init__(simulator)
        self.phase_type = Phases.END


class Phases(Enum):
    DRAW = 1
    STANDBY = 2
    MAIN_1 = 3
    BATTLE = 4
    MAIN_2 = 5
    END = 6
    NONE = 7




