import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "Hello from PCB Generator API"

@app.route("/api/build", methods=["POST"])
def build_pcb():
    data = request.get_json()
    project_name = data.get("projectName")
    spec = data.get("spec")
    
    # 🛠 Replace with your real backend logic
    return jsonify({
        "success": True,
        "message": f"Generating '{project_name}' with: {spec}",
        "downloadUrl": f"https://your-cdn.com/{project_name}.zip"
    })

@app.route("/api/spec-gen", methods=["POST"])
def spec_gen():
    description = request.json.get("description", "")
    prompt = f"Generate a concise PCB specification and a project name based on this description:\n{description}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content.strip()
        # 🛠 You can parse this more precisely
        return jsonify({
            "projectName": "GeneratedProject",
            "spec": reply
        })
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

@app.route("/api/chat", methods=["POST"])
def ai_chat():
    message = request.json.get("message", "")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({ "reply": reply })
    except Exception as e:
        return jsonify({ "reply": f"(error: {str(e)})" })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
