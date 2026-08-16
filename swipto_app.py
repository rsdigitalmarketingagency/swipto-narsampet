import os
import random
import flet as ft

# ==================== BRAND THEME & COLORS ====================
APP_NAME = "Swipto"
APP_OWNER = "Nimmanaboina Rajesh"
APP_LOCATION = "Narsampet, Warangal"
SWIGGY_ORANGE = "#FC8019"
SWIGGY_HEADER_BLUE = "#0047BA"
SWIGGY_DARK = "#282C3F"
SWIGGY_GRAY = "#686B78"
SWIGGY_LIGHT_GRAY = "#F0F0F5"
SWIGGY_GREEN = "#1BA672"
SWIGGY_OFFER_GREEN_BG = "#E5F7EE"
BG_COLOR = "#F4F5F8"

# ==================== RESTAURANTS & FOOD DATA ====================
CATEGORIES_DATA = [
    {"name": "Specials", "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=300&q=80"},
    {"name": "Biryani", "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=300&q=80"},
    {"name": "Cakes", "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300&q=80"},
    {"name": "Fried rice", "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=300&q=80"},
    {"name": "Pizzas", "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=300&q=80"},
    {"name": "Tiffins", "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=300&q=80"},
    {"name": "Burgers", "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&q=80"}
]

FAST_DELIVERY_DATA = [
    {
        "id": "fd1",
        "name": "Paradise Biryani",
        "cuisine": "Biryani",
        "rating": "4.5",
        "time": "20-25 mins",
        "offer": "70% OFF",
        "offer_sub": "UPTO ₹130 | AD",
        "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&q=80"
    },
    {
        "id": "fd2",
        "name": "Pizza Hut",
        "cuisine": "Pizzas",
        "rating": "4.1",
        "time": "25-30 mins",
        "offer": "50% OFF",
        "offer_sub": "USE SWIPTO50",
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&q=80"
    },
    {
        "id": "fd3",
        "name": "Domino's Pizza",
        "cuisine": "Pizzas",
        "rating": "4.2",
        "time": "25-30 mins",
        "offer": "ITEMS AT ₹49",
        "offer_sub": "AD",
        "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&q=80"
    }
]

