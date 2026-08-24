from flask import Flask, send_from_directory, jsonify

app = Flask(__name__, static_folder="static")


# Home page
@app.route("/")
def home():
    return send_from_directory("static", "index.html")


# Health check for Render
@app.route("/api/health")
def health():
    return jsonify({
        "status": "success",
        "message": "Swipto is running 🚀"
    })


# App information
@app.route("/api/info")
def info():
    return jsonify({
        "app": "Swipto",
        "location": "Narsampet",
        "service": "Food Delivery"
    })


# Run locally / Render
if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
