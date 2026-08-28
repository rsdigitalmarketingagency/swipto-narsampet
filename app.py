import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "swipto.db")

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)


# ==========================================
# DATABASE
# ==========================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dict(rows):
    return [dict(row) for row in rows]


# ==========================================
# INITIAL DATABASE
# ==========================================

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # CUSTOMERS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # RESTAURANTS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            rating REAL DEFAULT 4.0,
            image TEXT,
            address TEXT,
            active INTEGER DEFAULT 1
        )
    """)

    # FOODS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            type TEXT,
            rating REAL DEFAULT 4.0,
            image TEXT,
            available INTEGER DEFAULT 1
        )
    """)

    # ORDERS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
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
            delivery_partner TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ORDER ITEMS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            food_id INTEGER,
            food_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

    # SEED DATA
    restaurant_count = cur.execute(
        "SELECT COUNT(*) FROM restaurants"
    ).fetchone()[0]

    if restaurant_count == 0:

        restaurants = [
            (
                "Andhra Spice",
                "South Indian",
                4.6,
                "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=900&q=80",
                "Narsampet"
            ),
            (
                "SWIPTO Biryani House",
                "Biryani",
                4.5,
                "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=900&q=80",
                "Narsampet"
            ),
            (
                "Narsampet Food Hub",
                "Fast Food",
                4.3,
                "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80",
                "Narsampet"
            )
        ]

        cur.executemany("""
            INSERT INTO restaurants
            (name, category, rating, image, address)
            VALUES (?, ?, ?, ?, ?)
        """, restaurants)

        foods = [
            (
                1,
                "Andhra Chicken Curry",
                "Spicy Andhra style chicken curry",
                180,
                "Non-Veg",
                4.5,
                "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=700&q=80"
            ),
            (
                1,
                "Paneer Curry",
                "Rich paneer curry with spices",
                160,
                "Veg",
                4.3,
                "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=700&q=80"
            ),
            (
                1,
                "Veg Meals",
                "Rice, curry and side dishes",
                120,
                "Veg",
                4.4,
                "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=700&q=80"
            ),
            (
                2,
                "Chicken Biryani",
                "Hyderabadi style chicken biryani",
                130,
                "Non-Veg",
                4.5,
                "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=700&q=80"
            ),
            (
                2,
                "Mutton Biryani",
                "Special mutton dum biryani",
                220,
                "Non-Veg",
                4.4,
                "https://images.unsplash.com/photo-1631515242808-497c3fbd3972?auto=format&fit=crop&w=700&q=80"
            ),
            (
                2,
                "Veg Biryani",
                "Fresh vegetable biryani",
                100,
                "Veg",
                4.0,
                "https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=700&q=80"
            ),
            (
                3,
                "Chicken Fry",
                "Crispy spicy chicken fry",
                180,
                "Non-Veg",
                4.2,
                "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?auto=format&fit=crop&w=700&q=80"
            ),
            (
                3,
                "Veg Burger",
                "Loaded veg burger",
                110,
                "Veg",
                4.1,
                "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=700&q=80"
            ),
            (
                3,
                "Cheese Pizza",
                "Cheesy pizza with herbs",
                199,
                "Veg",
                4.3,
                "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=700&q=80"
            )
        ]

        cur.executemany("""
            INSERT INTO foods
            (restaurant_id, name, description, price, type, rating, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, foods)

    conn.commit()
    conn.close()


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# ==========================================
# RESTAURANTS
# ==========================================

@app.route("/api/restaurants")
def restaurants():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM restaurants
        WHERE active = 1
        ORDER BY rating DESC, id DESC
    """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route("/api/restaurant/<int:restaurant_id>")
def restaurant_details(restaurant_id):

    conn = get_db()

    restaurant = conn.execute("""
        SELECT *
        FROM restaurants
        WHERE id = ?
    """, (restaurant_id,)).fetchone()

    conn.close()

    if not restaurant:
        return jsonify(success=False, message="Restaurant not found"), 404

    return jsonify(success=True, restaurant=dict(restaurant))


# ==========================================
# MENU
# ==========================================

@app.route("/api/restaurant/<int:restaurant_id>/menu")
def menu(restaurant_id):

    food_type = request.args.get("type", "").strip()

    conn = get_db()

    if food_type in ("Veg", "Non-Veg"):

        rows = conn.execute("""
            SELECT *
            FROM foods
            WHERE restaurant_id = ?
            AND type = ?
            AND available = 1
            ORDER BY rating DESC
        """, (restaurant_id, food_type)).fetchall()

    else:

        rows = conn.execute("""
            SELECT *
            FROM foods
            WHERE restaurant_id = ?
            AND available = 1
            ORDER BY rating DESC
        """, (restaurant_id,)).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


# ==========================================
# POPULAR FOODS
# ==========================================

@app.route("/api/popular")
def popular():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            foods.*,
            restaurants.name AS restaurant_name
        FROM foods
        JOIN restaurants
        ON restaurants.id = foods.restaurant_id
        WHERE foods.available = 1
        AND restaurants.active = 1
        ORDER BY foods.rating DESC, foods.id DESC
        LIMIT 12
    """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


# ==========================================
# SEARCH
# ==========================================

@app.route("/api/search")
def search():

    q = request.args.get("q", "").strip()

    conn = get_db()

    if q:

        like = f"%{q}%"

        rows = conn.execute("""
            SELECT
                foods.*,
                restaurants.name AS restaurant_name
            FROM foods
            JOIN restaurants
            ON restaurants.id = foods.restaurant_id
            WHERE foods.available = 1
            AND restaurants.active = 1
            AND (
                foods.name LIKE ?
                OR foods.description LIKE ?
                OR foods.type LIKE ?
                OR restaurants.name LIKE ?
                OR restaurants.category LIKE ?
            )
            ORDER BY foods.rating DESC
        """, (like, like, like, like, like)).fetchall()

    else:

        rows = conn.execute("""
            SELECT
                foods.*,
                restaurants.name AS restaurant_name
            FROM foods
            JOIN restaurants
            ON restaurants.id = foods.restaurant_id
            WHERE foods.available = 1
            ORDER BY foods.rating DESC
            LIMIT 12
        """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


# ==========================================
# REGISTER / LOGIN CUSTOMER
# ==========================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()

    phone = "".join(filter(str.isdigit, phone))

    if len(name) < 2:
        return jsonify(
            success=False,
            message="Please enter your name."
        ), 400

    if len(phone) != 10:
        return jsonify(
            success=False,
            message="Please enter a valid 10 digit mobile number."
        ), 400

    conn = get_db()
    cur = conn.cursor()

    existing = cur.execute("""
        SELECT *
        FROM customers
        WHERE phone = ?
    """, (phone,)).fetchone()

    if existing:

        cur.execute("""
            UPDATE customers
            SET name = ?
            WHERE id = ?
        """, (name, existing["id"]))

        customer_id = existing["id"]

    else:

        cur.execute("""
            INSERT INTO customers
            (name, phone)
            VALUES (?, ?)
        """, (name, phone))

        customer_id = cur.lastrowid

    conn.commit()

    customer = conn.execute("""
        SELECT *
        FROM customers
        WHERE id = ?
    """, (customer_id,)).fetchone()

    conn.close()

    return jsonify(
        success=True,
        message="Login successful",
        user=dict(customer)
    )


# ==========================================
# PLACE ORDER
# ==========================================

@app.route("/api/order", methods=["POST"])
def place_order():

    data = request.get_json(silent=True) or {}

    customer_id = data.get("customer_id")
    restaurant_id = data.get("restaurant_id")
    items = data.get("items") or []

    payment_mode = str(
        data.get("payment_mode", "Cash on Delivery")
    ).strip()

    address = str(
        data.get("address", "")
    ).strip()

    instructions = str(
        data.get("instructions", "")
    ).strip()

    if not customer_id:
        return jsonify(
            success=False,
            message="Please login first."
        ), 400

    if not items:
        return jsonify(
            success=False,
            message="Your cart is empty."
        ), 400

    if len(address) < 5:
        return jsonify(
            success=False,
            message="Please enter delivery address."
        ), 400

    conn = get_db()

    customer = conn.execute("""
        SELECT *
        FROM customers
        WHERE id = ?
    """, (customer_id,)).fetchone()

    if not customer:
        conn.close()
        return jsonify(
            success=False,
            message="Customer not found. Please login again."
        ), 400

    item_total = 0
    clean_items = []

    for item in items:

        try:
            food_id = int(item.get("id"))
            quantity = max(
                1,
                int(item.get("quantity", 1))
            )
        except Exception:
            continue

        food = conn.execute("""
            SELECT *
            FROM foods
            WHERE id = ?
            AND available = 1
        """, (food_id,)).fetchone()

        if not food:
            continue

        line_total = float(food["price"]) * quantity

        item_total += line_total

        clean_items.append({
            "food": food,
            "quantity": quantity
        })

    if not clean_items:
        conn.close()

        return jsonify(
            success=False,
            message="No valid food items found."
        ), 400

    # FEES
    delivery_fee = 25.0

    # Free delivery above 500
    if item_total >= 500:
        delivery_fee = 0.0

    platform_fee = 5.0

    grand_total = (
        item_total
        + delivery_fee
        + platform_fee
    )

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders
        (
            customer_id,
            restaurant_id,
            item_total,
            delivery_fee,
            platform_fee,
            grand_total,
            payment_mode,
            address,
            instructions,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_id,
        restaurant_id,
        item_total,
        delivery_fee,
        platform_fee,
        grand_total,
        payment_mode,
        address,
        instructions,
        "Order Placed"
    ))

    order_id = cur.lastrowid

    for item in clean_items:

        food = item["food"]
        quantity = item["quantity"]

        cur.execute("""
            INSERT INTO order_items
            (
                order_id,
                food_id,
                food_name,
                price,
                quantity
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            order_id,
            food["id"],
            food["name"],
            food["price"],
            quantity
        ))

    conn.commit()
    conn.close()

    return jsonify(
        success=True,
        message="Order placed successfully!",
        order_id=order_id,
        item_total=round(item_total, 2),
        delivery_fee=round(delivery_fee, 2),
        platform_fee=round(platform_fee, 2),
        grand_total=round(grand_total, 2),
        status="Order Placed"
    )


