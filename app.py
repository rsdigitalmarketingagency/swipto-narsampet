import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "swipto.db")

app = Flask(__name__, static_folder="static", static_url_path="/static")


# =====================================================
# DATABASE
# =====================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def dicts(rows):
    return [dict(x) for x in rows]


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        address TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS restaurants(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        rating REAL DEFAULT 4.0,
        image TEXT,
        address TEXT,
        phone TEXT UNIQUE,
        password TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS foods(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        type TEXT DEFAULT 'Veg',
        rating REAL DEFAULT 4.0,
        image TEXT,
        available INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS delivery_partners(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        vehicle_number TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        restaurant_id INTEGER,
        delivery_partner_id INTEGER,
        item_total REAL DEFAULT 0,
        delivery_fee REAL DEFAULT 25,
        platform_fee REAL DEFAULT 5,
        discount REAL DEFAULT 0,
        grand_total REAL DEFAULT 0,
        payment_mode TEXT DEFAULT 'COD',
        address TEXT,
        instructions TEXT,
        status TEXT DEFAULT 'Order Placed',
        restaurant_status TEXT DEFAULT 'Pending',
        delivery_status TEXT DEFAULT 'Not Assigned',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        food_id INTEGER,
        food_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS coupons(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        discount_type TEXT NOT NULL,
        discount_value REAL NOT NULL,
        minimum_order REAL DEFAULT 0,
        active INTEGER DEFAULT 1
    )
    """)

    count = cur.execute(
        "SELECT COUNT(*) FROM restaurants"
    ).fetchone()[0]

    if count == 0:

        restaurants = [
            (
                "Andhra Spice",
                "South Indian",
                4.6,
                "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=900&q=80",
                "Narsampet",
                "9000000001",
                "1234"
            ),
            (
                "SWIPTO Biryani House",
                "Biryani",
                4.5,
                "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=900&q=80",
                "Narsampet",
                "9000000002",
                "1234"
            ),
            (
                "Narsampet Food Hub",
                "Fast Food",
                4.3,
                "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80",
                "Narsampet",
                "9000000003",
                "1234"
            )
        ]

        cur.executemany("""
        INSERT INTO restaurants
        (name,category,rating,image,address,phone,password)
        VALUES (?,?,?,?,?,?,?)
        """, restaurants)

        foods = [
            (1, "Andhra Chicken Curry", "Spicy Andhra chicken curry", 180, "Non-Veg", 4.5),
            (1, "Paneer Curry", "Fresh paneer curry", 160, "Veg", 4.3),
            (1, "Veg Meals", "Rice curry and sides", 120, "Veg", 4.4),

            (2, "Chicken Biryani", "Hyderabadi chicken biryani", 130, "Non-Veg", 4.6),
            (2, "Mutton Biryani", "Special dum biryani", 220, "Non-Veg", 4.5),
            (2, "Veg Biryani", "Fresh vegetable biryani", 100, "Veg", 4.1),

            (3, "Chicken Fry", "Crispy spicy chicken", 180, "Non-Veg", 4.2),
            (3, "Veg Burger", "Loaded vegetable burger", 110, "Veg", 4.2),
            (3, "Cheese Pizza", "Cheesy pizza", 199, "Veg", 4.3)
        ]

        cur.executemany("""
        INSERT INTO foods
        (restaurant_id,name,description,price,type,rating)
        VALUES (?,?,?,?,?,?)
        """, foods)

    coupon_count = cur.execute(
        "SELECT COUNT(*) FROM coupons WHERE code='SWIPTO50'"
    ).fetchone()[0]

    if coupon_count == 0:
        cur.execute("""
        INSERT INTO coupons
        (code,discount_type,discount_value,minimum_order)
        VALUES ('SWIPTO50','percent',50,199)
        """)

    conn.commit()
    conn.close()


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# =====================================================
# CUSTOMER
# =====================================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = "".join(
        filter(str.isdigit, str(data.get("phone", "")))
    )

    if len(name) < 2:
        return jsonify(
            success=False,
            message="Enter valid name"
        ), 400

    if len(phone) != 10:
        return jsonify(
            success=False,
            message="Enter valid 10 digit mobile number"
        ), 400

    conn = get_db()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM customers WHERE phone=?",
        (phone,)
    ).fetchone()

    if user:
        cur.execute(
            "UPDATE customers SET name=? WHERE id=?",
            (name, user["id"])
        )
        customer_id = user["id"]

    else:
        cur.execute(
            "INSERT INTO customers(name,phone) VALUES (?,?)",
            (name, phone)
        )
        customer_id = cur.lastrowid

    conn.commit()

    user = conn.execute(
        "SELECT * FROM customers WHERE id=?",
        (customer_id,)
    ).fetchone()

    conn.close()

    return jsonify(
        success=True,
        user=dict(user)
    )


# =====================================================
# RESTAURANTS
# =====================================================

@app.route("/api/restaurants")
def restaurants():

    conn = get_db()

    rows = conn.execute("""
    SELECT * FROM restaurants
    WHERE active=1
    ORDER BY rating DESC
    """).fetchall()

    conn.close()

    return jsonify(dicts(rows))


@app.route("/api/restaurant/<int:restaurant_id>/menu")
def menu(restaurant_id):

    food_type = request.args.get("type")

    conn = get_db()

    if food_type in ["Veg", "Non-Veg"]:

        rows = conn.execute("""
        SELECT * FROM foods
        WHERE restaurant_id=?
        AND type=?
        AND available=1
        ORDER BY rating DESC
        """, (
            restaurant_id,
            food_type
        )).fetchall()

    else:

        rows = conn.execute("""
        SELECT * FROM foods
        WHERE restaurant_id=?
        AND available=1
        ORDER BY rating DESC
        """, (
            restaurant_id,
        )).fetchall()

    conn.close()

    return jsonify(dicts(rows))


@app.route("/api/popular")
def popular():

    conn = get_db()

    rows = conn.execute("""
    SELECT
        foods.*,
        restaurants.name AS restaurant_name
    FROM foods
    JOIN restaurants
        ON restaurants.id=foods.restaurant_id
    WHERE foods.available=1
    AND restaurants.active=1
    ORDER BY foods.rating DESC
    LIMIT 20
    """).fetchall()

    conn.close()

    return jsonify(dicts(rows))


@app.route("/api/search")
def search():

    q = request.args.get("q", "").strip()

    conn = get_db()

    if q:

        like = "%" + q + "%"

        rows = conn.execute("""
        SELECT
            foods.*,
            restaurants.name AS restaurant_name
        FROM foods
        JOIN restaurants
            ON restaurants.id=foods.restaurant_id
        WHERE foods.available=1
        AND restaurants.active=1
        AND (
            foods.name LIKE ?
            OR foods.description LIKE ?
            OR restaurants.name LIKE ?
            OR restaurants.category LIKE ?
        )
        ORDER BY foods.rating DESC
        """, (
            like,
            like,
            like,
            like
        )).fetchall()

    else:

        rows = conn.execute("""
        SELECT
            foods.*,
            restaurants.name AS restaurant_name
        FROM foods
        JOIN restaurants
            ON restaurants.id=foods.restaurant_id
        WHERE foods.available=1
        AND restaurants.active=1
        ORDER BY foods.rating DESC
        """).fetchall()

    conn.close()

    return jsonify(dicts(rows))


# =====================================================
# COUPON
# =====================================================

@app.route("/api/coupon/apply", methods=["POST"])
def apply_coupon():

    data = request.get_json(silent=True) or {}

    code = str(
        data.get("code", "")
    ).upper().strip()

    try:
        amount = float(data.get("amount", 0))
    except:
        amount = 0

    if not code or amount <= 0:
        return jsonify(
            success=False,
            message="Enter valid coupon and amount"
        ), 400

    conn = get_db()

    coupon = conn.execute("""
    SELECT * FROM coupons
    WHERE code=? AND active=1
    """, (
        code,
    )).fetchone()

    conn.close()

    if not coupon:
        return jsonify(
            success=False,
            message="Invalid coupon"
        ), 400

    if amount < coupon["minimum_order"]:
        return jsonify(
            success=False,
            message=f"Minimum order ₹{coupon['minimum_order']} required"
        ), 400

    if coupon["discount_type"] == "percent":
        discount = (
            amount *
            coupon["discount_value"] /
            100
        )
    else:
        discount = coupon["discount_value"]

    discount = min(discount, amount)

    return jsonify(
        success=True,
        code=coupon["code"],
        discount=round(discount, 2)
    )


# =====================================================
# PLACE ORDER
# =====================================================

@app.route("/api/order", methods=["POST"])
def place_order():

    data = request.get_json(silent=True) or {}

    customer_id = data.get("customer_id")
    restaurant_id = data.get("restaurant_id")
    items = data.get("items", [])

    address = str(
        data.get("address", "")
    ).strip()

    payment_mode = str(
        data.get("payment_mode", "COD")
    ).upper().strip()

    instructions = str(
        data.get("instructions", "")
    ).strip()

    if not customer_id or not restaurant_id:
        return jsonify(
            success=False,
            message="Login and restaurant required"
        ), 400

    if not items:
        return jsonify(
            success=False,
            message="Cart is empty"
        ), 400

    if len(address) < 5:
        return jsonify(
            success=False,
            message="Enter delivery address"
        ), 400

    if payment_mode not in ["COD", "UPI"]:
        payment_mode = "COD"

    conn = get_db()
    cur = conn.cursor()

    customer = conn.execute("""
    SELECT * FROM customers
    WHERE id=?
    """, (
        customer_id,
    )).fetchone()

    restaurant = conn.execute("""
    SELECT * FROM restaurants
    WHERE id=? AND active=1
    """, (
        restaurant_id,
    )).fetchone()

    if not customer:
        conn.close()
        return jsonify(
            success=False,
            message="Customer not found. Please login again."
        ), 400

    if not restaurant:
        conn.close()
        return jsonify(
            success=False,
            message="Restaurant not available"
        ), 400

    item_total = 0
    valid_items = []

    for item in items:

        try:
            food_id = int(item.get("id"))
            qty = max(
                1,
                int(item.get("quantity", 1))
            )
        except:
            continue

        food = conn.execute("""
        SELECT * FROM foods
        WHERE id=?
        AND restaurant_id=?
        AND available=1
        """, (
            food_id,
            restaurant_id
        )).fetchone()

        if not food:
            continue

        valid_items.append(
            (food, qty)
        )

        item_total += (
            float(food["price"]) * qty
        )

    if not valid_items:
        conn.close()

        return jsonify(
            success=False,
            message="No valid food items found"
        ), 400

    discount = 0

    coupon_code = str(
        data.get("coupon_code", "")
    ).upper().strip()

    if coupon_code:

        coupon = conn.execute("""
        SELECT * FROM coupons
        WHERE code=? AND active=1
        """, (
            coupon_code,
        )).fetchone()

        if coupon and item_total >= coupon["minimum_order"]:

            if coupon["discount_type"] == "percent":
                discount = (
                    item_total *
                    coupon["discount_value"] /
                    100
                )
            else:
                discount = coupon["discount_value"]

            discount = min(
                discount,
                item_total
            )

    delivery_fee = (
        0 if item_total >= 500
        else 25
    )

    platform_fee = 5

    grand_total = (
        item_total
        - discount
        + delivery_fee
        + platform_fee
    )

    cur.execute("""
    INSERT INTO orders(
        customer_id,
        restaurant_id,
        item_total,
        delivery_fee,
        platform_fee,
        discount,
        grand_total,
        payment_mode,
        address,
        instructions
    )
    VALUES (?,?,?,?,?,?,?,?,?,?)
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
        instructions
    ))

    order_id = cur.lastrowid

    for food, qty in valid_items:

        cur.execute("""
        INSERT INTO order_items(
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

    cur.execute("""
    UPDATE customers
    SET address=?
    WHERE id=?
    """, (
        address,
        customer_id
    ))

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


# =====================================================
# CUSTOMER ORDERS
# =====================================================

@app.route("/api/orders/<int:customer_id>")
def customer_orders(customer_id):

    conn = get_db()

    orders = conn.execute("""
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
    """, (
        customer_id,
    )).fetchall()

    result = []

    for order in orders:

        obj = dict(order)

        items = conn.execute("""
        SELECT * FROM order_items
        WHERE order_id=?
        """, (
            order["id"],
        )).fetchall()

        obj["items"] = dicts(items)

        result.append(obj)

    conn.close()

    return jsonify(result)


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
    """, (
        order_id,
    )).fetchone()

    if not order:
        conn.close()

        return jsonify(
            message="Order not found"
        ), 404

    items = conn.execute("""
    SELECT * FROM order_items
    WHERE order_id=?
    """, (
        order_id,
    )).fetchall()

    conn.close()

    text = f"SWIPTO ORDER #{order_id}\n"
    text += f"Customer: {order['customer_name']}\n"
    text += f"Restaurant: {order['restaurant_name']}\n\n"

    for item in items:
        text += (
            f"{item['food_name']} x "
            f"{item['quantity']}\n"
        )

    text += f"\nTotal: ₹{order['grand_total']}"
    text += f"\nAddress: {order['address']}"
    text += f"\nStatus: {order['status']}"

    return jsonify(
        message=text
    )


# =====================================================
# RESTAURANT LOGIN
# =====================================================

@app.route("/api/restaurant/login", methods=["POST"])
def restaurant_login():

    data = request.get_json(silent=True) or {}

    phone = str(
        data.get("phone", "")
    ).strip()

    password = str(
        data.get("password", "")
    ).strip()

    conn = get_db()

    restaurant = conn.execute("""
    SELECT * FROM restaurants
    WHERE phone=?
    AND password=?
    AND active=1
    """, (
        phone,
        password
    )).fetchone()

    conn.close()

    if not restaurant:
        return jsonify(
            success=False,
            message="Invalid restaurant login"
        ), 401

    return jsonify(
        success=True,
        restaurant=dict(restaurant)
    )


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
    """, (
        restaurant_id,
    )).fetchall()

    result = []

    for order in rows:

        obj = dict(order)

        items = conn.execute("""
        SELECT * FROM order_items
        WHERE order_id=?
        """, (
            order["id"],
        )).fetchall()

        obj["items"] = dicts(items)

        result.append(obj)

    conn.close()

    return jsonify(result)


@app.route("/api/restaurant/<int:restaurant_id>/foods")
def restaurant_foods(restaurant_id):

    conn = get_db()

    rows = conn.execute("""
    SELECT * FROM foods
    WHERE restaurant_id=?
    ORDER BY id DESC
    """, (
        restaurant_id,
    )).fetchall()

    conn.close()

    return jsonify(dicts(rows))


@app.route(
    "/api/restaurant/order/<int:order_id>/status",
    methods=["POST"]
)
def restaurant_order_status(order_id):

    data = request.get_json(silent=True) or {}

    status = str(
        data.get("status", "")
    ).strip()

    restaurant_id = data.get("restaurant_id")

    valid = [
        "Accepted",
        "Preparing",
        "Ready for Pickup",
        "Rejected"
    ]

    if status not in valid:
        return jsonify(
            message="Invalid status"
        ), 400

    conn = get_db()

    order = conn.execute("""
    SELECT * FROM orders
    WHERE id=?
    """, (
        order_id,
    )).fetchone()

    if not order:
        conn.close()
        return jsonify(
            message="Order not found"
        ), 404

    if restaurant_id and int(restaurant_id) != order["restaurant_id"]:
        conn.close()
        return jsonify(
            message="You cannot update this order"
        ), 403

    if status == "Accepted":
        order_status = "Accepted"

    elif status == "Preparing":
        order_status = "Preparing"

    elif status == "Ready for Pickup":
        order_status = "Ready for Pickup"

    else:
        order_status = "Cancelled"

    conn.execute("""
    UPDATE orders
    SET restaurant_status=?,
        status=?
    WHERE id=?
    """, (
        status,
        order_status,
        order_id
    ))

    conn.commit()
    conn.close()

    return jsonify(
        success=True
    )


@app.route(
    "/api/restaurant/food",
    methods=["POST"]
)
def restaurant_add_food():

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

    try:
        price = float(
            data.get("price", 0)
        )
    except:
        price = 0

    if not restaurant_id or not name or price <= 0:
        return jsonify(
            message="Invalid food details"
        ), 400

    if food_type not in ["Veg", "Non-Veg"]:
        food_type = "Veg"

    conn = get_db()

    restaurant = conn.execute("""
    SELECT id FROM restaurants
    WHERE id=? AND active=1
    """, (
        restaurant_id,
    )).fetchone()

    if not restaurant:
        conn.close()

        return jsonify(
            message="Restaurant not found"
        ), 404

    cur = conn.cursor()

    cur.execute("""
    INSERT INTO foods(
        restaurant_id,
        name,
        price,
        type,
        description
    )
    VALUES (?,?,?,?,?)
    """, (
        restaurant_id,
        name,
        price,
        food_type,
        description
    ))

    conn.commit()

    food_id = cur.lastrowid

    conn.close()

    return jsonify(
        success=True,
        food_id=food_id
    )


@app.route(
    "/api/restaurant/food/<int:food_id>",
    methods=["PUT"]
)
def restaurant_food_update(food_id):

    data = request.get_json(silent=True) or {}

    try:
        available = int(
            data.get("available", 1)
        )
    except:
        available = 1

    available = 1 if available else 0

    conn = get_db()

    food = conn.execute("""
    SELECT * FROM foods
    WHERE id=?
    """, (
        food_id,
    )).fetchone()

    if not food:
        conn.close()

        return jsonify(
            message="Food not found"
        ), 404

    conn.execute("""
    UPDATE foods
    SET available=?
    WHERE id=?
    """, (
        available,
        food_id
    ))

    conn.commit()
    conn.close()

    return jsonify(
        success=True
    )


# =====================================================
# DELIVERY PARTNER
# =====================================================

@app.route("/api/delivery/register", methods=["POST"])
def delivery_register():

    data = request.get_json(silent=True) or {}

    name = str(
        data.get("name", "")
    ).strip()

    phone = "".join(
        filter(
            str.isdigit,
            str(data.get("phone", ""))
        )
    )

    password = str(
        data.get("password", "")
    ).strip()

    vehicle = str(
        data.get("vehicle_number", "")
    ).strip()

    if len(name) < 2:
        return jsonify(
            message="Enter valid name"
        ), 400

    if len(phone) != 10:
        return jsonify(
            message="Enter valid 10 digit mobile number"
        ), 400

    if len(password) < 4:
        return jsonify(
            message="Password must contain at least 4 characters"
        ), 400

    conn = get_db()
    cur = conn.cursor()

    try:

        cur.execute("""
        INSERT INTO delivery_partners(
            name,
            phone,
            password,
            vehicle_number
        )
        VALUES (?,?,?,?)
        """, (
            name,
            phone,
            password,
            vehicle
        ))

        partner_id = cur.lastrowid

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify(
            message="Mobile already registered"
        ), 400

    partner = conn.execute("""
    SELECT * FROM delivery_partners
    WHERE id=?
    """, (
        partner_id,
    )).fetchone()

    conn.close()

    return jsonify(
        success=True,
        partner=dict(partner)
    )


@app.route("/api/delivery/login", methods=["POST"])
def delivery_login():

    data = request.get_json(silent=True) or {}

    phone = str(
        data.get("phone", "")
    ).strip()

    password = str(
        data.get("password", "")
    ).strip()

    conn = get_db()

    partner = conn.execute("""
    SELECT * FROM delivery_partners
    WHERE phone=?
    AND password=?
    AND active=1
    """, (
        phone,
        password
    )).fetchone()

    conn.close()

    if not partner:
        return jsonify(
            message="Invalid delivery login"
        ), 401

    return jsonify(
        success=True,
        partner=dict(partner)
    )


@app.route("/api/delivery/orders")
def available_delivery_orders():

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
    WHERE orders.delivery_partner_id IS NULL
    AND orders.restaurant_status='Ready for Pickup'
    AND orders.status!='Cancelled'
    ORDER BY orders.id DESC
    """).fetchall()

    conn.close()

    return jsonify(dicts(rows))


