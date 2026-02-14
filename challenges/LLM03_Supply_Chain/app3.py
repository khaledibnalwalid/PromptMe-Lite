import subprocess
import threading
import os
import secrets
from flask import Flask, render_template, request, jsonify, session
from models import generate_response, MODEL_REGISTRY
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from main .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.secret_key = "S3cret_Key"  # Needed for session
CORS(app)  # Allow frontend JS to call backend APIs

# Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# ----- Home page -----
@app.route("/")
def index():
    return render_template("index.html")

# ----- Model Documentation -----
@app.route("/readme")
def readme():
    return render_template("readme.html")

# ----- List available models -----
@app.route("/models", methods=["GET"])
def list_models():
    return jsonify({"models": list(MODEL_REGISTRY.keys())})

# ----- Initialize model (could add lazy loading later) -----
@app.route("/init_model", methods=["POST"])
def init_model():
    data = request.json
    model_name = data.get("model")
    if model_name not in MODEL_REGISTRY:
        return jsonify({"error": "Invalid model"}), 400

    # Generate unique session ID for this user
    if "session_id" not in session:
        session["session_id"] = secrets.token_hex(8)  # 16 character session ID

    session["model"] = model_name
    session["history"] = []
    return jsonify({"message": f"{model_name} initialized"})

# ----- Handle chat -----
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "")
    model_name = session.get("model")
    history = session.get("history", [])

    if not model_name:
        return jsonify({"error": "Model not initialized"}), 400

    # Input validation: limit prompt length
    if len(prompt) > 5000:
        return jsonify({"error": "Prompt too long (max 5000 characters)"}), 400

    if not prompt.strip():
        return jsonify({"error": "Prompt cannot be empty"}), 400

    # Get or create session ID
    session_id = session.get("session_id", secrets.token_hex(8))
    session["session_id"] = session_id

    try:
        # Generate response (pass session_id for exfiltration tracking)
        response = generate_response(model_name, history, prompt, session_id)
    except Exception as e:
        return jsonify({"error": f"LLM error: {str(e)}"}), 500

    # Save conversation with truncation for user messages
    user_msg = prompt[:500] if len(prompt) > 500 else prompt  # Truncate long prompts
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": response})

    # Cap history at 10 messages for scalability (5 exchanges)
    if len(history) > 10:
        history = history[-10:]

    session["history"] = history

    return jsonify({"response": response})

if __name__ == "__main__":
	def listener():
		subprocess.Popen(["python3", "config/secret-service.py"], cwd=os.path.dirname(__file__), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)

	# Run in a thread so it doesn't block Flask
	threading.Thread(target=listener, daemon=True).start()

	# Print provider info
	print(f"[INFO] Starting LLM03 Supply Chain Challenge with provider: {LLM_PROVIDER}")
	if LLM_PROVIDER == "openai":
		print(f"[INFO] Using OpenAI model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
	else:
		print(f"[INFO] Using Ollama model: {os.getenv('OLLAMA_CHAT_MODEL', 'granite3.1-moe:1b')}")

	app.run(host="0.0.0.0", port=5003, debug=False)