STORE_99_DATA = [
    {"name": "Chicken Dum Biryani", "price": 98, "original": 219, "rating": "3.5 (2.7K+)", "hotel": "Green Park Biryani", "veg": False, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&q=80"},
    {"name": "Onion Samosa (4 pcs)", "price": 23, "original": 45, "rating": "4.0 (778)", "hotel": "Balaji Sweets", "veg": True, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80"},
    {"name": "Chicken Burger", "price": 89, "original": 99, "rating": "4.1 (13)", "hotel": "The Continental Cafe", "veg": False, "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80"}
]

RESTAURANTS_DATA = [
    {
        "id": "res_pizzahut",
        "name": "Pizza Hut",
        "tag": "Best in Pizza",
        "rating": "4.1",
        "rating_count": "7.4K+",
        "area": "Narsampet Town",
        "distance": "2.6 km",
        "time": "25-30 MINS",
        "offer": "50% off",
        "cuisine": "Pizzas • ₹350 for two",
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&q=80",
        "menu": [
            {
                "id": "p1",
                "name": "3in1 Triple Spice Pizza Veg Per.",
                "sub": "American Nashville Pizza, Mexican Mango Habanero, Korean Red Chilli",
                "price": 279,
                "original": 558,
                "veg": True,
                "category": "Pizzas",
                "customizable": True,
                "flavours_1": ["American Nashville Pizza", "Mexican Mango Habanero Pizza", "Korean Red Chilli Pizza"],
                "flavours_2": ["American Nashville Pizza", "Mexican Mango Habanero Pizza", "Korean Red Chilli Pizza"]
            },
            {
                "id": "p2",
                "name": "Margherita Classic Pizza",
                "sub": "Classic cheesy pizza loaded with fresh mozzarella & herb tomato sauce",
                "price": 199,
                "original": 299,
                "veg": True,
                "category": "Pizzas",
                "customizable": False
            }
        ]
    },
    {
        "id": "res_khursheed",
        "name": "Khursheed Biryani Hotel",
        "tag": "Best in Biryani",
        "rating": "4.3",
        "rating_count": "81K+",
        "area": "Main Road, Narsampet",
        "distance": "2.1 km",
        "time": "10-15 MINS",
        "offer": "Items at ₹89",
        "cuisine": "Biryani, Chinese • ₹300 for two",
        "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&q=80",
        "menu": [
            {
                "id": "b1",
                "name": "Hyderabadi Special Chicken Biryani",
                "sub": "Authentic long-grain basmati biryani with spiced slow-cooked chicken",
                "price": 220,
                "original": 280,
                "veg": False,
                "category": "Biryani",
                "customizable": False
            },
            {
                "id": "b2",
                "name": "Chicken 65 Starter",
                "sub": "Crisp fried spicy chicken tossed with curry leaves and green chillies",
                "price": 180,
                "original": 220,
                "veg": False,
                "category": "Biryani",
                "customizable": False
            }
        ]
    }
]

# ==================== MAIN APPLICATION ====================
def main(page: ft.Page):
    page.title = f"{APP_NAME} - {APP_LOCATION}"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = BG_COLOR

    cart = {}
    past_orders = []
    auth_state = {"logged_in": False, "phone": "", "otp": ""}
    selected_filter = {"category": None, "search": ""}

    def get_cart_total():
        return sum(item["price"] * item["qty"] for item in cart.values())

    def get_cart_original_total():
        return sum(item["original"] * item["qty"] for item in cart.values())

    def get_cart_count():
        return sum(item["qty"] for item in cart.values())

    def show_alert(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg, color="white"), bgcolor=SWIGGY_DARK)
        page.snack_bar.open = True
        page.update()

    # ----------------- OWNER PROFILE MODAL -----------------
    def show_owner_profile():
        bs = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS, color="white", size=28),
                            bgcolor=SWIGGY_ORANGE,
                            width=52, height=52,
                            border_radius=26,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(APP_OWNER, size=18, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                            ft.Text(f"Founder & App Owner • {APP_NAME}", size=12, color=SWIGGY_ORANGE, weight=ft.FontWeight.BOLD)
                        ], spacing=2)
                    ], spacing=12),
                    ft.Divider(),
                    ft.Row([ft.Icon(ft.icons.LOCATION_CITY, size=18, color=SWIGGY_GRAY), ft.Text(f"Location: {APP_LOCATION}", size=13, color=SWIGGY_DARK)]),
                    ft.Row([ft.Icon(ft.icons.VERIFIED, size=18, color=SWIGGY_GREEN), ft.Text("Official Swipto Operations Network", size=13, color=SWIGGY_DARK)]),
                    ft.Row([ft.Icon(ft.icons.PHONE_ANDROID, size=18, color=SWIGGY_GRAY), ft.Text(f"Account: {auth_state['phone'] if auth_state['logged_in'] else 'Guest User'}", size=13, color=SWIGGY_DARK)]),
                    ft.ElevatedButton("Close", bgcolor=SWIGGY_DARK, color="white", on_click=lambda e: close_owner_profile(bs))
                ], spacing=12),
                padding=24,
                bgcolor="white",
                border_radius=ft.border_radius.only(top_left=20, top_right=20)
            ),
            dismissible=True
        )
        page.overlay.append(bs)
        bs.open = True
        page.update()

    def close_owner_profile(bs):
        bs.open = False
        page.update()

    # ----------------- 1. SCREEN: LOGIN -----------------
    def show_login_screen():
        page.clean()

        phone_input = ft.TextField(
            keyboard_type=ft.KeyboardType.PHONE,
            border_color="transparent",
            focused_border_color="transparent",
            hint_text="Enter Mobile Number",
            text_size=15,
            expand=True,
            dense=True,
            content_padding=0
        )

        otp_input = ft.TextField(
            label="Enter 4-Digit OTP",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=SWIGGY_ORANGE,
            focused_border_color=SWIGGY_ORANGE,
            width=320,
            visible=False,
            text_size=16
        )

        demo_otp_box = ft.Container(visible=False, bgcolor="#FFF3E0", padding=8, border_radius=8, width=320)
        demo_otp_text = ft.Text(size=12, color=SWIGGY_ORANGE, weight=ft.FontWeight.BOLD)
        demo_otp_box.content = demo_otp_text

        login_btn = ft.ElevatedButton(
            "Continue",
            bgcolor="#E2E2E7",
            color="#93959F",
            width=320,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )

        def check_input(e):
            if len(phone_input.value.strip()) == 10:
                login_btn.bgcolor = SWIGGY_ORANGE
                login_btn.color = "white"
            else:
                login_btn.bgcolor = "#E2E2E7"
                login_btn.color = "#93959F"
            page.update()

        phone_input.on_change = check_input

        def handle_auth(e):
            if not otp_input.visible:
                phone = phone_input.value.strip()
                if len(phone) != 10 or not phone.isdigit():
                    show_alert("Please enter a valid 10-digit mobile number")
                    return
                otp = str(random.randint(1000, 9999))
                auth_state["phone"] = phone
                auth_state["otp"] = otp
                otp_input.visible = True
                demo_otp_box.visible = True
                demo_otp_text.value = f"Demo OTP: {otp}"
                login_btn.text = "Verify & Proceed"
                login_btn.bgcolor = SWIGGY_ORANGE
                login_btn.color = "white"
                page.update()
            else:
                if otp_input.value.strip() == auth_state["otp"]:
                    auth_state["logged_in"] = True
                    show_home_screen()
                else:
                    show_alert("Invalid OTP code!")

        login_btn.on_click = handle_auth

        top_orange_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text("Skip", color="white", weight=ft.FontWeight.BOLD, size=13),
                        bgcolor="#40000000",
                        padding=ft.Padding(14, 6, 14, 6),
                        border_radius=20,
                        on_click=lambda e: show_home_screen()
                    )
                ]),
                ft.Container(
                    content=ft.Column([
                        ft.Column([
                            ft.Text("swipto", color="white", size=42, weight=ft.FontWeight.BOLD),
                            ft.Text("‿‿‿‿", color="white", size=20, weight=ft.FontWeight.BOLD)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        ft.Text("One app for food, grocery, dining &\nmore in minutes!", color="white", size=15, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.Padding(0, 10, 0, 24)
                )
            ]),
            bgcolor=SWIGGY_ORANGE,
            padding=16
        )

        bottom_white_section = ft.Container(
            content=ft.Column([
                ft.Text("Enter your number", size=20, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Mobile Number", size=11, color=SWIGGY_ORANGE, weight=ft.FontWeight.W_500),
                        ft.Row([
                            ft.Text("🇮🇳 +91", size=15, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                            ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN, size=16, color=SWIGGY_DARK),
                            ft.VerticalDivider(width=1, thickness=1, color="#DCDCE0"),
                            phone_input
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=6)
                    ], spacing=2),
                    border=ft.border.all(1.5, SWIGGY_ORANGE),
                    border_radius=12,
                    padding=ft.Padding(14, 8, 14, 8),
                    width=320
                ),
                otp_input,
                demo_otp_box,
                login_btn,
                ft.Text("By clicking, I accept the Privacy policy,\nSwipto terms of use and Instamart terms of use", size=11, color=SWIGGY_GRAY, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            bgcolor="white",
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            padding=24,
            expand=True
        )

        page.add(ft.Column([top_orange_section, bottom_white_section], expand=True, spacing=0))

    # ----------------- 2. SCREEN: HOME -----------------
    def show_home_screen():
        page.clean()

        blue_header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.icons.LOCATION_ON, color="white", size=22),
                        ft.Column([
                            ft.Row([
                                ft.Text("Narsampet Town", size=16, weight=ft.FontWeight.BOLD, color="white"),
                                ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN, size=16, color="white")
                            ], spacing=2),
                            ft.Text("Warangal, Telangana...", size=11, color="#D0E2FF")
                        ], spacing=0)
                    ]),
                    ft.Container(
                        content=ft.Icon(ft.icons.MENU, color="white", size=20),
                        bgcolor="#1E5BCA",
                        padding=8,
                        border_radius=20,
                        on_click=lambda e: show_owner_profile()
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.LUNCH_DINING, color="white", size=24),
                            ft.Text("Food", color="white", size=12, weight=ft.FontWeight.BOLD)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                        bgcolor="#1E5BCA", padding=ft.Padding(24, 6, 24, 6), border_radius=12
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Container(content=ft.Text("6 mins", color="white", size=9, weight=ft.FontWeight.BOLD), bgcolor="#0080FF", padding=2, border_radius=4),
                            ft.Text("Instamart", color="#B8D5FF", size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                        padding=ft.Padding(16, 6, 16, 6)
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.ROOM_SERVICE, color="#B8D5FF", size=20),
                            ft.Text("Dineout", color="#B8D5FF", size=12)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                        padding=ft.Padding(16, 6, 16, 6)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
            ], spacing=12),
            bgcolor=SWIGGY_HEADER_BLUE,
            padding=14
        )

        search_field = ft.TextField(
            hint_text="Search for 'Pizza', 'Biryani' or 'Cake'...",
            prefix_icon=ft.icons.SEARCH,
            suffix_icon=ft.icons.MIC,
            bgcolor="white",
            border_radius=12,
            border_color="transparent",
            value=selected_filter["search"],
            on_submit=lambda e: filter_by_search(e.control.value),
            height=46,
            text_size=13
        )

        def filter_by_search(q):
            selected_filter["search"] = q
            show_home_screen()

        train_banner = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("Right To Your Train", color="white", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("At 200+ Stations", color="#D0E2FF", size=11),
                    ft.Container(
                        content=ft.Text("Enter PNR >", color="white", size=11, weight=ft.FontWeight.BOLD),
                        bgcolor=SWIGGY_ORANGE,
                        padding=ft.Padding(10, 4, 10, 4),
                        border_radius=12
                    )
                ], spacing=4),
                ft.Image(src="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=200&q=80", width=90, height=60, border_radius=8)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#1E5BCA",
            border_radius=12,
            padding=12,
            margin=ft.Padding(14, 0, 14, 0)
        )

        bolt_banner = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Text("Bolt⚡", color="white", size=15, weight=ft.FontWeight.BOLD),
                        ft.Text("Food In 15 Mins!", color="white", size=13)
                    ]),
                    ft.Text("Fresh, hot & crisp delights for you.", color="#FFD8B3", size=11),
                    ft.Container(
                        content=ft.Text("ORDER NOW", color="white", size=11, weight=ft.FontWeight.BOLD),
                        bgcolor=SWIGGY_ORANGE,
                        padding=ft.Padding(10, 4, 10, 4),
                        border_radius=8
                    )
                ], spacing=4),
                ft.Image(src="https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=200&q=80", width=80, height=60, border_radius=8)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#7A111E",
            border_radius=12,
            padding=12,
            margin=ft.Padding(14, 0, 14, 0)
        )

        fast_deliv_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=12)
        for fd in FAST_DELIVERY_DATA:
            fast_deliv_row.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Stack([
                            ft.Image(src=fd["image"], width=130, height=130, fit=ft.ImageFit.COVER, border_radius=14),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(fd["offer"], color="white", size=11, weight=ft.FontWeight.BOLD),
                                    ft.Text(fd["offer_sub"], color="white", size=8)
                                ], spacing=0),
                                bgcolor="#CC000000",
                                padding=4,
                                border_radius=ft.border_radius.only(bottom_left=14, bottom_right=14),
                                bottom=0, left=0, right=0
                            ),
                            ft.Icon(ft.icons.FAVORITE_BORDER, color="white", size=16, top=6, right=6)
                        ]),
                        ft.Text(fd["name"], size=13, weight=ft.FontWeight.BOLD, max_lines=1),
                        ft.Row([
                            ft.Icon(ft.icons.STAR, color="green", size=12),
                            ft.Text(f"{fd['rating']} • {fd['time']}", size=11, color=SWIGGY_GRAY)
                        ], spacing=2),
                        ft.Text(fd["cuisine"], size=10, color=SWIGGY_GRAY)
                    ], spacing=2),
                    width=130,
                    ink=True,
                    on_click=lambda e: show_menu_screen(RESTAURANTS_DATA[0])
                )
            )

        store_99_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=12)
        for s in STORE_99_DATA:
            store_99_row.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Stack([
                            ft.Image(src=s["image"], width=120, height=110, fit=ft.ImageFit.COVER, border_radius=12),
                            ft.Container(
                                content=ft.Icon(ft.icons.ADD, color=SWIGGY_GREEN, size=18),
                                bgcolor="white",
                                width=26, height=26,
                                border_radius=6,
                                alignment=ft.alignment.center,
                                bottom=6, right=6,
                                on_click=lambda e, it=s: direct_add_to_cart(it)
                            )
                        ]),
                        ft.Row([
                            ft.Icon(ft.icons.RADIO_BUTTON_CHECKED if s["veg"] else ft.icons.STOP_CIRCLE_ROUNDED, color="green" if s["veg"] else "red", size=12),
                            ft.Text(s["name"], size=12, weight=ft.FontWeight.BOLD, max_lines=1, expand=True)
                        ], spacing=4),
                        ft.Row([
                            ft.Text(f"₹{s['original']}", size=11, color=SWIGGY_GRAY, style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)),
                            ft.Container(content=ft.Text(f"₹{s['price']}", size=11, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK), bgcolor="#FFEB3B", padding=2, border_radius=4)
                        ], spacing=4),
                        ft.Text(f"★ {s['rating']}", size=10, color="green"),
                        ft.Text(s["hotel"], size=10, color=SWIGGY_GRAY, max_lines=1)
                    ], spacing=2),
                    width=120
                )
            )

        def direct_add_to_cart(item):
            cart[item["name"]] = {"name": item["name"], "price": item["price"], "original": item["original"], "qty": 1, "veg": item["veg"], "details": item["hotel"]}
            show_alert(f"{item['name']} added to Cart!")
            show_home_screen()

        cats_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=14)
        for cat in CATEGORIES_DATA:
            is_active = selected_filter["category"] == cat["name"]
            cats_row.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Image(src=cat["image"], width=58, height=58, fit=ft.ImageFit.COVER, border_radius=29),
                            border=ft.border.all(2, SWIGGY_ORANGE if is_active else "transparent"),
                            border_radius=32,
                            padding=2
                        ),
                        ft.Text(cat["name"], size=11, weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500, color=SWIGGY_ORANGE if is_active else SWIGGY_DARK)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    ink=True,
                    on_click=lambda e, c=cat["name"]: select_category(c)
                )
            )

        def select_category(cat_name):
            selected_filter["category"] = None if selected_filter["category"] == cat_name else cat_name
            show_home_screen()

        res_vertical_col = ft.Column(spacing=14)
        for r in RESTAURANTS_DATA:
            if selected_filter["category"] and selected_filter["category"].lower() not in r["cuisine"].lower() and not any(selected_filter["category"].lower() in m["category"].lower() for m in r["menu"]):
                continue
            if selected_filter["search"] and selected_filter["search"].lower() not in r["name"].lower() and selected_filter["search"].lower() not in r["cuisine"].lower() and not any(selected_filter["search"].lower() in m["name"].lower() for m in r["menu"]):
                continue

            res_vertical_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Stack([
                            ft.Image(src=r["image"], width=float("inf"), height=160, fit=ft.ImageFit.COVER, border_radius=16),
                            ft.Container(
                                content=ft.Text(r["offer"], color="white", size=12, weight=ft.FontWeight.BOLD),
                                bgcolor="#E0000000",
                                padding=ft.Padding(10, 4, 10, 4),
                                border_radius=ft.border_radius.only(top_left=16, bottom_right=12),
                                top=0, left=0
                            ),
                            ft.Container(
                                content=ft.Text(r["time"], color="white", size=10, weight=ft.FontWeight.BOLD),
                                bgcolor="#CC000000",
                                padding=ft.Padding(8, 4, 8, 4),
                                border_radius=6,
                                bottom=8, right=8
                            )
                        ]),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"👑 {r['tag']}", size=11, color="#D97706", weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Row([
                                    ft.Text(r["name"], size=17, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                                    ft.Icon(ft.icons.MORE_VERT, size=18, color=SWIGGY_GRAY)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([
                                    ft.Icon(ft.icons.STAR, color="green", size=14),
                                    ft.Text(f"{r['rating']} ({r['rating_count']}) • {r['area']}, {r['distance']}", size=12, color=SWIGGY_GRAY, weight=ft.FontWeight.W_500)
                                ], spacing=4),
                                ft.Text(r["cuisine"], size=12, color=SWIGGY_GRAY)
                            ], spacing=3),
                            padding=8
                        )
                    ]),
                    bgcolor="white",
                    border_radius=16,
                    padding=6,
                    ink=True,
                    on_click=lambda e, res=r: show_menu_screen(res),
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=6, color=ft.colors.BLACK12)
                )
            )

        bottom_nav = ft.Container(
            content=ft.Row([
                ft.Column([ft.Icon(ft.icons.FASTFOOD, color=SWIGGY_ORANGE, size=20), ft.Text("Food", size=10, color=SWIGGY_ORANGE, weight=ft.FontWeight.BOLD)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                ft.Column([ft.Icon(ft.icons.ELECTRIC_BOLT, color=SWIGGY_GRAY, size=20), ft.Text("Bolt 15m", size=10, color=SWIGGY_GRAY)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                ft.Column([ft.Icon(ft.icons.LOCAL_OFFER, color=SWIGGY_GRAY, size=20), ft.Text("99 store", size=10, color=SWIGGY_GRAY)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                ft.Column([ft.Icon(ft.icons.FAVORITE, color=SWIGGY_GRAY, size=20), ft.Text("EatRight", size=10, color=SWIGGY_GRAY)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                ft.Column([ft.Icon(ft.icons.PERSON, color=SWIGGY_GRAY, size=20), ft.Text("Profile", size=10, color=SWIGGY_GRAY)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor="white",
            padding=ft.Padding(0, 8, 0, 8),
            border=ft.border.only(top=ft.BorderSide(1, "#E2E2E7"))
        )

        floating_cart = ft.Container(
            content=ft.Row([
                ft.Text(f"{get_cart_count()} ITEMS  |  ₹{get_cart_total()}", color="white", weight=ft.FontWeight.BOLD),
                ft.Text("VIEW CART >", color="white", weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=SWIGGY_ORANGE,
            padding=14,
            border_radius=12,
            margin=10,
            on_click=lambda e: show_cart_screen(),
            visible=get_cart_count() > 0
        )

        scroll_view = ft.ListView([
            blue_header,
            ft.Container(content=search_field, padding=ft.Padding(14, 8, 14, 8), bgcolor=SWIGGY_HEADER_BLUE),
            ft.Container(height=8),
            train_banner,
            ft.Container(height=8),
            bolt_banner,
            ft.Container(
                content=ft.Column([
                    ft.Text("Fast delivery", size=15, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                    fast_deliv_row
                ], spacing=10),
                padding=14
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.icons.STOREFRONT, color=SWIGGY_ORANGE, size=20),
                            ft.Text("99 store", size=16, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK)
                        ]),
                        ft.Text("View All >", color=SWIGGY_ORANGE, size=12, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text("✔ Meals at ₹99 + Free Delivery", size=11, color="#D97706"),
                    store_99_row
                ], spacing=8),
                padding=14,
                bgcolor="white",
                margin=ft.Padding(0, 8, 0, 8)
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("What's on your mind?", size=15, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                    cats_row
                ], spacing=10),
                padding=14
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Explore Top Restaurants", size=15, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                    res_vertical_col
                ], spacing=12),
                padding=ft.Padding(14, 0, 14, 90)
            )
        ], expand=True)

        page.add(ft.Column([ft.Stack([scroll_view, ft.Container(content=floating_cart, bottom=0, left=0, right=0)], expand=True), bottom_nav], expand=True, spacing=0))

    # ----------------- 3. SCREEN: MENU -----------------
    def show_menu_screen(res):
        page.clean()

        def open_customizer_modal(item):
            sel_f1 = ft.RadioGroup(content=ft.Column([ft.Radio(value=f, label=f) for f in item["flavours_1"]]), value=item["flavours_1"][0])
            sel_f2 = ft.RadioGroup(content=ft.Column([ft.Radio(value=f, label=f) for f in item["flavours_2"]]), value=item["flavours_2"][0])

            def add_customized_item(e):
                custom_desc = f"{sel_f1.value}, {sel_f2.value}"
                cart[item["id"]] = {"name": item["name"], "price": item["price"], "original": item["original"], "qty": 1, "veg": item["veg"], "details": custom_desc}
                bs.open = False
                page.update()
                show_cart_screen()

            bs = ft.BottomSheet(
                content=ft.Container(
                    content=ft.ListView([
                        ft.Row([
                            ft.Image(src="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=120&q=80", width=50, height=50, border_radius=8),
                            ft.Text(item["name"], size=15, weight=ft.FontWeight.BOLD, expand=True)
                        ], spacing=10),
                        ft.Divider(),
                        ft.Text("Choose your 1st Flavour", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text("Select any 1", size=11, color=SWIGGY_GRAY),
                        sel_f1,
                        ft.Divider(),
                        ft.Text("Choose your 2nd Flavour", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text("Select any 1", size=11, color=SWIGGY_GRAY),
                        sel_f2,
                        ft.ElevatedButton(f"Add Item | ₹{item['price']}", bgcolor=SWIGGY_GREEN, color="white", height=48, on_click=add_customized_item)
                    ], spacing=10),
                    padding=20,
                    bgcolor="white",
                    border_radius=ft.border_radius.only(top_left=20, top_right=20)
                ),
                dismissible=True
            )
            page.overlay.append(bs)
            bs.open = True
            page.update()

        menu_items_col = ft.Column(spacing=12)
        for it in res["menu"]:
            menu_items_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Icon(ft.icons.RADIO_BUTTON_CHECKED if it["veg"] else ft.icons.STOP_CIRCLE_ROUNDED, color="green" if it["veg"] else "red", size=14),
                            ft.Text(it["name"], size=15, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                            ft.Row([
                                ft.Text(f"₹{it['original']}", size=12, color=SWIGGY_GRAY, style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)),
                                ft.Text(f"₹{it['price']}", size=14, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK)
                            ], spacing=6),
                            ft.Text(it["sub"], size=11, color=SWIGGY_GRAY, max_lines=2)
                        ], expand=True, spacing=4),
                        ft.ElevatedButton(
                            "ADD",
                            style=ft.ButtonStyle(color=SWIGGY_GREEN, bgcolor="white", side=ft.BorderSide(1, "#D4D5D9"), shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=lambda e, item=it: open_customizer_modal(item) if item.get("customizable") else direct_add_to_cart({"name": item["name"], "price": item["price"], "original": item["original"], "veg": item["veg"], "hotel": res["name"]})
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=14,
                    bgcolor="white",
                    border_radius=12
                )
            )

        page.add(
            ft.ListView([
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: show_home_screen()),
                        ft.Text(f"{res['name']} • {res['time']}", size=16, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Icon(ft.icons.SEARCH)
                    ]),
                    bgcolor="white", padding=10
                ),
                ft.Container(content=menu_items_col, padding=14)
            ], expand=True)
        )

    # ----------------- 4. SCREEN: CART -----------------
    def show_cart_screen():
        page.clean()

        if not cart:
            page.add(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.REMOVE_SHOPPING_CART, size=60, color=SWIGGY_GRAY),
                        ft.Text("Your Cart is Empty", size=18, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton("GO TO RESTAURANTS", bgcolor=SWIGGY_ORANGE, color="white", on_click=lambda e: show_home_screen())
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
                    alignment=ft.alignment.center, expand=True
                )
            )
            return

        saved_amount = get_cart_original_total() - get_cart_total() + 30
        savings_header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.AUTO_AWESOME, color=SWIGGY_GREEN, size=16),
                ft.Text(f"₹{saved_amount} saved! Including delivery fee savings", color=SWIGGY_GREEN, size=12, weight=ft.FontWeight.BOLD)
            ], spacing=6),
            bgcolor=SWIGGY_OFFER_GREEN_BG,
            padding=10,
            border_radius=10,
            margin=ft.Padding(14, 0, 14, 0)
        )

        cart_items_list = ft.Column(spacing=10)
        for k, v in list(cart.items()):
            def modify_cart(key, delta):
                cart[key]["qty"] += delta
                if cart[key]["qty"] <= 0:
                    del cart[key]
                show_cart_screen()

            cart_items_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.RADIO_BUTTON_CHECKED if v["veg"] else ft.icons.STOP_CIRCLE_ROUNDED, color="green" if v["veg"] else "red", size=14),
                            ft.Column([
                                ft.Text(v["name"], size=14, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                                ft.Text(v.get("details", ""), size=11, color=SWIGGY_GRAY)
                            ], expand=True, spacing=2),
                            ft.Container(
                                content=ft.Row([
                                    ft.IconButton(ft.icons.REMOVE, icon_size=12, icon_color=SWIGGY_GREEN, on_click=lambda e, key=k: modify_cart(key, -1)),
                                    ft.Text(str(v["qty"]), size=13, weight=ft.FontWeight.BOLD, color=SWIGGY_GREEN),
                                    ft.IconButton(ft.icons.ADD, icon_size=12, icon_color=SWIGGY_GREEN, on_click=lambda e, key=k: modify_cart(key, 1))
                                ], spacing=0),
                                bgcolor="white", border=ft.border.all(1, "#DCDCE0"), border_radius=6
                            ),
                            ft.Column([
                                ft.Text(f"₹{v['original'] * v['qty']}", size=11, color=SWIGGY_GRAY, style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)),
                                ft.Text(f"₹{v['price'] * v['qty']}", size=13, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK)
                            ], spacing=0)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.OutlinedButton("+ Add Items", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                            ft.OutlinedButton("✍ Cooking requests", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                            ft.OutlinedButton("Cutlery", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
                        ], spacing=6)
                    ], spacing=10),
                    bgcolor="white", padding=14, border_radius=14
                )
            )

        savings_corner = ft.Container(
            content=ft.Column([
                ft.Text("SAVINGS CORNER", size=11, weight=ft.FontWeight.BOLD, color=SWIGGY_GRAY),
                ft.Row([
                    ft.Icon(ft.icons.LOCAL_OFFER, color=SWIGGY_ORANGE, size=18),
                    ft.Text("Apply Coupon", size=14, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK, expand=True),
                    ft.Icon(ft.icons.CHEVRON_RIGHT, color=SWIGGY_GRAY, size=18)
                ]),
                ft.Divider(thickness=0.5),
                ft.Row([
                    ft.Icon(ft.icons.LOCAL_OFFER, color=SWIGGY_ORANGE, size=18),
                    ft.Text(f"₹{get_cart_original_total() - get_cart_total()} saved with 'Flat 50% off'", size=13, color=SWIGGY_DARK, expand=True),
                    ft.Text("✔ Applied", color=SWIGGY_GREEN, size=12, weight=ft.FontWeight.BOLD)
                ])
            ], spacing=8),
            bgcolor="white", padding=14, border_radius=14
        )

        def proceed_order():
            order_info = {
                "id": f"SWP-{random.randint(10000, 99999)}",
                "items": list(cart.values()),
                "total": get_cart_total(),
                "time": "Just now",
                "rider_name": "Ramesh K.",
                "rider_phone": "+91 9848022338"
            }
            past_orders.append(order_info)
            cart.clear()
            show_tracking_screen(order_info)

        bottom_order_bar = ft.Container(
            content=ft.Column([
                ft.Text("Almost There", size=16, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                ft.Text("Login/Create Account quickly to place order" if not auth_state["logged_in"] else f"Delivering to Narsampet (+91 {auth_state['phone']})", size=11, color=SWIGGY_GRAY),
                ft.ElevatedButton(
                    "Proceed with Phone Number" if not auth_state["logged_in"] else f"Pay ₹{get_cart_total()} & Place Order",
                    bgcolor=SWIGGY_ORANGE,
                    color="white",
                    height=50,
                    width=float("inf"),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    on_click=lambda e: show_login_screen() if not auth_state["logged_in"] else proceed_order()
                )
            ], spacing=6),
            bgcolor="white",
            padding=16,
            border=ft.border.only(top=ft.BorderSide(1, "#E2E2E7"))
        )

        cart_view = ft.ListView([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: show_home_screen()),
                    ft.Text("Swipto Cart", size=16, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK)
                ]),
                bgcolor="white", padding=10
            ),
            savings_header,
            ft.Container(content=cart_items_list, padding=ft.Padding(14, 6, 14, 6)),
            ft.Container(content=savings_corner, padding=ft.Padding(14, 6, 14, 6)),
            ft.Container(height=40)
        ], expand=True)

        page.add(ft.Column([cart_view, bottom_order_bar], expand=True, spacing=0))

    # ----------------- 5. LIVE TRACKING -----------------
    def show_tracking_screen(order):
        page.clean()

        tracking_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE, color=SWIGGY_GREEN, size=28),
                    ft.Column([
                        ft.Text("Order Placed Successfully!", size=16, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                        ft.Text(f"Order ID: {order['id']}", size=12, color=SWIGGY_GRAY)
                    ], spacing=2)
                ], spacing=10),
                ft.Divider(),
                ft.Row([
                    ft.Icon(ft.icons.TIMER, color=SWIGGY_ORANGE, size=24),
                    ft.Column([
                        ft.Text("Estimated Delivery Time", size=12, color=SWIGGY_GRAY),
                        ft.Text("20 - 25 Mins (Arriving at Narsampet)", size=15, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK)
                    ], spacing=2)
                ], spacing=10),
                ft.ProgressBar(value=0.5, color=SWIGGY_ORANGE, bgcolor="#FFE0B2"),
                ft.Text("Status: Restaurant is preparing your food 👨‍🍳", size=13, weight=ft.FontWeight.BOLD, color=SWIGGY_DARK),
                ft.Divider(),
                ft.Row([
                    ft.Container(content=ft.Icon(ft.icons.PERSON, color="white", size=20), bgcolor=SWIGGY_ORANGE, width=40, height=40, border_radius=20, alignment=ft.alignment.center),
                    ft.Column([
                        ft.Text(f"Delivery Partner: {order['rider_name']}", size=13, weight=ft.FontWeight.BOLD),
                        ft.Text("★ 4.8 Rating • Vaccinated", size=11, color=SWIGGY_GRAY)
                    ], expand=True, spacing=2),
                    ft.IconButton(ft.icons.CALL, icon_color=SWIGGY_GREEN, tooltip="Call Partner")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=12),
            bgcolor="white", padding=16, border_radius=16, margin=14,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.colors.BLACK12)
        )

        page.add(
            ft.ListView([
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: show_home_screen()),
                        ft.Text("Live Order Tracking", size=16, weight=ft.FontWeight.BOLD)
                    ]),
                    bgcolor="white", padding=10
                ),
                tracking_card,
                ft.Container(
                    content=ft.ElevatedButton("BACK TO HOME / BROWSE MORE", bgcolor=SWIGGY_ORANGE, color="white", height=46, on_click=lambda e: show_home_screen()),
                    padding=14
                )
            ], expand=True)
        )

    # Start with login screen
    show_login_screen()

# ==================== BOOTSTRAP ====================
if __name__ == "__main__":
    ft.app(target=main)
