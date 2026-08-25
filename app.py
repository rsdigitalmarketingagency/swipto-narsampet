from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
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

    # USERS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            email TEXT DEFAULT '',
            photo TEXT DEFAULT '',
            role TEXT DEFAULT 'customer',
            blocked INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    # ADDRESSES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT,
            phone TEXT,
            address TEXT,
            landmark TEXT DEFAULT '',
            pincode TEXT DEFAULT '',
            is_default INTEGER DEFAULT 0
        )
    """)

    # RESTAURANTS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image TEXT DEFAULT '',
            banner TEXT DEFAULT '',
            rating REAL DEFAULT 4.0,
            category TEXT DEFAULT '',
            address TEXT DEFAULT 'Narsampet',
            phone TEXT DEFAULT '',
            owner_id INTEGER,
            approved INTEGER DEFAULT 1,
            active INTEGER DEFAULT 1
        )
    """)

    # FOOD ITEMS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            price REAL NOT NULL,
            category TEXT DEFAULT '',
            food_type TEXT DEFAULT 'Veg',
            available INTEGER DEFAULT 1,
            image TEXT DEFAULT '',
            rating REAL DEFAULT 4.0,
            offer TEXT DEFAULT ''
        )
    """)

    # ORDERS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            restaurant_id INTEGER,
            delivery_partner_id INTEGER,
            item_total REAL DEFAULT 0,
            delivery_fee REAL DEFAULT 25,
            platform_fee REAL DEFAULT 5,
            discount REAL DEFAULT 0,
            grand_total REAL DEFAULT 0,
            payment_mode TEXT DEFAULT 'COD',
            address TEXT DEFAULT '',
            instructions TEXT DEFAULT '',
            status TEXT DEFAULT 'Order Placed',
            created_at TEXT
        )
    """)

    # ORDER ITEMS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            food_id INTEGER,
            food_name TEXT,
            price REAL,
            quantity INTEGER
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

    # FAVOURITES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_id INTEGER,
            restaurant_id INTEGER
        )
    """)

    # REVIEWS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            restaurant_id INTEGER,
            food_id INTEGER,
            rating INTEGER,
            comment TEXT DEFAULT '',
            created_at TEXT
        )
    """)

    # DELIVERY PARTNERS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS delivery_partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            vehicle_number TEXT DEFAULT '',
            available INTEGER DEFAULT 1,
            earnings REAL DEFAULT 0
        )
    """)

    # NOTIFICATIONS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_id INTEGER,
            title TEXT,
            message TEXT,
            read_status INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    # SETTINGS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT
        )
    """)

    # DEFAULT SETTINGS
    default_settings = [
        ("delivery_fee", "25"),
        ("platform_fee", "5"),
        ("commission_percent", "10"),
        ("support_phone", "9705586797"),
        ("whatsapp_number", "9705586797")
    ]

    for key, value in default_settings:
        cur.execute("""
            INSERT OR IGNORE INTO settings
            (setting_key, setting_value)
            VALUES (?, ?)
        """, (key, value))

    # DEFAULT RESTAURANTS
    restaurant_count = cur.execute(
        "SELECT COUNT(*) FROM restaurants"
    ).fetchone()[0]

    if restaurant_count == 0:

        restaurants = [
            (
                "SWIPTO Biryani House",
                "https://images.unsplash.com/photo-1563379926898-05f4575a45d8",
                "",
                4.5,
                "Biryani",
                "Narsampet",
                "9705586797"
            ),
            (
                "Narsampet Food Hub",
                "https://images.unsplash.com/photo-1513104890138-7c749659a591",
                "",
                4.3,
                "Fast Food",
                "Narsampet",
                "9705586797"
            ),
            (
                "Andhra Spice",
                "https://images.unsplash.com/photo-1585937421612-70a008356fbe",
                "",
                4.6,
                "South Indian",
                "Narsampet",
                "9705586797"
            )
        ]

        for restaurant in restaurants:
            cur.execute("""
                INSERT INTO restaurants (
                    name,
                    image,
                    banner,
                    rating,
                    category,
                    address,
                    phone
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, restaurant)

        foods = [
            (
                1,
                "Chicken Biryani",
                "Hyderabadi style chicken biryani",
                130,
                "Biryani",
                "Non-Veg"
            ),
            (
                1,
                "Mutton Biryani",
                "Special mutton biryani",
                220,
                "Biryani",
                "Non-Veg"
            ),
            (
                1,
                "Veg Biryani",
                "Fresh vegetable biryani",
                100,
                "Biryani",
                "Veg"
            ),
            (
                1,
                "Chicken Fry",
                "Spicy chicken fry",
                180,
                "Starters",
                "Non-Veg"
            ),
            (
                2,
                "Chicken Burger",
                "Loaded chicken burger",
                120,
                "Burger",
                "Non-Veg"
            ),
            (
                2,
                "Veg Burger",
                "Fresh veg burger",
                90,
                "Burger",
                "Veg"
            ),
            (
                2,
                "French Fries",
                "Crispy french fries",
                70,
                "Snacks",
                "Veg"
            ),
            (
                2,
                "Chicken Pizza",
                "Cheesy chicken pizza",
                250,
                "Pizza",
                "Non-Veg"
            ),
            (
                3,
                "Andhra Meals",
                "Traditional Andhra meals",
                120,
                "Meals",
                "Veg"
            ),
            (
                3,
                "Chicken Curry",
                "Andhra spicy chicken curry",
                180,
                "Curry",
                "Non-Veg"
            ),
            (
                3,
                "Paneer Curry",
                "Fresh paneer curry",
                160,
                "Curry",
                "Veg"
            ),
            (
                3,
                "Egg Fried Rice",
                "Special egg fried rice",
                110,
                "Rice",
                "Non-Veg"
            )
        ]

        for food in foods:
            cur.execute("""
                INSERT INTO food_items (
                    restaurant_id,
                    name,
                    description,
                    price,
                    category,
                    food_type
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, food)

    # DEFAULT COUPON
    cur.execute("""
        INSERT OR IGNORE INTO coupons (
            code,
            discount_type,
            discount_value,
            min_order,
            active
        )
        VALUES ('SWIPTO50', 'flat', 50, 299, 1)
    """)

    conn.commit()
    conn.close()


# =========================================================
# HELPERS
# =========================================================

def get_setting(key, default_value):
    conn = get_db()

    row = conn.execute("""
        SELECT setting_value
        FROM settings
        WHERE setting_key = ?
    """, (key,)).fetchone()

    conn.close()

    if row:
        return row["setting_value"]

    return default_value


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
        SELECT *
        FROM restaurants
        WHERE approved = 1
        AND active = 1
        ORDER BY rating DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/restaurant/<int:restaurant_id>")
def get_restaurant(restaurant_id):

    conn = get_db()

    row = conn.execute("""
        SELECT *
        FROM restaurants
        WHERE id = ?
    """, (restaurant_id,)).fetchone()

    conn.close()

    if not row:
        return jsonify({
            "success": False,
            "message": "Restaurant not found"
        }), 404

    return jsonify(dict(row))


# =========================================================
# RESTAURANT MENU
# =========================================================

@app.route("/api/restaurant/<int:restaurant_id>/menu")
def get_menu(restaurant_id):

    food_type = request.args.get("type")

    conn = get_db()

    if food_type and food_type.lower() != "all":

        rows = conn.execute("""
            SELECT *
            FROM food_items
            WHERE restaurant_id = ?
            AND available = 1
            AND food_type = ?
            ORDER BY rating DESC
        """, (
            restaurant_id,
            food_type
        )).fetchall()

    else:

        rows = conn.execute("""
            SELECT *
            FROM food_items
            WHERE restaurant_id = ?
            AND available = 1
            ORDER BY rating DESC
        """, (
            restaurant_id,
        )).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# SEARCH
# =========================================================

@app.route("/api/search")
def search_food():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    conn = get_db()

    rows = conn.execute("""
        SELECT
            food_items.*,
            restaurants.name AS restaurant_name
        FROM food_items
        INNER JOIN restaurants
            ON food_items.restaurant_id = restaurants.id
        WHERE food_items.available = 1
        AND restaurants.active = 1
        AND restaurants.approved = 1
        AND (
            food_items.name LIKE ?
            OR food_items.category LIKE ?
            OR restaurants.name LIKE ?
        )
        ORDER BY food_items.rating DESC
    """, (
        f"%{query}%",
        f"%{query}%",
        f"%{query}%"
    )).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# REGISTER / LOGIN
# =========================================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip()
    photo = str(data.get("photo", "")).strip()
    role = str(data.get("role", "customer")).strip()

    if not name or not phone:
        return jsonify({
            "success": False,
            "message": "Name and phone number are required"
        }), 400

    conn = get_db()

    existing = conn.execute("""
        SELECT *
        FROM users
        WHERE phone = ?
    """, (phone,)).fetchone()

    if existing:

        if existing["blocked"]:
            conn.close()

            return jsonify({
                "success": False,
                "message": "This account is blocked"
            }), 403

        conn.close()

        return jsonify({
            "success": True,
            "user": dict(existing)
        })

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (
            name,
            phone,
            email,
            photo,
            role,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        email,
        photo,
        role,
        now()
    ))

    user_id = cur.lastrowid

    conn.commit()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE id = ?
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

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "User ID is required"
        }), 400

    conn = get_db()

    if data.get("is_default"):

        conn.execute("""
            UPDATE addresses
            SET is_default = 0
            WHERE user_id = ?
        """, (user_id,))

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO addresses (
            user_id,
            name,
            phone,
            address,
            landmark,
            pincode,
            is_default
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data.get("name", ""),
        data.get("phone", ""),
        data.get("address", ""),
        data.get("landmark", ""),
        data.get("pincode", ""),
        int(data.get("is_default", 0))
    ))

    address_id = cur.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "address_id": address_id
    })


