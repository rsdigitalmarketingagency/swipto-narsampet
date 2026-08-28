
import os
import sqlite3
from functools import wraps
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


def rows_to_dict(rows):
    return [dict(row) for row in rows]


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        role TEXT DEFAULT 'customer',
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
        owner_id INTEGER,
        name TEXT NOT NULL,
        category TEXT,
        rating REAL DEFAULT 4.0,
        image TEXT,
        address TEXT,
        phone TEXT,
        approved INTEGER DEFAULT 1,
        active INTEGER DEFAULT 1,
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
        type TEXT DEFAULT 'Veg',
        rating REAL DEFAULT 4.0,
        image TEXT,
        available INTEGER DEFAULT 1,
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
        payment_status TEXT DEFAULT 'Pending',
        address TEXT NOT NULL,
        instructions TEXT,
        coupon_code TEXT,
        status TEXT DEFAULT 'Order Placed',
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

    # FAVORITES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        food_id INTEGER,
        restaurant_id INTEGER
    )
    """)

    # COUPONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        discount_type TEXT DEFAULT 'flat',
        discount_value REAL DEFAULT 0,
        min_order REAL DEFAULT 0,
        active INTEGER DEFAULT 1
    )
    """)

    # APP SETTINGS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        setting_key TEXT PRIMARY KEY,
        setting_value TEXT
    )
    """)

    # DEFAULT SETTINGS
    defaults = {
        "delivery_fee": "25",
        "platform_fee": "5",
        "admin_phone": "9999999999",
        "support_phone": "919999999999",
        "commission": "10"
    }

    for key, value in defaults.items():
        cur.execute(
            "INSERT OR IGNORE INTO settings (setting_key, setting_value) VALUES (?,?)",
            (key, value)
        )

    # DEFAULT ADMIN
    cur.execute("""
    INSERT OR IGNORE INTO users (name, phone, role)
    VALUES ('NIMMANABOINA RAJESH', '9999999999', 'admin')
    """)

    # SAMPLE DATA
    count = cur.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]

    if count == 0:
        restaurants = [
            (
                "Andhra Spice",
                "South Indian",
                4.6,
                "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=900&q=80",
                "Narsampet",
                "",
                1,
                1
            ),
            (
                "SWIPTO Biryani House",
                "Biryani",
                4.5,
                "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=900&q=80",
                "Narsampet",
                "",
                1,
                1
            ),
            (
                "Narsampet Food Hub",
                "Fast Food",
                4.3,
                "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80",
                "Narsampet",
                "",
                1,
                1
            )
        ]

        cur.executemany("""
        INSERT INTO restaurants
        (name,category,rating,image,address,phone,approved,active)
        VALUES (?,?,?,?,?,?,?,?)
        """, restaurants)

        foods = [
            (1, "Andhra Chicken Curry", "Spicy Andhra style chicken curry", 180, "Non-Veg", 4.5, "", 1),
            (1, "Paneer Curry", "Rich paneer curry with spices", 160, "Veg", 4.3, "", 1),
            (1, "Veg Meals", "Rice, curry and side dishes", 120, "Veg", 4.4, "", 1),

            (2, "Chicken Biryani", "Hyderabadi style chicken biryani", 130, "Non-Veg", 4.5, "", 1),
            (2, "Mutton Biryani", "Special mutton dum biryani", 220, "Non-Veg", 4.6, "", 1),
            (2, "Veg Biryani", "Fresh vegetable biryani", 100, "Veg", 4.0, "", 1),

            (3, "Chicken Fry", "Crispy spicy chicken fry", 180, "Non-Veg", 4.2, "", 1),
            (3, "Veg Burger", "Loaded veg burger", 110, "Veg", 4.1, "", 1),
            (3, "Cheese Pizza", "Cheesy pizza with herbs", 199, "Veg", 4.3, "", 1)
        ]

        cur.executemany("""
        INSERT INTO foods
        (restaurant_id,name,description,price,type,rating,image,available)
        VALUES (?,?,?,?,?,?,?,?)
        """, foods)

    # DEFAULT COUPON
    cur.execute("""
    INSERT OR IGNORE INTO coupons
    (code,discount_type,discount_value,min_order,active)
    VALUES ('SWIPTO50','flat',50,299,1)
    """)

    conn.commit()
    conn.close()


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# =========================
# SETTINGS
# =========================

def get_setting(key, default=None):
    conn = get_db()
    row = conn.execute(
        "SELECT setting_value FROM settings WHERE setting_key=?",
        (key,)
    ).fetchone()
    conn.close()

    return row["setting_value"] if row else default


@app.route("/api/settings/public")
def public_settings():
    return jsonify({
        "delivery_fee": float(get_setting("delivery_fee", "25")),
        "platform_fee": float(get_setting("platform_fee", "5")),
        "support_phone": get_setting("support_phone", "")
    })


# =========================
# USER LOGIN / REGISTER
# =========================

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    role = str(data.get("role", "customer")).strip()

    if len(name) < 2:
        return jsonify(success=False, message="Enter valid name."), 400

    if len(phone) < 10:
        return jsonify(success=False, message="Enter valid mobile number."), 400

    allowed_roles = ["customer", "restaurant", "delivery"]

    if role not in allowed_roles:
        role = "customer"

    conn = get_db()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM users WHERE phone=?",
        (phone,)
    ).fetchone()

    if user:
        if user["blocked"] == 1:
            conn.close()
            return jsonify(
                success=False,
                message="Your account is blocked. Contact SWIPTO support."
            ), 403

        cur.execute(
            "UPDATE users SET name=? WHERE id=?",
            (name, user["id"])
        )

        user_id = user["id"]

    else:
        cur.execute("""
        INSERT INTO users (name,phone,role)
        VALUES (?,?,?)
        """, (name, phone, role))

        user_id = cur.lastrowid

    conn.commit()

    user = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    return jsonify(
        success=True,
        user=dict(user)
    )


@app.route("/api/profile/<int:user_id>")
def profile(user_id):
    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    if not user:
        return jsonify(success=False), 404

    return jsonify(success=True, user=dict(user))


@app.route("/api/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    address = str(data.get("address", "")).strip()

    conn = get_db()

    conn.execute("""
    UPDATE users
    SET name=?, address=?
    WHERE id=?
    """, (name, address, user_id))

    conn.commit()

    user = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    return jsonify(success=True, user=dict(user))


# =========================
# RESTAURANTS
# =========================

@app.route("/api/restaurants")
def restaurants():
    conn = get_db()

    rows = conn.execute("""
    SELECT * FROM restaurants
    WHERE approved=1 AND active=1
    ORDER BY rating DESC, id
    """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route("/api/restaurant/<int:restaurant_id>")
def restaurant_details(restaurant_id):
    conn = get_db()

    restaurant = conn.execute(
        "SELECT * FROM restaurants WHERE id=?",
        (restaurant_id,)
    ).fetchone()

    conn.close()

    if not restaurant:
        return jsonify(success=False), 404

    return jsonify(success=True, restaurant=dict(restaurant))


# =========================
# MENU
# =========================

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

    query += " ORDER BY rating DESC, id"

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route("/api/popular")
def popular():
    conn = get_db()

    rows = conn.execute("""
    SELECT foods.*, restaurants.name AS restaurant_name
    FROM foods
    JOIN restaurants ON restaurants.id=foods.restaurant_id
    WHERE foods.available=1
    AND restaurants.approved=1
    AND restaurants.active=1
    ORDER BY foods.rating DESC
    LIMIT 20
    """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip()

    conn = get_db()

    if q:
        like = f"%{q}%"

        rows = conn.execute("""
        SELECT foods.*, restaurants.name AS restaurant_name
        FROM foods
        JOIN restaurants ON restaurants.id=foods.restaurant_id
        WHERE foods.available=1
        AND (
            foods.name LIKE ?
            OR foods.description LIKE ?
            OR restaurants.name LIKE ?
            OR restaurants.category LIKE ?
        )
        ORDER BY foods.rating DESC
        """, (like, like, like, like)).fetchall()

    else:
        rows = conn.execute("""
        SELECT foods.*, restaurants.name AS restaurant_name
        FROM foods
        JOIN restaurants ON restaurants.id=foods.restaurant_id
        WHERE foods.available=1
        ORDER BY foods.rating DESC
        LIMIT 20
        """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


# =========================
# FAVORITES
# =========================

@app.route("/api/favorites/<int:user_id>")
def get_favorites(user_id):
    conn = get_db()

    rows = conn.execute("""
    SELECT favorites.*, foods.name AS food_name,
           foods.price, foods.type,
           restaurants.name AS restaurant_name
    FROM favorites
    LEFT JOIN foods ON foods.id=favorites.food_id
    LEFT JOIN restaurants ON restaurants.id=favorites.restaurant_id
    WHERE favorites.user_id=?
    ORDER BY favorites.id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route("/api/favorite", methods=["POST"])
