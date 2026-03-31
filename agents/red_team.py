import json
import random

class RedTeamAgent:

    def __init__(self):
        with open("configs/prompt_injection.json") as f:
            self.data = json.load(f)

    def generate(self):
        category = random.choice(self.data["categories"])
        attack = random.choice(category["attacks"])
        return f"[{category['name']}] {attack}"