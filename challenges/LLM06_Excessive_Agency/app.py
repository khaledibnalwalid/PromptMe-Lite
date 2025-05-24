from app import app
from app.utils.llm06_2025_utils.llm06_2025_service import process_user_input

@app.route('/llm06_2025_chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    return process_user_input(user_message)