# =========================================================
# GET USER ADDRESSES
# =========================================================

@app.route("/api/user/<int:user_id>/addresses")
def user_addresses(user_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM addresses
        WHERE user_id = ?
        ORDER BY is_default DESC, id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# CREATE ORDER
# =========================================================

@app.route("/api/order", methods=["POST"])
def create_order():

    data = request.get_json(silent=True) or {}

    customer_id = data.get("customer_id")
    restaurant_id = data.get("restaurant_id")
    items = data.get("items", [])
    address = data.get("address", "")
    instructions = data.get("instructions", "")
    payment_mode = data.get("payment_mode", "COD")
    discount = float(data.get("discount", 0) or 0)

    if not customer_id:
        return jsonify({
            "success": False,
            "message": "Please login first"
        }), 400

    if not restaurant_id:
        return jsonify({
            "success": False,
            "message": "Restaurant is required"
        }), 400

    if not items:
        return jsonify({
            "success": False,
            "message": "Cart is empty"
        }), 400

    conn = get_db()
    cur = conn.cursor()

    item_total = 0

    for item in items:

        price = float(item.get("price", 0))
        quantity = int(item.get("quantity", 1))

        if quantity < 1:
            quantity = 1

        item_total += price * quantity

    delivery_fee = float(
        get_setting("delivery_fee", "25")
    )

    platform_fee = float(
        get_setting("platform_fee", "5")
    )

    if discount < 0:
        discount = 0

    before_discount = (
        item_total +
        delivery_fee +
        platform_fee
    )

    if discount > before_discount:
        discount = before_discount

    grand_total = (
        before_discount -
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
        now()
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
            item.get("name", ""),
            float(item.get("price", 0)),
            int(item.get("quantity", 1))
        ))

    # Notification
    cur.execute("""
        INSERT INTO notifications (
            user_id,
            order_id,
            title,
            message,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        customer_id,
        order_id,
        "SWIPTO Order Confirmed",
        f"Your order #{order_id} has been placed successfully.",
        now()
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
        "discount": discount,
        "grand_total": grand_total,
        "payment_mode": payment_mode
    })


# =========================================================
# ORDER DETAILS
# =========================================================

@app.route("/api/order/<int:order_id>")
def order_details(order_id):

    conn = get_db()

    order = conn.execute("""
        SELECT
            orders.*,
            restaurants.name AS restaurant_name,
            restaurants.phone AS restaurant_phone,
            users.name AS customer_name,
            users.phone AS customer_phone
        FROM orders
        LEFT JOIN restaurants
            ON orders.restaurant_id = restaurants.id
        LEFT JOIN users
            ON orders.customer_id = users.id
        WHERE orders.id = ?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    items = conn.execute("""
        SELECT *
        FROM order_items
        WHERE order_id = ?
    """, (order_id,)).fetchall()

    conn.close()

    return jsonify({
        "success": True,
        "order": dict(order),
        "items": [dict(item) for item in items]
    })


# =========================================================
# ORDER STATUS
# =========================================================

@app.route("/api/order/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):

    data = request.get_json(silent=True) or {}

    status = str(
        data.get("status", "")
    ).strip()

    allowed_statuses = [
        "Order Placed",
        "Restaurant Accepted",
        "Preparing",
        "Ready for Pickup",
        "Picked Up",
        "On The Way",
        "Delivered",
        "Rejected",
        "Cancelled"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid order status"
        }), 400

    conn = get_db()

    conn.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ?
    """, (
        status,
        order_id
    ))

    order = conn.execute("""
        SELECT customer_id
        FROM orders
        WHERE id = ?
    """, (order_id,)).fetchone()

    if order and order["customer_id"]:

        conn.execute("""
            INSERT INTO notifications (
                user_id,
                order_id,
                title,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            order["customer_id"],
            order_id,
            "Order Update",
            f"Order #{order_id}: {status}",
            now()
        ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "order_id": order_id,
        "status": status
    })