# ==========================================
# CUSTOMER ORDERS
# ==========================================

@app.route("/api/orders/<int:customer_id>")
def customer_orders(customer_id):

    conn = get_db()

    orders = conn.execute("""
        SELECT *
        FROM orders
        WHERE customer_id = ?
        ORDER BY id DESC
    """, (customer_id,)).fetchall()

    result = []

    for order in orders:

        order_data = dict(order)

        items = conn.execute("""
            SELECT *
            FROM order_items
            WHERE order_id = ?
        """, (order["id"],)).fetchall()

        order_data["items"] = rows_to_dict(items)

        result.append(order_data)

    conn.close()

    return jsonify(result)


# ==========================================
# SINGLE ORDER
# ==========================================

@app.route("/api/order/<int:order_id>")
def get_order(order_id):

    conn = get_db()

    order = conn.execute("""
        SELECT *
        FROM orders
        WHERE id = ?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        return jsonify(
            success=False,
            message="Order not found."
        ), 404

    items = conn.execute("""
        SELECT *
        FROM order_items
        WHERE order_id = ?
    """, (order_id,)).fetchall()

    conn.close()

    return jsonify(
        success=True,
        order=dict(order),
        items=rows_to_dict(items)
    )


# ==========================================
# ADMIN LOGIN
# ==========================================

@app.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json(silent=True) or {}

    username = str(
        data.get("username", "")
    ).strip()

    password = str(
        data.get("password", "")
    ).strip()

    admin_user = os.environ.get(
        "ADMIN_USER",
        "admin"
    )

    admin_password = os.environ.get(
        "ADMIN_PASSWORD",
        "swipto123"
    )

    if (
        username == admin_user
        and password == admin_password
    ):
        return jsonify(
            success=True,
            message="Admin login successful",
            admin={
                "name": "SWIPTO Admin",
                "role": "Owner"
            }
        )

    return jsonify(
        success=False,
        message="Invalid admin username or password."
    ), 401


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/api/admin/dashboard")
def admin_dashboard():

    conn = get_db()

    total_orders = conn.execute("""
        SELECT COUNT(*)
        FROM orders
    """).fetchone()[0]

    total_customers = conn.execute("""
        SELECT COUNT(*)
        FROM customers
    """).fetchone()[0]

    total_restaurants = conn.execute("""
        SELECT COUNT(*)
        FROM restaurants
        WHERE active = 1
    """).fetchone()[0]

    total_sales = conn.execute("""
        SELECT COALESCE(SUM(grand_total), 0)
        FROM orders
        WHERE status != 'Cancelled'
    """).fetchone()[0]

    pending_orders = conn.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE status IN
        ('Order Placed', 'Preparing', 'Out for Delivery')
    """).fetchone()[0]

    conn.close()

    return jsonify(
        success=True,
        total_orders=total_orders,
        total_customers=total_customers,
        total_restaurants=total_restaurants,
        total_sales=round(total_sales, 2),
        pending_orders=pending_orders
    )


