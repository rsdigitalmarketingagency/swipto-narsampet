from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder="static")

DB_NAME = "swipto.db"


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT UNIQUE,
        email TEXT,
        photo TEXT,
        role TEXT DEFAULT 'customer',
        blocked INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        phone TEXT,
        address TEXT,
        landmark TEXT,
        pincode TEXT,
        is_default INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        image TEXT,
        banner TEXT,
        rating REAL DEFAULT 4.0,
        category TEXT,
        address TEXT,
        phone TEXT,
        owner_id INTEGER,
        approved INTEGER DEFAULT 1,
        active INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS food_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER,
        name TEXT,
        description TEXT,
        price REAL,
        category TEXT,
        food_type TEXT,
        available INTEGER DEFAULT 1,
        image TEXT,
        rating REAL DEFAULT 4.0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        restaurant_id INTEGER,
        delivery_partner_id INTEGER,
        item_total REAL,
        delivery_fee REAL,
        platform_fee REAL,
        discount REAL,
        grand_total REAL,
        payment_mode TEXT,
        address TEXT,
        instructions TEXT,
        status TEXT DEFAULT 'Order Placed',
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        food_id INTEGER,
        food_name TEXT,
        price REAL,
        quantity INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        discount_type TEXT,
        discount_value REAL,
        min_order REAL DEFAULT 0,
        active INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS favourites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        food_id INTEGER,
        restaurant_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        restaurant_id INTEGER,
        food_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS delivery_partners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        vehicle_number TEXT,
        available INTEGER DEFAULT 1,
        earnings REAL DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_key TEXT UNIQUE,
        setting_value TEXT
    )
    """)

    conn.commit()

    # DEFAULT SETTINGS
    settings = [
        ("delivery_fee", "25"),
        ("platform_fee", "5"),
        ("commission_percent", "10")
    ]

    for key, value in settings:
        cur.execute("""
        INSERT OR IGNORE INTO settings
        (setting_key, setting_value)
        VALUES (?, ?)
        """, (key, value))

    # SAMPLE DATA
    count = cur.execute(
        "SELECT COUNT(*) FROM restaurants"
    ).fetchone()[0]

    if count == 0:

        restaurants = [
            (
                "SWIPTO Biryani House",
                "https://images.unsplash.com/photo-1563379926898-05f4575a45d8",
                "",
                4.5,
                "Biryani",
                "Narsampet",
                "9705586797",
                None
            ),
            (
                "Narsampet Food Hub",
                "https://images.unsplash.com/photo-1513104890138-7c749659a591",
                "",
                4.3,
                "Fast Food",
                "Narsampet",
                "9705586797",
                None
            ),
            (
                "Andhra Spice",
                "https://images.unsplash.com/photo-1585937421612-70a008356fbe",
                "",
                4.6,
                "South Indian",
                "Narsampet",
                "9705586797",
                None
            )
        ]

        for r in restaurants:
            cur.execute("""
            INSERT INTO restaurants
            (name, image, banner, rating, category,
             address, phone, owner_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, r)

        foods = [
            (1, "Chicken Biryani", "Hyderabadi style chicken biryani", 130, "Biryani", "Non-Veg"),
            (1, "Mutton Biryani", "Special mutton biryani", 220, "Biryani", "Non-Veg"),
            (1, "Veg Biryani", "Fresh veg biryani", 100, "Biryani", "Veg"),
            (1, "Chicken Fry", "Spicy chicken fry", 180, "Starters", "Non-Veg"),

            (2, "Chicken Burger", "Loaded chicken burger", 120, "Burger", "Non-Veg"),
            (2, "Veg Burger", "Fresh veg burger", 90, "Burger", "Veg"),
            (2, "French Fries", "Crispy french fries", 70, "Snacks", "Veg"),
            (2, "Chicken Pizza", "Cheesy chicken pizza", 250, "Pizza", "Non-Veg"),

            (3, "Andhra Meals", "Traditional Andhra meals", 120, "Meals", "Veg"),
            (3, "Chicken Curry", "Andhra spicy chicken curry", 180, "Curry", "Non-Veg"),
            (3, "Paneer Curry", "Fresh paneer curry", 160, "Curry", "Veg"),
            (3, "Egg Fried Rice", "Special egg fried rice", 110, "Rice", "Non-Veg")
        ]

        for food in foods:
            cur.execute("""
            INSERT INTO food_items
            (restaurant_id, name, description, price,
             category, food_type)
            VALUES (?, ?, ?, ?, ?, ?)
            """, food)

        cur.execute("""
        INSERT OR IGNORE INTO coupons
        (code, discount_type, discount_value, min_order)
        VALUES ('SWIPTO50', 'flat', 50, 299)
        """)

    conn.commit()
    conn.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return send_from_directory("static", "index.html")


