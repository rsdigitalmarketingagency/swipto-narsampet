import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "swipto.db")

app = Flask(__name__, static_folder="static", static_url_path="/static")


# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_list(rows):
    return [dict(row) for row in rows]


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # CUSTOMERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        photo TEXT,
        address TEXT,
        blocked INTEGER DEFAULT 0,
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
        owner_name TEXT,
        phone TEXT,
        password TEXT,
        address TEXT,
        approved INTEGER DEFAULT 1,
        commission REAL DEFAULT 10,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
        available INTEGER DEFAULT 1,
        image TEXT
    )
    """)

    # DELIVERY PARTNERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS delivery_partners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        password TEXT,
        vehicle_number TEXT,
        available INTEGER DEFAULT 1,
        blocked INTEGER DEFAULT 0,
        earnings REAL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ORDERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        restaurant_id INTEGER,
        delivery_partner_id INTEGER,
        item_total REAL NOT NULL,
        delivery_fee REAL NOT NULL,
        platform_fee REAL NOT NULL,
        discount REAL DEFAULT 0,
        grand_total REAL NOT NULL,
        payment_mode TEXT NOT NULL,
        address TEXT NOT NULL,
        instructions TEXT,
        coupon_code TEXT,
        status TEXT DEFAULT 'Order Placed',
        restaurant_status TEXT DEFAULT 'Pending',
        delivery_status TEXT DEFAULT 'Waiting',
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

    # COUPONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        discount_type TEXT DEFAULT 'flat',
        discount_value REAL NOT NULL,
        min_order REAL DEFAULT 0,
        active INTEGER DEFAULT 1
    )
    """)

    # FAVOURITES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS favourites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        restaurant_id INTEGER,
        food_id INTEGER
    )
    """)

    # REVIEWS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        restaurant_id INTEGER,
        food_id INTEGER,
        rating REAL NOT NULL,
        review TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # APP SETTINGS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        setting_key TEXT PRIMARY KEY,
        setting_value TEXT
    )
    """)

    settings = {
        "delivery_fee": "25",
        "platform_fee": "5",
        "commission": "10",
        "owner_name": "NIMMANABOINA RAJESH",
        "owner_whatsapp": "",
        "app_name": "SWIPTO"
    }

    for key, value in settings.items():
        cur.execute("""
        INSERT OR IGNORE INTO app_settings
        (setting_key, setting_value)
        VALUES (?, ?)
        """, (key, value))

    # DEFAULT COUPONS
    cur.execute("""
    INSERT OR IGNORE INTO coupons
    (code, discount_type, discount_value, min_order, active)
    VALUES ('SWIPTO50', 'flat', 50, 300, 1)
    """)

    cur.execute("""
    INSERT OR IGNORE INTO coupons
    (code, discount_type, discount_value, min_order, active)
    VALUES ('WELCOME10', 'percent', 10, 200, 1)
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
                "Restaurant Owner",
                "9000000001",
                "1234",
                "Narsampet",
                1,
                10
            ),
            (
                "SWIPTO Biryani House",
                "Biryani",
                4.5,
                "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=900&q=80",
                "Biryani Owner",
                "9000000002",
                "1234",
                "Narsampet",
                1,
                10
            ),
            (
                "Narsampet Food Hub",
                "Fast Food",
                4.3,
                "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80",
                "Food Hub Owner",
                "9000000003",
                "1234",
                "Narsampet",
                1,
                10
            )
        ]

        cur.executemany("""
        INSERT INTO restaurants
        (name,category,rating,image,owner_name,phone,password,address,approved,commission)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """, restaurants)

        foods = [
            (1, "Andhra Chicken Curry", "Spicy Andhra style chicken curry", 180, "Non-Veg", 4.5, 1, ""),
            (1, "Paneer Curry", "Rich paneer curry with spices", 160, "Veg", 4.3, 1, ""),
            (1, "Veg Meals", "Rice, curry and side dishes", 120, "Veg", 4.4, 1, ""),
            (2, "Chicken Biryani", "Hyderabadi style chicken biryani", 130, "Non-Veg", 4.5, 1, ""),
            (2, "Mutton Biryani", "Special mutton dum biryani", 220, "Non-Veg", 4.4, 1, ""),
            (2, "Veg Biryani", "Fresh vegetable biryani", 100, "Veg", 4.0, 1, ""),
            (3, "Chicken Fry", "Crispy spicy chicken fry", 180, "Non-Veg", 4.2, 1, ""),
            (3, "Veg Burger", "Loaded veg burger", 110, "Veg", 4.1, 1, ""),
            (3, "Cheese Pizza", "Cheesy pizza with herbs", 199, "Veg", 4.3, 1, "")
        ]

        cur.executemany("""
        INSERT INTO foods
        (restaurant_id,name,description,price,type,rating,available,image)
        VALUES (?,?,?,?,?,?,?,?)
        """, foods)

    conn.commit()
    conn.close()


# =========================
# HELPER FUNCTIONS
# =========================

def get_setting(key, default=""):
    conn = get_db()
    row = conn.execute(
        "SELECT setting_value FROM app_settings WHERE setting_key=?",
        (key,)
    ).fetchone()
    conn.close()
    return row["setting_value"] if row else default


def get_order_items(order_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT food_name, price, quantity
        FROM order_items
        WHERE order_id=?
    """, (order_id,)).fetchall()
    conn.close()
    return rows_to_list(rows)


