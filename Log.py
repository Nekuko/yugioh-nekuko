class Log:
    def __init__(self, obj):
        self.object = obj


class ConjunctionLog(Log):
    def __init__(self, obj):
        super().__init__(obj)


class ConditionLog(Log):
    def __init__(self, obj):
        super().__init__(obj)


class EffectLog(Log):
    def __init__(self, obj):
        super().__init__(obj)


class ActionLog(Log):
    def __init__(self, obj):
        super().__init__(obj)


class SummonLog(Log):
    def __init__(self, obj):
        super().__init__(obj)


class CostLog(Log):
    def __init__(self, obj):
        super().__init__(obj)


class PhaseLog(Log):
    def __init__(self, obj):
        super().__init__(obj)


class TributeLog(Log):
    def __init__(self, obj):
        super().__init__(obj)
