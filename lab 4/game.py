import json
import random
from datetime import datetime
from collections import Counter
from typing import Iterator
from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# Item {3}
class Item:
    def __init__(self, id: int, name: str, power: int):
        self.id = id
        self.name = name
        self.power = power

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.id == other.id
        return False

    def __str__(self):
        return f"Item(id={self.id}, name='{self.name}', power={self.power})"

# Inventory {4, 5,18}
class Inventory:
    def __init__(self):
        self._items: list[Item] = []

    def add_item(self, item: Item):
        if item not in self._items:
            self._items.append(item)

    def remove_item(self, id: int):
        self._items = [i for i in self._items if i.id != id]

    def get_items(self):
        return self._items

    def unique_items(self):
        return set(self._items)

    def to_dict(self):
        return {i.id: i for i in self._items}

    def __iter__(self):
        return iter(self._items)

    def get_strong_items(selfself, min_power: int):
        is_strong = lambda i: i.power >= min_power
        return [i for i in self if is_strong(i)]

#Player {1, 2, 7, 16, 17}
class Player:
    def __init__(self, id: int, name: str, hp: int):
        self._id = id
        self._name = name.strip().title()
        self._hp = max(0, hp)
        self._inventory = Inventory()

        @property
        def hp(self):
            return self._hp

        @hp.setter
        def hp(self, value):
            self._hp = max(0, value)

        @property
        def inventory(self):
            return self._inventory

        @property
        def id(self):
            return self._id

        @classmethod
        def from_string(cls, dsts: str):
            try:
                p_id, p_name, p_hp = map(str.strip, data.split(','))
                return cls(int(p_id), p_name, int(p_hp))
            except ValueError:
                raise ValueError("Неверный формат строки. Ожидается: 'id,name,hp'")

        def handle_event(self, event: "Event"):
            if event.type == "ATTACK"
                self.hp -= event.data.get("damage", 0)
            elif event.type == "HEAL":
                self.hp += event.data.get("amount", 0)
            elif event.type == "LOOT":
                item_data = event.data.get("item")
                if item_data:
                    self.inventory.add_item(Item(**item_data))

        def __str__(self):
            return f"Player(id={self._id}, name='{self._name}', hp={self._hp})"

class Warrior(Player):
    def handle_event(self, event: 'Event'):
        if event.type == "ATTACK":
            damage = event.data.get("damage", 0)
            event.data["damage"] = int(damage * 0.9)
            super().handle_event(event)

class Mage(Player):
    def handle_event(self, event: 'Event'):
        if event.type == "LOOT":
            item_data = event.data.get("item")
            if item_data:
                item_data["power"] = int(item_data["power"] * 1.1)
        super().handle_event(event)


#EventIterator {10}
class EventIterator:
    def __init__(selfself, events: list[Event]):
        self._events = events
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._events):
            result = self._events[self._index]
            self._index += 1
            return result
        raise StopIteration

#11
def damage_stream(events: list[Event])
    for i in events:
        if i.type == "ATTACK":
            yield i.data.get("damage", 0)

#12
def generate_events(players: lise[Player, items: list[Item], n: int]):
    generated = []
    pick_type = lambda: random.choice(["ATTACK", "HEAL", "LOOT"])
    for _ in range(n):
        for i in players:
            e_type = pick_type()
            if e_type == "ATTACK"
                data = {"damage": random.randint(10, 30)}
            elif e_type == "HEAL":
                data = {"amount": random.randint(10, 20)}
            else:
                itm = random.choice(items)
                dsts = {"item": {"item_id": itm.id, "name": itm.name, "power": itm.power}}

            generated.append((player, Event(e_type, data)))
    return generated





if __name__ == '__main__':
    app.run(port=5000)