def full_order(row):
    order = dict(row)
    order["items"] = get_order_items(order["id"])
    return order


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# =========================
# PUBLIC SETTINGS
# =========================

@app.route("/api/settings/public")
def public_settings():
    return jsonify({
        "delivery_fee": float(get_setting("delivery_fee", "25")),
        "platform_fee": float(get_setting("platform_fee", "5")),
        "app_name": get_setting("app_name", "SWIPTO"),
        "owner_name": get_setting("owner_name", "NIMMANABOINA RAJESH")
    })


# =========================
# RESTAURANTS
# =========================

@app.route("/api/restaurants")
def restaurants():
    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM restaurants
        WHERE approved=1
        ORDER BY rating DESC, id DESC
    """).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


@app.route("/api/restaurant/<int:restaurant_id>/menu")
def menu(restaurant_id):

    food_type = request.args.get("type")

    conn = get_db()

    query = """
        SELECT * FROM foods
        WHERE restaurant_id=? AND available=1
    """

    params = [restaurant_id]

    if food_type in ("Veg", "Non-Veg"):
        query += " AND type=?"
        params.append(food_type)

    query += " ORDER BY rating DESC, id DESC"

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


@app.route("/api/popular")
def popular():

    conn = get_db()

    rows = conn.execute("""
        SELECT foods.*, restaurants.name AS restaurant_name
        FROM foods
        LEFT JOIN restaurants
        ON restaurants.id=foods.restaurant_id
        WHERE foods.available=1
        AND restaurants.approved=1
        ORDER BY foods.rating DESC, foods.id DESC
        LIMIT 20
    """).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


# =========================
# SEARCH
# =========================

@app.route("/api/search")
def search():

    q = request.args.get("q", "").strip()

    conn = get_db()

    if not q:
        rows = conn.execute("""
            SELECT foods.*, restaurants.name AS restaurant_name
            FROM foods
            JOIN restaurants
            ON restaurants.id=foods.restaurant_id
            WHERE foods.available=1
            AND restaurants.approved=1
            ORDER BY foods.rating DESC
            LIMIT 20
        """).fetchall()

    else:

        like = f"%{q}%"

        rows = conn.execute("""
            SELECT foods.*, restaurants.name AS restaurant_name
            FROM foods
            JOIN restaurants
            ON restaurants.id=foods.restaurant_id
            WHERE foods.available=1
            AND restaurants.approved=1
            AND (
                foods.name LIKE ?
                OR foods.description LIKE ?
                OR foods.type LIKE ?
                OR restaurants.name LIKE ?
                OR restaurants.category LIKE ?
            )
            ORDER BY foods.rating DESC
        """, (like, like, like, like, like)).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


# =========================
# CUSTOMER REGISTER / LOGIN
# =========================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()

    if len(name) < 2:
        return jsonify(
            success=False,
            message="Enter valid name."
        ), 400

    if len(phone) < 10:
        return jsonify(
            success=False,
            message="Enter valid mobile number."
        ), 400

    conn = get_db()
    cur = conn.cursor()

    row = cur.execute("""
        SELECT * FROM customers
        WHERE phone=?
    """, (phone,)).fetchone()

    if row:

        if row["blocked"]:
            conn.close()
            return jsonify(
                success=False,
                message="Your account is blocked."
            ), 403

        cur.execute("""
            UPDATE customers
            SET name=?
            WHERE id=?
        """, (name, row["id"]))

        customer_id = row["id"]

    else:

        cur.execute("""
            INSERT INTO customers (name,phone)
            VALUES (?,?)
        """, (name, phone))

        customer_id = cur.lastrowid

    conn.commit()

    user = conn.execute("""
        SELECT * FROM customers
        WHERE id=?
    """, (customer_id,)).fetchone()

    conn.close()

    return jsonify(
        success=True,
        user=dict(user)
    )


# =========================
# ADD ADDRESS
# =========================

@app.route("/api/customer/address", methods=["POST"])
def save_address():

    data = request.get_json(silent=True) or {}

    customer_id = data.get("customer_id")
    address = str(data.get("address", "")).strip()

    if not customer_id or not address:
        return jsonify(
            success=False,
            message="Customer and address required."
        ), 400

    conn = get_db()

    conn.execute("""
        UPDATE customers
        SET address=?
        WHERE id=?
    """, (address, customer_id))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# =========================
# COUPON
# =========================

@app.route("/api/coupon/apply", methods=["POST"])
def apply_coupon():

    data = request.get_json(silent=True) or {}

    code = str(data.get("code", "")).strip().upper()
    amount = float(data.get("amount", 0))

    if not code:
        return jsonify(
            success=False,
            message="Enter coupon code."
        ), 400

    conn = get_db()

    coupon = conn.execute("""
        SELECT * FROM coupons
        WHERE code=? AND active=1
    """, (code,)).fetchone()

    conn.close()

    if not coupon:
        return jsonify(
            success=False,
            message="Invalid coupon."
        ), 400

    if amount < coupon["min_order"]:
        return jsonify(
            success=False,
            message=f"Minimum order ₹{coupon['min_order']} required."
        ), 400

    if coupon["discount_type"] == "percent":
        discount = amount * coupon["discount_value"] / 100
    else:
        discount = coupon["discount_value"]

    discount = min(discount, amount)

    return jsonify(
        success=True,
        code=coupon["code"],
        discount=round(discount, 2)
    )


# =========================
# PLACE ORDER
# =========================

@app.route("/api/order", methods=["POST"])
def order():

    data = request.get_json(silent=True) or {}

    customer_id = data.get("customer_id")
    restaurant_id = data.get("restaurant_id")
    items = data.get("items") or []
    payment_mode = data.get("payment_mode", "COD")
    address = str(data.get("address", "")).strip()
    instructions = str(data.get("instructions", "")).strip()
    coupon_code = str(data.get("coupon_code", "")).strip().upper()

    if not customer_id:
        return jsonify(
            success=False,
            message="Customer required."
        ), 400

    if not items:
        return jsonify(
            success=False,
            message="Cart is empty."
        ), 400

    if not address:
        return jsonify(
            success=False,
            message="Delivery address required."
        ), 400

    conn = get_db()

    customer = conn.execute("""
        SELECT * FROM customers
        WHERE id=?
    """, (customer_id,)).fetchone()

    if not customer:
        conn.close()
        return jsonify(
            success=False,
            message="Customer not found."
        ), 400

    if customer["blocked"]:
        conn.close()
        return jsonify(
            success=False,
            message="Your account is blocked."
        ), 403

    clean_items = []
    item_total = 0.0
    detected_restaurant_id = None

    for item in items:

        try:
            food_id = int(item.get("id"))
            qty = max(1, int(item.get("quantity", 1)))
        except Exception:
            continue

        food = conn.execute("""
            SELECT * FROM foods
            WHERE id=? AND available=1
        """, (food_id,)).fetchone()

        if not food:
            continue

        if detected_restaurant_id is None:
            detected_restaurant_id = food["restaurant_id"]

        if food["restaurant_id"] != detected_restaurant_id:
            conn.close()
            return jsonify(
                success=False,
                message="You can order from one restaurant at a time."
            ), 400

        line_total = float(food["price"]) * qty
        item_total += line_total

        clean_items.append({
            "food": food,
            "quantity": qty
        })

    if not clean_items:
        conn.close()
        return jsonify(
            success=False,
            message="No valid food items."
        ), 400

    restaurant_id = detected_restaurant_id

    delivery_fee = float(get_setting("delivery_fee", "25"))
    platform_fee = float(get_setting("platform_fee", "5"))

    discount = 0

    if coupon_code:

        coupon = conn.execute("""
            SELECT * FROM coupons
            WHERE code=? AND active=1
        """, (coupon_code,)).fetchone()

        if coupon and item_total >= coupon["min_order"]:

            if coupon["discount_type"] == "percent":
                discount = (
                    item_total * coupon["discount_value"] / 100
                )
            else:
                discount = coupon["discount_value"]

            discount = min(discount, item_total)

        else:
            coupon_code = ""

    grand_total = (
        item_total
        + delivery_fee
        + platform_fee
        - discount
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
            discount,
            grand_total,
            payment_mode,
            address,
            instructions,
            coupon_code,
            status,
            restaurant_status,
            delivery_status
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        customer_id,
        restaurant_id,
        item_total,
        delivery_fee,
        platform_fee,
        discount,
        grand_total,
        payment_mode,
        address,
        instructions,
        coupon_code,
        "Order Placed",
        "Pending",
        "Waiting"
    ))

    order_id = cur.lastrowid

    for item in clean_items:

        food = item["food"]
        qty = item["quantity"]

        cur.execute("""
            INSERT INTO order_items
            (
                order_id,
                food_id,
                food_name,
                price,
                quantity
            )
            VALUES (?,?,?,?,?)
        """, (
            order_id,
            food["id"],
            food["name"],
            food["price"],
            qty
        ))

    conn.commit()

    restaurant = conn.execute("""
        SELECT name FROM restaurants
        WHERE id=?
    """, (restaurant_id,)).fetchone()

    conn.close()

    return jsonify(
        success=True,
        order_id=order_id,
        restaurant=restaurant["name"] if restaurant else "",
        item_total=round(item_total, 2),
        delivery_fee=round(delivery_fee, 2),
        platform_fee=round(platform_fee, 2),
        discount=round(discount, 2),
        grand_total=round(grand_total, 2),
        status="Order Placed"
    )


# =========================
# CUSTOMER ORDERS
# =========================

@app.route("/api/orders/<int:customer_id>")
def customer_orders(customer_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
            restaurants.name AS restaurant_name,
            delivery_partners.name AS delivery_partner_name
        FROM orders
        LEFT JOIN restaurants
        ON restaurants.id=orders.restaurant_id
        LEFT JOIN delivery_partners
        ON delivery_partners.id=orders.delivery_partner_id
        WHERE orders.customer_id=?
        ORDER BY orders.id DESC
    """, (customer_id,)).fetchall()

    conn.close()

    return jsonify([
        full_order(row)
        for row in rows
    ])


