from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Hello, PCB Generator!"

@app.route("/api/build", methods=["POST"])
def build_pcb():
    data = request.get_json()
    return jsonify({ "success": True, "message": "Build started" })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
