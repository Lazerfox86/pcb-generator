from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Import Flask-CORS

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

@app.route("/")
def home():
    return "Hello, PCB Generator!"

@app.route("/api/build", methods=["POST"])
def build_pcb():
    data = request.get_json()
    spec = data.get("spec")
    project_name = data.get("projectName")

    # Placeholder logic
    return jsonify({
        "success": True,
        "message": f"Started building {project_name} with spec: {spec}",
        "downloadUrl": f"https://your-render-url.onrender.com/downloads/{project_name}.zip"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