# =========================
# RESTAURANT LOGIN
# =========================

@app.route("/api/restaurant/login", methods=["POST"])
def restaurant_login():

    data = request.get_json(silent=True) or {}

    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", "")).strip()

    conn = get_db()

    row = conn.execute("""
        SELECT * FROM restaurants
        WHERE phone=? AND password=?
    """, (phone, password)).fetchone()

    conn.close()

    if not row:
        return jsonify(
            success=False,
            message="Invalid login."
        ), 401

    if not row["approved"]:
        return jsonify(
            success=False,
            message="Restaurant approval pending."
        ), 403

    return jsonify(
        success=True,
        restaurant=dict(row)
    )


# =========================
# RESTAURANT ORDERS
# =========================

@app.route("/api/restaurant/<int:restaurant_id>/orders")
def restaurant_orders(restaurant_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
            customers.name AS customer_name,
            customers.phone AS customer_phone
        FROM orders
        LEFT JOIN customers
        ON customers.id=orders.customer_id
        WHERE orders.restaurant_id=?
        ORDER BY orders.id DESC
    """, (restaurant_id,)).fetchall()

    conn.close()

    return jsonify([
        full_order(row)
        for row in rows
    ])


@app.route("/api/restaurant/order/<int:order_id>/status", methods=["POST"])
def restaurant_order_status(order_id):

    data = request.get_json(silent=True) or {}

    status = str(data.get("status", "")).strip()

    allowed = [
        "Accepted",
        "Rejected",
        "Preparing",
        "Ready for Pickup"
    ]

    if status not in allowed:
        return jsonify(
            success=False,
            message="Invalid status."
        ), 400

    conn = get_db()

    if status == "Rejected":

        conn.execute("""
            UPDATE orders
            SET restaurant_status=?,
                status=?
            WHERE id=?
        """, (
            status,
            "Order Rejected",
            order_id
        ))

    elif status == "Accepted":

        conn.execute("""
            UPDATE orders
            SET restaurant_status=?,
                status=?
            WHERE id=?
        """, (
            status,
            "Restaurant Accepted",
            order_id
        ))

    elif status == "Preparing":

        conn.execute("""
            UPDATE orders
            SET restaurant_status=?,
                status=?
            WHERE id=?
        """, (
            status,
            "Preparing",
            order_id
        ))

    elif status == "Ready for Pickup":

        conn.execute("""
            UPDATE orders
            SET restaurant_status=?,
                status=?
            WHERE id=?
        """, (
            status,
            "Ready for Pickup"
        , order_id))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# =========================
# RESTAURANT FOOD MANAGEMENT
# =========================

@app.route("/api/restaurant/<int:restaurant_id>/foods")
def restaurant_foods(restaurant_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM foods
        WHERE restaurant_id=?
        ORDER BY id DESC
    """, (restaurant_id,)).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


