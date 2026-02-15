from flask import request, render_template, session
from app import app
from app.utils.llm06_2025_utils.llm06_2025_service import process_user_input

@app.route("/")
def home():
    # Clear session on page load to ensure fresh start
    session.clear()
    session["query_count"] = 0

    return render_template("index.html", query_count=session.get("query_count", 0))


@app.route('/llm06_2025_chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    return process_user_input(user_message)