# SWIPTO Final Starter App

Run locally:
pip install -r requirements.txt
python app.py

Open: http://127.0.0.1:5000

Render:
Build command: pip install -r requirements.txt
Start command: gunicorn app:app

Important:
- Phone OTP is intentionally not included.
- Google Login is shown as a UI hook. For real Firebase Google login, add your Firebase Web App config and secure backend/session handling.
- Orders currently use browser localStorage for demo purposes. Production should use a real database and server-side APIs.
- Configure your own owner WhatsApp integration on the backend. Do not expose API keys or secrets in index.html.
