from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3, json, os, uuid
from datetime import datetime

DB = os.getenv("SWIPTO_DB", "swipto.db")
app = FastAPI(title="Swipto Food Delivery API", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

FOODS = [
    {"id":1,"name":"Chicken Biryani","restaurant":"Spice Route","category":"Biryani","price":189,"rating":4.6,"time":"25-30 min","emoji":"🍗","image":"https://images.unsplash.com/photo-1563379091339-03246963d96c?auto=format&fit=crop&w=900&q=80"},
    {"id":2,"name":"Paneer Biryani","restaurant":"Spice Route","category":"Biryani","price":169,"rating":4.5,"time":"25-30 min","emoji":"🍚","image":"https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=900&q=80"},
    {"id":3,"name":"Chicken 65","restaurant":"Tandoori Hub","category":"Starters","price":159,"rating":4.7,"time":"20-25 min","emoji":"🍗","image":"https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=80"},
    {"id":4,"name":"Masala Dosa","restaurant":"South Bowl","category":"South Indian","price":89,"rating":4.8,"time":"15-20 min","emoji":"🥞","image":"https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=900&q=80"},
    {"id":5,"name":"Veg Fried Rice","restaurant":"Wok Street","category":"Chinese","price":129,"rating":4.4,"time":"20-25 min","emoji":"🍜","image":"https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=900&q=80"},
    {"id":6,"name":"Classic Burger","restaurant":"Burger Lab","category":"Burgers","price":149,"rating":4.5,"time":"20-25 min","emoji":"🍔","image":"https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80"},
    {"id":7,"name":"Chicken Shawarma","restaurant":"Arabian Bites","category":"Rolls","price":139,"rating":4.6,"time":"20-25 min","emoji":"🌯","image":"https://images.unsplash.com/photo-1529006557810-274b9b2fc783?auto=format&fit=crop&w=900&q=80"},
    {"id":8,"name":"Chocolate Cake","restaurant":"Sweet Truth","category":"Desserts","price":119,"rating":4.7,"time":"20-25 min","emoji":"🍰","image":"https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=80"},
]

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS orders(
        id TEXT PRIMARY KEY, customer TEXT, phone TEXT, address TEXT,
        items TEXT, total REAL, status TEXT, created_at TEXT)""")
    c.commit(); c.close()

init_db()

class OrderIn(BaseModel):
    customer: str
    phone: str
    address: str
    items: list
    total: float

@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/api/foods")
def foods(q: str = "", category: str = "All"):
    data = FOODS
    if category != "All":
        data = [x for x in data if x["category"] == category]
    if q:
        ql = q.lower()
        data = [x for x in data if ql in x["name"].lower() or ql in x["restaurant"].lower()]
    return data

@app.get("/api/categories")
def categories():
    return ["All","Biryani","Starters","South Indian","Chinese","Burgers","Rolls","Desserts"]

@app.get("/api/restaurants")
def restaurants():
    names = {}
    for f in FOODS:
        names.setdefault(f["restaurant"], {"name":f["restaurant"],"rating":f["rating"],"items":0,"time":f["time"],"image":f["image"]})
        names[f["restaurant"]]["items"] += 1
    return list(names.values())

@app.post("/api/orders")
def create_order(order: OrderIn):
    oid = "SWP-" + uuid.uuid4().hex[:8].upper()
    now = datetime.now().isoformat(timespec="seconds")
    c = db()
    c.execute("INSERT INTO orders VALUES(?,?,?,?,?,?,?,?)",
              (oid, order.customer, order.phone, order.address,
               json.dumps(order.items), order.total, "Confirmed", now))
    c.commit(); c.close()
    return {"id": oid, "status":"Confirmed", "message":"Order placed successfully"}

@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    c = db()
    row = c.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    c.close()
    if not row:
        raise HTTPException(404, "Order not found")
    return dict(row)

@app.get("/health")
def health():
    return {"status":"ok","service":"swipto"}
