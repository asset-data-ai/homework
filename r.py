from fastapi import FastAPI, HTTPException, Query
import os
from datetime import datetime
import numpy as np
import pandas as pd
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
            raise ValueError("error")
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
    return str(u1)

@app.get("/task2")
def task2():
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
    inv.add_product(p1)
    inv.add_product(p2)
    inv.add_product(p3)
    inventory_dict = inv.to_dict()
    response_data = {product_id: product.to_dict() for product_id, product in inventory_dict.items()}
    return {"total_items_in_list": len(inv.get_all_products()), "inventory_data": response_data}

@app.get("/task5")
def task5():
    inv = Inventory()
    inv.add_product(p1)
    inv.add_product(p2)
    expensive = inv.filter_by_price(100.0)
    return [p.name for p in expensive]

#6
class Logger:
    @staticmethod
    def log_action(user, action: str, product, filename: str):
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

@app.post("/task6")
def task6():
    log_file = "shop_logs.txt"
    Logger.log_action(user, "VIEW", p3, log_file)
    Logger.log_action(user, "ADD_TO_CART", p3, log_file)
    Logger.log_action(user, "BUY", p3, log_file)
    history = Logger.read_logs(log_file)
    return {"file_used": log_file, "logs_data": history}

#7-8
class Order:
    def __init__(self, id: int, user):
        self.id = id
        self.user = user
        self.products = []
    def add_product(self, product):
        self.products.append(product)
    def remove_product(self, product_id: int):
        self.products = [p for p in self.products if p.id != product_id]
    def total_price(self):
        return sum(p.price for p in self.products)
    def __str__(self):
        product_names = ", ".join([p.name for p in self.products])
        return f"Order(id={self.id}, user='{self.user._name}', total_price={self.total_price()}, items=[{product_names}])"
    def most_expensive_products(self, n: int):
        return sorted(self.products, key=lambda p: p.price, reverse=True)[:n]

@app.get("/task7")
def task7():
    order = Order(101, user)
    order.add_product(p1)
    order.add_product(p2)
    order.add_product(p2)
    return {"order_string_format": str(order), "total_calculated_price": order.total_price(), "total_items_in_order": len(order.products)}

#8
@app.get("/task8")
def task8():
    order = Order(102, user)
    order.add_product(p1)
    order.add_product(p2)
    order.add_product(p3)
    order.add_product(p4)
    order.add_product(p5)
    top_2_expensive = order.most_expensive_products(2)
    return {"order_id": order.id, "total_items": len(order.products), "top_2_expensive_items": [{"name": p.name, "price": p.price} for p in top_2_expensive]}



#data
p1 = Product(1, "Laptop", 1200.0, "Electronics")
p2 = Product(2, "T-Shirt", 20.0, "Clothing")
p3 = Product(3, "Apple", 2.0, "Groceries")
p4 = Product(4, "Mouse", 25.0, "Electronics")
p5 = Product(5, "USB Cable", 15.0, "Accessories")
user = User("66", " Askhat ", "askhat@def.com")
u1 = User(1,"John Doe","john@example.com")
u2 = User(2,"Alice","alice@example.com")

#9
def price_stream(products: list):
    for p in products:
        yield p.price

@app.get("/task9")
def task9():
    user = User("42", " Askhat ", "askhat@def.com")
    order = Order(103, user)
    order.add_product(p1)
    order.add_product(p2)
    order.add_product(p3)
    stream = price_stream(order.products)
    first_price = next(stream)
    remaining_prices = list(stream)
    return {"first_price_extracted": first_price, "remaining_prices_extracted": remaining_prices}

#10
class OrderIterator:
    def __init__(self, orders: list):
        self._orders = orders
        self._index = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self._index < len(self._orders):
            c_order = self._orders[self._index]
            self._index += 1
            return c_order
        else:
            raise StopIteration

@app.get("/task10")
def task10():
    order1 = Order(104, user)
    order2 = Order(105, user)
    order3 = Order(106, user)
    orders_list = [order1, order2, order3]
    order_iterator = OrderIterator(orders_list)
    w = []
    for order in order_iterator:
        w.append(order.id)
    return len(orders_list), w

#11
@app.get("/task11")
def task11():
    products = [p1, p2, p3, p4]
    price_np = np.array([p.price for p in products], dtype = float)
    return price_np.tolist()


#12
@app.get("/task12")
def task12():
    prices = np.array([1200.0, 25.0, 450.0])
    mean_price = np.mean(prices)
    median_price = np.median(prices)
    return (mean_price, median_price)

#13
@app.get("/task13")
def task13():
    prices = np.array([1200.0, 25.0, 450.0])
    min_val = np.min(prices)
    max_val = np.max(prices)
    normalize = (prices - min_val) / (max_val - min_val)
    return normalize.tolist()

#14
@app.get("/task14")
def task14():
    p_list = [p1, p2, p3, p4]
    ct_list = [i.category for i in p_list]
    ct_array = np.array(ct_list)
    return ct_array.tolist()

#15
@app.get("/task15")
def task15():
    q = np.array(["Electronics", "Clothing", "Electronics", "Groceries", "Clothing", "Electronics", "Books"])
    return len(set(q))


#16
@app.get("/task16")
def task16():
    p_list = [p1, p2, p3]
    p_np = np.array([p.price for p in p_list], dtype=float)
    mask = p_np > np.mean(p_np)
    p = [p_list[i] for i in range(len(p_list)) if mask[i]]
    return [i.to_dict() for i in p]

#17
@app.get("/task17")
def task17():
    prices = np.array([1200.0, 25.0, 450.0])
    w = prices * 0.9
    return w.tolist()

#18
@app.get("/task18")
def task18():
    order1 = Order(1, u1)
    order1.add_product(p1)
    order2 = Order(2, u2)
    order2.add_product(p4)
    order2.add_product(p1)
    orders = [order1, order2]
    matrix_2d = np.array([[o.total_price()] for o in orders], dtype=float)
    return matrix_2d.tolist()

#19
@app.get("/task19")
def task19():
    q = np.array([1200.0, 1225.0])
    return float(np.mean(q))

#20
@app.get("/task20")
def task20():
    q = np.array([1200.0, 900.0, 1500.0])
    return np.where(q > 1000)[0].tolist()

#21
@app.get("/task21")
def task21():
    u_list = [u1, u2]
    current_date = datetime.now().strftime("%Y-%m-%d")
    data = [{"id": u._id, "name": u._name, "email": u._email, "registration_date": current_date} for u in u_list]
    df = pd.DataFrame(data)
    return df.to_dict(orient="records")
# uvicorn r:app --reload