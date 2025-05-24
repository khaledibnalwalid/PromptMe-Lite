from flask import request, render_template
from flask import Flask, jsonify
from app import app
from app.utils.llm09_2025_utils.llm09_2025_service import process_user_input_llm09




@app.route("/")
def dashboard():
    return render_template("index.html")



@app.route('/ask', methods=['POST'])
def chat09():
    data = request.json
    user_message = data.get('message', '')
    return process_user_input_llm09(user_message)