# ==========================================
# ADMIN ALL ORDERS
# ==========================================

@app.route("/api/admin/orders")
def admin_orders():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
            customers.name AS customer_name,
            customers.phone AS customer_phone,
            restaurants.name AS restaurant_name
        FROM orders
        LEFT JOIN customers
        ON customers.id = orders.customer_id
        LEFT JOIN restaurants
        ON restaurants.id = orders.restaurant_id
        ORDER BY orders.id DESC
    """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


# ==========================================
# UPDATE ORDER STATUS
# ==========================================

@app.route(
    "/api/admin/order/<int:order_id>/status",
    methods=["PUT"]
)
def update_order_status(order_id):

    data = request.get_json(silent=True) or {}

    status = str(
        data.get("status", "")
    ).strip()

    valid_statuses = [
        "Order Placed",
        "Preparing",
        "Out for Delivery",
        "Delivered",
        "Cancelled"
    ]

    if status not in valid_statuses:
        return jsonify(
            success=False,
            message="Invalid order status."
        ), 400

    conn = get_db()

    cur = conn.cursor()

    cur.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ?
    """, (status, order_id))

    conn.commit()

    if cur.rowcount == 0:
        conn.close()

        return jsonify(
            success=False,
            message="Order not found."
        ), 404

    conn.close()

    return jsonify(
        success=True,
        message="Order status updated.",
        status=status
    )


