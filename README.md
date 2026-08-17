# Swipto Advanced Food Delivery

A clean Python/FastAPI food-delivery starter for Swipto, designed for Narsampet.

## Run on Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000

## Render

This repo includes `render.yaml`. Use a Python Web Service and the start command:

`uvicorn app:app --host 0.0.0.0 --port $PORT`

## Included

- Responsive Swipto customer UI
- Food search
- Categories
- Restaurant discovery
- Cart with local persistence
- Checkout
- SQLite order storage
- Order tracking
- Health endpoint
- Render deployment configuration

This is the foundation. Production payments, OTP, maps, push notifications, restaurant dashboard, delivery partner app and admin authentication should be added before real-world launch.
