class Cost:
    def __init__(self, action):
        self.action = action

    @property
    def complete(self):
        return self.action.complete

    def can_pay(self):
        return self.action.can_activate()

    def perform(self):
        return self.action.perform()