# ==========================================
# ADD RESTAURANT
# ==========================================

@app.route(
    "/api/admin/restaurant",
    methods=["POST"]
)
def add_restaurant():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "")).strip()
    image = str(data.get("image", "")).strip()
    address = str(data.get("address", "")).strip()

    try:
        rating = float(data.get("rating", 4.0))
    except Exception:
        rating = 4.0

    if len(name) < 2:
        return jsonify(
            success=False,
            message="Restaurant name is required."
        ), 400

    conn = get_db()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO restaurants
        (name, category, rating, image, address)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        category,
        rating,
        image,
        address
    ))

    restaurant_id = cur.lastrowid

    conn.commit()
    conn.close()

    return jsonify(
        success=True,
        message="Restaurant added successfully.",
        restaurant_id=restaurant_id
    )


# ==========================================
# ADD FOOD
# ==========================================

@app.route(
    "/api/admin/food",
    methods=["POST"]
)
def add_food():

    data = request.get_json(silent=True) or {}

    restaurant_id = data.get("restaurant_id")

    name = str(
        data.get("name", "")
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()

    food_type = str(
        data.get("type", "Veg")
    ).strip()

    image = str(
        data.get("image", "")
    ).strip()

    try:
        price = float(data.get("price", 0))
    except Exception:
        price = 0

    try:
        rating = float(data.get("rating", 4.0))
    except Exception:
        rating = 4.0

    if not restaurant_id:
        return jsonify(
            success=False,
            message="Restaurant is required."
        ), 400

    if len(name) < 2:
        return jsonify(
            success=False,
            message="Food name is required."
        ), 400

    if price <= 0:
        return jsonify(
            success=False,
            message="Enter valid food price."
        ), 400

    conn = get_db()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO foods
        (
            restaurant_id,
            name,
            description,
            price,
            type,
            rating,
            image
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        restaurant_id,
        name,
        description,
        price,
        food_type,
        rating,
        image
    ))

    food_id = cur.lastrowid

    conn.commit()
    conn.close()

    return jsonify(
        success=True,
        message="Food added successfully.",
        food_id=food_id
    )


# ==========================================
# UPDATE FOOD
# ==========================================

@app.route(
    "/api/admin/food/<int:food_id>",
    methods=["PUT"]
)
def update_food(food_id):

    data = request.get_json(silent=True) or {}

    name = str(
        data.get("name", "")
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()

    food_type = str(
        data.get("type", "Veg")
    ).strip()

    image = str(
        data.get("image", "")
    ).strip()

    try:
        price = float(data.get("price", 0))
    except Exception:
        price = 0

    try:
        rating = float(data.get("rating", 4.0))
    except Exception:
        rating = 4.0

    available = int(
        data.get("available", 1)
    )

    conn = get_db()

    cur = conn.cursor()

    cur.execute("""
        UPDATE foods
        SET
            name = ?,
            description = ?,
            price = ?,
            type = ?,
            rating = ?,
            image = ?,
            available = ?
        WHERE id = ?
    """, (
        name,
        description,
        price,
        food_type,
        rating,
        image,
        available,
        food_id
    ))

    conn.commit()

    if cur.rowcount == 0:
        conn.close()

        return jsonify(
            success=False,
            message="Food not found."
        ), 404

    conn.close()

    return jsonify(
        success=True,
        message="Food updated successfully."
    )


# ==========================================
# DELETE FOOD
# ==========================================

@app.route(
    "/api/admin/food/<int:food_id>",
    methods=["DELETE"]
)
def delete_food(food_id):

    conn = get_db()

    cur = conn.cursor()

    cur.execute("""
        DELETE FROM foods
        WHERE id = ?
    """, (food_id,))

    conn.commit()

    if cur.rowcount == 0:
        conn.close()

        return jsonify(
            success=False,
            message="Food not found."
        ), 404

    conn.close()

    return jsonify(
        success=True,
        message="Food deleted successfully."
    )


# ==========================================
# APP INFO
# ==========================================

@app.route("/api/app-info")
def app_info():

    return jsonify({
        "app_name": "SWIPTO",
        "tagline": "Narsampet Food Delivery Platform",
        "founder": "NIMMANABOINA RAJESH",
        "city": "Narsampet",
        "delivery_fee": 25,
        "free_delivery_above": 500
    })


# ==========================================
# RUN APP
# ==========================================

if __name__ == "__main__":

    init_db()

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )

else:
    init_db()
