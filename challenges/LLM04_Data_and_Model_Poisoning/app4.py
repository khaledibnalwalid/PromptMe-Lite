import os, time, sys
from flask import Flask, render_template, request, jsonify, session
from llm_service_1 import get_answer, reload_knowledge_base
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from main .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.secret_key = "S3cr3t_K3y_LLM04"  # For session management

@app.route("/")
def index():
    return render_template("index.html")  # Render the main UI

@app.route("/ask", methods=["POST"])
def ask_question():
    # Rate limiting: max 20 queries per session
    query_count = session.get("query_count", 0)
    if query_count >= 20:
        return jsonify({"error": "Rate limit exceeded. Maximum 20 queries per session. Please refresh the page."}), 429

    question = request.json.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Input validation
    if len(question) > 5000:
        return jsonify({"error": "Question too long (max 5000 characters)"}), 400

    try:
        output = get_answer(question)

        # Increment session query counter
        session["query_count"] = query_count + 1

        return jsonify({"answer": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reload", methods=["POST"])
def reload_data():
    success = reload_knowledge_base()
    if success:
        return jsonify({"message": "🔄 Knowledge base reloaded successfully!"})
    else:
        return jsonify({"error": "❌ Failed to reload knowledge base"}), 500

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5004)