def toggle_favorite():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    food_id = data.get("food_id")
    restaurant_id = data.get("restaurant_id")

    if not user_id:
        return jsonify(success=False, message="Login required."), 400

    conn = get_db()

    existing = conn.execute("""
    SELECT id FROM favorites
    WHERE user_id=?
    AND food_id IS ?
    AND restaurant_id IS ?
    """, (user_id, food_id, restaurant_id)).fetchone()

    if existing:
        conn.execute(
            "DELETE FROM favorites WHERE id=?",
            (existing["id"],)
        )

        active = False

    else:
        conn.execute("""
        INSERT INTO favorites (user_id,food_id,restaurant_id)
        VALUES (?,?,?)
        """, (user_id, food_id, restaurant_id))

        active = True

    conn.commit()
    conn.close()

    return jsonify(success=True, active=active)


# =========================
# COUPONS
# =========================

@app.route("/api/coupon/validate", methods=["POST"])
def validate_coupon():
    data = request.get_json(silent=True) or {}

    code = str(data.get("code", "")).upper().strip()
    amount = float(data.get("amount", 0))

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
        discount=round(discount, 2),
        coupon=dict(coupon)
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

    payment_mode = str(
        data.get("payment_mode", "COD")
    ).upper()

    address = str(
        data.get("address", "")
    ).strip()

    instructions = str(
        data.get("instructions", "")
    ).strip()

    coupon_code = str(
        data.get("coupon_code", "")
    ).upper().strip()

    if not customer_id:
        return jsonify(
            success=False,
            message="Login required."
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

    customer = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (customer_id,)
    ).fetchone()

    if not customer or customer["blocked"]:
        conn.close()
        return jsonify(
            success=False,
            message="Customer account unavailable."
        ), 400

    item_total = 0
    clean_items = []

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

        if restaurant_id and int(food["restaurant_id"]) != int(restaurant_id):
            continue

        item_total += float(food["price"]) * qty

        clean_items.append((food, qty))

    if not clean_items:
        conn.close()

        return jsonify(
            success=False,
            message="No valid food items found."
        ), 400

    restaurant_id = clean_items[0][0]["restaurant_id"]

    delivery_fee = float(
        get_setting("delivery_fee", "25")
    )

    platform_fee = float(
        get_setting("platform_fee", "5")
    )

    discount = 0

    if coupon_code:
        coupon = conn.execute("""
        SELECT * FROM coupons
        WHERE code=? AND active=1
        """, (coupon_code,)).fetchone()

        if coupon and item_total >= coupon["min_order"]:
            if coupon["discount_type"] == "percent":
                discount = (
                    item_total *
                    coupon["discount_value"] / 100
                )
            else:
                discount = coupon["discount_value"]

            discount = min(discount, item_total)

    grand_total = (
        item_total +
        delivery_fee +
        platform_fee -
        discount
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
        status
    )
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
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
        "Order Placed"
    ))

    order_id = cur.lastrowid

    for food, qty in clean_items:
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

    # SAVE ADDRESS
    conn.execute("""
    UPDATE users
    SET address=?
    WHERE id=?
    """, (address, customer_id))

    conn.commit()
    conn.close()

    return jsonify(
        success=True,
        order_id=order_id,
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
    SELECT orders.*, restaurants.name AS restaurant_name
    FROM orders
    LEFT JOIN restaurants
    ON restaurants.id=orders.restaurant_id
    WHERE orders.customer_id=?
    ORDER BY orders.id DESC
    """, (customer_id,)).fetchall()

    result = []

    for order_row in rows:
        order_data = dict(order_row)

        items = conn.execute("""
        SELECT * FROM order_items
        WHERE order_id=?
        """, (order_data["id"],)).fetchall()

        order_data["items"] = rows_to_dict(items)

        result.append(order_data)

    conn.close()

    return jsonify(result)


@app.route("/api/order/<int:order_id>")
def get_order(order_id):
    conn = get_db()

    order_row = conn.execute("""
    SELECT orders.*,
           users.name AS customer_name,
           users.phone AS customer_phone,
           restaurants.name AS restaurant_name
    FROM orders
    LEFT JOIN users ON users.id=orders.customer_id
    LEFT JOIN restaurants ON restaurants.id=orders.restaurant_id
    WHERE orders.id=?
    """, (order_id,)).fetchone()

    if not order_row:
        conn.close()
        return jsonify(success=False), 404

    order_data = dict(order_row)

    items = conn.execute("""
    SELECT * FROM order_items
    WHERE order_id=?
    """, (order_id,)).fetchall()

    order_data["items"] = rows_to_dict(items)

    conn.close()

    return jsonify(success=True, order=order_data)


# =========================
# REORDER
# =========================

@app.route("/api/reorder/<int:order_id>")
def reorder(order_id):
    conn = get_db()

    rows = conn.execute("""
    SELECT order_items.*,
           foods.restaurant_id
    FROM order_items
    LEFT JOIN foods ON foods.id=order_items.food_id
    WHERE order_items.order_id=?
    """, (order_id,)).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


# =========================
# RESTAURANT PANEL
# =========================

@app.route("/api/restaurant/orders/<int:restaurant_id>")
def restaurant_orders(restaurant_id):
    conn = get_db()

    rows = conn.execute("""
    SELECT orders.*,
           users.name AS customer_name,
           users.phone AS customer_phone
    FROM orders
    LEFT JOIN users ON users.id=orders.customer_id
    WHERE orders.restaurant_id=?
    ORDER BY orders.id DESC
    """, (restaurant_id,)).fetchall()

    result = []

    for order_row in rows:
        order_data = dict(order_row)

        items = conn.execute("""
        SELECT * FROM order_items
        WHERE order_id=?
        """, (order_data["id"],)).fetchall()

        order_data["items"] = rows_to_dict(items)

        result.append(order_data)

    conn.close()

    return jsonify(result)


@app.route(
    "/api/restaurant/order/<int:order_id>/status",
    methods=["POST"]
)
def restaurant_order_status(order_id):
    data = request.get_json(silent=True) or {}

    status = data.get("status")

    allowed = [
        "Restaurant Accepted",
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

    conn.execute("""
    UPDATE orders
    SET status=?
    WHERE id=?
    """, (status, order_id))

    conn.commit()
    conn.close()

    return jsonify(success=True)


@app.route("/api/restaurant/<int:restaurant_id>/foods")
def restaurant_foods(restaurant_id):
    conn = get_db()

    rows = conn.execute("""
    SELECT * FROM foods
    WHERE restaurant_id=?
    ORDER BY id DESC
    """, (restaurant_id,)).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route("/api/restaurant/food", methods=["POST"])
def add_food():
    data = request.get_json(silent=True) or {}

    restaurant_id = data.get("restaurant_id")
    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    price = data.get("price", 0)
    food_type = data.get("type", "Veg")

    if not restaurant_id or not name or float(price) <= 0:
        return jsonify(
            success=False,
            message="Invalid food details."
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
        available
    )
    VALUES (?,?,?,?,?,1)
    """, (
        restaurant_id,
        name,
        description,
        price,
        food_type
    ))

    food_id = cur.lastrowid

    conn.commit()
    conn.close()

    return jsonify(success=True, food_id=food_id)