@app.route(
    "/api/delivery/order/<int:order_id>/accept",
    methods=["POST"]
)
def accept_delivery(order_id):

    data = request.get_json(silent=True) or {}

    partner_id = data.get("partner_id")

    if not partner_id:
        return jsonify(
            message="Delivery partner required"
        ), 400

    conn = get_db()

    partner = conn.execute("""
    SELECT id FROM delivery_partners
    WHERE id=? AND active=1
    """, (
        partner_id,
    )).fetchone()

    if not partner:
        conn.close()

        return jsonify(
            message="Delivery partner not found"
        ), 404

    cur = conn.cursor()

    cur.execute("""
    UPDATE orders
    SET
        delivery_partner_id=?,
        delivery_status='Assigned',
        status='Out for Delivery'
    WHERE id=?
    AND delivery_partner_id IS NULL
    AND restaurant_status='Ready for Pickup'
    """, (
        partner_id,
        order_id
    ))

    updated = cur.rowcount

    conn.commit()
    conn.close()

    if updated == 0:
        return jsonify(
            message="Order is no longer available"
        ), 400

    return jsonify(
        success=True
    )


@app.route(
    "/api/delivery/order/<int:order_id>/status",
    methods=["POST"]
)
def update_delivery_status(order_id):

    data = request.get_json(silent=True) or {}

    partner_id = data.get("partner_id")

    status = str(
        data.get("status", "")
    ).strip()

    valid = [
        "Picked Up",
        "On the Way",
        "Delivered"
    ]

    if not partner_id:
        return jsonify(
            message="Delivery partner required"
        ), 400

    if status not in valid:
        return jsonify(
            message="Invalid status"
        ), 400

    if status == "Delivered":
        main_status = "Delivered"
    else:
        main_status = "Out for Delivery"

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    UPDATE orders
    SET
        delivery_status=?,
        status=?
    WHERE id=?
    AND delivery_partner_id=?
    """, (
        status,
        main_status,
        order_id,
        partner_id
    ))

    updated = cur.rowcount

    conn.commit()
    conn.close()

    if updated == 0:
        return jsonify(
            message="Order not found or not assigned to you"
        ), 404

    return jsonify(
        success=True
    )


@app.route("/api/delivery/<int:partner_id>/history")
def delivery_history(partner_id):

    conn = get_db()

    rows = conn.execute("""
    SELECT
        orders.*,
        restaurants.name AS restaurant_name
    FROM orders
    LEFT JOIN restaurants
        ON restaurants.id=orders.restaurant_id
    WHERE orders.delivery_partner_id=?
    ORDER BY orders.id DESC
    """, (
        partner_id,
    )).fetchall()

    earnings = conn.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE delivery_partner_id=?
    AND delivery_status='Delivered'
    """, (
        partner_id,
    )).fetchone()[0] * 30

    conn.close()

    return jsonify(
        orders=dicts(rows),
        earnings=earnings
    )


