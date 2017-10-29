from collections import defaultdict


class Info:
    def __init__(self):
        self.name = ''
        self.counter = 0
        self.tickets_id = defaultdict(set)
        self.areas = set()