@app.route("/api/restaurant/food/<int:food_id>", methods=["PUT"])
def update_food(food_id):
    data = request.get_json(silent=True) or {}

    conn = get_db()

    conn.execute("""
    UPDATE foods
    SET name=?,
        description=?,
        price=?,
        type=?,
        available=?
    WHERE id=?
    """, (
        data.get("name"),
        data.get("description"),
        data.get("price"),
        data.get("type"),
        1 if data.get("available", True) else 0,
        food_id
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# =========================
# DELIVERY PARTNER
# =========================

@app.route("/api/delivery/available-orders")
def available_delivery_orders():
    conn = get_db()

    rows = conn.execute("""
    SELECT orders.*,
           restaurants.name AS restaurant_name,
           restaurants.address AS restaurant_address
    FROM orders
    LEFT JOIN restaurants
    ON restaurants.id=orders.restaurant_id
    WHERE orders.status IN
    ('Ready for Pickup','Picked Up')
    AND orders.delivery_partner_id IS NULL
    ORDER BY orders.id DESC
    """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route(
    "/api/delivery/order/<int:order_id>/accept",
    methods=["POST"]
)
def accept_delivery(order_id):
    data = request.get_json(silent=True) or {}

    delivery_partner_id = data.get("delivery_partner_id")

    if not delivery_partner_id:
        return jsonify(success=False), 400

    conn = get_db()

    conn.execute("""
    UPDATE orders
    SET delivery_partner_id=?,
        status='Delivery Assigned'
    WHERE id=?
    AND delivery_partner_id IS NULL
    """, (delivery_partner_id, order_id))

    conn.commit()
    conn.close()

    return jsonify(success=True)


@app.route(
    "/api/delivery/order/<int:order_id>/status",
    methods=["POST"]
)
def delivery_status(order_id):
    data = request.get_json(silent=True) or {}

    status = data.get("status")

    allowed = [
        "Picked Up",
        "On the Way",
        "Delivered"
    ]

    if status not in allowed:
        return jsonify(success=False), 400

    conn = get_db()

    conn.execute("""
    UPDATE orders
    SET status=?
    WHERE id=?
    """, (status, order_id))

    conn.commit()
    conn.close()

    return jsonify(success=True)


@app.route("/api/delivery/orders/<int:partner_id>")
def delivery_orders(partner_id):
    conn = get_db()

    rows = conn.execute("""
    SELECT orders.*,
           restaurants.name AS restaurant_name
    FROM orders
    LEFT JOIN restaurants
    ON restaurants.id=orders.restaurant_id
    WHERE orders.delivery_partner_id=?
    ORDER BY orders.id DESC
    """, (partner_id,)).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route("/api/delivery/earnings/<int:partner_id>")
def delivery_earnings(partner_id):
    conn = get_db()

    count = conn.execute("""
    SELECT COUNT(*) FROM orders
    WHERE delivery_partner_id=?
    AND status='Delivered'
    """, (partner_id,)).fetchone()[0]

    conn.close()

    # SIMPLE DEFAULT EARNING
    earning_per_delivery = 30

    return jsonify(
        deliveries=count,
        earning=count * earning_per_delivery
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/api/admin/dashboard")
def admin_dashboard():
    conn = get_db()

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
    WHERE status!='Rejected'
    """).fetchone()[0]

    customers = conn.execute("""
    SELECT COUNT(*) FROM users
    WHERE role='customer'
    """).fetchone()[0]

    restaurants = conn.execute(
        "SELECT COUNT(*) FROM restaurants"
    ).fetchone()[0]

    delivery_partners = conn.execute("""
    SELECT COUNT(*) FROM users
    WHERE role='delivery'
    """).fetchone()[0]

    conn.close()

    return jsonify({
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "revenue": revenue,
        "customers": customers,
        "restaurants": restaurants,
        "delivery_partners": delivery_partners
    })


@app.route("/api/admin/orders")
def admin_orders():
    conn = get_db()

    rows = conn.execute("""
    SELECT orders.*,
           users.name AS customer_name,
           users.phone AS customer_phone,
           restaurants.name AS restaurant_name,
           dp.name AS delivery_partner_name
    FROM orders
    LEFT JOIN users
    ON users.id=orders.customer_id
    LEFT JOIN restaurants
    ON restaurants.id=orders.restaurant_id
    LEFT JOIN users dp
    ON dp.id=orders.delivery_partner_id
    ORDER BY orders.id DESC
    """).fetchall()

    result = []

    for order_row in rows:
        order_data = dict(order_row)

        items = conn.execute("""
        SELECT * FROM order_items
        WHERE order_id=?
        """, (order_data["id"],)).fetchall()

        order_data["items"] = rows_to_dict(items)

        result.append(order_data)

    conn.close()

    return jsonify(result)


@app.route(
    "/api/admin/order/<int:order_id>/status",
    methods=["POST"]
)
def admin_order_status(order_id):
    data = request.get_json(silent=True) or {}

    status = data.get("status")

    allowed = [
        "Order Placed",
        "Restaurant Accepted",
        "Rejected",
        "Preparing",
        "Ready for Pickup",
        "Delivery Assigned",
        "Picked Up",
        "On the Way",
        "Delivered"
    ]

    if status not in allowed:
        return jsonify(
            success=False,
            message="Invalid status."
        ), 400

    conn = get_db()

    conn.execute("""
    UPDATE orders
    SET status=?
    WHERE id=?
    """, (status, order_id))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# =========================
# ADMIN USERS
# =========================

@app.route("/api/admin/users")
def admin_users():
    conn = get_db()

    rows = conn.execute("""
    SELECT * FROM users
    ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route(
    "/api/admin/user/<int:user_id>/block",
    methods=["POST"]
)
def block_user(user_id):
    data = request.get_json(silent=True) or {}

    blocked = 1 if data.get("blocked", True) else 0

    conn = get_db()

    conn.execute("""
    UPDATE users
    SET blocked=?
    WHERE id=?
    """, (blocked, user_id))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# =========================
# ADMIN RESTAURANTS
# =========================

@app.route("/api/admin/restaurants")
def admin_restaurants():
    conn = get_db()

    rows = conn.execute("""
    SELECT * FROM restaurants
    ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route(
    "/api/admin/restaurant/<int:restaurant_id>",
    methods=["PUT"]
)
def admin_update_restaurant(restaurant_id):
    data = request.get_json(silent=True) or {}

    conn = get_db()

    conn.execute("""
    UPDATE restaurants
    SET approved=?,
        active=?,
        commission=?
    WHERE id=?
    """, (
        1 if data.get("approved", True) else 0,
        1 if data.get("active", True) else 0,
        data.get(
            "commission",
            get_setting("commission", "10")
        ),
        restaurant_id
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# =========================
# ADMIN SETTINGS
# =========================

@app.route("/api/admin/settings")
def admin_get_settings():
    conn = get_db()

    rows = conn.execute(
        "SELECT * FROM settings"
    ).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route(
    "/api/admin/settings",
    methods=["POST"]
)
def admin_update_settings():
    data = request.get_json(silent=True) or {}

    conn = get_db()

    for key, value in data.items():
        conn.execute("""
        INSERT INTO settings
        (setting_key,setting_value)
        VALUES (?,?)
        ON CONFLICT(setting_key)
        DO UPDATE SET setting_value=excluded.setting_value
        """, (str(key), str(value)))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# =========================
# ADMIN COUPONS
# =========================

@app.route("/api/admin/coupons")
def admin_coupons():
    conn = get_db()

    rows = conn.execute(
        "SELECT * FROM coupons ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify(rows_to_dict(rows))


@app.route(
    "/api/admin/coupon",
    methods=["POST"]
)
def admin_add_coupon():
    data = request.get_json(silent=True) or {}

    code = str(
        data.get("code", "")
    ).upper().strip()

    if not code:
        return jsonify(success=False), 400

    conn = get_db()

    try:
        conn.execute("""
        INSERT INTO coupons
        (
            code,
            discount_type,
            discount_value,
            min_order,
            active
        )
        VALUES (?,?,?,?,?)
        """, (
            code,
            data.get("discount_type", "flat"),
            float(data.get("discount_value", 0)),
            float(data.get("min_order", 0)),
            1
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
# HEALTH CHECK
# =========================

@app.route("/api/health")
def health():
    return jsonify(
        success=True,
        app="SWIPTO",
        status="running"
    )


# =========================
# START APP
# =========================

if __name__ == "__main__":
    init_db()

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )

else:
    init_db()