# =====================================================
# ADMIN
# =====================================================

@app.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json(silent=True) or {}

    username = str(
        data.get("username", "")
    )

    password = str(
        data.get("password", "")
    )

    admin_user = os.environ.get(
        "ADMIN_USER",
        "admin"
    )

    admin_pass = os.environ.get(
        "ADMIN_PASSWORD",
        "swipto123"
    )

    if (
        username != admin_user
        or password != admin_pass
    ):
        return jsonify(
            message="Invalid admin login"
        ), 401

    return jsonify(
        success=True
    )


@app.route("/api/admin/dashboard")
def admin_dashboard():

    conn = get_db()

    customers = conn.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    restaurants = conn.execute(
        "SELECT COUNT(*) FROM restaurants WHERE active=1"
    ).fetchone()[0]

    delivery_partners = conn.execute(
        "SELECT COUNT(*) FROM delivery_partners WHERE active=1"
    ).fetchone()[0]

    total_orders = conn.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    revenue = conn.execute("""
    SELECT COALESCE(SUM(grand_total),0)
    FROM orders
    WHERE status!='Cancelled'
    """).fetchone()[0]

    conn.close()

    return jsonify(
        customers=customers,
        restaurants=restaurants,
        delivery_partners=delivery_partners,
        total_orders=total_orders,
        revenue=round(revenue, 2)
    )


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

    return jsonify(dicts(rows))


