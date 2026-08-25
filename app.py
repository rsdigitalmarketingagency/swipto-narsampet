import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "swipto.db")

app = Flask(__name__, static_folder="static", static_url_path="/static")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        rating REAL,
        image TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        type TEXT,
        rating REAL DEFAULT 4.0
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        restaurant_id INTEGER,
        item_total REAL NOT NULL,
        delivery_fee REAL NOT NULL,
        platform_fee REAL NOT NULL,
        grand_total REAL NOT NULL,
        payment_mode TEXT NOT NULL,
        address TEXT NOT NULL,
        instructions TEXT,
        status TEXT DEFAULT 'Order Placed',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        food_id INTEGER,
        food_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )""")

    count = cur.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]
    if count == 0:
        restaurants = [
            ("Andhra Spice", "South Indian", 4.6, "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=900&q=80"),
            ("SWIPTO Biryani House", "Biryani", 4.5, "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=900&q=80"),
            ("Narsampet Food Hub", "Fast Food", 4.3, "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80")
        ]
        cur.executemany("INSERT INTO restaurants (name, category, rating, image) VALUES (?,?,?,?)", restaurants)

        foods = [
            (1, "Andhra Chicken Curry", "Spicy Andhra style chicken curry", 180, "Non-Veg", 4.5),
            (1, "Paneer Curry", "Rich paneer curry with spices", 160, "Veg", 4.3),
            (1, "Veg Meals", "Rice, curry and side dishes", 120, "Veg", 4.4),
            (2, "Chicken Biryani", "Hyderabadi style chicken biryani", 130, "Non-Veg", 4.0),
            (2, "Mutton Biryani", "Special mutton dum biryani", 220, "Non-Veg", 4.4),
            (2, "Veg Biryani", "Fresh vegetable biryani", 100, "Veg", 4.0),
            (3, "Chicken Fry", "Crispy spicy chicken fry", 180, "Non-Veg", 4.2),
            (3, "Veg Burger", "Loaded veg burger", 110, "Veg", 4.1),
            (3, "Cheese Pizza", "Cheesy pizza with herbs", 199, "Veg", 4.3),
        ]
        cur.executemany("""INSERT INTO foods
            (restaurant_id,name,description,price,type,rating)
            VALUES (?,?,?,?,?,?)""", foods)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/restaurants")
def restaurants():
    conn = get_db()
    rows = conn.execute("SELECT * FROM restaurants ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/restaurant/<int:restaurant_id>/menu")
def menu(restaurant_id):
    food_type = request.args.get("type")
    conn = get_db()
    if food_type in ("Veg", "Non-Veg"):
        rows = conn.execute(
            "SELECT * FROM foods WHERE restaurant_id=? AND type=? ORDER BY id",
            (restaurant_id, food_type)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM foods WHERE restaurant_id=? ORDER BY id",
            (restaurant_id,)
        ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/popular")
def popular():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM foods ORDER BY rating DESC, id LIMIT 8"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip()
    conn = get_db()
    if q:
        like = f"%{q}%"
        rows = conn.execute(
            """SELECT foods.* FROM foods
               JOIN restaurants ON restaurants.id=foods.restaurant_id
               WHERE foods.name LIKE ? OR foods.description LIKE ? OR restaurants.name LIKE ?
               ORDER BY foods.rating DESC""",
            (like, like, like)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM foods ORDER BY rating DESC LIMIT 8").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()

    if len(name) < 2 or len(phone) < 10:
        return jsonify(success=False, message="Enter valid name and mobile number."), 400

    conn = get_db()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM customers WHERE phone=?", (phone,)).fetchone()

    if row:
        cur.execute("UPDATE customers SET name=? WHERE id=?", (name, row["id"]))
        customer_id = row["id"]
    else:
        cur.execute("INSERT INTO customers (name,phone) VALUES (?,?)", (name, phone))
        customer_id = cur.lastrowid

    conn.commit()
    user = conn.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
    conn.close()
    return jsonify(success=True, user=dict(user))


@app.route("/api/order", methods=["POST"])
def order():
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customer_id")
    restaurant_id = data.get("restaurant_id")
    items = data.get("items") or []
    payment_mode = data.get("payment_mode", "COD")
    address = str(data.get("address", "")).strip()
    instructions = str(data.get("instructions", "")).strip()

    if not customer_id or not items or not address:
        return jsonify(success=False, message="Customer, items and delivery address are required."), 400

    item_total = 0.0
    clean_items = []
    for item in items:
        try:
            food_id = int(item.get("id"))
            qty = max(1, int(item.get("quantity", 1)))
        except Exception:
            continue

        conn = get_db()
        food = conn.execute(
            "SELECT * FROM foods WHERE id=?",
            (food_id,)
        ).fetchone()
        conn.close()

        if not food:
            continue

        line_total = float(food["price"]) * qty
        item_total += line_total
        clean_items.append((food, qty))

    if not clean_items:
        return jsonify(success=False, message="No valid food items found."), 400

    delivery_fee = 25.0
    platform_fee = 5.0
    grand_total = item_total + delivery_fee + platform_fee

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""INSERT INTO orders
        (customer_id,restaurant_id,item_total,delivery_fee,platform_fee,grand_total,payment_mode,address,instructions,status)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (customer_id, restaurant_id, item_total, delivery_fee, platform_fee,
         grand_total, payment_mode, address, instructions, "Order Placed")
    )
    order_id = cur.lastrowid

    for food, qty in clean_items:
        cur.execute("""INSERT INTO order_items
            (order_id,food_id,food_name,price,quantity)
            VALUES (?,?,?,?,?)""",
            (order_id, food["id"], food["name"], food["price"], qty)
        )

    conn.commit()
    conn.close()

    return jsonify(
        success=True,
        order_id=order_id,
        item_total=round(item_total),
        delivery_fee=round(delivery_fee),
        platform_fee=round(platform_fee),
        grand_total=round(grand_total),
        status="Order Placed"
    )


@app.route("/api/orders/<int:customer_id>")
def customer_orders(customer_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC",
        (customer_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
else:
    init_db()
