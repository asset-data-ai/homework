import json
import random
from datetime import datetime
from collections import Counter
from typing import Iterator
from flask import Flask, jsonify

app = Flask(__name__)

#3
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

#4,5,18
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
    def get_strong_items(self, min_power: int):
        is_strong = lambda i: i.power >= min_power
        return [i for i in self if is_strong(i)]

#1,2,7,16,17
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
    def from_string(cls, data):
        p_id, p_name, p_hp = map(str.strip, data.split(','))
        return cls(p_id, p_name, int(p_hp))
    def handle_event(self, event: "Event"):
        if event.type == "ATTACK":
            self.hp -= event.data.get("damage", 0)
        elif event.type == "HEAL":
            self.hp += event.data.get("amount", 0)
        elif event.type == "LOOT":
            item_data = event.data.get("item")
            if item_data:
                self.inventory.add_item(Item(id=item_data["item_id"], name=item_data["name"], power=item_data["power"]))
    def __str__(self):
        return f"Player(id={self._id}, name='{self._name}', hp={self._hp})"
    def __del__(self):
        print(f"Player {self._name} удалён")

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


#6
class Event:
    def __init__(self, type: str, data: dict, timestamp: str = None):
        self.type = type
        self.data = data
        self.timestamp = timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    def __str__(self):
        return f"Event(type='{self.type}', data={self.data}, timestamp='{self.timestamp}')"

#8,9
class Logger:
    @staticmethod
    def log(event: Event, player: Player, filename: str):
        with open(filename, "a", encoding="utf-8") as f:
            data_str = json.dumps(event.data)
            f.write(f"{event.timestamp};{player.id};{event.type};{data_str}\n")
    @staticmethod
    def read_logs(filename: str) -> list[Event]:
        events = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    ts, p_id, e_type, data_str = line.strip().split(';', 3)
                    events.append(Event(e_type, json.loads(data_str), ts))
        except FileNotFoundError:
            pass
        return events

#10
class EventIterator:
    def __init__(self, events: list[Event]):
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
def damage_stream(events: list[Event]):
    for i in events:
        if i.type == "ATTACK":
            yield i.data.get("damage", 0)

#12
def generate_events(players: list[Player], items: list[Item], n: int):
    generated = []
    pick_type = lambda: random.choice(["ATTACK", "HEAL", "LOOT"])
    for _ in range(n):
        for player in players:
            e_type = pick_type()
            if e_type == "ATTACK":
                data = {"damage": random.randint(10, 30)}
            elif e_type == "HEAL":
                data = {"amount": random.randint(10, 20)}
            else:
                itm = random.choice(items)
                dats = {"item": {"item_id": itm.id, "name": itm.name, "power": itm.power}}
            generated.append((player, Event(e_type, data)))
    return generated

#13
def analyze_logs(events: list[Event], filename: str):
    raw_logs = []
    with open(filename, "r") as f:
        for line in f:
            raw_logs.append(line.strip().split(";"))
    damage_by_player = {}
    total_damage = sum(damage_stream(events))
    event_types = [e.type for e in events]
    most_common_event = Counter(event_types).most_common(1)[0][0] if event_types else None
    for log in raw_logs:
        if log[2] == "ATTACK":
            p_id = int(log[1])
            dmg = json.loads(log[3]).get("damage", 0)
            damage_by_player[p_id] = damage_by_player.get(p_id, 0) + dmg
    top_player = max(damage_by_player, key=damage_by_player.get) if damage_by_player else None
    return {"total_damage": total_damage, "top_player_id": top_player, "most_common_event": most_common_event}

#14
decide_action = lambda hp, inv_size: "HEAL" if hp < 30 else ("LOOT" if inv_size < 3 else "ATTACK")

#19
def analyze_inventory(inventories: list[Inventory]) -> dict:
    all_items = []
    for inv in inventories:
        all_items.extend(inv.get_items())
    unique_items = set(all_items)
    top_power_item = max(all_items, key=lambda x: x.power) if all_items else None
    return {"unique_items": unique_items, "top_power_item": top_power_item}



#-----------------------------------------------------
#20
@app.route("/sim")
def run_simulation():
    log_file = "game_log.txt"
    open(log_file, 'w').close()
    items = [Item(1, "Excalibur", 100),
        Item(2, "Health Potion", 0),
        Item(3, "Magic Staff", 80)]
    p1 = Warrior.from_string("1, arthur, 120")
    p2 = Mage(2, "merlin", 90)
    players = [p1, p2]
    simulated_data = generate_events(players, items, 3)
    events_history = []
    for player, event in simulated_data:
        ai_action = decide_action(player.hp, len(player.inventory.get_items()))
        player.handle_event(event)
        Logger.log(event, player, log_file)
        events_history.append({"player": player._name,
            "ai_wanted_to": ai_action,
            "actual_event": event.type,
            "event_data": event.data})
    players_status = []
    for p in players:
        players_status.append({"name": p._name,
            "hp": p.hp,
            "strong_items": [i.name for i in p.inventory.get_strong_items(50)]})
    logged_events = Logger.read_logs(log_file)
    log_stats = analyze_logs(logged_events, log_file)
    inv_stats = analyze_inventory([p.inventory for p in players])
    return jsonify({
        "status": "Simulation finished successfully",
        "events_history": events_history,
        "players_final_status": players_status,
        "analytics": {
            "total_damage_taken": log_stats.get("total_damage"),
            "most_common_event": log_stats.get("most_common_event"),
            "unique_items_in_world": len(inv_stats['unique_items']),
            "top_power_item": inv_stats['top_power_item'].name if inv_stats['top_power_item'] else None
        }
    })

if __name__ == '__main__':
    app.run(port=5000)