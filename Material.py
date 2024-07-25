class Material:
    def __init__(self):
        self.text = ""


class SynchroMaterial(Material):
    def __init__(self):
        super().__init__()
        self.tuner_count = 0
        self.non_tuner_count = 0
        self.multiple_non_tuners = False


class LinkMaterial(Material):
    def __init__(self):
        super().__init__()
        self.minimum = 1
        self.condition = None
        self.multiple = False