# =========================================================
# USER ORDER HISTORY
# =========================================================

@app.route("/api/user/<int:user_id>/orders")
def user_orders(user_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
            restaurants.name AS restaurant_name,
            restaurants.image AS restaurant_image
        FROM orders
        LEFT JOIN restaurants
            ON orders.restaurant_id = restaurants.id
        WHERE orders.customer_id = ?
        ORDER BY orders.id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# COUPON
# =========================================================

@app.route("/api/coupon", methods=["POST"])
def apply_coupon():

    data = request.get_json(silent=True) or {}

    code = str(
        data.get("code", "")
    ).strip().upper()

    amount = float(
        data.get("amount", 0) or 0
    )

    conn = get_db()

    coupon = conn.execute("""
        SELECT *
        FROM coupons
        WHERE code = ?
        AND active = 1
    """, (code,)).fetchone()

    conn.close()

    if not coupon:
        return jsonify({
            "success": False,
            "message": "Invalid or inactive coupon"
        })

    if amount < coupon["min_order"]:

        return jsonify({
            "success": False,
            "message": (
                f"Minimum order ₹"
                f"{coupon['min_order']} required"
            )
        })

    if coupon["discount_type"] == "percent":

        discount = (
            amount *
            coupon["discount_value"] /
            100
        )

    else:

        discount = coupon["discount_value"]

    if discount > amount:
        discount = amount

    return jsonify({
        "success": True,
        "code": code,
        "discount": discount
    })


# =========================================================
# FAVOURITES
# =========================================================

@app.route("/api/favourite", methods=["POST"])
def add_favourite():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    food_id = data.get("food_id")
    restaurant_id = data.get("restaurant_id")

    conn = get_db()

    existing = conn.execute("""
        SELECT *
        FROM favourites
        WHERE user_id = ?
        AND COALESCE(food_id, 0) = COALESCE(?, 0)
        AND COALESCE(restaurant_id, 0) = COALESCE(?, 0)
    """, (
        user_id,
        food_id,
        restaurant_id
    )).fetchone()

    if existing:

        conn.execute("""
            DELETE FROM favourites
            WHERE id = ?
        """, (existing["id"],))

        action = "removed"

    else:

        conn.execute("""
            INSERT INTO favourites (
                user_id,
                food_id,
                restaurant_id
            )
            VALUES (?, ?, ?)
        """, (
            user_id,
            food_id,
            restaurant_id
        ))

        action = "added"

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "action": action
    })


