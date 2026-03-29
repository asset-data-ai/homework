from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List
from uuid import uuid4
import json
import os
from datetime import datetime

app = FastAPI()

@app.get("/")
def ooo():
    return 'hi hi hi hi hi'

#1-2
class User:
    def __init__(self, id: str, name: str, email: str):
        self._id = id
        self._name = name.strip().title()
        if "@" not in email:
            raise ValueError("Некорректный email: должен содержать символ '@'")
        self._email = email.strip().lower()
    def __str__(self):
        return f"User(id={self._id}, name='{self._name}', email='{self._email}')"
    def __del__(self):
        return f"Uset {self._name} deleted"

    @classmethod
    def from_string(cls, data: str):
        raw_id, raw_name, raw_email = map(str.strip, data.split(","))
        return cls(int(raw_id), raw_name, raw_email)

@app.get("/task1")
def task1():
    u1 = User(9, " john doe ", "John@Example.COM")
    return str(user1)

@app.get("/task2")
def task1():
    u2 = User.from_string("2, Alice Wonderland , alice@wonder.com")
    return u2

#3
class Product:
    def __init__(self, id: int, name: str, price: float, category: str):
        self.id = id
        self.name = name
        self.price = price
        self.category = category

    def __str__(self):
        return f"User(id={self.id}, name='{self.name}', price={self.price}, category='{self.category}')"

    def __eq__(self, other):
        if isinstance(other, Product):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def to_dict(self):
        return {'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category}

@app.get("/task3")
def task3():
    p1 = Product(5004785, "banaba", 1299.99, "fruits")
    p2 = Product(5004785, "banana clone", 1299.99, "fruits")
    return {"1": str(p1), "2": p1 == p2, "3": hash(p1),  "4": p1.to_dict()}

#4-5
class Inventory:
    def __init__(self):
        self._products = []

    def add_product(self, product: Product):
        if not any(p.id == product.id for p in self._products):
            self._products.append(product)

    def remove_product(self, product_id: int):
        self._products = [p for p in self._products if p.id != product_id]

    def get_product(self, product_id: int):
        for p in self._products:
            if p.id == product_id:
                return p
            return None

    def get_all_products(self):
        return self._products

    def unique_products(self):
        return set(self._products)

    def to_dict(self):
        return {p.id: p for p in self._products}

    def filter_by_price(self, min_price: float):
        check = lambda p: p.price >= min_price
        return [p for p in self._products if check(p)]

@app.get("/task4")
def task4():
    inv = Inventory()
    p1 = Product(1, "Laptop", 1200.0, "Electronics")
    p2 = Product(2, "Mouse", 25.0, "Electronics")
    p3 = Product(1, "Laptop Clone", 18800.0, "Electronics")
    inv.add_product(p1)
    inv.add_product(p2)
    inv.add_product(p3)
    inventory_dict = inv.to_dict()
    response_data = {product_id: product.to_dict() for product_id, product in inventory_dict.items()}
    return {"total_items_in_list": len(inv.get_all_products()), "inventory_data": response_data}

@app.get("/task5")
def task5():
    inv = Inventory()
    inv.add_product(Product(1, "Laptop", 1200.0, "Electronics"))
    inv.add_product(Product(2, "Mouse", 25.0, "Electronics"))
    expensive = inv.filter_by_price(100.0)
    return [p.name for p in expensive]

#6
class Logger:
    @staticmethod
    def log_action(user: 'User', action: str, product: 'Product', filename: str):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, "a", encoding="utf-8") as f:
            q = f"{t};{user._id};{action};{product.id}\n"
            f.write(q)
    @staticmethod
    def read_logs(filename: str):
        w = []
        if not os.path.exists(filename):
            return w
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                e = line.strip().split(";")
                if len(e) == 4:
                    w.append({'timestamp': e[0], 'user_id': e[1], 'action': e[2], 'product_id': e[3]})
        return w

@app.get("/task6")
def task6():
    user = User("42", " Alice Smith ", "ALICE@wonder.com")
    product = Product(1, "Magic Wand", 99.99, "Accessories")
    log_file = "shop_logs.txt"
    Logger.log_action(user, "VIEW", product, log_file)
    Logger.log_action(user, "ADD_TO_CART", product, log_file)
    Logger.log_action(user, "BUY", product, log_file)
    history = Logger.read_logs(log_file)
    return {"file_used": log_file, "logs_data": history}





# uvicorn r:app --reload