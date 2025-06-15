import os
import json
import requests
import subprocess
import zipfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

CHAT_FILE = "chat_history.json"
BUILD_DIR = "builds"

def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE) as f:
            return json.load(f)
    return []

def save_chat(history):
    with open(CHAT_FILE, "w") as f:
        json.dump(history[-20:], f)

chat_history = load_chat()

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
    return jsonify(r.json())

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
    data = request.get_json()
    name = data.get("projectName", "MyPCB")
    build_dir = os.path.join(BUILD_DIR, name)
    os.makedirs(build_dir, exist_ok=True)

    kibot_cmd = [
        "kibot",
        "-e", f"{build_dir}/{name}.kicad_sch",
        "-b", f"{build_dir}/{name}.kicad_pcb",
        "-d", f"{build_dir}/output"
    ]

    result = subprocess.run(kibot_cmd, capture_output=True)
    if result.returncode != 0:
        return jsonify({ "success": False, "message": result.stderr.decode() })

    zip_path = os.path.join(build_dir, f"{name}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk(f"{build_dir}/output"):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

    return jsonify({
        "success": True,
        "message": "Build completed.",
        "downloadUrl": f"/{zip_path.replace(os.sep, '/')}"
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
