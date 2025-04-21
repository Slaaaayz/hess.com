from flask import Flask, request, jsonify
from datetime import datetime, UTC
import os
import json

app = Flask(__name__)

LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

@app.route("/", methods=["POST"])
def root():
    # Forward the request to the /log endpoint
    return receive_log()

@app.route("/log", methods=["POST"])
def receive_log():
    try:
        data = request.get_json()
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(LOG_FOLDER, f"log_{timestamp}.json")

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/log", methods=["GET"])
def get_logs():
    try:
        logs = []
        for filename in os.listdir(LOG_FOLDER):
            if filename.endswith(".json"):
                with open(os.path.join(LOG_FOLDER, filename), "r") as f:
                    logs.append(json.load(f))
        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
