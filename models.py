import random


class MonthEventsData:
    def __init__(self, callback):
        self.month = None
        self.year = None
        self.number_events = 0
        self.callback = callback

    def random(self):
        self.month = random.randint(1, 12)
        self.year = random.randint(2023, 2024)
        self.number_events = random.randint(0, 5)