# =========================================================
# FAVOURITE LIST
# =========================================================

@app.route("/api/user/<int:user_id>/favourites")
def get_favourites(user_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            favourites.*,
            food_items.name AS food_name,
            food_items.price AS food_price,
            restaurants.name AS restaurant_name
        FROM favourites
        LEFT JOIN food_items
            ON favourites.food_id = food_items.id
        LEFT JOIN restaurants
            ON favourites.restaurant_id = restaurants.id
        WHERE favourites.user_id = ?
        ORDER BY favourites.id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# REVIEWS
# =========================================================

@app.route("/api/review", methods=["POST"])
def add_review():

    data = request.get_json(silent=True) or {}

    rating = int(data.get("rating", 0))

    if rating < 1 or rating > 5:
        return jsonify({
            "success": False,
            "message": "Rating must be between 1 and 5"
        }), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO reviews (
            user_id,
            restaurant_id,
            food_id,
            rating,
            comment,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("user_id"),
        data.get("restaurant_id"),
        data.get("food_id"),
        rating,
        data.get("comment", ""),
        now()
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Review submitted"
    })


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/api/admin/dashboard")
def admin_dashboard():

    conn = get_db()

    total_orders = conn.execute("""
        SELECT COUNT(*)
        FROM orders
    """).fetchone()[0]

    delivered_orders = conn.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE status = 'Delivered'
    """).fetchone()[0]

    total_revenue = conn.execute("""
        SELECT COALESCE(
            SUM(grand_total), 0
        )
        FROM orders
        WHERE status = 'Delivered'
    """).fetchone()[0]

    total_customers = conn.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role = 'customer'
        AND blocked = 0
    """).fetchone()[0]

    total_restaurants = conn.execute("""
        SELECT COUNT(*)
        FROM restaurants
    """).fetchone()[0]

    total_delivery_partners = conn.execute("""
        SELECT COUNT(*)
        FROM delivery_partners
    """).fetchone()[0]

    pending_orders = conn.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE status NOT IN (
            'Delivered',
            'Rejected',
            'Cancelled'
        )
    """).fetchone()[0]

    conn.close()

    return jsonify({
        "success": True,
        "owner": "NIMMANABOINA RAJESH",
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "total_restaurants": total_restaurants,
        "total_delivery_partners": total_delivery_partners
    })


# =========================================================
# ADMIN ALL ORDERS
# =========================================================

@app.route("/api/admin/orders")
def admin_orders():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
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
# ADMIN CUSTOMERS
# =========================================================

@app.route("/api/admin/customers")
def admin_customers():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM users
        WHERE role = 'customer'
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# ADMIN BLOCK / UNBLOCK USER
# =========================================================

@app.route("/api/admin/user/<int:user_id>/block", methods=["PUT"])
def block_user(user_id):

    data = request.get_json(silent=True) or {}

    blocked = int(
        data.get("blocked", 1)
    )

    conn = get_db()

    conn.execute("""
        UPDATE users
        SET blocked = ?
        WHERE id = ?
    """, (
        blocked,
        user_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "blocked": blocked
    })


# =========================================================
# ADMIN RESTAURANTS
# =========================================================

@app.route("/api/admin/restaurants")
def admin_restaurants():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM restaurants
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# ADMIN RESTAURANT APPROVAL
# =========================================================

@app.route(
    "/api/admin/restaurant/<int:restaurant_id>/approval",
    methods=["PUT"]
)
def restaurant_approval(restaurant_id):

    data = request.get_json(silent=True) or {}

    approved = int(
        data.get("approved", 1)
    )

    conn = get_db()

    conn.execute("""
        UPDATE restaurants
        SET approved = ?
        WHERE id = ?
    """, (
        approved,
        restaurant_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "approved": approved
    })


# =========================================================
# RESTAURANT ADD FOOD
# =========================================================

@app.route("/api/restaurant/food", methods=["POST"])
def add_food():

    data = request.get_json(silent=True) or {}

    required = [
        "restaurant_id",
        "name",
        "price"
    ]

    for field in required:

        if data.get(field) in (
            None,
            ""
        ):
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

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
            image,
            rating,
            offer
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("restaurant_id"),
        data.get("name"),
        data.get("description", ""),
        float(data.get("price")),
        data.get("category", ""),
        data.get("food_type", "Veg"),
        1,
        data.get("image", ""),
        4.0,
        data.get("offer", "")
    ))

    food_id = cur.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "food_id": food_id
    })


# =========================================================
# RESTAURANT EDIT FOOD
# =========================================================

@app.route(
    "/api/restaurant/food/<int:food_id>",
    methods=["PUT"]
)
def edit_food(food_id):

    data = request.get_json(silent=True) or {}

    conn = get_db()

    existing = conn.execute("""
        SELECT *
        FROM food_items
        WHERE id = ?
    """, (food_id,)).fetchone()

    if not existing:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Food item not found"
        }), 404

    conn.execute("""
        UPDATE food_items
        SET
            name = ?,
            description = ?,
            price = ?,
            category = ?,
            food_type = ?,
            image = ?,
            offer = ?
        WHERE id = ?
    """, (
        data.get("name", existing["name"]),
        data.get(
            "description",
            existing["description"]
        ),
        float(
            data.get(
                "price",
                existing["price"]
            )
        ),
        data.get(
            "category",
            existing["category"]
        ),
        data.get(
            "food_type",
            existing["food_type"]
        ),
        data.get(
            "image",
            existing["image"]
        ),
        data.get(
            "offer",
            existing["offer"]
        ),
        food_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


# =========================================================
# FOOD AVAILABILITY ON / OFF
# =========================================================

@app.route(
    "/api/food/<int:food_id>/availability",
    methods=["PUT"]
)
def food_availability(food_id):

    data = request.get_json(silent=True) or {}

    available = int(
        data.get("available", 1)
    )

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

    return jsonify({
        "success": True,
        "available": available
    })


# =========================================================
# RESTAURANT INCOMING ORDERS
# =========================================================

@app.route(
    "/api/restaurant/<int:restaurant_id>/orders"
)
def restaurant_orders(restaurant_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
            users.name AS customer_name,
            users.phone AS customer_phone
        FROM orders
        LEFT JOIN users
            ON orders.customer_id = users.id
        WHERE orders.restaurant_id = ?
        ORDER BY orders.id DESC
    """, (
        restaurant_id,
    )).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# DELIVERY AVAILABLE ORDERS