@app.route("/api/restaurant/food", methods=["POST"])
def add_food():

    data = request.get_json(silent=True) or {}

    restaurant_id = data.get("restaurant_id")
    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    price = data.get("price")
    food_type = str(data.get("type", "Veg")).strip()

    if not restaurant_id or not name or price is None:
        return jsonify(
            success=False,
            message="Restaurant, food name and price required."
        ), 400

    conn = get_db()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO foods
        (restaurant_id,name,description,price,type)
        VALUES (?,?,?,?,?)
    """, (
        restaurant_id,
        name,
        description,
        float(price),
        food_type
    ))

    food_id = cur.lastrowid

    conn.commit()
    conn.close()

    return jsonify(
        success=True,
        food_id=food_id
    )


@app.route("/api/restaurant/food/<int:food_id>", methods=["PUT"])
def update_food(food_id):

    data = request.get_json(silent=True) or {}

    conn = get_db()

    food = conn.execute("""
        SELECT * FROM foods
        WHERE id=?
    """, (food_id,)).fetchone()

    if not food:
        conn.close()
        return jsonify(
            success=False,
            message="Food not found."
        ), 404

    name = str(data.get("name", food["name"])).strip()
    description = str(
        data.get("description", food["description"] or "")
    ).strip()

    price = float(
        data.get("price", food["price"])
    )

    food_type = str(
        data.get("type", food["type"])
    ).strip()

    available = int(
        data.get("available", food["available"])
    )

    conn.execute("""
        UPDATE foods
        SET
            name=?,
            description=?,
            price=?,
            type=?,
            available=?
        WHERE id=?
    """, (
        name,
        description,
        price,
        food_type,
        available,
        food_id
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# =========================
# DELIVERY PARTNER REGISTER
# =========================

@app.route("/api/delivery/register", methods=["POST"])
def delivery_register():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", "")).strip()
    vehicle_number = str(
        data.get("vehicle_number", "")
    ).strip()

    if len(name) < 2 or len(phone) < 10 or len(password) < 4:
        return jsonify(
            success=False,
            message="Enter valid details."
        ), 400

    conn = get_db()
    cur = conn.cursor()

    existing = cur.execute("""
        SELECT id FROM delivery_partners
        WHERE phone=?
    """, (phone,)).fetchone()

    if existing:
        conn.close()
        return jsonify(
            success=False,
            message="Mobile number already registered."
        ), 400

    cur.execute("""
        INSERT INTO delivery_partners
        (name,phone,password,vehicle_number)
        VALUES (?,?,?,?)
    """, (
        name,
        phone,
        password,
        vehicle_number
    ))

    partner_id = cur.lastrowid

    conn.commit()

    partner = conn.execute("""
        SELECT * FROM delivery_partners
        WHERE id=?
    """, (partner_id,)).fetchone()

    conn.close()

    return jsonify(
        success=True,
        partner=dict(partner)
    )


# =========================
# DELIVERY LOGIN
# =========================

@app.route("/api/delivery/login", methods=["POST"])
def delivery_login():

    data = request.get_json(silent=True) or {}

    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", "")).strip()

    conn = get_db()

    row = conn.execute("""
        SELECT * FROM delivery_partners
        WHERE phone=? AND password=?
    """, (phone, password)).fetchone()

    conn.close()

    if not row:
        return jsonify(
            success=False,
            message="Invalid login."
        ), 401

    if row["blocked"]:
        return jsonify(
            success=False,
            message="Account blocked."
        ), 403

    return jsonify(
        success=True,
        partner=dict(row)
    )


# =========================
# AVAILABLE DELIVERIES
# =========================

@app.route("/api/delivery/orders")
def available_delivery_orders():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
            restaurants.name AS restaurant_name,
            restaurants.address AS restaurant_address,
            customers.name AS customer_name,
            customers.phone AS customer_phone
        FROM orders
        LEFT JOIN restaurants
        ON restaurants.id=orders.restaurant_id
        LEFT JOIN customers
        ON customers.id=orders.customer_id
        WHERE orders.restaurant_status='Ready for Pickup'
        AND orders.delivery_partner_id IS NULL
        ORDER BY orders.id ASC
    """).fetchall()

    conn.close()

    return jsonify([
        full_order(row)
        for row in rows
    ])


