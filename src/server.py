import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Hello from your locally supercharged PCB Generator!"

@app.route("/api/build", methods=["POST"])
def build_pcb():
    data = request.get_json()
    project_name = data.get("projectName")
    spec = data.get("spec")

    # 🛠 Replace with actual build logic if needed
    return jsonify({
        "success": True,
        "message": f"Build initiated for '{project_name}' with spec: {spec}",
        "downloadUrl": f"https://your-cdn.com/{project_name}.zip"
    })

@app.route("/api/spec-gen", methods=["POST"])
def spec_gen():
    description = request.json.get("description", "")
    ollama_response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": f"Generate a concise PCB spec and project name for this project idea:\n{description}",
        "stream": False
    })

    result = ollama_response.json().get("response", "").strip()

    # You could parse response here if needed
    return jsonify({
        "projectName": "GeneratedProject",
        "spec": result
    })

@app.route("/api/chat", methods=["POST"])
def ai_chat():
    message = request.json.get("message", "")
    ollama_response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": f"You are an electronics and PCB design expert. Respond to this user query:\n{message}",
        "stream": False
    })

    reply = ollama_response.json().get("response", "").strip()
    return jsonify({ "reply": reply })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
