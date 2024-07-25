class Card:
    def __init__(self):
        self.name = "Card Name"
        self.password = "12345678"
        self.face_down = False
        self.owner = None
        self.text = None
        self.card_type = None
        self.global_id = -1
        self.equipped = False

    def move_reset(self):
        self.owner.reset()

    def get_json(self):
        desc = self.text.replace("\r\n", "\\n\\n")
        return {"name": self.name.value, "id": str(self.password), "desc": desc, "card_type": self.card_type,
                "global_id": self.global_id}
