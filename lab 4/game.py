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

#Player {1, 2, 16, 17}
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






if __name__ == '__main__':
    app.run(port=5000)