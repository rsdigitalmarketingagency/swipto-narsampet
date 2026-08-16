import flet as ft
import urllib.parse

# Brand Configuration
APP_NAME = "SWIPTO"
PRIMARY_COLOR = "#FF5200"
ADMIN_WHATSAPP_NUMBER = "919705586797"

CATEGORIES_DATA = [
    {"name": "Biryani", "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=300"},
    {"name": "Tiffins", "img": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=300"},
    {"name": "Fast Food", "img": "https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=300"},
    {"name": "Dhaba Dishes", "img": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=300"},
    {"name": "Bakery & Cakes", "img": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300"},
    {"name": "Shawarma", "img": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=300"},
]

RESTAURANTS_DATA = [
    {
        "id": 1,
        "name": "Ruchulu Family Restaurant & Biryani Point",
        "cuisine": "Chicken Dum Biryani, Mandi, Chinese",
        "rating": "4.4 ★",
        "time": "20-25 mins",
        "offer": "FLAT ₹50 OFF",
        "area": "Clock Tower Center, Narsampet",
        "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600",
        "items": [
            {"name": "Single Chicken Biryani", "price": 130, "veg": False, "desc": "Telangana spicy dum biryani with gravy", "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=300"},
            {"name": "Special Chicken Dum Biryani", "price": 220, "veg": False, "desc": "Extra pieces with fragrant basmati & eggs", "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=300"},
            {"name": "Chicken Lollipop (5 Pcs)", "price": 180, "veg": False, "desc": "Crispy fried juicy chicken wings", "img": "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=300"},
            {"name": "Butter Chicken Curry", "price": 160, "veg": False, "desc": "Creamy tomato gravy with tender chicken", "img": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=300"},
            {"name": "Butter Naan", "price": 35, "veg": True, "desc": "Hot clay oven baked tandoori naan", "img": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=300"},
        ]
    },
    {
        "id": 2,
        "name": "Sri Balaji Tiffins & Veg Meals",
        "cuisine": "Ghee Dosa, Poori, Idli, Veg Meals",
        "rating": "4.6 ★",
        "time": "15-20 mins",
        "offer": "20% OFF on Morning Breakfast",
        "area": "Warangal Road, Narsampet",
        "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600",
        "items": [
            {"name": "Ghee Karam Masala Dosa", "price": 55, "veg": True, "desc": "Hot crispy roasted dosa with allam & coconut chutney", "img": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=300"},
            {"name": "Garma Garam Idli Vada Combo", "price": 50, "veg": True, "desc": "2 Soft Idlis + 1 Crispy Vada with Sambar", "img": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=300"},
            {"name": "Poori Curry (3 Pcs)", "price": 45, "veg": True, "desc": "Puffed pooris with Bombay potato curry", "img": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=300"},
            {"name": "Special South Indian Veg Meals", "price": 100, "veg": True, "desc": "Rice, Pappu, Sambar, Rasam, Curd, Sweet", "img": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?w=300"},
        ]
    },
    {
        "id": 3,
        "name": "Village Highway Family Dhaba",
        "cuisine": "Dhaba Curries, Rotis, Tandoori Starters",
        "rating": "4.3 ★",
        "time": "25-30 mins",
        "offer": "FREE Delivery Above ₹299",
        "area": "Nekkonda Road, Narsampet",
        "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600",
        "items": [
            {"name": "Mutton Rogan Josh", "price": 270, "veg": False, "desc": "Slow cooked tender mutton dhaba curry", "img": "https://images.unsplash.com/photo-1544025162-d76694265947?w=300"},
            {"name": "Telangana Kaju Chicken Curry", "price": 190, "veg": False, "desc": "Cashew loaded rich village style spicy curry", "img": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=300"},
            {"name": "Paneer Butter Masala Dhaba Special", "price": 150, "veg": True, "desc": "Fresh soft paneer in rich creamy gravy", "img": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=300"},
            {"name": "Tandoori Roti with Butter", "price": 20, "veg": True, "desc": "Whole wheat freshly roasted roti", "img": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=300"},
        ]
    },
    {
        "id": 4,
        "name": "Narsampet Fast Food & Shawarma Corner",
        "cuisine": "Fried Rice, Noodles, Shawarma, Manchurian",
        "rating": "4.2 ★",
        "time": "15-20 mins",
        "offer": "Buy 2 Get 1 Cold Drink Free",
        "area": "Bus Stand Complex, Narsampet",
        "image": "https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=600",
        "items": [
            {"name": "Special Chicken Fried Rice", "price": 110, "veg": False, "desc": "Street style wok tossed spicy chicken rice", "img": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=300"},
            {"name": "Double Egg Chicken Noodles", "price": 120, "veg": False, "desc": "Hot loaded street noodles with sauce", "img": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=300"},
            {"name": "Rumali Roti Chicken Shawarma", "price": 90, "veg": False, "desc": "Grilled chicken roll with mayonnaise & spices", "img": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=300"},
            {"name": "Crispy Veg Manchurian", "price": 80, "veg": True, "desc": "Golden fried veggie balls in spicy tangy sauce", "img": "https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=300"},
        ]
    },
    {
        "id": 5,
        "name": "SLN Iyengar Bakery & Sweet House",
        "cuisine": "Cakes, Puffs, Snacks, Sweets",
        "rating": "4.5 ★",
        "time": "10-15 mins",
        "offer": "Fresh Oven Baked",
        "area": "Pakala Road, Narsampet",
        "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600",
        "items": [
            {"name": "Egg Puff (2 Pcs)", "price": 40, "veg": False, "desc": "Crispy hot baked puff loaded with spiced egg", "img": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300"},
            {"name": "Paneer Puff", "price": 30, "veg": True, "desc": "Flaky puff with spicy paneer stuffing", "img": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300"},
            {"name": "Fresh Black Forest Pastry", "price": 60, "veg": True, "desc": "Layered chocolate sponge pastry with cherries", "img": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300"},
            {"name": "Hot Milk Bread & Butter Biscuits", "price": 50, "veg": True, "desc": "Daily fresh bakery items pack", "img": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300"},
        ]
    },
    {
        "id": 6,
        "name": "Bawarchi Grand Biryani & Grill",
        "cuisine": "Pot Biryani, Tandoori Chicken, Kebabs",
        "rating": "4.4 ★",
        "time": "20-30 mins",
        "offer": "Flat ₹60 OFF on Family Packs",
        "area": "Ashok Nagar Road, Narsampet",
        "image": "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=600",
        "items": [
            {"name": "Special Pot Clay Handi Biryani", "price": 250, "veg": False, "desc": "Slow cooked in traditional clay pot with ghee", "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=300"},
            {"name": "Full Tandoori Chicken", "price": 340, "veg": False, "desc": "Charcoal grilled juicy whole chicken with green chutney", "img": "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=300"},
            {"name": "Chicken Tikka Kebab (6 Pcs)", "price": 190, "veg": False, "desc": "Boneless chicken skewers marinated in tandoori masala", "img": "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=300"},
        ]
    }
]

def main(page: ft.Page):
    page.title = f"{APP_NAME} - Narsampet Food Delivery"
    page.bgcolor = "#F8F9FA"
    page.padding = 0

    cart = {}
    selected_restaurant = {"name": "Local Restaurant"}

    cart_badge = ft.Text("0 Items", weight=ft.FontWeight.BOLD, color="white", size=13)
    cart_total = ft.Text("₹0", weight=ft.FontWeight.BOLD, size=18, color="white")
    content_area = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)

    def show_alert(message):
        page.snack_bar = ft.SnackBar(ft.Text(message))
        page.snack_bar.open = True
        page.update()

    def update_cart():
        total_items = sum(item["count"] for item in cart.values())
        total_price = sum(item["count"] * item["price"] for item in cart.values())
        cart_badge.value = f"{total_items} Items Added"
        cart_total.value = f"₹{total_price}"
        bottom_bar.visible = total_items > 0
        page.update()

    def add_item(name, price, res_name):
        selected_restaurant["name"] = res_name
        if name in cart:
            cart[name]["count"] += 1
        else:
            cart[name] = {"price": price, "count": 1}
        update_cart()

    def show_checkout_screen(e):
        content_area.controls.clear()
        bottom_bar.visible = False

        item_total = sum(item["count"] * item["price"] for item in cart.values())
        delivery_fee = 25
        grand_total = item_total + delivery_fee

        cust_name = ft.TextField(label="Full Name", hint_text="Enter your name", height=50)
        cust_phone = ft.TextField(label="Mobile Number", hint_text="10-digit number", keyboard_type=ft.KeyboardType.PHONE, height=50)
        cust_address = ft.TextField(label="Delivery Address (Narsampet)", hint_text="House No, Landmark, Area", height=70, multiline=True)
        payment_mode = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="UPI", label="PhonePe / Google Pay / Paytm (UPI)"),
                ft.Radio(value="COD", label="Cash on Delivery (COD)")
            ]),
            value="UPI"
        )

        def place_final_order(ev):
            if not cust_name.value or not cust_phone.value or not cust_address.value:
                show_alert("⚠️ Please fill in all delivery details!")
                return

            items_summary = "\n".join([f"• {name} x {info['count']} = ₹{info['count'] * info['price']}" for name, info in cart.items()])
            whatsapp_msg = (
                f"🛵 *NEW SWIPTO ORDER - NARSAMPET*\n\n"
                f"🏪 *Restaurant:* {selected_restaurant['name']}\n"
                f"👤 *Customer:* {cust_name.value}\n"
                f"📞 *Phone:* {cust_phone.value}\n"
                f"📍 *Address:* {cust_address.value}\n\n"
                f"📦 *Ordered Items:*\n{items_summary}\n\n"
                f"💵 *Item Total:* ₹{item_total}\n"
                f"🛵 *Delivery Fee:* ₹{delivery_fee}\n"
                f"💰 *Grand Total:* ₹{grand_total}\n"
                f"💳 *Payment Mode:* {payment_mode.value}\n\n"
                f"⚡ *Delivering via SWIPTO Express*"
            )

            encoded_msg = urllib.parse.quote(whatsapp_msg)
            whatsapp_url = f"https://api.whatsapp.com/send?phone={ADMIN_WHATSAPP_NUMBER}&text={encoded_msg}"

            cart.clear()
            update_cart()

            # Clean Confirmation UI (No alignment attributes)
            content_area.controls.clear()
            content_area.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="#2E7D32", size=60),
                        ft.Text("Order Placed Successfully!", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Grand Total: ₹{grand_total} ({payment_mode.value})", size=15, color="#555555"),
                        ft.Text("Click below to send receipt to WhatsApp:", size=13, color="#777777"),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "📲 Open WhatsApp & Send Order →",
                            bgcolor="#25D366",
                            color="white",
                            height=50,
                            url=whatsapp_url
                        ),
                        ft.TextButton("← Back to Home", on_click=lambda _: show_home())
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=25
                )
            )
            page.update()

        checkout_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: show_home()),
                    ft.Text("Checkout & Payment", size=18, weight=ft.FontWeight.BOLD)
                ]),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Delivery Address", size=15, weight=ft.FontWeight.BOLD),
                        cust_name,
                        cust_phone,
                        cust_address,
                    ], spacing=10),
                    padding=12,
                    bgcolor="white",
                    border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Payment Method", size=15, weight=ft.FontWeight.BOLD),
                        payment_mode
                    ], spacing=6),
                    padding=12,
                    bgcolor="white",
                    border_radius=10
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Bill Summary", size=15, weight=ft.FontWeight.BOLD),
                        ft.Row([ft.Text("Item Total"), ft.Text(f"₹{item_total}")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("Delivery Partner Fee"), ft.Text(f"₹{delivery_fee}")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(),
                        ft.Row([ft.Text("To Pay", weight=ft.FontWeight.BOLD, size=16), ft.Text(f"₹{grand_total}", weight=ft.FontWeight.BOLD, size=16, color=PRIMARY_COLOR)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], spacing=6),
                    padding=12,
                    bgcolor="white",
                    border_radius=10
                ),
                ft.ElevatedButton(
                    f"Confirm Order (₹{grand_total}) →",
                    bgcolor=PRIMARY_COLOR,
                    color="white",
                    height=50,
                    width=400,
                    on_click=place_final_order
                )
            ], spacing=12),
            padding=14
        )
        content_area.controls.append(checkout_container)
        page.update()

    bottom_bar = ft.Container(
        content=ft.Row([
            ft.Column([cart_badge, cart_total], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
            ft.ElevatedButton("Proceed to Pay →", color=PRIMARY_COLOR, bgcolor="white", on_click=show_checkout_screen)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=PRIMARY_COLOR,
        padding=16,
        border_radius=16,
        margin=10,
        visible=False
    )

    def show_menu(res):
        content_area.controls.clear()

        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW, icon_color="white", bgcolor=PRIMARY_COLOR, on_click=lambda _: show_home()),
                    ft.Text(res["name"], size=16, weight=ft.FontWeight.BOLD)
                ]),
                ft.Image(src=res["image"], height=140, width=400, border_radius=10),
                ft.Container(
                    content=ft.Column([
                        ft.Text(res["name"], size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(res["cuisine"], size=12, color="#757575"),
                        ft.Row([
                            ft.Container(content=ft.Text(res["rating"], color="white", size=11, weight=ft.FontWeight.BOLD), bgcolor="#2E7D32", padding=4, border_radius=4),
                            ft.Text(f"• ⏱ {res['time']}", size=12, color="#616161"),
                            ft.Text(f"• 📍 {res['area']}", size=12, color="#616161")
                        ], spacing=6),
                    ], spacing=4),
                    bgcolor="white",
                    padding=12,
                    border_radius=10
                )
            ], spacing=10),
            padding=10
        )
        content_area.controls.append(header)
        content_area.controls.append(
            ft.Container(padding=12, content=ft.Text("Menu Items & Specials", size=16, weight=ft.FontWeight.BOLD))
        )

        for item in res["items"]:
            veg_tag = ft.Container(
                content=ft.Text("VEG" if item["veg"] else "NON-VEG", size=9, weight=ft.FontWeight.BOLD, color="#2E7D32" if item["veg"] else "#C62828"),
                bgcolor="#E8F5E9" if item["veg"] else "#FFEBEE",
                padding=3,
                border_radius=4
            )

            item_card = ft.Container(
                content=ft.Row([
                    ft.Column([
                        veg_tag,
                        ft.Text(item["name"], size=15, weight=ft.FontWeight.BOLD),
                        ft.Text(f"₹{item['price']}", size=14, weight=ft.FontWeight.W_600, color="#212121"),
                        ft.Text(item["desc"], size=11, color="#757575", max_lines=2, width=190),
                    ], expand=True, spacing=3),
                    ft.Column([
                        ft.Image(src=item["img"], width=90, height=80, border_radius=8),
                        ft.ElevatedButton("+ ADD", color=PRIMARY_COLOR, bgcolor="white", on_click=lambda e, n=item["name"], p=item["price"], r=res["name"]: add_item(n, p, r))
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=12,
                margin=6,
                bgcolor="white",
                border_radius=10
            )
            content_area.controls.append(item_card)
        page.update()

    def show_home():
        content_area.controls.clear()

        brand_logo = ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.ELECTRIC_BOLT, color="#FFD700", size=24),
                bgcolor="#D84315",
                padding=5,
                border_radius=8
            ),
            ft.Column([
                ft.Text(APP_NAME, size=20, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("FOOD EXPRESS", size=9, weight=ft.FontWeight.BOLD, color="#FFE0B2")
            ], spacing=0)
        ], spacing=8)

        top_bar = ft.Container(
            content=ft.Column([
                ft.Row([
                    brand_logo,
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOCAL_SHIPPING, size=14, color="white"),
                            ft.Text("20-30 MINS", size=10, color="white", weight=ft.FontWeight.BOLD)
                        ]),
                        bgcolor="#D84315",
                        padding=6,
                        border_radius=6
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text("📍 Delivering in: Narsampet Town (506132)", size=12, color="#FFF3E0"),
                ft.TextField(prefix_icon=ft.Icons.SEARCH, hint_text="Search for Biryani, Shawarma, Dosa...", bgcolor="white", border_radius=10, height=45, content_padding=10)
            ], spacing=10),
            padding=15,
            bgcolor=PRIMARY_COLOR
        )
        content_area.controls.append(top_bar)

        cat_items = []
        for cat in CATEGORIES_DATA:
            cat_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Image(src=cat["img"], width=60, height=60, border_radius=30),
                        ft.Text(cat["name"], size=11, weight=ft.FontWeight.W_600)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=4
                )
            )

        categories_section = ft.Container(
            content=ft.Column([
                ft.Text("What's on your mind?", size=15, weight=ft.FontWeight.BOLD),
                ft.Row(cat_items, scroll=ft.ScrollMode.AUTO)
            ], spacing=8),
            padding=12
        )
        content_area.controls.append(categories_section)

        content_area.controls.append(
            ft.Container(padding=12, content=ft.Text("All Top Restaurants in Narsampet", size=16, weight=ft.FontWeight.BOLD))
        )

        for r in RESTAURANTS_DATA:
            card = ft.Container(
                content=ft.Column([
                    ft.Stack([
                        ft.Image(src=r["image"], height=140, width=400, border_radius=10),
                        ft.Container(
                            content=ft.Text(f"🏷 {r['offer']}", color="white", size=11, weight=ft.FontWeight.BOLD),
                            bgcolor="#1E88E5",
                            padding=5,
                            border_radius=4,
                            margin=8
                        )
                    ]),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(r["name"], size=15, weight=ft.FontWeight.BOLD),
                                ft.Container(content=ft.Text(r["rating"], color="white", size=11, weight=ft.FontWeight.BOLD), bgcolor="#2E7D32", padding=4, border_radius=4)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(r["cuisine"], size=12, color="#757575"),
                            ft.Row([
                                ft.Text(f"⏱ {r['time']}", size=11, color="#424242", weight=ft.FontWeight.W_600),
                                ft.Text(f"• 📍 {r['area']}", size=11, color="#757575"),
                            ])
                        ], spacing=3),
                        padding=10
                    )
                ]),
                bgcolor="white",
                border_radius=10,
                margin=6,
                on_click=lambda e, res=r: show_menu(res)
            )
            content_area.controls.append(card)

        page.update()

    show_home()
    page.add(ft.Column([content_area, bottom_bar], expand=True, spacing=0))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
