import os
import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory chat history (can be replaced with Redis or DB later)
chat_history = []

# Helper to parse structured spec output
def parse_spec_response(text):
    name_match = re.search(r"Project Name:\s*(.+)", text)
    spec_match = re.search(r"Spec:\s*(.+)", text)
    return {
        "projectName": name_match.group(1).strip() if name_match else "UnnamedProject",
        "spec": spec_match.group(1).strip() if spec_match else text.strip()
    }

@app.route("/")
def home():
    return "Hello from your locally supercharged PCB Generator!"

@app.route("/api/build", methods=["POST"])
def build_pcb():
    data = request.get_json()
    project_name = data.get("projectName")
    spec = data.get("spec")
    return jsonify({
        "success": True,
        "message": f"Build initiated for '{project_name}' with spec: {spec}",
        "downloadUrl": f"https://pcb-generator.onrender.com/{project_name}.zip"
    })

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

@app.route("/api/chat", methods=["POST"])
def ai_chat():
    message = request.json.get("message", "")
    chat_history.append({"role": "user", "content": message})

    # Flatten history into a single prompt
    full_prompt = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history[-10:]
    ) + "\nAssistant:"

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": full_prompt,
        "stream": False
    })

    reply = response.json().get("response", "").strip()
    chat_history.append({"role": "assistant", "content": reply})
    return jsonify({ "reply": reply })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