# =========================================================
# RESTAURANTS
# =========================================================

@app.route("/api/restaurants")
def get_restaurants():

    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM restaurants
        WHERE approved = 1 AND active = 1
        ORDER BY rating DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/restaurant/<int:restaurant_id>")
def get_restaurant(restaurant_id):

    conn = get_db()

    restaurant = conn.execute("""
        SELECT * FROM restaurants
        WHERE id = ?
    """, (restaurant_id,)).fetchone()

    conn.close()

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    return jsonify(dict(restaurant))


# =========================================================
# MENU
# =========================================================

@app.route("/api/restaurant/<int:restaurant_id>/menu")
def get_menu(restaurant_id):

    food_type = request.args.get("type")

    conn = get_db()

    if food_type:
        rows = conn.execute("""
            SELECT * FROM food_items
            WHERE restaurant_id = ?
            AND available = 1
            AND food_type = ?
        """, (restaurant_id, food_type)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM food_items
            WHERE restaurant_id = ?
            AND available = 1
        """, (restaurant_id,)).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# SEARCH
# =========================================================

@app.route("/api/search")
def search_food():

    query = request.args.get("q", "").strip()

    conn = get_db()

    rows = conn.execute("""
        SELECT food_items.*, restaurants.name AS restaurant_name
        FROM food_items
        JOIN restaurants
        ON food_items.restaurant_id = restaurants.id
        WHERE food_items.available = 1
        AND (
            food_items.name LIKE ?
            OR food_items.category LIKE ?
            OR restaurants.name LIKE ?
        )
    """, (
        f"%{query}%",
        f"%{query}%",
        f"%{query}%"
    )).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# USER REGISTER
# =========================================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email", "")
    role = data.get("role", "customer")

    if not name or not phone:
        return jsonify({
            "success": False,
            "message": "Name and phone required"
        }), 400

    conn = get_db()

    existing = conn.execute("""
        SELECT * FROM users
        WHERE phone = ?
    """, (phone,)).fetchone()

    if existing:
        conn.close()

        return jsonify({
            "success": True,
            "user": dict(existing)
        })

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users
        (name, phone, email, role, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        email,
        role,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    user_id = cur.lastrowid

    conn.commit()

    user = conn.execute("""
        SELECT * FROM users WHERE id = ?
    """, (user_id,)).fetchone()

    conn.close()

    return jsonify({
        "success": True,
        "user": dict(user)
    })


# =========================================================
# ADD ADDRESS
# =========================================================

@app.route("/api/address", methods=["POST"])
def add_address():

    data = request.get_json()

    conn = get_db()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO addresses
        (user_id, name, phone, address,
         landmark, pincode, is_default)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("user_id"),
        data.get("name"),
        data.get("phone"),
        data.get("address"),
        data.get("landmark", ""),
        data.get("pincode", ""),
        data.get("is_default", 0)
    ))

    conn.commit()

    address_id = cur.lastrowid

    conn.close()

    return jsonify({
        "success": True,
        "address_id": address_id
    })


# =========================================================
# USER ADDRESSES
# =========================================================

@app.route("/api/user/<int:user_id>/addresses")
def user_addresses(user_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM addresses
        WHERE user_id = ?
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# CREATE ORDER
# =========================================================

@app.route("/api/order", methods=["POST"])
def create_order():

    data = request.get_json()

    customer_id = data.get("customer_id")
    restaurant_id = data.get("restaurant_id")
    items = data.get("items", [])

    payment_mode = data.get("payment_mode", "COD")
    address = data.get("address")
    instructions = data.get("instructions", "")

    if not items:
        return jsonify({
            "success": False,
            "message": "Cart is empty"
        }), 400

    conn = get_db()
    cur = conn.cursor()

    item_total = 0

    for item in items:
        item_total += (
            float(item["price"]) *
            int(item["quantity"])
        )

    settings = conn.execute("""
        SELECT setting_key, setting_value
        FROM settings
    """).fetchall()

    setting_dict = {
        row["setting_key"]: row["setting_value"]
        for row in settings
    }

    delivery_fee = float(
        setting_dict.get("delivery_fee", 25)
    )

    platform_fee = float(
        setting_dict.get("platform_fee", 5)
    )

    discount = float(
        data.get("discount", 0)
    )

    grand_total = (
        item_total +
        delivery_fee +
        platform_fee -
        discount
    )

    cur.execute("""
        INSERT INTO orders (
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
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        "Order Placed",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    order_id = cur.lastrowid

    for item in items:

        cur.execute("""
            INSERT INTO order_items (
                order_id,
                food_id,
                food_name,
                price,
                quantity
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            order_id,
            item.get("id"),
            item.get("name"),
            item.get("price"),
            item.get("quantity")
        ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "order_id": order_id,
        "status": "Order Placed",
        "item_total": item_total,
        "delivery_fee": delivery_fee,
        "platform_fee": platform_fee,
        "grand_total": grand_total
    })


# =========================================================
# ORDER DETAILS
# =========================================================

@app.route("/api/order/<int:order_id>")
def order_details(order_id):

    conn = get_db()

    order = conn.execute("""
        SELECT orders.*,
               restaurants.name AS restaurant_name
        FROM orders
        LEFT JOIN restaurants
        ON orders.restaurant_id = restaurants.id
        WHERE orders.id = ?
    """, (order_id,)).fetchone()

    items = conn.execute("""
        SELECT * FROM order_items
        WHERE order_id = ?
    """, (order_id,)).fetchall()

    conn.close()

    if not order:
        return jsonify({
            "error": "Order not found"
        }), 404

    return jsonify({
        "order": dict(order),
        "items": [dict(item) for item in items]
    })


# =========================================================
# UPDATE ORDER STATUS
# =========================================================

@app.route(
    "/api/order/<int:order_id>/status",
    methods=["PUT"]
)
def update_order_status(order_id):

    data = request.get_json()

    status = data.get("status")

    allowed_statuses = [
        "Order Placed",
        "Restaurant Accepted",
        "Preparing",
        "Ready for Pickup",
        "Picked Up",
        "On The Way",
        "Delivered",
        "Rejected"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid status"
        }), 400

    conn = get_db()

    conn.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ?
    """, (status, order_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "status": status
    })


# =========================================================
# USER ORDER HISTORY
# =========================================================

@app.route("/api/user/<int:user_id>/orders")
def user_orders(user_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT orders.*,
               restaurants.name AS restaurant_name
        FROM orders
        LEFT JOIN restaurants
        ON orders.restaurant_id = restaurants.id
        WHERE customer_id = ?
        ORDER BY orders.id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# COUPON
# =========================================================

@app.route("/api/coupon", methods=["POST"])
def apply_coupon():

    data = request.get_json()

    code = data.get("code", "").upper()
    amount = float(data.get("amount", 0))

    conn = get_db()

    coupon = conn.execute("""
        SELECT * FROM coupons
        WHERE code = ?
        AND active = 1
    """, (code,)).fetchone()

    conn.close()

    if not coupon:
        return jsonify({
            "success": False,
            "message": "Invalid coupon"
        })

    if amount < coupon["min_order"]:

        return jsonify({
            "success": False,
            "message": f"Minimum order ₹{coupon['min_order']} required"
        })

    if coupon["discount_type"] == "flat":

        discount = coupon["discount_value"]

    else:

        discount = (
            amount *
            coupon["discount_value"] / 100
        )

    return jsonify({
        "success": True,
        "discount": discount,
        "code": code
    })


# =========================================================
# FAVOURITES
# =========================================================

@app.route("/api/favourite", methods=["POST"])
def add_favourite():

    data = request.get_json()

    conn = get_db()

    conn.execute("""
        INSERT INTO favourites
        (user_id, food_id, restaurant_id)
        VALUES (?, ?, ?)
    """, (
        data.get("user_id"),
        data.get("food_id"),
        data.get("restaurant_id")
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# =========================================================
# REVIEWS
# =========================================================

@app.route("/api/review", methods=["POST"])
def add_review():

    data = request.get_json()

    conn = get_db()

    conn.execute("""
        INSERT INTO reviews
        (user_id, restaurant_id, food_id,
         rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("user_id"),
        data.get("restaurant_id"),
        data.get("food_id"),
        data.get("rating"),
        data.get("comment"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/api/admin/dashboard")
def admin_dashboard():

    conn = get_db()

    total_orders = conn.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    total_revenue = conn.execute("""
        SELECT COALESCE(
            SUM(grand_total), 0
        ) FROM orders
        WHERE status = 'Delivered'
    """).fetchone()[0]

    total_customers = conn.execute("""
        SELECT COUNT(*) FROM users
        WHERE role = 'customer'
    """).fetchone()[0]

    total_restaurants = conn.execute("""
        SELECT COUNT(*) FROM restaurants
    """).fetchone()[0]

    total_partners = conn.execute("""
        SELECT COUNT(*) FROM delivery_partners
    """).fetchone()[0]

    conn.close()

    return jsonify({
        "owner": "NIMMANABOINA RAJESH",
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "total_restaurants": total_restaurants,
        "total_delivery_partners": total_partners
    })


# =========================================================
# ADMIN ALL ORDERS
# =========================================================

@app.route("/api/admin/orders")
def admin_orders():

    conn = get_db()

    rows = conn.execute("""
        SELECT orders.*,
               restaurants.name AS restaurant_name,
               users.name AS customer_name,
               users.phone AS customer_phone
        FROM orders
        LEFT JOIN restaurants
        ON orders.restaurant_id = restaurants.id
        LEFT JOIN users
        ON orders.customer_id = users.id
        ORDER BY orders.id DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# RESTAURANT OWNER ADD FOOD
# =========================================================

@app.route("/api/restaurant/food", methods=["POST"])
def add_food():

    data = request.get_json()

    conn = get_db()

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO food_items (
            restaurant_id,
            name,
            description,
            price,
            category,
            food_type,
            available,
            image
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("restaurant_id"),
        data.get("name"),
        data.get("description"),
        data.get("price"),
        data.get("category"),
        data.get("food_type"),
        1,
        data.get("image", "")
    ))

    conn.commit()

    food_id = cur.lastrowid

    conn.close()

    return jsonify({
        "success": True,
        "food_id": food_id
    })


# =========================================================
# FOOD AVAILABILITY ON / OFF
# =========================================================

@app.route(
    "/api/food/<int:food_id>/availability",
    methods=["PUT"]
)
def food_availability(food_id):

    data = request.get_json()

    available = data.get("available", 1)

    conn = get_db()

    conn.execute("""
        UPDATE food_items
        SET available = ?
        WHERE id = ?
    """, (
        available,
        food_id
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# =========================================================
# DELIVERY PARTNER AVAILABLE ORDERS
# =========================================================

@app.route("/api/delivery/orders")
def delivery_available_orders():

    conn = get_db()

    rows = conn.execute("""
        SELECT orders.*,
               restaurants.name AS restaurant_name
        FROM orders
        LEFT JOIN restaurants
        ON orders.restaurant_id = restaurants.id
        WHERE orders.status = 'Ready for Pickup'
        AND orders.delivery_partner_id IS NULL
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# DELIVERY ACCEPT ORDER
# =========================================================

@app.route(
    "/api/delivery/<int:partner_id>/accept/<int:order_id>",
    methods=["PUT"]
)
def delivery_accept_order(partner_id, order_id):

    conn = get_db()

    conn.execute("""
        UPDATE orders
        SET delivery_partner_id = ?,
            status = 'Picked Up'
        WHERE id = ?
    """, (
        partner_id,
        order_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Delivery accepted"
    })


# =========================================================
# START APP
# =========================================================

if __name__ == "__main__":

    init_db()

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
