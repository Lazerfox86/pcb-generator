import os
import re
import json
import requests
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# 📁 File Upload Config
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 🧠 Persistent Chat Memory
CHAT_FILE = "chat_history.json"

def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat(history):
    with open(CHAT_FILE, "w") as f:
        json.dump(history[-20:], f)

chat_history = load_chat()

# 🔍 Parse AI responses for project name and spec
def parse_spec_response(text):
    name_match = re.search(r"Project Name:\s*(.+)", text)
    spec_match = re.search(r"Spec:\s*(.+)", text)
    return {
        "projectName": name_match.group(1).strip() if name_match else "UnnamedProject",
        "spec": spec_match.group(1).strip() if spec_match else text.strip()
    }

@app.route("/")
def home():
    return "Hello from your AI PCB backend!"

# ✅ AI Spec Generator using Ollama
@app.route("/api/spec-gen", methods=["POST"])
def spec_gen():
    description = request.json.get("description", "")
    prompt = f"""Generate a concise PCB specification and project name.
Format:
Project Name: ...
Spec: ...

Idea: {description}
"""
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    raw = response.json().get("response", "")
    parsed = parse_spec_response(raw)
    return jsonify(parsed)

# 💬 Chat Assistant with Memory
@app.route("/api/chat", methods=["POST"])
def ai_chat():
    message = request.json.get("message", "")
    chat_history.append({"role": "user", "content": message})
    prompt = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in chat_history[-10:]) + "\nAssistant:"

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    reply = response.json().get("response", "").strip()
    chat_history.append({"role": "assistant", "content": reply})
    save_chat(chat_history)
    return jsonify({ "reply": reply })

# 🔧 Mock PCB build route (replace with real build logic later)
@app.route("/api/build", methods=["POST"])
def build_pcb():
    data = request.get_json()
    project_name = data.get("projectName")
    spec = data.get("spec")
    return jsonify({
        "success": True,
        "message": f"Build simulated for '{project_name}' with spec: {spec}",
        "downloadUrl": f"https://your-cdn.com/{project_name}.zip"
    })

# 📤 File Upload Endpoint
@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({ "error": "No file uploaded" }), 400
    file = request.files["file"]
    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    return jsonify({ "success": True, "filename": filename, "path": path })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
