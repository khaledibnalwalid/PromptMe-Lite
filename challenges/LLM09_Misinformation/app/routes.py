from flask import request, render_template, jsonify, session
from app import app
from app.utils.llm09_2025_utils.llm09_2025_service import process_user_input_llm09

@app.route("/")
def dashboard():
    if "query_count" not in session:
        session["query_count"] = 0

    return render_template("index.html", query_count=session.get("query_count", 0))

@app.route('/ask', methods=['POST'])
def chat09():
    if "query_count" not in session:
        session["query_count"] = 0

    # Rate limiting: max 20 queries per session
    query_count = session.get("query_count", 0)
    if query_count >= 20:
        return jsonify({
            "reply": "Rate limit exceeded. Maximum 20 queries per session. Please refresh the page.",
            "query_count": query_count
        }), 429

    data = request.json
    user_message = data.get('message', '').strip()

    # Input validation
    if not user_message:
        return jsonify({
            "reply": "Please provide a message",
            "query_count": query_count
        }), 400

    if len(user_message) > 5000:
        return jsonify({
            "reply": "Message too long (max 5000 characters)",
            "query_count": query_count
        }), 400

    # Process the message
    response = process_user_input_llm09(user_message)

    # Increment query counter
    session["query_count"] = query_count + 1
    session.modified = True

    # Add query_count to response
    response_data = response.get_json()
    response_data["query_count"] = session["query_count"]

    return jsonify(response_data)

@app.route("/reset", methods=["POST"])
def reset():
    """Reset session - clear messages and query counter"""
    session.clear()
    return "", 200