# =========================================================

@app.route("/api/delivery/orders")
def delivery_available_orders():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            orders.*,
            restaurants.name AS restaurant_name,
            restaurants.address AS restaurant_address
        FROM orders
        LEFT JOIN restaurants
            ON orders.restaurant_id = restaurants.id
        WHERE orders.status = 'Ready for Pickup'
        AND orders.delivery_partner_id IS NULL
        ORDER BY orders.id ASC
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
def delivery_accept_order(
    partner_id,
    order_id
):

    conn = get_db()

    order = conn.execute("""
        SELECT *
        FROM orders
        WHERE id = ?
    """, (order_id,)).fetchone()

    if not order:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    conn.execute("""
        UPDATE orders
        SET
            delivery_partner_id = ?,
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
# DELIVERY EARNINGS
# =========================================================

@app.route(
    "/api/delivery/<int:partner_id>/earnings"
)
def delivery_earnings(partner_id):

    conn = get_db()

    orders = conn.execute("""
        SELECT *
        FROM orders
        WHERE delivery_partner_id = ?
        AND status = 'Delivered'
        ORDER BY id DESC
    """, (
        partner_id,
    )).fetchall()

    # Example delivery earning = delivery fee
    total = sum(
        float(order["delivery_fee"] or 0)
        for order in orders
    )

    conn.close()

    return jsonify({
        "success": True,
        "total_earnings": total,
        "deliveries": [dict(order) for order in orders]
    })


# =========================================================
# NOTIFICATIONS
# =========================================================

@app.route(
    "/api/user/<int:user_id>/notifications"
)
def notifications(user_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM notifications
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        user_id,
    )).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# =========================================================
# ADMIN SETTINGS
# =========================================================

@app.route(
    "/api/admin/settings"
)
def admin_settings():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM settings
        ORDER BY setting_key
    """).fetchall()

    conn.close()

    return jsonify({
        row["setting_key"]: row["setting_value"]
        for row in rows
    })


@app.route(
    "/api/admin/settings",
    methods=["PUT"]
)
def update_admin_settings():

    data = request.get_json(silent=True) or {}

    conn = get_db()

    for key, value in data.items():

        conn.execute("""
            INSERT INTO settings (
                setting_key,
                setting_value
            )
            VALUES (?, ?)

            ON CONFLICT(setting_key)
            DO UPDATE SET
                setting_value = excluded.setting_value
        """, (
            str(key),
            str(value)
        ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


# =========================================================
# APP START
# =========================================================

# IMPORTANT:
# Database initialize happens when Gunicorn imports this file.
# This is required for Render deployment.

init_db()


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
