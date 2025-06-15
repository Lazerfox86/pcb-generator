import os
import re
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

CHAT_FILE = "chat_history.json"

def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE) as f:
            return json.load(f)
    return []

def save_chat(history):
    with open(CHAT_FILE, "w") as f:
        json.dump(history[-20:], f)

chat_history = load_chat()

def parse_spec_response(text):
    name = re.search(r"Project Name:\s*(.+)", text)
    spec = re.search(r"Spec:\s*(.+)", text)
    return {
        "projectName": name.group(1).strip() if name else "Unnamed",
        "spec": spec.group(1).strip() if spec else text.strip()
    }

@app.route("/")
def home():
    return "👋 PCB AI Backend is live"

@app.route("/api/spec-gen", methods=["POST"])
def spec_gen():
    description = request.json.get("description", "")
    prompt = f"Generate a concise PCB specification and project name.\n\nIdea: {description}\n\nFormat:\nProject Name: ...\nSpec: ..."
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    parsed = parse_spec_response(r.json().get("response", ""))
    return jsonify(parsed)

@app.route("/api/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "")
    chat_history.append({"role": "user", "content": msg})
    prompt = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in chat_history[-10:]) + "\nAssistant:"
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    reply = r.json().get("response", "").strip()
    chat_history.append({"role": "assistant", "content": reply})
    save_chat(chat_history)
    return jsonify({ "reply": reply })

@app.route("/api/build", methods=["POST"])
def build():
    name = request.json.get("projectName")
    spec = request.json.get("spec")
    return jsonify({
        "success": True,
        "message": f"Build simulated for {name}",
        "downloadUrl": f"https://example.com/downloads/{name}.zip"
    })

@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({ "error": "No file uploaded" }), 400
    file = request.files["file"]
    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    return jsonify({ "success": True, "filename": filename, "path": path })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