@app.route("/api/delivery/order/<int:order_id>/accept", methods=["POST"])
def accept_delivery(order_id):

    data = request.get_json(silent=True) or {}

    partner_id = data.get("partner_id")

    if not partner_id:
        return jsonify(
            success=False,
            message="Delivery partner required."
        ), 400

    conn = get_db()

    order = conn.execute("""
        SELECT * FROM orders
        WHERE id=?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        return jsonify(
            success=False,
            message="Order not found."
        ), 404

    if order["delivery_partner_id"]:
        conn.close()
        return jsonify(
            success=False,
            message="Order already accepted."
        ), 400

    conn.execute("""
        UPDATE orders
        SET
            delivery_partner_id=?,
            delivery_status=?,
            status=?
        WHERE id=?
    """, (
        partner_id,
        "Accepted",
        "Delivery Partner Assigned",
        order_id
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


@app.route("/api/delivery/order/<int:order_id>/status", methods=["POST"])
def delivery_status(order_id):

    data = request.get_json(silent=True) or {}

    partner_id = data.get("partner_id")
    status = str(data.get("status", "")).strip()

    allowed = [
        "Picked Up",
        "On the Way",
        "Delivered"
    ]

    if not partner_id or status not in allowed:
        return jsonify(
            success=False,
            message="Invalid delivery update."
        ), 400

    conn = get_db()

    order = conn.execute("""
        SELECT * FROM orders
        WHERE id=? AND delivery_partner_id=?
    """, (
        order_id,
        partner_id
    )).fetchone()

    if not order:
        conn.close()
        return jsonify(
            success=False,
            message="Order not assigned to you."
        ), 403

    conn.execute("""
        UPDATE orders
        SET
            delivery_status=?,
            status=?
        WHERE id=?
    """, (
        status,
        status,
        order_id
    ))

    if status == "Delivered":

        earning = float(order["delivery_fee"])

        conn.execute("""
            UPDATE delivery_partners
            SET earnings = earnings + ?
            WHERE id=?
        """, (
            earning,
            partner_id
        ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


@app.route("/api/delivery/<int:partner_id>/history")
def delivery_history(partner_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
            restaurants.name AS restaurant_name,
            customers.name AS customer_name
        FROM orders
        LEFT JOIN restaurants
        ON restaurants.id=orders.restaurant_id
        LEFT JOIN customers
        ON customers.id=orders.customer_id
        WHERE orders.delivery_partner_id=?
        ORDER BY orders.id DESC
    """, (partner_id,)).fetchall()

    partner = conn.execute("""
        SELECT * FROM delivery_partners
        WHERE id=?
    """, (partner_id,)).fetchone()

    conn.close()

    return jsonify({
        "earnings": partner["earnings"] if partner else 0,
        "orders": [
            full_order(row)
            for row in rows
        ]
    })


