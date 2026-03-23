class Memory:

    def __init__(self):
        self.logs = []
        self.violations = 0

    def update(self, entry):

        self.logs.append(entry)

        if entry["evaluation"]["violation"]:
            self.violations += 1