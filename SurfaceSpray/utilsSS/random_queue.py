import random

class RandomQueue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop(random.random(0, self.size()-1))

    def size(self):
        return len(self.items)