# =========================
# FAVOURITES
# =========================

@app.route("/api/favourite", methods=["POST"])
def add_favourite():

    data = request.get_json(silent=True) or {}

    customer_id = data.get("customer_id")
    restaurant_id = data.get("restaurant_id")
    food_id = data.get("food_id")

    if not customer_id:
        return jsonify(
            success=False,
            message="Customer required."
        ), 400

    conn = get_db()

    exists = conn.execute("""
        SELECT id FROM favourites
        WHERE customer_id=?
        AND COALESCE(restaurant_id,0)=?
        AND COALESCE(food_id,0)=?
    """, (
        customer_id,
        restaurant_id or 0,
        food_id or 0
    )).fetchone()

    if exists:
        conn.execute("""
            DELETE FROM favourites
            WHERE id=?
        """, (exists["id"],))

        action = "removed"

    else:

        conn.execute("""
            INSERT INTO favourites
            (customer_id,restaurant_id,food_id)
            VALUES (?,?,?)
        """, (
            customer_id,
            restaurant_id,
            food_id
        ))

        action = "added"

    conn.commit()
    conn.close()

    return jsonify(
        success=True,
        action=action
    )


@app.route("/api/favourites/<int:customer_id>")
def favourites(customer_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            favourites.*,
            foods.name AS food_name,
            foods.price AS food_price,
            restaurants.name AS restaurant_name
        FROM favourites
        LEFT JOIN foods
        ON foods.id=favourites.food_id
        LEFT JOIN restaurants
        ON restaurants.id=favourites.restaurant_id
        WHERE favourites.customer_id=?
        ORDER BY favourites.id DESC
    """, (customer_id,)).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


# =========================
# REVIEWS
# =========================

@app.route("/api/review", methods=["POST"])
def add_review():

    data = request.get_json(silent=True) or {}

    customer_id = data.get("customer_id")
    restaurant_id = data.get("restaurant_id")
    food_id = data.get("food_id")
    rating = float(data.get("rating", 0))
    review = str(data.get("review", "")).strip()

    if not customer_id or rating < 1 or rating > 5:
        return jsonify(
            success=False,
            message="Valid customer and rating required."
        ), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO reviews
        (customer_id,restaurant_id,food_id,rating,review)
        VALUES (?,?,?,?,?)
    """, (
        customer_id,
        restaurant_id,
        food_id,
        rating,
        review
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


@app.route("/api/reviews/restaurant/<int:restaurant_id>")
def restaurant_reviews(restaurant_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            reviews.*,
            customers.name AS customer_name
        FROM reviews
        LEFT JOIN customers
        ON customers.id=reviews.customer_id
        WHERE reviews.restaurant_id=?
        ORDER BY reviews.id DESC
    """, (restaurant_id,)).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


# =========================
# ADMIN LOGIN
# =========================

@app.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    admin_user = os.environ.get(
        "ADMIN_USER",
        "admin"
    )

    admin_password = os.environ.get(
        "ADMIN_PASSWORD",
        "swipto123"
    )

    if username == admin_user and password == admin_password:
        return jsonify(
            success=True,
            owner=get_setting(
                "owner_name",
                "NIMMANABOINA RAJESH"
            )
        )

    return jsonify(
        success=False,
        message="Invalid admin login."
    ), 401


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/api/admin/dashboard")
def admin_dashboard():

    conn = get_db()

    customers = conn.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    restaurants = conn.execute(
        "SELECT COUNT(*) FROM restaurants"
    ).fetchone()[0]

    delivery_partners = conn.execute(
        "SELECT COUNT(*) FROM delivery_partners"
    ).fetchone()[0]

    total_orders = conn.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    delivered_orders = conn.execute("""
        SELECT COUNT(*) FROM orders
        WHERE status='Delivered'
    """).fetchone()[0]

    revenue = conn.execute("""
        SELECT COALESCE(SUM(grand_total),0)
        FROM orders
        WHERE status='Delivered'
    """).fetchone()[0]

    pending_orders = conn.execute("""
        SELECT COUNT(*) FROM orders
        WHERE status NOT IN ('Delivered','Order Rejected')
    """).fetchone()[0]

    conn.close()

    return jsonify({
        "customers": customers,
        "restaurants": restaurants,
        "delivery_partners": delivery_partners,
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "revenue": round(revenue, 2),
        "pending_orders": pending_orders
    })


@app.route("/api/admin/orders")
def admin_orders():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
            customers.name AS customer_name,
            customers.phone AS customer_phone,
            restaurants.name AS restaurant_name,
            delivery_partners.name AS delivery_partner_name
        FROM orders
        LEFT JOIN customers
        ON customers.id=orders.customer_id
        LEFT JOIN restaurants
        ON restaurants.id=orders.restaurant_id
        LEFT JOIN delivery_partners
        ON delivery_partners.id=orders.delivery_partner_id
        ORDER BY orders.id DESC
    """).fetchall()

    conn.close()

    return jsonify([
        full_order(row)
        for row in rows
    ])


@app.route("/api/admin/customers")
def admin_customers():

    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM customers
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


@app.route("/api/admin/customer/<int:customer_id>/block", methods=["POST"])
def block_customer(customer_id):

    data = request.get_json(silent=True) or {}

    blocked = int(data.get("blocked", 1))

    conn = get_db()

    conn.execute("""
        UPDATE customers
        SET blocked=?
        WHERE id=?
    """, (
        blocked,
        customer_id
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


@app.route("/api/admin/restaurants")
def admin_restaurants():

    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM restaurants
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


@app.route("/api/admin/restaurant/<int:restaurant_id>/approve", methods=["POST"])
def approve_restaurant(restaurant_id):

    data = request.get_json(silent=True) or {}

    approved = int(data.get("approved", 1))

    conn = get_db()

    conn.execute("""
        UPDATE restaurants
        SET approved=?
        WHERE id=?
    """, (
        approved,
        restaurant_id
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


@app.route("/api/admin/delivery-partners")
def admin_delivery_partners():

    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM delivery_partners
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify(rows_to_list(rows))


@app.route("/api/admin/settings", methods=["GET", "POST"])
def admin_settings():

    if request.method == "GET":

        conn = get_db()

        rows = conn.execute("""
            SELECT * FROM app_settings
        """).fetchall()

        conn.close()

        return jsonify({
            row["setting_key"]: row["setting_value"]
            for row in rows
        })

    data = request.get_json(silent=True) or {}

    conn = get_db()

    for key, value in data.items():

        conn.execute("""
            INSERT INTO app_settings
            (setting_key,setting_value)
            VALUES (?,?)
            ON CONFLICT(setting_key)
            DO UPDATE SET setting_value=excluded.setting_value
        """, (
            str(key),
            str(value)
        ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


@app.route("/api/admin/coupons", methods=["GET", "POST"])
def admin_coupons():

    conn = get_db()

    if request.method == "GET":

        rows = conn.execute("""
            SELECT * FROM coupons
            ORDER BY id DESC
        """).fetchall()

        conn.close()

        return jsonify(rows_to_list(rows))

    data = request.get_json(silent=True) or {}

    code = str(data.get("code", "")).strip().upper()
    discount_type = str(
        data.get("discount_type", "flat")
    ).strip()

    discount_value = float(
        data.get("discount_value", 0)
    )

    min_order = float(
        data.get("min_order", 0)
    )

    if not code or discount_value <= 0:
        conn.close()
        return jsonify(
            success=False,
            message="Valid coupon required."
        ), 400

    try:

        conn.execute("""
            INSERT INTO coupons
            (code,discount_type,discount_value,min_order,active)
            VALUES (?,?,?,?,1)
        """, (
            code,
            discount_type,
            discount_value,
            min_order
        ))

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify(
            success=False,
            message="Coupon already exists."
        ), 400

    conn.close()

    return jsonify(success=True)


# =========================
# WHATSAPP MESSAGE FORMAT
# =========================

@app.route("/api/order/<int:order_id>/whatsapp-message")
def whatsapp_message(order_id):

    conn = get_db()

    order = conn.execute("""
        SELECT
            orders.*,
            customers.name AS customer_name,
            customers.phone AS customer_phone,
            restaurants.name AS restaurant_name
        FROM orders
        LEFT JOIN customers
        ON customers.id=orders.customer_id
        LEFT JOIN restaurants
        ON restaurants.id=orders.restaurant_id
        WHERE orders.id=?
    """, (order_id,)).fetchone()

    conn.close()

    if not order:
        return jsonify(
            success=False,
            message="Order not found."
        ), 404

    items = get_order_items(order_id)

    item_lines = []

    for item in items:

        total = (
            float(item["price"])
            * int(item["quantity"])
        )

        item_lines.append(
            f"• {item['food_name']} x {item['quantity']} = ₹{total:.0f}"
        )

    message = f"""🛵 NEW SWIPTO ORDER - NARSAMPET

🏪 Restaurant: {order['restaurant_name']}
👤 Customer: {order['customer_name']}
📞 Phone: {order['customer_phone']}
📍 Address: {order['address']}

📦 Ordered Items:
{chr(10).join(item_lines)}

💰 Item Total: ₹{order['item_total']:.0f}
🛵 Delivery Fee: ₹{order['delivery_fee']:.0f}
💰 Grand Total: ₹{order['grand_total']:.0f}
💳 Payment Mode: {order['payment_mode']}

⚡ Delivering via SWIPTO Express"""

    return jsonify(
        success=True,
        message=message
    )


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port
    )
else:
    init_db()