@app.route("/api/admin/coupons", methods=["POST"])
def admin_add_coupon():

    data = request.get_json(silent=True) or {}

    code = str(
        data.get("code", "")
    ).upper().strip()

    discount_type = str(
        data.get("discount_type", "flat")
    ).strip()

    try:
        value = float(
            data.get("discount_value", 0)
        )

        minimum = float(
            data.get("minimum_order", 0)
        )

    except:
        return jsonify(
            message="Invalid values"
        ), 400

    if discount_type not in ["flat", "percent"]:
        return jsonify(
            message="Invalid discount type"
        ), 400

    if not code or value <= 0:
        return jsonify(
            message="Enter valid coupon"
        ), 400

    if minimum < 0:
        minimum = 0

    conn = get_db()

    try:

        conn.execute("""
        INSERT INTO coupons(
            code,
            discount_type,
            discount_value,
            minimum_order
        )
        VALUES (?,?,?,?)
        """, (
            code,
            discount_type,
            value,
            minimum
        ))

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify(
            message="Coupon already exists"
        ), 400

    conn.close()

    return jsonify(
        success=True
    )


# =====================================================
# APP INFO
# =====================================================

@app.route("/api/app-info")
def app_info():

    return jsonify({
        "app_name": "SWIPTO",
        "city": "Narsampet",
        "founder": "NIMMANABOINA RAJESH"
    })


# =====================================================
# RUN APP
# =====================================================

init_db()

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
